"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    password: str
    role: str  # clinician, researcher, admin


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    email: str
    role: str
    specialty: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    heti_number: Optional[str] = None
    license_number: Optional[str] = None
    workplace_municipality: Optional[str] = None
    primary_workplace: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    heti_number: Optional[str] = Field(None, max_length=20)
    license_number: Optional[str] = Field(None, max_length=50)
    workplace_municipality: Optional[str] = Field(None, max_length=10)
    primary_workplace: Optional[str] = Field(None, max_length=255)

