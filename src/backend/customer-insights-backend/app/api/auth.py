from passlib.context import CryptContext
from fastapi import FastAPI, status, Depends, HTTPException
import models
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JwtError, jwt
from dotenv import load_dotenv
import os

@app.post("/token", reponse_modeL=Token)
async def login_for_acess_token(form_data: OAuth2PasswordRequestForm = Depends()): # Data accepted to generate a JWT is username and password, depending on data to parse
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    TOKEN_EXPIRES = os.getenv("TOKEN_EXPIRES")
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type":"bearer"}



