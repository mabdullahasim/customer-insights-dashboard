"""
customer.py (schemas)
=====================
Pydantic request and response schemas for the customer module.

Defines the data shapes used for creating, reading, updating, and deleting
customer records. These schemas are used as request body types and
response_model declarations in the customer and analytics routers.

Schemas:
  CustomerCreate  - Fields accepted when creating a new customer record
  CustomerInDB    - Minimal internal representation of a persisted customer
  CustomerRead    - Full customer record returned by API responses
  CustomerUpdate  - Partial update payload; all fields optional
  CustomerDelete  - Minimal schema for identifying a customer to delete

Dependencies:
  - Pydantic BaseModel, field_validator
"""

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class CustomerCreate(BaseModel):
    full_name: str
    email: str
    country: Optional[str]
    total_spent: Decimal
    last_purchase_date: Optional[datetime]
    review_score: Optional[int]
    review_text: Optional[str]


class CustomerInDB(BaseModel):
    email: str
    id: int

    model_config = {"from_attributes": True}


class CustomerRead(BaseModel):
    id: int                              # DB primary key
    user_id: int                         # owner (the logged-in user)
    full_name: str
    email: str
    country: Optional[str]
    total_spent: Decimal
    last_purchase_date: Optional[datetime]
    review_score: Optional[int]
    review_text: Optional[str]
    sentiment_score: Optional[Decimal]
    segment: Optional[str]
    churn_risk: Optional[Decimal]
    churn_prediction: Optional[Decimal]
    churn_label: Optional[str]
    confidence_label: Optional[str]
    confidence_score: Optional[Decimal]
    account_created_at: Optional[datetime]
    updated_at: datetime
    model_config = {"from_attributes": True}


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    total_spent: Optional[float] = None
    last_purchase_date: Optional[datetime] = None
    review_score: Optional[int] = None
    review_text: Optional[str] = None
    confidence_label: Optional[str] = None
    confidence_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    segment: Optional[str] = None
    churn_risk: Optional[float] = None
    churn_prediction: Optional[float] = None
    churn_label: Optional[str] = None
    account_created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CustomerDelete(BaseModel):
    id: int
    user_id: int
    model_config = {"from_attributes": True}