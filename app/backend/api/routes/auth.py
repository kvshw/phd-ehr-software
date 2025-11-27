"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
)
from services.auth_service import AuthService
from core.dependencies import require_admin, get_current_user
from core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Login endpoint - returns JWT tokens and optionally sets cookies"""
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = AuthService.create_tokens(user)
    
    # Optionally set cookies (frontend can also handle this via API route)
    # Uncomment if you want backend to set cookies directly:
    # response.set_cookie(
    #     key="access_token",
    #     value=tokens["access_token"],
    #     httponly=True,
    #     secure=settings.NODE_ENV == "production",
    #     samesite="lax",
    #     max_age=30 * 60,  # 30 minutes
    # )
    # response.set_cookie(
    #     key="refresh_token",
    #     value=tokens["refresh_token"],
    #     httponly=True,
    #     secure=settings.NODE_ENV == "production",
    #     samesite="lax",
    #     max_age=7 * 24 * 60 * 60,  # 7 days
    # )
    
    return tokens


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),  # Only admins can create users
):
    """Register a new user (admin only)"""
    try:
        user = AuthService.create_user(db, user_data)
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token"""
    tokens = AuthService.refresh_access_token(refresh_data.refresh_token, db)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user information"""
    user = AuthService.get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        specialty=user.specialty,
        first_name=user.first_name,
        last_name=user.last_name,
        title=user.title,
        department=user.department,
        heti_number=user.heti_number,
        license_number=user.license_number,
        workplace_municipality=user.workplace_municipality,
        primary_workplace=user.primary_workplace,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile (specialty, name, etc.)"""
    from models.user import User
    
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Allowed fields for self-update
    allowed_fields = [
        'specialty', 'first_name', 'last_name', 'title', 
        'department', 'primary_workplace', 'workplace_municipality'
    ]
    
    for field in allowed_fields:
        if field in update_data:
            setattr(user, field, update_data[field])
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        specialty=user.specialty,
        first_name=user.first_name,
        last_name=user.last_name,
        title=user.title,
        department=user.department,
        heti_number=user.heti_number,
        license_number=user.license_number,
        workplace_municipality=user.workplace_municipality,
        primary_workplace=user.primary_workplace,
    )

