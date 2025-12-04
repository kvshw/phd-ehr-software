"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
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
    request: Request,
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
    
    # Set cookies directly from backend (works across subdomains with proper domain)
    # Determine domain for cookies (shared parent domain for subdomains)
    origin = request.headers.get("origin", "")
    cookie_domain = None
    if "rahtiapp.fi" in origin:
        cookie_domain = ".2.rahtiapp.fi"  # Shared domain for all .2.rahtiapp.fi subdomains
    
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,  # Always secure in production (HTTPS)
        samesite="lax",
        max_age=8 * 60 * 60,  # 8 hours (480 minutes)
        path="/",
        domain=cookie_domain,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,  # Always secure in production (HTTPS)
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
        path="/",
        domain=cookie_domain,
    )
    
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


class RegistrationRequest(BaseModel):
    """Schema for self-registration request"""
    email: str
    password: str
    role: str  # 'clinician' (doctor) or 'nurse'
    specialty: Optional[str] = None
    department: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    license_number: Optional[str] = None
    heti_number: Optional[str] = None
    primary_workplace: Optional[str] = None


@router.post("/register-request", status_code=status.HTTP_201_CREATED)
async def register_request(
    request: RegistrationRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a registration request (public endpoint).
    
    For this research platform, we create the user immediately but log it for audit.
    In a production system, this would require admin approval.
    """
    from models.user import User
    from core.security import get_password_hash
    
    try:
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )
        
        # Validate role
        valid_roles = ["clinician", "nurse"]
        if request.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role for self-registration. Must be one of: {', '.join(valid_roles)}",
            )
        
        # Create user
        hashed_password = get_password_hash(request.password)
        db_user = User(
            email=request.email,
            password_hash=hashed_password,
            role=request.role,
            specialty=request.specialty,
            department=request.department,
            first_name=request.first_name,
            last_name=request.last_name,
            title=request.title or ("Dr." if request.role == "clinician" else "RN"),
            license_number=request.license_number,
            heti_number=request.heti_number,
            primary_workplace=request.primary_workplace,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "success": True,
            "message": "Registration successful. You can now log in.",
            "user_id": str(db_user.id),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token"""
    tokens = AuthService.refresh_access_token(refresh_data.refresh_token, db)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Set cookies directly from backend (works across subdomains with proper domain)
    origin = request.headers.get("origin", "")
    cookie_domain = None
    if "rahtiapp.fi" in origin:
        cookie_domain = ".2.rahtiapp.fi"  # Shared domain for all .2.rahtiapp.fi subdomains
    
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=8 * 60 * 60,  # 8 hours
        path="/",
        domain=cookie_domain,
    )
    if tokens.get("refresh_token"):
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 24 * 60 * 60,  # 30 days
            path="/",
            domain=cookie_domain,
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


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user = Depends(get_current_user),
):
    """
    Logout endpoint - clears authentication cookies.
    Requires valid authentication to logout (prevents CSRF).
    """
    # Determine domain for cookies (same as login)
    origin = request.headers.get("origin", "")
    cookie_domain = None
    if "rahtiapp.fi" in origin:
        cookie_domain = ".2.rahtiapp.fi"
    
    # Clear cookies by setting them to expire immediately
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,  # Expire immediately
        path="/",
        domain=cookie_domain,
    )
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,  # Expire immediately
        path="/",
        domain=cookie_domain,
    )
    
    return {"success": True, "message": "Logged out successfully"}

