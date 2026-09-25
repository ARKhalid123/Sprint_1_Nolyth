"""
Database configuration and session management for Personal Expense Tracker.
Uses SQLite for simple local database storage with SQLAlchemy ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file location (SQLite will create expenses.db in the project folder)
SQLALCHEMY_DATABASE_URL = "sqlite:///./expenses.db"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is required for SQLite when used with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session for each API request.
    Automatically closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
