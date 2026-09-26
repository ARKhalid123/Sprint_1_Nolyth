"""
Main entry point for the Personal Expense Tracker backend.
FastAPI application with SQLite database and modular routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.database import engine, Base
from backend.routers import auth_router, expense_router

# Create all database tables in SQLite (if they don't already exist)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Personal Expense Tracker API",
    description="A modular REST API for managing personal expenses with JWT authentication and SQLite storage.",
    version="1.0.0"
)

# Configure CORS so Streamlit (or other frontends) can communicate without issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router.router)
app.include_router(expense_router.router)



if __name__ == "__main__":
    # Allows running directly with: python main.py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)