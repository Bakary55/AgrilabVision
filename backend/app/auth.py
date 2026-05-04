import os
import re
import secrets
from datetime import datetime, timedelta
from typing import Dict

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    PasswordResetConfirm,
    PasswordResetRequest,
    UserLogin,
    UserOut,
    UserRegister,
)

# ------------------------------
# Security settings
# ------------------------------

SECRET_KEY = (os.getenv("SECRET_KEY") or "").strip()
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Configure it in environment variables.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing using bcrypt directly (passlib has compatibility issues with bcrypt 4.x).

# OAuth2 helper for extracting Bearer tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------------
# Helper functions
# ------------------------------


def hash_password(password: str) -> str:
    """Hash a raw password using bcrypt."""

    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a raw password against the stored hash."""

    return bcrypt.checkpw(
        plain_password.encode("utf-8"), password_hash.encode("utf-8")
    )


def validate_password_strength(password: str) -> None:
    """
    Validate password rules using a clear regex.

    Rules:
    - min 8 chars
    - at least 1 uppercase
    - at least 1 lowercase
    - at least 1 number
    - at least 1 special character
    """

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
    if not re.match(pattern, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long and include "
                "uppercase, lowercase, number, and special character."
            ),
        )


def create_reset_token() -> str:
    """Generate a secure random token for password resets."""

    return secrets.token_urlsafe(32)


def create_access_token(payload: Dict[str, str]) -> str:
    """Create a JWT access token with an expiry time."""

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**payload, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the currently logged-in user from the JWT."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


# ------------------------------
# Auth endpoints
# ------------------------------


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegister, db: Session = Depends(get_db)
) -> User:
    """Register a new user account."""

    validate_password_strength(payload.password)

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        age=payload.age,
        user_type=payload.user_type,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login")
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Dict[str, object]:
    """Login and return a JWT token plus user details."""

    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token({"user_id": user.id, "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user, from_attributes=True),
    }


@router.post("/forgot-password")
def forgot_password(
    payload: PasswordResetRequest, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Create a reset token if the email exists (always return success)."""

    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        user.reset_token = create_reset_token()
        user.reset_token_expiration = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

    # Always return a generic message for security.
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(
    payload: PasswordResetConfirm, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Reset password using a valid reset token."""

    validate_password_strength(payload.new_password)

    user = db.query(User).filter(User.reset_token == payload.reset_token).first()
    if not user or not user.reset_token_expiration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token.")

    if user.reset_token_expiration < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired.")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expiration = None
    db.commit()

    return {"message": "Password has been reset successfully."}


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the current logged-in user."""

    return current_user
