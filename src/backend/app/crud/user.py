"""
user.py
=======
CRUD operations for the User model.

Handles database interactions for user account management including
account creation and password updates. Password hashing is handled
upstream by the caller before these functions are invoked.

Operations:
  - create_user      : Insert a new user record with a hashed password
  - change_password  : Update the hashed password for an existing user

Dependencies:
  - SQLAlchemy ORM session
  - Internal: app.schemas.user, app.models.user, app.core.security
"""

from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import UserModel, get_user


async def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User:
    """
    Insert a new user record into the database.

    The caller is responsible for hashing the password before passing it in.
    New accounts are assigned the default role of "user" and are active on creation
    Args:
        db:              Active SQLAlchemy session.
        user_in:         Validated UserCreate schema containing username and email.
        hashed_password: Bcrypt-hashed password string to store.
    Returns:
        The newly created User ORM object, refreshed from the database.
    """
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        role="user",
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def change_password(db: Session, db_user: UserModel, hashed_password: str) -> User:
    """
    Update the hashed password for an existing user.
    The caller is responsible for hashing the new password before passing it in.
    Args:
        db:              Active SQLAlchemy session.
        db_user:         The authenticated UserModel ORM object to update.
        hashed_password: New bcrypt-hashed password string to store.
    Returns:
        The updated User ORM object, refreshed from the database.
    """
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user