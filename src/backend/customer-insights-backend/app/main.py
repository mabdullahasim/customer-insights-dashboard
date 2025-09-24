from fastapi import FastAPI, status, Depends, HTTPException
import models
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.sequrity import OAuth2PasswordBearer, OAuth2PasswordRequestFrom
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JwtError, jwt

app = FastApi()

models.Base.metadata.create_all(bind=engine)

@app.get("/test")
as
