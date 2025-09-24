from passlib.context import CryptContext
from fastapi import FastAPI, status, Depends, HTTPException
import models
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.sequrity import OAuth2PasswordBearer, OAuth2PasswordRequestFrom
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JwtError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
TOKEN_EXPIRES = os.getenv("TOKEN_EXPIRES")

class Token(BaseModeL):
    access_token: str
    token_type: str

class TokenData(BaseModeL):
    username: str or None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

