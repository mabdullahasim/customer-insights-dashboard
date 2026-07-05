"""
user.py (schemas)
=================
Pydantic request and response schemas for the user module.

Defines the data shapes used for user registration, authentication,
profile reads, password resets, and JWT token responses.

Schemas:
  User           - Base user response schema returned by protected endpoints
  UserInDB       - Extends User with hashed_password for internal auth use
  UserCreate     - Registration payload with username validation
  UserRead       - Lightweight public profile response
  UserUpdate     - Payload for updating user account fields
  Token          - JWT bearer token response returned on successful login
  ForgotPassword - Payload for resetting a password via email

Dependencies:
  - Pydantic BaseModel, field_validator
"""

from pydantic import BaseModel, field_validator
import re


class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserInDB(User):
    hashed_password: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    def check_username(cls, v: str) -> str:
        """
        Validate that the username meets format requirements.

        Rules: 8–12 characters, letters, numbers, and underscores only.

        Raises:
            ValueError: If the username does not match the required pattern.

        Returns:
            The validated username string.
        """
        if not re.match(r'^[a-zA-Z0-9_]{8,12}$', v):
            raise ValueError("Username must be 8–12 characters, letters/numbers/underscores only")
        return v


class UserRead(BaseModel):
    username: str
    email: str
    is_active: bool


class UserUpdate(BaseModel):
    username: str
    email: str
    hashed_password: str


# Token model for JWT responses
class Token(BaseModel):
    access_token: str
    token_type: str


class ForgotPassword(BaseModel):
    email: str
    password: str