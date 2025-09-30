from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from app.core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
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
    # bookkeeping
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    # (optional) relationship back to User if you have it defined
    # user = relationship("User", back_populates="customers")
    __table_args__ = (
        # allow same email in different accounts, but unique within one account
        UniqueConstraint("user_id", "email", name="uq_customers_user_email"),
        Index("ix_customers_country", "country"),
        Index("ix_customers_last_purchase_date", "last_purchase_date"),
    )
    
