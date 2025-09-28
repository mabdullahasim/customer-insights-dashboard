from fastapi import FastAPI
from app.api import auth
from app.core.database import engine, Base

app = FastAPI(title="Customer Insights Dashboard API")

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Test endpoint
@app.get("/test")
def test():
    return {"message": "API is working!"}