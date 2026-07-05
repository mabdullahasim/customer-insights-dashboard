"""
analytics.py
============
Customer analytics service layer for the CRM backend.

Provides async endpoint logic for computing and returning business intelligence
metrics, ML-driven sentiment analysis, churn risk scoring, and supervised churn
prediction using a trained Random Forest classifier.

Responsibilities:
  - Dashboard summary stats (revenue, review scores, churn risk counts, top countries)
  - Monthly revenue time-series aggregation
  - Per-country revenue breakdown
  - Customer feature export for frontend tables
  - Review score distribution with percentages
  - Sentiment scoring via DistilBERT + numeric rating blend (compute_satisfaction)
  - Rule-based churn risk using purchase recency (compute_churn_risk)
  - Supervised churn prediction via Random Forest trained on customer features

Dependencies:
  - NLTK VADER (loaded at module level, used for legacy reference)
  - HuggingFace DistilBERT fine-tuned on SST-2 (loaded at module level)
  - SQLAlchemy ORM session
  - scikit-learn RandomForestClassifier
  - Internal: app.schemas.analytics, app.models.customer, app.crud.customer
"""

import nltk
nltk.download("vader_lexicon")
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline as hf_pipeline
from sqlalchemy.orm import Session
from app.schemas.analytics import *
from app.models.customer import *
from app.crud.customer import *
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# ---------------------------------------------------------------------------
# Module-level model initialization
# Models are instantiated once at import time to avoid reloading on every
# request, which would add significant latency for transformer-based models.
# ---------------------------------------------------------------------------

sia = SentimentIntensityAnalyzer()

# DistilBERT fine-tuned on SST-2 for binary sentiment classification.
# Returns POSITIVE/NEGATIVE label + confidence score (0.0–1.0).
classifier = hf_pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


# ---------------------------------------------------------------------------
# Summary analytics
# ---------------------------------------------------------------------------

async def get_summary(db: Session, user_id: int) -> AnalyticsSummary:
    """
    Return a high-level dashboard summary for the authenticated user.

    Aggregates total customers, total and average revenue, average review
    score, 30-day active customer count, average ML sentiment score, high
    churn risk count (churn_risk > 0.7), and the top 3 countries by revenue.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are queried.

    Returns:
        AnalyticsSummary schema populated with all computed metrics.
    """
    total_customers = customer_count(db, user_id)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Sum all total_spent values for this user's customers; fall back to 0.00
    # if no records exist (scalar() returns None on empty result set).
    total_spent = (
        db.query(func.sum(Customer.total_spent))
        .filter(Customer.user_id == user_id)
        .scalar()
    ) or Decimal("0.00")

    # Guard against division by zero when no customers have been created yet.
    average_revenue_per_customer = (
        total_spent / total_customers if total_customers > 0 else Decimal("0.00")
    )

    # func.avg() returns None when the column has no non-null values.
    avg_review_score = (
        db.query(func.avg(Customer.review_score))
        .filter(Customer.user_id == user_id)
        .scalar()
    ) or 0

    # Count customers whose last_purchase_date falls within the last 30 days.
    customers_30_days = (
        db.query(func.count(Customer.id))
        .filter(Customer.user_id == user_id)
        .filter(Customer.last_purchase_date >= thirty_days_ago)
        .scalar()
    ) or 0

    # Average ML sentiment score across all customers; None if scores have not
    # been computed yet (run-sentiment endpoint has not been called).
    avg_sentiment_score = (
        db.query(func.avg(Customer.sentiment_score))
        .filter(Customer.user_id == user_id)
        .scalar()
    )

    # Customers flagged as high churn risk using the 0.7 threshold.
    high_churn_risk_count = (
        db.query(func.count(Customer.id))
        .filter(Customer.user_id == user_id)
        .filter(Customer.churn_risk > 0.7)
        .scalar()
    ) or 0

    # Aggregate revenue by country, exclude null countries, return top 3.
    top_countries_rows = (
        db.query(
            Customer.country,
            func.sum(Customer.total_spent).label("revenue")
        )
        .filter(Customer.user_id == user_id)
        .filter(Customer.country != None)
        .group_by(Customer.country)
        .order_by(func.sum(Customer.total_spent).desc())
        .limit(3)
        .all()
    )

    # Strip the revenue column; the schema only expects country name strings.
    top_countries = [row.country for row in top_countries_rows]

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


# ---------------------------------------------------------------------------
# Monthly revenue time-series
# ---------------------------------------------------------------------------

