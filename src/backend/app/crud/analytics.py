import nltk
nltk.download("vader_lexicon")
from nltk.sentiment import SentimentIntensityAnalyzer
from sqlalchemy.orm import Session
from app.schemas.analytics import *
from app.models.customer import *
from app.crud.customer import *
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from decimal import Decimal


async def get_summary(db: Session, user_id: int) -> AnalyticsSummary:
    total_customers = customer_count(db, user_id)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_spent = (db.query(func.sum(Customer.total_spent)).filter(Customer.user_id == user_id).scalar()) or Decimal("0.00")  # sum all total_spent for this user, fallback to 0.00
    average_revenue_per_customer = (total_spent / total_customers if total_customers > 0 else Decimal("0.00"))  # avoid division by zero
    avg_review_score = (db.query(func.avg(Customer.review_score)).filter(Customer.user_id == user_id).scalar()) or 0  # average review score, fallback to 0
    customers_30_days = (db.query(func.count(Customer.id)).filter(Customer.user_id == user_id).filter(Customer.last_purchase_date >= thirty_days_ago).scalar()) or 0  # customers active in last 30 days
    avg_sentiment_score = (db.query(func.avg(Customer.sentiment_score)).filter(Customer.user_id == user_id).scalar())  # average sentiment score, None if no scores exist yet
    high_churn_risk_count = (db.query(func.count(Customer.id)).filter(Customer.user_id == user_id).filter(Customer.churn_risk > 0.7).scalar()) or 0  # customers flagged as high churn risk
    top_countries_rows = (
        db.query(Customer.country, func.sum(Customer.total_spent).label("revenue"))
        .filter(Customer.user_id == user_id)
        .filter(Customer.country != None) # exclude null countries
        .group_by(Customer.country) # one row per country
        .order_by(func.sum(Customer.total_spent).desc())  # highest revenue first
        .limit(3)  # top 3 only
        .all()
    )
    top_countries = [row.country for row in top_countries_rows]  # extract only the country names

    return AnalyticsSummary(
        total_customers=total_customers,
        total_revenue=total_spent,
        avg_revenue_per_customer=average_revenue_per_customer,
        average_review_score=avg_review_score,
        avg_sentiment_score=float(avg_sentiment_score) if avg_sentiment_score else None,
        high_churn_risk_count=high_churn_risk_count,
        top_countries_by_revenue=top_countries,
        recent_customers_30d=customers_30_days
    )


async def get_monthly_revenue(db: Session, user_id: int) -> list[MonthlyRevenuePoint]:
    rows = (
        db.query(
            func.extract("year", Customer.last_purchase_date).label("year"), #pull year out of date
            func.extract("month", Customer.last_purchase_date).label("month"),  #pull month out of date
            func.sum(Customer.total_spent).label("revenue"), #sum total spent for this month
            func.count(Customer.id).label("customer_count"),  #count customers in this month
            func.avg(Customer.review_score).label("avg_review_score")   #average review score, ignores nulls
        )
        .filter(Customer.user_id == user_id)                  #filter by current users customers
        .filter(Customer.last_purchase_date != None)          #exclude null dates
        .group_by(
            func.extract("year", Customer.last_purchase_date),   #collapse into one row per unique year+month
            func.extract("month", Customer.last_purchase_date)
        )
        .order_by(
            func.extract("year", Customer.last_purchase_date),   #sort oldest month first
            func.extract("month", Customer.last_purchase_date)
        )
        .all()
    )

    return [
        MonthlyRevenuePoint(
            month=f"{int(row.year)}-{int(row.month):02d}",                                      #format into "YYYY-MM"
            revenue=row.revenue or Decimal("0.00"),                                              #fallback to 0.00 if somehow null
            customer_count=row.customer_count,                                                   #plain int count from func.count()
            avg_review_score=float(row.avg_review_score) if row.avg_review_score else None      #convert to float, or None if no reviews
        )
        for row in rows  # one MonthlyRevenuePoint built per year+month group
    ]


