"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime


class SignupRequest(BaseModel):
    """User signup/registration request."""
    attid: str = Field(..., min_length=3, max_length=50, description="AT&T ID")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has minimum complexity."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request."""
    attid: str = Field(..., description="AT&T ID")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """User login response with JWT token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    attid: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    roles: list[str] = Field(default_factory=list, description="User role names")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str = Field(..., description="Subject (user_id)")
    exp: datetime = Field(..., description="Expiration time")
