"""
database.py
===========
SQLAlchemy database engine and session configuration.

Reads the database connection URL from the DATABASE_URL environment variable
and configures the engine, session factory, and declarative base used across
all models and CRUD operations. Falls back to a local SQLite database if no
environment variable is set, which is useful for development and testing.

Exports:
  engine       - SQLAlchemy engine instance bound to the configured database
  SessionLocal - Session factory used to create individual DB sessions
  Base         - Declarative base class for all ORM models
  get_db       - FastAPI dependency that yields a scoped DB session per request

Dependencies:
  - SQLAlchemy
  - python-dotenv
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a database session for the duration of a request.

    Yields a SQLAlchemy session and ensures it is closed after the request
    completes, whether or not an exception was raised.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()