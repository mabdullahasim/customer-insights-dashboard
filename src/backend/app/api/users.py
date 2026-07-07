"""
users.py (router)
=================
FastAPI route definitions for user account management.

Handles password reset and authenticated user self-lookup. Password
hashing is performed before the CRUD layer is invoked — plaintext
passwords are never stored or logged.

Endpoints:
  POST /users/forgotPassword - Reset password for a user identified by email
  GET  /users/me             - Return the currently authenticated user's profile

Dependencies:
  - FastAPI APIRouter, Depends, HTTPException
  - SQLAlchemy ORM session via get_db
  - JWT auth via get_current_active_user
  - Internal: app.core.security, app.crud.user, app.schemas.user
"""

from app.models.user import User
from app.schemas.user import ForgotPassword
from fastapi import APIRouter, status, Depends, HTTPException
from app.core.security import get_user_by_email, get_password_hash
from sqlalchemy.orm import Session
from app.crud.user import change_password
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from app.schemas.user import *
from app.core.security import get_current_active_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/forgotPassword", response_model=User, status_code=status.HTTP_200_OK)
async def forgotPassword(user_in: ForgotPassword, db: Session = Depends(get_db)):
    """
    Reset the password for a user identified by their email address.

    Looks up the user by email, hashes the new password, and persists the
    update via the change_password CRUD function. No authentication token
    is required — the email address acts as the identity proof.

    Args:
        user_in: ForgotPassword schema containing the user's email and new password.
        db:      Active SQLAlchemy session.

    Raises:
        HTTPException 400: If no user with the provided email address exists.

    Returns:
        The updated User object with status 200 OK.
    """
    db_user = get_user_by_email(db, user_in.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User with that email does not exist")

    hashed_password = await get_password_hash(user_in.password)
    updated_user = change_password(db, db_user, hashed_password)

    return updated_user


@router.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_active_user)):
    """
    Return the profile of the currently authenticated user.

    Args:
        current_user: Authenticated user injected via JWT dependency.

    Returns:
        User object for the currently logged-in user.
    """
    return current_user