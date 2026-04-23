from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import UserModel, get_user
async def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User:
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        role="user",
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def change_password(db: Session, db_user: UserModel, hashed_password: str) -> User:
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

