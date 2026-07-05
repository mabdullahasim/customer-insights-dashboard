"""
analytics.py (schemas)
======================
Pydantic response schemas for the analytics module.

Defines the data shapes returned by all analytics endpoints. These schemas
are used as response_model declarations in the analytics router and are
populated by the aggregation and ML functions in app.crud.analytics.

Schemas:
  AnalyticsSummary       - High-level dashboard summary stats
  MonthlyRevenuePoint    - Single month in a revenue time-series
  ReviewScoreDistribution - Count and percentage for a single review score value
  CountryStats           - Revenue and customer metrics for a single country
  CustomerFeaturesRow    - Full feature row per customer for the frontend table
  Message                - Generic success/status message response

Dependencies:
  - Pydantic BaseModel
"""

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
    churn_prediction: Optional[float]
    churn_label: Optional[str]
    confidence_label: Optional[str]
    confidence_score: Optional[float]
    model_config = {"from_attributes": True}


class Message(BaseModel):
    message: str