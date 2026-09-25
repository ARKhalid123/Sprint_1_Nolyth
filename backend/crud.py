"""
CRUD (Create, Read, Update, Delete) operations for the database.
Keeps SQL / ORM operations separated from route handlers for clean modular architecture.
"""

from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend import models, schemas
from backend.auth import hash_password


# ==========================================
# User CRUD Operations
# ==========================================

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Retrieve a user by their unique username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Retrieve a user by their unique email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with a hashed password."""
    hashed_pwd = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==========================================
# Expense CRUD Operations
# ==========================================

def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int) -> models.Expense:
    """Create a new expense linked to the authenticated user."""
    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        description=expense.description,
        user_id=user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(
    db: Session,
    user_id: int,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Expense]:
    """
    Get a list of expenses for a specific user with optional filters:
    - category filter
    - date range (start_date to end_date)
    - keyword search in title or description
    - pagination (skip, limit)
    """
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)

    if category and category != "All":
        query = query.filter(models.Expense.category == category)

    if start_date:
        query = query.filter(models.Expense.date >= start_date)

    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Expense.title.ilike(search_pattern)) | 
            (models.Expense.description.ilike(search_pattern))
        )

    # Order newest first
    return query.order_by(models.Expense.date.desc(), models.Expense.id.desc()).offset(skip).limit(limit).all()


def get_expense_by_id(db: Session, expense_id: int, user_id: int) -> Optional[models.Expense]:
    """Retrieve a single expense by ID belonging to the user."""
    return db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()


def update_expense(
    db: Session,
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    user_id: int
) -> Optional[models.Expense]:
    """Update fields of an existing expense."""
    db_expense = get_expense_by_id(db, expense_id=expense_id, user_id=user_id)
    if not db_expense:
        return None

    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int, user_id: int) -> bool:
    """Delete an expense record."""
    db_expense = get_expense_by_id(db, expense_id=expense_id, user_id=user_id)
    if not db_expense:
        return False

    db.delete(db_expense)
    db.commit()
    return True


def get_expense_summary(db: Session, user_id: int) -> Dict:
    """
    Calculate summary metrics for a user's expenses:
    - total amount spent
    - total number of expenses
    - average expense amount
    - breakdown by category
    - top 5 recent expenses
    """
    expenses = db.query(models.Expense).filter(models.Expense.user_id == user_id).all()

    total_amount = sum(e.amount for e in expenses)
    total_count = len(expenses)
    average_amount = (total_amount / total_count) if total_count > 0 else 0.0

    category_breakdown: Dict[str, float] = {}
    for e in expenses:
        category_breakdown[e.category] = round(category_breakdown.get(e.category, 0.0) + e.amount, 2)

    recent_expenses = (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .order_by(models.Expense.date.desc(), models.Expense.id.desc())
        .limit(5)
        .all()
    )

    return {
        "total_amount": round(total_amount, 2),
        "total_count": total_count,
        "average_amount": round(average_amount, 2),
        "category_breakdown": category_breakdown,
        "recent_expenses": recent_expenses
    }
