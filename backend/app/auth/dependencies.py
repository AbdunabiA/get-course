# backend/app/auth/dependencies.py - SIMPLIFIED VERSION
from fastapi import Response
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.models import User, UserRole
from app.auth.utils import verify_access_token
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_from_cookie(request: Request) -> str:
    """Extract access token from HTTP-only cookie"""
    token = request.cookies.get("access_token")
    if not token:
        raise AuthenticationError("Access token not found")
    return token


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """
    Get current user from access token
    NO auto-refresh - frontend handles token refresh
    """
    # Get access token from cookie
    access_token = get_token_from_cookie(request)

    # Verify token
    payload = verify_access_token(access_token)
    if payload is None:
        raise AuthenticationError("Invalid or expired access token")

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    # Get user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if user is None:
        raise AuthenticationError("User not found")

    return user


# Role-based access control
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {UserRole.ADMIN},
    UserRole.INSTRUCTOR: {UserRole.ADMIN, UserRole.INSTRUCTOR},
    UserRole.STUDENT: {UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.STUDENT}
}


def require_role(required_role: UserRole):


    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        allowed = ROLE_PERMISSIONS.get(required_role, set())
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.name} access required"
            )
        return current_user

    return role_checker


# Convenience dependencies
require_admin = require_role(UserRole.ADMIN)
require_instructor = require_role(UserRole.INSTRUCTOR)
require_student = require_role(UserRole.STUDENT)

# Cookie utilities (moved from old dependencies)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HTTP-only cookies for authentication"""

    # Set access token cookie (30 minutes)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )

    # Set refresh token cookie (30 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=30 * 24 * 60 * 60,  # 30 days in seconds
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )


def clear_auth_cookies(response: Response):
    """Clear authentication cookies"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
