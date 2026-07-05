"""
analytics.py (router)
=====================
FastAPI route definitions for the analytics module.

Exposes GET endpoints for dashboard metrics and POST endpoints for
triggering ML pipeline jobs. All routes are protected by JWT authentication
via get_current_active_user and are scoped to the authenticated user's data.

Endpoints:
  GET  /analytics/summary                  - High-level dashboard summary stats
  GET  /analytics/monthly-revenue          - Monthly revenue time-series
  GET  /analytics/by-country               - Revenue and stats grouped by country
  GET  /analytics/customer-features        - Full customer feature table for the frontend
  GET  /analytics/review_score_distribution - Review score counts and percentages

  POST /analytics/run-sentiment            - Compute and persist sentiment scores
  POST /analytics/run-churn               - Compute and persist churn risk scores
  POST /analytics/run-all                 - Run all ML jobs sequentially (pending)

Dependencies:
  - FastAPI APIRouter, Depends
  - SQLAlchemy ORM session via get_db
  - JWT auth via get_current_active_user
  - Internal: app.crud.analytics, app.schemas.analytics
"""

from app.models.customer import Customer
from app.schemas.customer import *
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import List
from app.core.security import get_current_active_user
from app.schemas.analytics import *
from app.crud.analytics import *


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Return high-level dashboard summary stats for the authenticated user."""
    return await get_summary(db, current_user.id)


@router.get("/monthly-revenue", response_model=list[MonthlyRevenuePoint])
async def monthly_revenue(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Return monthly revenue time-series data for the authenticated user."""
    return await get_monthly_revenue(db, current_user.id)


@router.get("/by-country", response_model=list[CountryStats])
async def stats_by_country(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Return revenue and customer stats grouped by country for the authenticated user."""
    return await get_by_country(db, current_user.id)


@router.get("/customer-features", response_model=list[CustomerFeaturesRow])
async def customer_features(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Return all customer records with their computed ML feature values."""
    return await get_customer_features(db, current_user.id)


@router.get("/review_score_distribution", response_model=list[ReviewScoreDistribution])
async def customer_features(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Return review score distribution with counts and percentages."""
    return await get_review_score_distribution(db, current_user.id)


# ---------------------------------------------------------------------------
# ML pipeline endpoints
# ---------------------------------------------------------------------------

@router.post("/run-sentiment", response_model=Message)
async def run_sentiment(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Trigger sentiment analysis and persist scores for all customers."""
    return await sentiment_analysis(db, current_user.id)


@router.post("/run-churn", response_model=Message)
async def run_churn(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Trigger churn risk calculation and persist scores for all customers."""
    return await churn(db, current_user.id)


@router.post("/run-all", response_model=Message)
async def run_all(current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    """Trigger all ML pipeline jobs sequentially for the authenticated user."""
    return await run_all(db, current_user.id)