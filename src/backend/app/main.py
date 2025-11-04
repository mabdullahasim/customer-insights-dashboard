from fastapi import FastAPI
from app.api import auth
from app.api import secure
from app.core.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Customer Insights Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(secure.router)

# Test endpoint
@app.get("/test")
def test():
    return {"message": "API is working!"}

