"""
Dependencies for dependency injection
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from core.database import get_db
from core.security import decode_token
from services.auth_service import AuthService
from schemas.auth import TokenData

security = HTTPBearer(auto_error=False)


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from Authorization header or cookies"""
    # Try Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    # Try cookies
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token
    
    return None


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> TokenData:
    """Get current authenticated user from JWT token (header or cookie)"""
    # Get token from header or cookie
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = get_token_from_request(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    return TokenData(
        user_id=UUID(user_id),
        email=payload.get("email"),
        role=payload.get("role"),
    )


def require_role(allowed_roles: list[str]):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker


# Convenience dependencies for common role checks
def require_admin(current_user: TokenData = Depends(require_role(["admin"]))) -> TokenData:
    """Require admin role"""
    return current_user


def require_clinician(current_user: TokenData = Depends(require_role(["clinician", "admin"]))) -> TokenData:
    """Require clinician or admin role"""
    return current_user


def require_researcher(current_user: TokenData = Depends(require_role(["researcher", "admin"]))) -> TokenData:
    """Require researcher or admin role"""
    return current_user

