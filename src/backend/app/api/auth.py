"""
auth.py (router)
================
FastAPI route definitions for authentication and user registration.

Handles JWT token generation on login and new user account creation.
Token expiry is configurable via the TOKEN_EXPIRES environment variable.
All passwords are hashed before storage — plaintext is never persisted.

Endpoints:
  GET  /ping     - Health check to confirm the auth router is reachable
  POST /token    - Authenticate with username + password, returns JWT bearer token
  POST /signUp   - Register a new user account

Dependencies:
  - FastAPI APIRouter, Depends, HTTPException
  - OAuth2PasswordRequestForm for standard login form parsing
  - SQLAlchemy ORM session via get_db
  - Internal: app.core.security, app.schemas.user, app.crud.user
"""

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
    """Health check endpoint to confirm the auth router is reachable."""
    return {"message": "Auth route is working!"}


@router.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a signed JWT bearer token.

    Accepts standard OAuth2 username and password form fields. Token expiry
    is read from the TOKEN_EXPIRES environment variable (default: 30 minutes).

    Args:
        db:        Active SQLAlchemy session.
        form_data: OAuth2 form containing username and password fields.

    Raises:
        HTTPException 401: If the username does not exist or the password is incorrect.

    Returns:
        Dict containing the signed access_token and token_type ("bearer").
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    TOKEN_EXPIRES = int(os.getenv("TOKEN_EXPIRES", "30"))
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signUp", response_model=User, status_code=status.HTTP_201_CREATED)
async def signUp(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Checks for an existing account with the same username before creating.
    The plaintext password is hashed before being passed to the CRUD layer —
    it is never stored or logged.

    Args:
        user_in: Validated UserCreate schema containing username, email, and password.
        db:      Active SQLAlchemy session.

    Raises:
        HTTPException 400: If a user with the same username already exists.

    Returns:
        The newly created User object with status 201 Created.
    """
    existing = get_user(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = await get_password_hash(user_in.password)
    new_user = await create_user(db, user_in, hashed_password)

    return new_user