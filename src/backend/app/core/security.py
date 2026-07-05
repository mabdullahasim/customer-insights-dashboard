"""
security.py
===========
Authentication and security utilities for the FastAPI application.

Handles all JWT token creation and validation, password hashing and
verification, user lookup, and FastAPI dependency injection for
protected routes. Password validation enforces complexity rules before
any hash is generated.

Exports:
  pwd_context              - Bcrypt password hashing context
  oauth_2_scheme           - OAuth2 bearer token scheme
  Token                    - Pydantic model for token response
  TokenData                - Pydantic model for decoded token payload
  verify_password          - Compare plaintext against a bcrypt hash
  get_password_hash        - Validate and hash a plaintext password
  get_user                 - Fetch a user by username from the database
  get_user_by_email        - Fetch a user by email from the database
  authenticate_user        - Validate username + password combination
  create_access_token      - Sign and return a JWT bearer token
  get_current_user         - FastAPI dependency to decode and validate a JWT
  get_current_active_user  - FastAPI dependency to enforce active user status
  password_validation      - Enforce password complexity rules

Dependencies:
  - passlib (bcrypt), python-jose (JWT), password-validator
  - FastAPI Depends, HTTPException
  - SQLAlchemy ORM session
  - python-dotenv
"""

from passlib.context import CryptContext
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from app.schemas.user import UserInDB
from app.models.user import User as UserModel
from app.core.database import get_db
from pydantic import BaseModel
from password_validator import PasswordValidator
import re


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRES = int(os.getenv("TOKEN_EXPIRES", 30))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Handling password hashing using bcrypt
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # Tells FastAPI where to get the token from


class Token(BaseModel): #token model
    access_token: str
    token_type: str


class TokenData(BaseModel): #tokenData model
    username: str | None = None


def verify_password(plain_password, hashed_password):       # Compares the plain text password from user input with hashed password stored in DB
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:                 # Takes plain text pwd and returns hashed password.
    password_check = await password_validation(password) #calls password_validation to check if password is valid
    return pwd_context.hash(password) #return password hash


def get_user(db: Session, username: str) -> UserInDB | None:
    """
    Fetch a user record by username.

    Args:
        db:       Active SQLAlchemy session passed in from the route.
        username: The username string to look up.

    Returns:
        UserInDB Pydantic object if found, otherwise None.
    """
    # Query the DB for a user with this username
    db_user = db.query(UserModel).filter(UserModel.username == username).first()

    # If user exists, return as a Pydantic object
    if db_user:
        return UserInDB.from_orm(db_user)

    return None


def get_user_by_email(db: Session, email: str) -> UserInDB | None:
    """
    Fetch a user record by email address.

    Args:
        db:    Active SQLAlchemy session.
        email: The email address to look up.

    Returns:
        UserInDB Pydantic object if found, otherwise None.
    """
    db_user = db.query(UserModel).filter(UserModel.email == email).first()

    if not db_user:
        return None

    return UserInDB.from_orm(db_user)


def authenticate_user(db: Session, username: str, password: str):
    """
    Validate a username and password combination against the database.

    Args:
        db:       Active SQLAlchemy session.
        username: Username string submitted by the client.
        password: Plaintext password submitted by the client.

    Returns:
        UserInDB object if credentials are valid, otherwise False.
    """
    user = get_user(db, username)  # Calls get user to fetch user from database using SQLAlchemy, User will be a pydantic model or none

    if not user: #if username does not match return false.
        return False

    if not verify_password(password, user.hashed_password): #if password does not match return false.
        return False

    return user # Return user in DB object


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create and sign a JWT bearer token.

    Args:
        data:          Dict of claims to encode into the token (e.g. {"sub": username}).
        expires_delta: Optional custom expiry duration; defaults to 15 minutes.

    Returns:
        Signed JWT string.
    """
    to_encode = data.copy()

    if expires_delta:   # if expiration time was passed use it otherwise default to 15 minutes
        expire = datetime.utcnow() + expires_delta # Set token expiration time to now + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # Set now + 15 minutes as expiration time

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth_2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency that decodes and validates a JWT bearer token.

    Extracts the username from the token payload and fetches the matching
    user from the database. Raises 401 if the token is invalid, expired,
    or the user no longer exists.

    Args:
        token: Bearer token extracted from the Authorization header.
        db:    Active SQLAlchemy session.

    Raises:
        HTTPException 401: If credentials cannot be validated.

    Returns:
        Validated UserInDB Pydantic object for the token owner.
    """
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

    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception

    return UserInDB.model_validate(user)


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    """
    FastAPI dependency that enforces the authenticated user is active.

    Args:
        current_user: UserInDB object injected by get_current_user.

    Raises:
        HTTPException 400: If the user account is marked inactive.

    Returns:
        The active UserInDB object.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def password_validation(password: str):
    """
    Enforce password complexity rules before hashing.

    Rules: 8–16 characters, must include uppercase, lowercase, digit,
    and symbol, and must contain no spaces.

    Args:
        password: Plaintext password string to validate.

    Raises:
        HTTPException 400: If the password does not meet complexity requirements.

    Returns:
        The original password string if validation passes.
    """
    PASSWORD_SCHEMA = (
        PasswordValidator()
        .min(8).max(16)
        .has().uppercase()
        .has().lowercase()
        .has().digits()
        .has().symbols()
        .no().spaces()
    )
    if not PASSWORD_SCHEMA.validate(password):     # returns bool
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8–16 chars, include upper, lower, digit, symbol, and have no spaces."
        )
    return password