from passlib.context import CryptContext
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from app.schemas.user import UserInDB, User, Token
from app.models.user import User
from app.core.database import get_db
from pydantic import BaseModel
from password_validator import PasswordValidator

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRES = int(os.getenv("TOKEN_EXPIRES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Handling password hashing using bcrypt
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # Tells FastAPI where to get the token from


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def verify_password(plain_password, hashed_password):       # Compares the plain text password from user input with hashed password stored in DB
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):                            # Takes plain text pwd and returns hashed password.
    password_check = await password_validation(password)
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> UserInDB | None:
    # DB:session SQLALchemy database session passed in from route
    # Username: str (the username to look up)
    # --> UserInDB : None (returns pydantic object if found otherwise none)

    # Query the DB for a user with this username
    db_user = db.query(User).filter(User.username == username).first()
    
    # If user exists, return as a Pydantic object
    if db_user:
        return UserInDB.from_orm(db_user)
    
    return None


def authenticate_user(db: Session, username: str, password: str):
    # Check if username and password combination is valid
    # Returns UserInDB object if successful

    user = get_user(db, username)  # Calls get user to fetch user from database using SQLAlchemy, User will be a pydantic model or none

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user # Return user in DB object


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:   # if expiration time was passed use it otherwise default to 15 minutes
        expire = datetime.utcnow() + expires_delta # Set token expiration time to now + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # Set now + 15 minutes as expiration time

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth_2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def password_validation(password: str):
    schema = PasswordValidator()
    schema.min(8).max(20).has().uppercase().has().lowercase().has().digits().has().symbols()

    result = schema.validate(password, details=True)

    if result is True:
        return password
    else:
        for rule in results:
            if rule == 'min':
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
            elif rule == 'max':
                raise HTTPException(status_code=400, detail="Password must not exceed 20 characters")
            elif rule == 'uppercase':
                raise HTTPException(status_code=400, detail="Password must include at least one uppercase")
            elif rule == 'lowercase':
                raise HTTPException(status_code=400, detail="Password must include at least one lowercase")
            elif rule == 'digits':
                raise HTTPException(status_code=400, detail="Password must include at least one digit")
            elif rule == 'symbols':
                raise HTTPException(status_code=400, detail="Password must inlcude at least 1 symbol")

    
async def username_validation():