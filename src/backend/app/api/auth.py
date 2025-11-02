from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from dotenv import load_dotenv
import os
from app.core.security import authenticate_user, create_access_token, get_current_active_user, get_current_user, get_user, get_password_hash
from app.schemas.user import User, Token, UserInDB, UserCreate, UserRead
from app.core.database import get_db
from app.models import user
from sqlalchemy.orm import Session
from app.crud.user import create_user
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

load_dotenv()
router = APIRouter()
@router.get("/ping")
def ping():
    return {"message": "Auth route is working!"}

#route for user login in and token is generated
@router.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()): # Data accepted to generate a JWT is username and password, depending on data to parse
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    TOKEN_EXPIRES = int(os.getenv("TOKEN_EXPIRES", "30"))
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type":"bearer"}

#rotue for user signup
@router.post("/signUp", response_model=User, status_code=status.HTTP_201_CREATED) #response modle is of type User
async def signUp(user_in: UserCreate , db: Session = Depends(get_db)): #user_in is of type schema

    existing = get_user(db, user_in.username) #check if user already exists by fetching user by username
    if existing: #if user exists raise HTTP exception with status code 400 and display message as User already exists
        raise HTTPException(status_code=400, detail="User already exists")
    
    #get the password hash for the user if new user
    hashed_password = await get_password_hash(user_in.password)
    #send the hash and UserCreate data to create_user crud function
    new_user = await create_user(db, user_in, hashed_password)

    return new_user #return the new user created




