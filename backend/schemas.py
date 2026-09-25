"""
Pydantic schemas for request and response validation.
Ensures strong typing, input sanitation, and automated documentation.
"""

from datetime import date as dt_date, datetime as dt_datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# ==========================================
# User Schemas
# ==========================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid user email address")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password with at least 6 characters")

    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        clean_name = v.strip()
        if len(clean_name) < 3:
            raise ValueError("Username must contain at least 3 non-whitespace characters.")
        return clean_name


class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    id: int
    created_at: dt_datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ==========================================
# Expense Schemas
# ==========================================

ALLOWED_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Utilities",
    "Entertainment & Leisure",
    "Shopping & Groceries",
    "Health & Medical",
    "Education",
    "Personal Care",
    "Bills & Subscriptions",
    "Other",
]


class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Short title of the expense")
    amount: float = Field(..., gt=0, description="Expense amount must be greater than 0")
    category: str = Field(..., description="Category for grouping expenses")
    date: dt_date = Field(default_factory=dt_date.today, description="Date of the expense")
    description: Optional[str] = Field(None, max_length=255, description="Optional extra notes")

    @field_validator("title")
    def title_cannot_be_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Expense title cannot be empty or just spaces.")
        return clean

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Category cannot be empty.")
        return clean


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    date: Optional[dt_date] = None
    description: Optional[str] = Field(None, max_length=255)

    @field_validator("title")
    def title_cannot_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Expense title cannot be empty.")
            return clean
        return v


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    created_at: dt_datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseSummary(BaseModel):
    total_amount: float
    total_count: int
    average_amount: float
    category_breakdown: Dict[str, float]
    recent_expenses: List[ExpenseResponse]
