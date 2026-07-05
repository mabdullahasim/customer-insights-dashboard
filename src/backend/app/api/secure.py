"""
secure.py (router)
==================
FastAPI route definitions for authenticated user profile access.

Exposes protected endpoints that require a valid JWT token. Used to
verify authentication is working and to retrieve basic profile data
for the currently logged-in user.

Endpoints:
  GET /secure/profile - Return the authenticated user's username

Dependencies:
  - FastAPI APIRouter, Depends
  - JWT auth via get_current_user
  - Internal: app.core.security, app.schemas.user
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user import UserInDB


router = APIRouter(prefix="/secure", tags=["secure"])


@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    """
    Return the authenticated user's profile data.

    Args:
        current_user: Authenticated user injected via JWT dependency.

    Returns:
        Dict containing the authenticated user's username.
    """
    return {"username": current_user.username}