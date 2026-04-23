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
    return list_customers(db, skip, current_user.id)

@router.get("/{customer_id}", response_model=CustomerRead)
async def get_one_customer(customer_id: int, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    customer = get_customer(db, customer_id, current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer

@router.put("/{customer_id}", response_model=CustomerRead)
async def update(customer_id: int, updates: CustomerUpdate, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    customer = customer_update(db, customer_id, current_user.id, updates)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.delete("/{customer_id}", response_model=CustomerRead)
async def delete(customer_id: int, current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    customer = customer_delete(db, customer_id, current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return None