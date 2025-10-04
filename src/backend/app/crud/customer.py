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

def get_customer(db: Session, id, user_id) -> CustomerRead | None:
    db_customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    # If user exists, return as a Pydantic object
    if db_customer:
        return CustomerRead.from_orm(db_customer)
    
    return None

def list_customers(db: Session, skip: int, current_user.id: int) -> list[CustomerRead]:
    
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
    customer = get_customer(db, id, user_id)
     if not db_customer:
        return False
    db.delete(customer)
    db.commit()
    return True

def customer_update(db: Session, id: int, user_id: int, updates: CustomerUpdate) -> CustomerRead | None:
    customer = get_customer(db, id, user_id)
    if not db_customer:
        return False

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)

    return CustomerRead.from_orm(db_customer)

