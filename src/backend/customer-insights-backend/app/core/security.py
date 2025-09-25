from passlib.context import CryptContext
from fastapi import FastAPI, status, Depends, HTTPException
import models
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JwtError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
TOKEN_EXPIRES = os.getenv("TOKEN_EXPIRES")

class Token(BaseModel): # Response shape for JWT tokens
    access_token: str
    token_type: str

class TokenData(BaseModel): # Stores decoded token info after verifying JWT
    username: str or None = None

#----------------------------
#    Password hashing
#----------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Handling password hashing using bcrypt
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token") # Tells FastAPI where to get the token from

def verify_password(plain_password, hashed_password):       # Compares the plain text password from user input with hashed password stored in DB
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):                            # Takes plain text pwd and returns hashed password.
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

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    # Create a JWT to  authenticate requests from the user

    to_encode = data.copy() # Copy data which is a dictionary containing user info, Copy so we dont modify the original

    if expires_delta:   # if experation time was passed use it otherwise default to 15 minutes
        expire = datetime.utcnow() + expires_delta # Set token expiration time to now + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # Set now + 15 minutes as expiration time

    to_encode.update({"exp": expire}) # Adds the expiration time to the payload of the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Creates the actual JWT string using the data to_encode, secret key and algo.

    return encoded_jwt # REturn the JWT string