async def get_by_country(db: Session, user_id: int) -> list[CountryStats]:
    rows = (
        db.query(
            Customer.country.label("country"),
            func.sum(Customer.total_spent).label("revenue"), #sum total spent per country
            func.count(Customer.id).label("customer_count"),   #count customers per country
            func.avg(Customer.review_score).label("avg_review_score") #average review score per country
        )
        .filter(Customer.user_id == user_id) #filter by current users customers
        .filter(Customer.country != None) #exclude null countries
        .group_by(Customer.country)   #one row per country
        .order_by(func.sum(Customer.total_spent).desc())  #highest revenue first
        .all()
    )

    return [
        CountryStats(
            country=row.country,
            revenue=row.revenue or Decimal("0.00"),  #fallback to 0.00 if somehow null
            customer_count=row.customer_count,  #plain int count
            avg_review_score=float(row.avg_review_score) if row.avg_review_score else None, #convert to float, or None if no reviews
            avg_revenue_per_customer=(row.revenue / row.customer_count if row.customer_count else Decimal("0.00"))  #avoid division by zero
        )
        for row in rows  #one CountryStats built per country
    ]


async def get_customer_features(db: Session, user_id: int) -> list[CustomerFeaturesRow]:
    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)  # fetch all customers belonging to this user
        .all()
    )
    today = datetime.now(timezone.utc)  # current UTC time to calculate recency against

    return [
        CustomerFeaturesRow(
            id=customer.id,  # DB primary key
            full_name=customer.full_name, # customer name
            total_spent=customer.total_spent,  # total revenue from this customer
            recency_days=((today - customer.last_purchase_date.replace(tzinfo=timezone.utc)).days if customer.last_purchase_date else None),  # days since last purchase, None if never purchased
            review_score=customer.review_score, # optional 1-5 rating, None if not set
            sentiment_score=float(customer.sentiment_score) if customer.sentiment_score else None, # ML sentiment score from review_text
            segment=customer.segment, # ML segment label e.g. "high_value"
            churn_risk=float(customer.churn_risk) if customer.churn_risk else None, # ML churn probability 0.0-1.0
            country=customer.country,  # optional country, None if not set
        )
        for customer in customers  #one CustomerFeaturesRow built per customer
    ]


async def get_review_score_distribution(db: Session, user_id: int) -> list[ReviewScoreDistribution]:
    total_reviewed = db.query(func.count(Customer.id)).filter(Customer.user_id == user_id).filter(Customer.review_score != None).scalar() or 0
    rows = (
        db.query(
            Customer.review_score.label("review_score"),
            func.count(Customer.id).label("customer_count")
        )
        .filter(Customer.user_id == user_id)
        .filter(Customer.review_score != None) # exclude null reviews
        .group_by(Customer.review_score)  #group by review score
        .order_by(Customer.review_score.asc())  #order by review score in ascneding order
        .all()
    )
    return [
        ReviewScoreDistribution(
            review_score=row.review_score, # optional 1-5 rating, None if not set
            count = row.customer_count,
            percentage=round((row.customer_count / total_reviewed) * 100, 2) if total_reviewed > 0 else 0.0
        )
        for row in rows  #one CustomerFeaturesRow built per customer
    ]

async def sentiment_analysis(db: Session, user_id: int) -> Message:
    sia = SentimentIntensityAnalyzer()
    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)  # fetch all customers belonging to this user
        .all()
    )
    for customer in customers:
        if customer.review_text is not None:
            text_score = sia.polarity_scores(customer.review_text)["compound"]
        else:
            text_score = 0
        if customer.review_score is not None:
            rating_score = (customer.review_score - 3) / 2
        else:
            rating_score = 0
        sentiment = 0.7 * text_score + 0.3 * rating_score
        customer.sentiment_score = sentiment
    return Message(message="Sentiment analysis completed")

async def segmentation(db: Session, user_id: int) -> Message:
    return Message(message="Segmentation completed")

async def churn(db: Session, user_id: int) -> Message:
    return Message(message="Churn completed")

async def run_all(db: Session, user_id: int) -> Message:
    return Message(message="All completed")