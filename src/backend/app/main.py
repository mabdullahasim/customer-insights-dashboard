"""
main.py
=======
FastAPI application entry point for the Customer Insights Dashboard API.

Initializes the FastAPI app, registers CORS middleware, creates all database
tables on startup, and mounts all API routers under their respective prefixes.

Routers:
  /auth        - Authentication (login, registration)
  /secure      - Protected profile endpoints
  /customers   - Customer CRUD operations
  /utils       - Utility operations (CSV import)
  /analytics   - Analytics and ML pipeline endpoints

CORS:
  Allowed origin: http://localhost:5173 (Vite dev server)

Dependencies:
  - FastAPI
  - SQLAlchemy engine and Base from app.core.database
  - Internal routers from app.api
"""

from fastapi import FastAPI
from app.api import auth
from app.api import secure
from app.api import customers
from app.api import csv_parser
from app.api import analytics
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


Base.metadata.create_all(bind=engine)


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(secure.router)
app.include_router(customers.router)
app.include_router(csv_parser.router)
app.include_router(analytics.router)


@app.get("/test")
def test():
    """Health check endpoint to confirm the API is running."""
    return {"message": "API is working!"}