"""
customers.py (router)
=====================
FastAPI route definitions for customer record management.

Exposes standard CRUD endpoints for creating, reading, updating, and deleting
customer records. All routes are protected by JWT authentication and all
queries are scoped to the authenticated user's data.

Endpoints:
  GET    /customers/              - Paginated list of the current user's customers
  GET    /customers/{customer_id} - Fetch a single customer by ID
  PUT    /customers/{customer_id} - Partially update a customer record
  DELETE /customers/{customer_id} - Delete a customer record

Dependencies:
  - FastAPI APIRouter, Depends, HTTPException
  - SQLAlchemy ORM session via get_db
  - JWT auth via get_current_active_user
  - Internal: app.crud.customer, app.schemas.customer
"""

from app.models.customer import Customer
from app.schemas.customer import *
from fastapi import APIRouter, status, Depends, HTTPException
from app.core.security import get_user_by_email, get_password_hash
from sqlalchemy.orm import Session
from app.crud.customer import *
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from typing import List
from app.core.security import get_current_active_user


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=list[CustomerRead])
async def list(skip: int = 0, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """
    Return a paginated list of customers belonging to the authenticated user.

    Args:
        skip:         Number of records to skip for pagination (default: 0).
        current_user: Authenticated user injected via JWT dependency.
        db:           Active SQLAlchemy session.

    Returns:
        List of CustomerRead objects (max 10 per page).
    """
    return list_customers(db, skip, current_user.id)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_one_customer(customer_id: int, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """
    Fetch a single customer by ID, scoped to the authenticated user.

    Args:
        customer_id:  Primary key of the customer to retrieve.
        current_user: Authenticated user injected via JWT dependency.
        db:           Active SQLAlchemy session.

    Raises:
        HTTPException 404: If no customer with that ID exists for this user.

    Returns:
        CustomerRead object for the requested customer.
    """
    customer = get_customer(db, customer_id, current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.put("/{customer_id}", response_model=CustomerRead)
async def update(customer_id: int, updates: CustomerUpdate, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """
    Partially update a customer record for the authenticated user.

    Only fields present in the request body are updated; omitted fields
    retain their current values.

    Args:
        customer_id:  Primary key of the customer to update.
        updates:      CustomerUpdate schema containing the fields to change.
        current_user: Authenticated user injected via JWT dependency.
        db:           Active SQLAlchemy session.

    Raises:
        HTTPException 404: If no customer with that ID exists for this user.

    Returns:
        Updated CustomerRead object.
    """
    customer = customer_update(db, customer_id, current_user.id, updates)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.delete("/{customer_id}", response_model=CustomerRead)
async def delete(customer_id: int, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """
    Delete a customer record for the authenticated user.

    Args:
        customer_id:  Primary key of the customer to delete.
        current_user: Authenticated user injected via JWT dependency.
        db:           Active SQLAlchemy session.

    Raises:
        HTTPException 404: If no customer with that ID exists for this user.

    Returns:
        None on successful deletion.
    """
    customer = customer_delete(db, customer_id, current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return None