from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import List


class AnalyticsSummary(BaseModel): #pydantic schema for analytics summary
    total_customers: int
    total_revenue: Decimal
    avg_revenue_per_customer: Decimal
    average_review_score: Optional[float]
    avg_sentiment_score: Optional[float]
    high_churn_risk_count: int
    top_countries_by_revenue: List[str]
    recent_customers_30d: int


class MonthlyRevenuePoint(BaseModel): #pydantic schema for monthly revenue point
    month: str
    revenue: Decimal
    customer_count: int
    avg_review_score: Optional[float] # average review score for the month to show change over time

class ReviewScoreDistribution(BaseModel): #pydantic schema for review score distribution
    review_score: int
    count: int
    percentage: float

class CountryStats(BaseModel): #pydantic schema for country stats
    country: str
    revenue: Decimal
    customer_count: int
    avg_review_score: Optional[float]
    avg_revenue_per_customer: Decimal

class CustomerFeaturesRow(BaseModel): # pydantic schma represents one row per customer, clean feature table for machine learning model
    id: int
    full_name: str
    total_spent: Decimal
    recency_days: Optional[int]
    review_score: Optional[int]
    sentiment_score: Optional[float]
    segment: Optional[str]
    churn_risk: Optional[float]
    country: Optional[str]

    model_config = {"from_attributes": True}

class Message(BaseModel):
    message: str