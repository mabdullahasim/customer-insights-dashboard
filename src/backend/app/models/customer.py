"""
customer.py (model)
===================
SQLAlchemy ORM model for the customers table.

Represents a customer record owned by a registered user. Each customer is
scoped to a single user account via a foreign key on user_id, enforcing
strict data isolation between accounts.

Table: customers

Column Groups:
  Identity      : id, user_id, full_name, email, country, account_created_at
  Commerce      : total_spent, last_purchase_date, review_score
  ML Fields     : review_text, sentiment_score, segment, churn_risk,
                  churn_label, churn_prediction, confidence_label, confidence_score
  Bookkeeping   : created_at, updated_at

Constraints & Indexes:
  uq_customers_user_email         - Unique email per user account (same email
                                    allowed across different user accounts)
  ix_customers_country            - Index on country for analytics group-by queries
  ix_customers_last_purchase_date - Index on last_purchase_date for recency filters

Dependencies:
  - SQLAlchemy
  - Internal: app.core.database.Base
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) # logged in user owns this customer
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    country = Column(String, nullable=True)
    account_created_at = Column(DateTime, nullable=True)

    # Commerce metrics (Numeric used for money fields to avoid float rounding errors)
    total_spent = Column(Numeric(12, 2), nullable=False, default=0)
    last_purchase_date = Column(DateTime, nullable=True)
    review_score = Column(Integer, nullable=True)          # optional rating (1–5)

    # ML fields
    review_text = Column(String, nullable=True)            # written review from CSV
    sentiment_score = Column(Numeric(4, 3), nullable=True) # computed from review_text (0.0 – 1.0)
    segment = Column(String, nullable=True)                # computed by segmentation model e.g. "high_value"
    churn_risk = Column(Numeric(4, 3), nullable=True)      # computed by churn model (0.0 – 1.0)
    churn_label = Column(String, nullable=True)            # computed by churn label model e.g. "churn"
    churn_prediction = Column(Numeric(4, 3), nullable=True) # computed by churn prediction model (0.0 – 1.0)
    confidence_label = Column(String, nullable=True)       # computed by confidence label model e.g. "high_confidence"
    confidence_score = Column(Numeric(3, 2), nullable=True) # computed by confidence score model (0.0 – 1.0)

    # Bookkeeping
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "email", name="uq_customers_user_email"), # allow same email in different accounts, but unique within one account
        Index("ix_customers_country", "country"),
        Index("ix_customers_last_purchase_date", "last_purchase_date"),
    )