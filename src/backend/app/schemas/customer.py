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
    id: int # DB primary key
    user_id: int # owner (the logged-in user)
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
    created_at: datetime
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

    sentiment_score: Optional[float] = None
    segment: Optional[str] = None
    churn_risk: Optional[float] = None
    updated_at: Optional[datetime] = None



class CustomerDelete(BaseModel):
    id: int
    user_id: int
    model_config = {"from_attributes": True}