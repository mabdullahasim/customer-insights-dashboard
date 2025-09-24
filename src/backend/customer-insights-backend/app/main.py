from fastapi import FastAPI, status, Depends, HTTPException
import models
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JwtError, jwt

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/test")

