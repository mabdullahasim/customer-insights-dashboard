"""
user.py (model)
===============
SQLAlchemy ORM model for the users table.

Defines the schema for user accounts, including authentication fields
and account status. This model is used by the auth and user routers
for login, registration, and password management.

Table: users

Columns:
  id              - Primary key, auto-incremented integer
  username        - Non-nullable display name and login identifier
  email           - Unique, non-nullable email address
  role            - Account role string (e.g. "user", "admin")
  hashed_password - Bcrypt-hashed password; plaintext is never stored
  is_active       - Boolean flag; False disables access via get_current_active_user

Dependencies:
  - SQLAlchemy
  - Internal: app.core.database.Base
"""

from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)