from fastapi import APIRouter, status, Depends, HTTPException
import models
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()
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

@app.get("/users/me/", reponse_modeL=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id" : 1, "owner" :current_user}]