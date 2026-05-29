from decimal import Decimal


from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship # allows you to define relationships between models
from app.core.database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) # logged in user owns this customer

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    country = Column(String, nullable=True)

    # commerce metrics (DECIMAL via Numeric for money to avoid float rounding)
    total_spent = Column(Numeric(12, 2), nullable=False, default=0)
    last_purchase_date = Column(DateTime, nullable=True)

    # optional rating (1-5).
    review_score = Column(Integer, nullable=True)

    # ML fields
    review_text = Column(String, nullable=True)  #written review from CSV
    sentiment_score = Column(Numeric(4, 3), nullable=True)  #computed from review_text (0.0 - 1.0)
    segment = Column(String, nullable=True) #computed by segmentation model e.g. "high_value"
    churn_risk = Column(Numeric(4, 3), nullable=True)  # computed by churn model (0.0 - 1.0)
    confidence_label = Column(String, nullable=True) #computed by confidence label model e.g. "high_confidence"
    confidence_score = Column(Numeric(3, 2), nullable=True) #computed by confidence score model (0.0 - 1.0)
    # bookkeeping
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # allow same email in different accounts, but unique within one account
        UniqueConstraint("user_id", "email", name="uq_customers_user_email"),
        Index("ix_customers_country", "country"),
        Index("ix_customers_last_purchase_date", "last_purchase_date"),
    )
    
