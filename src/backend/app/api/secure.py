from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user import UserInDB

router = APIRouter(prefix="/secure", tags=["secure"])
@router.get("/profile")
def profile(current_user = Depends(get_current_user)):
    return {"username": current_user.username}