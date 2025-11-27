"""
Authentication service
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User
from schemas.auth import UserCreate, UserResponse, UserUpdate
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from datetime import timedelta
from core.config import settings


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Validate role
        valid_roles = ["clinician", "researcher", "admin"]
        if user_data.role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")

        # Create user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for a user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> Optional[dict]:
        """Refresh an access token using a refresh token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = UUID(payload.get("sub"))
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return None

        return AuthService.create_tokens(user)

    @staticmethod
    def list_users(db: Session) -> list[User]:
        """List all users"""
        stmt = select(User).order_by(User.email)
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update a user"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return None

        # Update email if provided
        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = AuthService.get_user_by_email(db, user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already in use")
            user.email = user_data.email

        # Update password if provided
        if user_data.password is not None:
            user.password_hash = get_password_hash(user_data.password)

        # Update role if provided
        if user_data.role is not None:
            valid_roles = ["clinician", "researcher", "admin"]
            if user_data.role not in valid_roles:
                raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
            user.role = user_data.role

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Delete a user"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True

