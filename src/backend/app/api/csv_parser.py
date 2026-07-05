"""
utils.py (router)
=================
FastAPI route definitions for utility operations.

Provides endpoints for bulk data management tasks such as CSV file imports.
All routes are protected by JWT authentication and scoped to the authenticated
user's account.

Endpoints:
  POST /utils/upload/customers - Upload a CSV file to bulk import customer records

Dependencies:
  - FastAPI APIRouter, Depends, UploadFile, File, HTTPException
  - SQLAlchemy ORM session via get_db
  - JWT auth via get_current_active_user
  - Internal: app.crud.data_import, app.schemas.analytics
"""

from fastapi import FastAPI, UploadFile, File
from app.schemas.customer import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, HTTPException
from app.schemas.analytics import Message
from fastapi import APIRouter
from app.crud.data_import import data_import
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi import Depends
from app.core.security import get_current_active_user

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post("/upload/customers", response_model=Message)
async def upload_customers(file: UploadFile = File(...), current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """
    Accept a CSV file upload and bulk upsert customer records for the authenticated user.

    Validates that the uploaded file is a CSV before passing it to the
    data_import service, which handles parsing, validation, and database upserts.

    Args:
        file:         Uploaded file; must have a .csv extension.
        current_user: Authenticated user injected via JWT dependency.
        db:           Active SQLAlchemy session.

    Raises:
        HTTPException 400: If the uploaded file is not a CSV.

    Returns:
        Message confirming how many customer rows were imported.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")

    return await data_import(file, current_user.id, db)