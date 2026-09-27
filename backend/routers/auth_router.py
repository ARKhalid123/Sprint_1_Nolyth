

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas, crud
from backend.auth import verify_password, create_access_token, get_current_user
from backend.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if username already exists
    existing_username = crud.get_user_by_username(db, username=user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered. Please choose another."
        )

    # Check if email already exists
    existing_email = crud.get_user_by_email(db, email=user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered. Please login or use a different email."
        )

    # Create new user in the database
    new_user = crud.create_user(db=db, user=user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Search by username first, if not found search by email
    user = crud.get_user_by_username(db, username=login_data.username)
    if not user:
        user = crud.get_user_by_email(db, email=login_data.username)

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT access token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def read_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
