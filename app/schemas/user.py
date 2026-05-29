"""
schemas/user.py
---------------
Pydantic schemas for User endpoints.
- UserCreate     : data required to register a new account
- UserLogin      : data required to log in
- UserUpdate     : optional fields for updating a profile
- UserResponse   : what the API returns when showing a user (no password)
- TokenResponse  : what the API returns after a successful login
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Request Schemas (incoming data) ───────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for registering a new user — all fields required."""
    username: str
    email: EmailStr
    password: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        """Username must be 3-50 chars and contain no spaces."""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be under 50 characters")
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v):
        """Password must be at least 6 characters."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    """Schema for logging in — email + password only."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a profile — all fields optional."""
    username: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


# ── Response Schemas (outgoing data) ──────────────────────────────────────────

class UserResponse(BaseModel):
    """
    What the API returns when showing user data.
    Never includes the hashed password.
    """
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    # Tells Pydantic to read data from SQLAlchemy model attributes
    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """
    Lightweight user info embedded inside post/comment responses.
    Avoids exposing full user details in nested objects.
    """
    id: int
    username: str
    profile_picture_url: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Returned after a successful login."""
    access_token: str
    token_type: str = "bearer"
