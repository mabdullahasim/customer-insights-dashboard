from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from dotenv import load_dotenv
import os
from app.core.security import authenticate_user, create_access_token, get_current_active_user
from app.schemas.user import User, Token, UserInDB
from app.core.database import get_db
from app.models import user

load_dotenv()
router = APIRouter()
@router.get("/ping")
def ping():
    return {"message": "Auth route is working!"}

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

@router.post("/signUp", response_model=User, status_code=status.HTTP_201_CREATED)
async def signUp(user_in: UserCreate , db: Session = Depends(get_db)):
    existing = get_user(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail"User already exists")
    
    hashed_password = get_password_hash(user_in.password)

    new_user = user_create(db, user_in hashed_password)

    return new_user


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user.dict()}]