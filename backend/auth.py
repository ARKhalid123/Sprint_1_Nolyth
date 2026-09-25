"""
Authentication module: password hashing, JWT token generation,
and FastAPI dependency to verify the current logged-in user.
"""

import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models

# Configuration for JWT
# In production, this should be stored in environment variables
SECRET_KEY = "nolyth_sprint_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours token validity

# HTTP Bearer scheme for token extraction in FastAPI docs and headers
security = HTTPBearer()


# ==========================================
# Password Hashing Utilities
# (Uses standard library hashlib PBKDF2 for simplicity, safety, and no external C-build issues)
# ==========================================

def hash_password(password: str) -> str:
    """
    Hashes a password with a random salt using PBKDF2-HMAC-SHA256.
    Returns format: salt$hash
    """
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations=100_000
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches the stored salted hash.
    """
    try:
        salt, stored_key = hashed_password.split("$")
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100_000
        )
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False


# ==========================================
# JWT Token Generation & Verification
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes user data into a JSON Web Token (JWT) with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    FastAPI dependency that extracts the Bearer token, validates it,
    and returns the corresponding User database record.
    Raises HTTPException 401 if token is invalid or user is not found.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or session has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Query the user from the database
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    return user
