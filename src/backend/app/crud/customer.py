from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate
from app.models.customer import Customer
async def create_customer(db: Session, user_in: CustomerCreate,) -> Customer:
    new_customer = Customer(
        full_name=user_in.full_name;,
        email=user_in.email,
        country = user_in.country,
        total_spent=user_in.total_spent,
        last_purchase_date = user_in.last_purchase_date,
        review_score = user_in.review_scorem
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

def get_customer(db: Session, id) -> CustomerInDB | None:
    db_customer = db.query(Customer).filter(Customer.id == id)
    
    # If user exists, return as a Pydantic object
    if db_customer:
        return Customer.from_orm(db_customer)
    
    return None