async def get_monthly_revenue(db: Session, user_id: int) -> list[MonthlyRevenuePoint]:
    """
    Return a time-ordered list of monthly revenue data points.

    Groups customers by the year and month of their last_purchase_date and
    aggregates total revenue, customer count, and average review score per
    period. Customers with no purchase date are excluded.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are queried.

    Returns:
        List of MonthlyRevenuePoint, one per unique year-month, sorted
        chronologically (oldest month first).
    """
    rows = (
        db.query(
            func.extract("year", Customer.last_purchase_date).label("year"),
            func.extract("month", Customer.last_purchase_date).label("month"),
            func.sum(Customer.total_spent).label("revenue"),
            func.count(Customer.id).label("customer_count"),
            func.avg(Customer.review_score).label("avg_review_score")
        )
        .filter(Customer.user_id == user_id)
        .filter(Customer.last_purchase_date != None)
        .group_by(
            func.extract("year", Customer.last_purchase_date),
            func.extract("month", Customer.last_purchase_date)
        )
        .order_by(
            func.extract("year", Customer.last_purchase_date),
            func.extract("month", Customer.last_purchase_date)
        )
        .all()
    )

    return [
        MonthlyRevenuePoint(
            # Format the extracted year/month floats into "YYYY-MM" string.
            month=f"{int(row.year)}-{int(row.month):02d}",
            revenue=row.revenue or Decimal("0.00"),
            customer_count=row.customer_count,
            # func.avg() returns None when all review_score values are null.
            avg_review_score=float(row.avg_review_score) if row.avg_review_score else None
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Country-level revenue breakdown
# ---------------------------------------------------------------------------

async def get_by_country(db: Session, user_id: int) -> list[CountryStats]:
    """
    Return revenue, customer count, and review metrics grouped by country.

    Customers with no country set are excluded. Results are sorted by total
    revenue descending so the highest-value markets appear first.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are queried.

    Returns:
        List of CountryStats, one per country, sorted by revenue descending.
    """
    rows = (
        db.query(
            Customer.country.label("country"),
            func.sum(Customer.total_spent).label("revenue"),
            func.count(Customer.id).label("customer_count"),
            func.avg(Customer.review_score).label("avg_review_score")
        )
        .filter(Customer.user_id == user_id)
        .filter(Customer.country != None)
        .group_by(Customer.country)
        .order_by(func.sum(Customer.total_spent).desc())
        .all()
    )

    return [
        CountryStats(
            country=row.country,
            revenue=row.revenue or Decimal("0.00"),
            customer_count=row.customer_count,
            avg_review_score=float(row.avg_review_score) if row.avg_review_score else None,
            # Guard against division by zero if customer_count is somehow 0.
            avg_revenue_per_customer=(
                row.revenue / row.customer_count if row.customer_count else Decimal("0.00")
            )
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Customer feature export
# ---------------------------------------------------------------------------

async def get_customer_features(db: Session, user_id: int) -> list[CustomerFeaturesRow]:
    """
    Return all customers with their computed ML feature values.

    Used to populate the customer data table in the frontend, exposing
    raw and ML-derived fields: sentiment score, churn risk, churn prediction,
    segment label, confidence label/score, and purchase recency in days.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are queried.

    Returns:
        List of CustomerFeaturesRow, one per customer, in DB order.
    """
    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .all()
    )

    # Anchor recency calculations to a single "now" timestamp for consistency
    # across all customers in this response.
    today = datetime.now(timezone.utc)

    return [
        CustomerFeaturesRow(
            id=customer.id,
            full_name=customer.full_name,
            total_spent=customer.total_spent,
            # Days since last purchase; None if the customer has never purchased.
            recency_days=(
                (today - customer.last_purchase_date.replace(tzinfo=timezone.utc)).days
                if customer.last_purchase_date else None
            ),
            review_score=customer.review_score,
            sentiment_score=float(customer.sentiment_score) if customer.sentiment_score else None,
            segment=customer.segment,
            churn_risk=float(customer.churn_risk) if customer.churn_risk else None,
            country=customer.country,
            churn_prediction=float(customer.churn_prediction) if customer.churn_prediction else None,
            churn_label=customer.churn_label,
            confidence_label=customer.confidence_label,
            confidence_score=float(customer.confidence_score) if customer.confidence_score else None,
        )
        for customer in customers
    ]


# ---------------------------------------------------------------------------
# Review score distribution
# ---------------------------------------------------------------------------

async def get_review_score_distribution(db: Session, user_id: int) -> list[ReviewScoreDistribution]:
    """
    Return the count and percentage of customers at each review score.

    Only customers with a non-null review_score are included. Percentages
    are computed relative to the total reviewed customer count.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are queried.

    Returns:
        List of ReviewScoreDistribution sorted by review_score ascending,
        one entry per distinct score value that has been submitted.
    """
    # Pre-compute total reviewed count so each row can calculate its percentage
    # without an additional subquery per row.
    total_reviewed = (
        db.query(func.count(Customer.id))
        .filter(Customer.user_id == user_id)
        .filter(Customer.review_score != None)
        .scalar()
    ) or 0

    rows = (
        db.query(
            Customer.review_score.label("review_score"),
            func.count(Customer.id).label("customer_count")
        )
        .filter(Customer.user_id == user_id)
        .filter(Customer.review_score != None)
        .group_by(Customer.review_score)
        .order_by(Customer.review_score.asc())
        .all()
    )

    return [
        ReviewScoreDistribution(
            review_score=row.review_score,
            count=row.customer_count,
            # Avoid division by zero; percentage is 0.0 if no reviews exist.
            percentage=round((row.customer_count / total_reviewed) * 100, 2) if total_reviewed > 0 else 0.0
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Sentiment scoring helpers
# ---------------------------------------------------------------------------

def get_distilbert_score(text: str) -> float:
    """
    Run the DistilBERT SST-2 classifier on the provided text and return a
    signed confidence score.

    The raw model output is a confidence value in [0, 1] paired with a label.
    This function maps it to a signed float:
      - POSITIVE → +score  (range: 0.0 to +1.0)
      - NEGATIVE → -score  (range: -1.0 to 0.0)

    Args:
        text: Review text to classify. Truncated to 512 tokens for the model.

    Returns:
        Signed float sentiment score in the range [-1.0, +1.0].
    """
    result = classifier(text, truncation=True, max_length=512)
    label = result[0]["label"]
    score = result[0]["score"]

    if label == "POSITIVE":
        return score
    elif label == "NEGATIVE":
        return -score
    else:
        return 0.0


def compute_satisfaction(review_text, review_score):
    """
    Compute a blended customer satisfaction score from text and/or rating.

    Scoring strategy:
      - Both text and rating available (high confidence):
            satisfaction = 0.5 * distilbert_score + 0.5 * rating_score
            where rating_score = (review_score - 3) / 2 maps [1–5] → [-1, +1]
      - Rating only, no text (low confidence):
            satisfaction = rating_score alone
      - Neither available:
            Returns (None, None, None) — no score is stored.

    Args:
        review_text:  Raw review string, or None/empty.
        review_score: Numeric score 1–5, or None.

    Returns:
        Tuple of (satisfaction: float|None, confidence_label: str|None,
                  confidence_score: float|None).
    """
    has_text = review_text is not None and str(review_text).strip() != ""
    has_rating = review_score is not None

    if has_text and has_rating:
        # Full-signal path: blend DistilBERT score with normalised star rating.
        distilbert_score = get_distilbert_score(review_text)
        rating_score = (review_score - 3) / 2          # maps [1,5] → [-1, +1]
        satisfaction = (0.5 * distilbert_score) + (0.5 * rating_score)
        return round(satisfaction, 3), "high", 1.0

    elif has_rating and not has_text:
        # Rating-only path: lower confidence since no linguistic signal exists.
        rating_score = (review_score - 3) / 2
        return round(rating_score, 3), "low", 0.25

    else:
        # No usable signal; caller should skip persisting a score.
        return None, None, None


# ---------------------------------------------------------------------------
# Sentiment analysis endpoint
# ---------------------------------------------------------------------------

async def sentiment_analysis(db: Session, user_id: int) -> Message:
    """
    Compute and persist sentiment scores for all of a user's customers.

    Iterates over every customer record, calls compute_satisfaction() for
    each, and writes the resulting sentiment_score, confidence_label, and
    confidence_score back to the database in a single commit.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are processed.

    Returns:
        Message confirming how many customers were processed.
    """
    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .all()
    )

    for customer in customers:
        satisfaction, confidence_label, confidence_score = compute_satisfaction(
            customer.review_text,
            customer.review_score
        )
        customer.sentiment_score = satisfaction
        customer.confidence_label = confidence_label
        customer.confidence_score = confidence_score

    db.commit()
    return Message(message=f"Sentiment analysis completed for {len(customers)} customers")


# ---------------------------------------------------------------------------
# Churn risk helpers
# ---------------------------------------------------------------------------

def compute_churn_risk(customer: Customer) -> float:
    """
    Calculate a rule-based churn risk score from purchase recency.

    Uses a linear ramp between 60 and 90 days since last purchase:
      - 0–60 days  → risk = 0.0 (active customer, no risk)
      - 60–90 days → risk linearly scales 0.0 → 1.0
      - 90+ days   → risk clamped to 1.0 (fully churned)

    Args:
        customer: Customer ORM object with a last_purchase_date attribute.

    Returns:
        Float churn risk in [0.0, 1.0], or None if last_purchase_date is null.
    """
    if customer.last_purchase_date is None:
        return None

    recency_days = (
        datetime.now(timezone.utc) - customer.last_purchase_date.replace(tzinfo=timezone.utc)
    ).days

    # Linear interpolation between the 60-day and 90-day thresholds.
    churn_risk = (recency_days - 60) / (90 - 60)
    churn_risk = max(0.0, min(1.0, churn_risk))    # clamp to [0, 1]
    return churn_risk


async def churn(db: Session, user_id: int) -> Message:
    """
    Compute and persist rule-based churn risk for all of a user's customers.

    Sets churn_risk (float) and churn_label ("Yes"/"No") on every customer
    based on purchase recency using compute_churn_risk(). The 0.5 threshold
    determines the binary label used later as training target for the ML model.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are processed.

    Returns:
        Message confirming completion.
    """
    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .all()
    )

    for customer in customers:
        churn_risk = compute_churn_risk(customer)
        customer.churn_risk = churn_risk
        # Binary label used as y in the downstream Random Forest classifier.
        customer.churn_label = "Yes" if churn_risk and churn_risk > 0.5 else "No"

    db.commit()
    return Message(message="Churn completed")


# ---------------------------------------------------------------------------
# ML churn prediction
# ---------------------------------------------------------------------------

async def churn_prediction(db: Session, user_id: int) -> Message:
    """
    Train a Random Forest classifier on labelled customer data and write
    predicted churn probabilities back to each customer record.

    Workflow:
      1. Query customers that have churn_label, sentiment_score, and
         review_score populated (requires prior calls to /run-churn and
         /run-sentiment).
      2. Require at least 50 labelled samples for a meaningful model.
      3. Build feature matrix X (7 features) and binary target vector y.
      4. Split 80/20 for evaluation; compute test accuracy.
      5. Retrain on the full dataset for maximum coverage.
      6. Predict churn probabilities for all customers and persist.

    Feature set (7 columns):
      total_spent, sentiment_score, review_score, confidence_score,
      confidence_label (encoded: high=1.0, low=0.5), recency_days,
      account_age_days

    Note: The final predict_proba call uses only 3 features (total_spent,
    sentiment_score, review_score). This is a known inconsistency with the
    7-feature training matrix and should be unified in a future refactor.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are processed.

    Returns:
        Message with customer count and rounded test accuracy, or an
        insufficient-data message if fewer than 50 labelled customers exist.
    """
    

    customers = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .filter(Customer.churn_label.isnot(None))
        .filter(Customer.sentiment_score.isnot(None))
        .filter(Customer.review_score.isnot(None))
        .all()
    )

    if len(customers) < 50:
        return Message(
            message="Not enough customer data to train a churn model. "
                    "Upload more customers and run sentiment and churn first."
        )

    today = datetime.now(timezone.utc)

    X = np.array([
        [
            float(c.total_spent),
            float(c.sentiment_score),
            float(c.review_score),
            float(c.confidence_score) if c.confidence_score else 0.0,
            {"high": 1.0, "low": 0.5}.get(c.confidence_label, 0.0),
            (today - c.last_purchase_date.replace(tzinfo=timezone.utc)).days
                if c.last_purchase_date else 0,
            (today - c.account_created_at.replace(tzinfo=timezone.utc)).days
                if c.account_created_at else 0,
        ]
        for c in customers
    ])

    y = np.array([1 if c.churn_label == "Yes" else 0 for c in customers])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    model.fit(X, y)

    predicted_probabilities = model.predict_proba(X)[:, 1]

    for customer, prob in zip(customers, predicted_probabilities):
        customer.churn_prediction = round(float(prob), 3)

    db.commit()
    return Message(
        message=f"Churn prediction completed for {len(customers)} customers "
                f"with accuracy {round(accuracy, 4)}"
    )


# ---------------------------------------------------------------------------
# Run-all convenience endpoint
# ---------------------------------------------------------------------------

async def run_all(db: Session, user_id: int) -> Message:
    """
    Placeholder for a combined pipeline that runs all ML jobs sequentially.

    Intended to execute sentiment_analysis → churn → churn_prediction in
    order for a given user. Currently returns a completion message without
    invoking the individual steps; implementation is pending.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user to process.

    Returns:
        Message confirming all jobs completed.
    """
    await sentiment_analysis(db, user_id)
    await churn(db, user_id)
    await churn_prediction(db, user_id)

    return Message(message="All completed")