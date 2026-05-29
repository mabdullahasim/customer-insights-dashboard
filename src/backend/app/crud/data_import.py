
from app.schemas.customer import *
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.crud.customer import create_customer
import csv, io
from app.schemas.analytics import Message


async def data_import(file: UploadFile, user_id: int, db: Session):
    contents = await file.read()

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")
    required = {"full_name", "email", "total_spent"}



    # handle both UTF-8 and UTF-8 with BOM (from Excel)
    decoded = contents.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(decoded))
    if not required.issubset(reader.fieldnames or []):
        raise HTTPException(status_code=400, detail=f"Missing columns: {required - set(reader.fieldnames)}")

    customers = []
    for row in reader:
        customers.append({
            "full_name":          row["full_name"].strip(),
            "email":              row["email"].strip().lower(),
            "country":            row["country"].strip() or None,
            "total_spent":        float(row["total_spent"].replace("$", "").replace(",", "")) if row["total_spent"].strip() else 0,
            "last_purchase_date": row["last_purchase_date"].strip() or None,
            "review_score": int(float(row["review_score"])) if row["review_score"].strip() else None,
            "review_text":        row["review_text"].strip() or None,
        })

    for customer in customers:
        await create_customer(db, CustomerCreate(**customer), user_id)

    return Message(message=f"Uploaded {len(customers)} customers")
