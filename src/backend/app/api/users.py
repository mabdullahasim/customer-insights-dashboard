from app.models.user import User
from fastapi import APIRouter, status, Depends, HTTPException
from app.core.security import get_user_by_email, get_password_hash
from sqlalchemy.orm import Session
from app.crud.user import change_password
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db

@router.post("/forgotPassword", response_model=User, status_code=status.HTTP_200_ok) #response modle is of type User
async def forgotPassword(user_in: User , db: Session = Depends(get_db)): #user_in is of type schema

    db_user = get_user_by_email(db, user_in.email) #check if user exists by fetching user by email
    if not db_user: #check if user exsits raise code 400 if not
        raise HTTPException(status_code=400, detail="User with that email does not exist")

    #get the password hash for the user if new user
    hashed_password = await get_password_hash(user_in.password)

    updated_user = change_password(db, db_user, hashed_password)

    return updated_user