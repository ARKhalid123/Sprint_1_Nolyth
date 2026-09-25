"""
SQLAlchemy database models for Users and Expenses.
Defines the table structure and relationships.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    """
    User model representing registered users in the database.
    Each user can have multiple expenses.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many relationship: One user can have many expenses
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")


class Expense(Base):
    """
    Expense model representing a single expense record.
    Connected to a specific user via foreign key.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # e.g., Food, Travel, Utilities, Entertainment, Health
    date = Column(Date, default=date.today, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key pointing to the user who created this expense
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Many-to-one relationship: Many expenses belong to one user
    owner = relationship("User", back_populates="expenses")
