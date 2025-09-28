from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from datetime import datetime
class customer(Base):
    __tablename__ = "Customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    review = Column(Integer, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow)
    country = Column(String, nullable=False)
    total_spent = Column(Float, nullable=False)
    purchase_frequency = Column(Float, nullable=False)
    last_purchase_date = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(Float, nullable=False)
