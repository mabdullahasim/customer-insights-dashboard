from fastapi import FastAPI, UploadFile, File
from app.schemas.customer import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, HTTPException
from app.schemas.analytics import Message
from fastapi import APIRouter
from app.crud.data_import import data_import
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi import Depends
from app.core.security import get_current_active_user
router = APIRouter(prefix="/utils", tags=["utils"])

@router.post("/upload/customers", response_model=Message)
async def upload_customers(file: UploadFile = File(...), current_user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")


    return await data_import(file, current_user.id, db)
