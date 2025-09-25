from fastapi import FastAPI
from core.database import engine, Base
from api import auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/test")
async def test():
    return {"message": "API working!"}