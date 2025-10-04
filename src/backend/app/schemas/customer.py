from pydantic import BaseModel, field_validator
from datetime import datetime

class customer_create(BaseModel):
    full_name: str
    email: str
    country: str
    total_spent: Decimal
    last_purchase_date: Optional[datetime]
    review_score: Optional[int]

class CustomerInDB(BaseModel):
    email: str
    id: int

    model_config = {"from_attributes": True}

class CustomerRead(BaseModel):
    id: int → DB primary key
    user_id: int → owner (the logged-in user)
    full_name: str
    email: str
    country: Optional[str]
    total_spent: Decimal
    last_purchase_date: Optional[datetime]
    review_score: Optional[int]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}.

class CustomerUpdate(BaseModel):
    total_spent: Decimal
    last_purchase_date: Optional[datetime]
    review_score: Optional[int]
    updated_at: datetime