"""
data_import.py
==============
CSV import service for bulk customer data ingestion.

Accepts a CSV file upload, validates its structure and size, parses each
row into a CustomerCreate schema, and upserts every record into the database
via create_customer (insert or update if email already exists for this user).

Expected CSV columns:
  Required : full_name, email, total_spent
  Optional : country, last_purchase_date, review_score, review_text

Constraints:
  - Maximum file size : 5MB
  - Encoding         : UTF-8 or UTF-8 with BOM (Excel exports supported)
  - total_spent      : Strips $ and commas before parsing as float
  - review_score     : Parsed as int; skipped if blank

Dependencies:
  - FastAPI UploadFile / HTTPException
  - SQLAlchemy ORM session
  - Internal: app.schemas.customer, app.crud.customer, app.schemas.analytics
"""

from app.schemas.customer import *
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.crud.customer import create_customer
import csv, io
from app.schemas.analytics import Message


async def data_import(file: UploadFile, user_id: int, db: Session):
    """
    Parse and bulk-upsert customers from an uploaded CSV file.

    Reads the uploaded file into memory, validates size and required columns,
    parses each row into a customer dict, and calls create_customer() for
    every row (which handles insert-or-update by email).

    Args:
        file:    FastAPI UploadFile object containing the CSV data.
        user_id: ID of the authenticated user; all imported customers areassigned to this account.
        db:      Active SQLAlchemy session.

    Raises:
        HTTPException 400: If the file exceeds 5MB.
        HTTPException 400: If any required columns are missing from the CSV header.

    Returns:
        Message confirming how many customer rows were processed.
    """
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    required = {"full_name", "email", "total_spent"}

    decoded = contents.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(decoded))

    if not required.issubset(reader.fieldnames or []):
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {required - set(reader.fieldnames)}"
        )

    customers = []
    for row in reader:
        customers.append({
            "full_name":          row["full_name"].strip(),
            "email":              row["email"].strip().lower(),
            "country":            row["country"].strip() or None,
            "total_spent":        float(row["total_spent"].replace("$", "").replace(",", "")) if row["total_spent"].strip() else 0,
            "last_purchase_date": row["last_purchase_date"].strip() or None,
            "review_score":       int(float(row["review_score"])) if row["review_score"].strip() else None,
            "review_text":        row["review_text"].strip() or None,
        })
    for customer in customers:
        await create_customer(db, CustomerCreate(**customer), user_id)

    return Message(message=f"Uploaded {len(customers)} customers")