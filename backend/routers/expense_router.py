"""
Expense router: handles CRUD endpoints for personal expenses
as well as filtering, search, and analytics summary.
All endpoints require JWT Bearer token authentication.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas, crud
from backend.auth import get_current_user
from backend.models import User

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_new_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new expense entry for the current authenticated user.
    Pydantic automatically validates amount > 0 and non-empty title.
    """
    return crud.create_expense(db=db, expense=expense, user_id=current_user.id)


@router.get("/", response_model=List[schemas.ExpenseResponse])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category name"),
    start_date: Optional[date] = Query(None, description="Filter expenses on or after this date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter expenses on or before this date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Keyword search in title or description"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all expenses for the authenticated user.
    Supports filtering by category, date range, search query, and pagination.
    """
    expenses = crud.get_expenses(
        db=db,
        user_id=current_user.id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=skip,
        limit=limit
    )
    return expenses


@router.get("/summary", response_model=schemas.ExpenseSummary)
def get_expenses_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated summary statistics for the user's spending:
    total spent, total count, average transaction, category breakdown, and recent expenses.
    """
    return crud.get_expense_summary(db=db, user_id=current_user.id)


@router.get("/categories/list", response_model=List[str])
def get_categories():
    """
    Return the standard list of expense categories.
    """
    return schemas.ALLOWED_CATEGORIES


@router.get("/{expense_id}", response_model=schemas.ExpenseResponse)
def get_single_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific expense by ID.
    Only allows access if the expense belongs to the current user.
    """
    expense = crud.get_expense_by_id(db=db, expense_id=expense_id, user_id=current_user.id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return expense


@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_existing_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing expense by ID.
    Can update one or more fields (title, amount, category, date, description).
    """
    updated_expense = crud.update_expense(
        db=db,
        expense_id=expense_id,
        expense_update=expense_update,
        user_id=current_user.id
    )
    if not updated_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return updated_expense


@router.delete("/{expense_id}", status_code=status.HTTP_200_OK)
def delete_existing_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an expense entry by ID.
    """
    success = crud.delete_expense(db=db, expense_id=expense_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found."
        )
    return {"message": f"Expense {expense_id} deleted successfully."}
