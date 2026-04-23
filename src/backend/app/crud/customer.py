from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.customer import *
from app.models.customer import *

async def create_customer(db: Session, user_in: CustomerCreate, user_id: int) -> Customer:
    existing = db.execute(
        select(Customer).where(
            Customer.user_id == user_id,
            Customer.email == user_in.email,
        )
    ).scalar_one_or_none()

    if existing:
        updates = CustomerUpdate(
            full_name=user_in.full_name,
            country=user_in.country,
            total_spent=user_in.total_spent,
            last_purchase_date=user_in.last_purchase_date,
            review_score=user_in.review_score,
            review_text=user_in.review_text,
        )
        return await customer_update(
            db=db,
            id=existing.id,
            user_id=user_id,
            updates=updates,
        )

    new_customer = Customer(
        user_id = user_id,
        full_name=user_in.full_name,
        email=user_in.email,
        country = user_in.country,
        total_spent=user_in.total_spent,
        last_purchase_date = user_in.last_purchase_date,
        review_score = user_in.review_score,
        review_text=user_in.review_text  
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

async def get_customer(db: Session, id, user_id) -> CustomerRead | None:
    db_customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    # If user exists, return as a Pydantic object
    if db_customer:
        return CustomerRead.from_orm(db_customer)
    
    return None

async def list_customers(db: Session, skip: int, current_user_id: int) -> list[CustomerRead]:
    db_customers = (
        db.query(Customer)
        .filter(Customer.user_id == current_user_id) #restricts results to logged in users data for if the customer exists among other users
        .offset(skip) #skip by the passed in parameter skip
        .limit(10) #return a max of 10 customers
        .all() #exectues the sql query
    )
    customer_list = [CustomerRead.from_orm(cust) for cust in db_customers] #returns a list of customers of type schmea CustomerRead
    return customer_list


def customer_delete(db: Session, id, user_id) -> bool:
    customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    if not customer:
        return False
    db.delete(customer)
    db.commit()
    return True

async def customer_update(db: Session, id: int, user_id: int, updates: CustomerUpdate) -> CustomerRead | None:
    customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    if not customer:
        return None

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return CustomerRead.from_orm(customer)


    
def customer_count(db: Session, user_id: int) -> int:
    """
    Returns count of customers owned by a specific user.
    """
    return db.query(Customer).filter(Customer.user_id == user_id).count()