"""
customer.py
===========
CRUD (Create, Read, Update, Delete) operations for the Customer model.

Provides all database interaction logic for customer records scoped to
the authenticated user. All queries are filtered by user_id to ensure
strict data isolation between accounts.

Operations:
  - create_customer   : Insert a new customer, or update if email already exists
  - get_customer      : Fetch a single customer by ID
  - list_customers    : Paginated list of customers for the current user
  - customer_delete   : Hard delete a customer record
  - customer_update   : Partial update of customer fields
  - customer_count    : Count of all customers owned by a user

Dependencies:
  - SQLAlchemy ORM session
  - Internal: app.schemas.customer, app.models.customer
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.customer import *
from app.models.customer import *


async def create_customer(db: Session, user_in: CustomerCreate, user_id: int) -> Customer:
    """
    Create a new customer record, or update the existing one if the email
    already exists for this user (upsert behaviour).

    If a customer with the same email already exists under this user_id,
    all provided fields are forwarded to customer_update() instead of
    inserting a duplicate. Otherwise, a new Customer row is inserted.

    Args:
        db:      Active SQLAlchemy session.
        user_in: Validated CustomerCreate schema containing the new record data.
        user_id: ID of the authenticated user who owns this customer.

    Returns:
        The newly created or updated Customer ORM object.
    """
    # Check for an existing customer with the same email under this user account.
    existing = db.execute(
        select(Customer).where(
            Customer.user_id == user_id,
            Customer.email == user_in.email,
        )
    ).scalar_one_or_none()

    if existing:
        # Email already exists — update the record instead of creating a duplicate.
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

    # No existing record — insert a fresh customer row.
    new_customer = Customer(
        user_id=user_id,
        full_name=user_in.full_name,
        email=user_in.email,
        country=user_in.country,
        total_spent=user_in.total_spent,
        last_purchase_date=user_in.last_purchase_date,
        review_score=user_in.review_score,
        review_text=user_in.review_text
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


async def get_customer(db: Session, id, user_id) -> CustomerRead | None:
    """
    Fetch a single customer by primary key, scoped to the current user.

    Args:
        db:      Active SQLAlchemy session.
        id:      Primary key of the customer to retrieve.
        user_id: ID of the authenticated user; ensures the customer belongs to them.

    Returns:
        CustomerRead Pydantic object if found, otherwise None.
    """
    db_customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()

    # If the customer exists, return it serialized as a Pydantic schema object.
    if db_customer:
        return CustomerRead.from_orm(db_customer)

    return None


async def list_customers(db: Session, skip: int, current_user_id: int) -> list[CustomerRead]:
    """
    Return a paginated list of customers belonging to the current user.

    Always returns a maximum of 10 records per page. The caller controls
    the starting offset via the skip parameter for pagination.

    Args:
        db:              Active SQLAlchemy session.
        skip:            Number of records to skip (pagination offset).
        current_user_id: ID of the authenticated user; restricts results to
                         their data only, isolating records from other users.

    Returns:
        List of CustomerRead Pydantic objects (max 10 per call).
    """
    db_customers = (
        db.query(Customer)
        .filter(Customer.user_id == current_user_id)  # restrict to logged-in user's customers only
        .offset(skip)                                  # skip by the passed-in offset for pagination
        .limit(10)                                     # return a maximum of 10 customers per page
        .all()                                         # execute the SQL query and fetch all results
    )

    # Serialize each ORM object into a CustomerRead Pydantic schema.
    customer_list = [CustomerRead.from_orm(cust) for cust in db_customers]
    return customer_list


def customer_delete(db: Session, id, user_id) -> bool:
    """
    Hard delete a customer record from the database.

    Scoped to the authenticated user so a user cannot delete another
    user's customer records.

    Args:
        db:      Active SQLAlchemy session.
        id:      Primary key of the customer to delete.
        user_id: ID of the authenticated user who owns the customer.

    Returns:
        True if the record was found and deleted, False if not found.
    """
    customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    if not customer:
        return False
    db.delete(customer)
    db.commit()
    return True


async def customer_update(db: Session, id: int, user_id: int, updates: CustomerUpdate) -> CustomerRead | None:
    """
    Apply a partial update to an existing customer record.

    Only fields explicitly provided in the updates payload are written;
    unset fields are left unchanged (via model_dump(exclude_unset=True)).

    Args:
        db:      Active SQLAlchemy session.
        id:      Primary key of the customer to update.
        user_id: ID of the authenticated user; ensures ownership before updating.
        updates: CustomerUpdate schema containing only the fields to change.

    Returns:
        Updated CustomerRead Pydantic object, or None if the customer was not found.
    """
    customer = db.query(Customer).filter(Customer.id == id).filter(Customer.user_id == user_id).first()
    if not customer:
        return None

    #Iterate only over fields that were explicitly set in the request payload.
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return CustomerRead.from_orm(customer)


def customer_count(db: Session, user_id: int) -> int:
    """
    Return the total number of customers owned by a specific user.

    Args:
        db:      Active SQLAlchemy session.
        user_id: ID of the authenticated user whose customers are counted.

    Returns:
        Integer count of customer records belonging to this user.
    """
    return db.query(Customer).filter(Customer.user_id == user_id).count()