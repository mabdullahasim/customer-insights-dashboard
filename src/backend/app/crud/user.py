async def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user






def update_user():



def delete_user():

