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
async def summary(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await get_summary(db, current_user.id)

@router.get("/monthly-revenue", response_model=list[MonthlyRevenuePoint])
async def monthly_revenue(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await get_monthly_revenue(db, current_user.id)


@router.get("/by-country", response_model=list[CountryStats])
async def stats_by_country(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await get_by_country(db, current_user.id)

@router.get("/customer-features", response_model=list[CustomerFeaturesRow])
async def customer_features(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await get_customer_features(db, current_user.id)

@router.get("/review_score_distribution", response_model=list[ReviewScoreDistribution])
async def customer_features(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await get_review_score_distribution(db, current_user.id)


# ML model endpoints
@router.post("/run-sentiment", response_model=Message)
async def run_sentiment(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await sentiment_analysis(db, current_user.id)

@router.post("/run-segmentation", response_model=Message)
async def run_segmentation(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await segmentation(db, current_user.id)

@router.post("/run-churn", response_model=Message)
async def run_churn(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await churn(db, current_user.id)

@router.post("/run-all", response_model=Message)
async def run_all(current_user =Depends(get_current_active_user), db: Session=Depends(get_db)):
    return await run_all(db, current_user.id)