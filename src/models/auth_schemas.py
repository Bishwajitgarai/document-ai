"""Pydantic schemas for authentication."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload."""
    email: str | None = None


class UserResponse(BaseModel):
    """Schema for user information response."""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
