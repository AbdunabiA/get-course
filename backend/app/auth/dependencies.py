# backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request, Response
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.models import User, RefreshToken, UserRole
from app.core.config import settings
from app.auth.utils import verify_access_token, verify_refresh_token_hash, create_access_token, generate_refresh_token, hash_refresh_token
from datetime import datetime, timedelta
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


def get_refresh_token_from_cookie(request: Request) -> str:
    """Extract refresh token from HTTP-only cookie"""
    token = request.cookies.get("refresh_token")
    if not token:
        raise AuthenticationError("Refresh token not found")
    return token


async def get_current_user(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
) -> User:
    """
    Get current user from access token, with automatic refresh if needed
    This dependency handles token refresh automatically
    """
    try:
        # Try to get access token
        access_token = get_token_from_cookie(request)
        payload = verify_access_token(access_token)

        if payload is None:
            raise AuthenticationError("Invalid access token")

        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")

    except AuthenticationError:
        # Access token failed, try refresh token
        try:
            refresh_token = get_refresh_token_from_cookie(request)
            user = await refresh_user_token(refresh_token, response, session)
            return user
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("Authentication failed")

    # Get user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if user is None:
        raise AuthenticationError("User not found")

    return user


async def refresh_user_token(
    refresh_token: str,
    response: Response,
    session: Session
) -> User:
    """Handle token refresh and rotation"""
    # Hash the refresh token to look up in database
    hashed_token = hash_refresh_token(refresh_token)

    # Find the refresh token in database
    statement = select(RefreshToken).where(
        RefreshToken.hashed_token == hashed_token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    )
    db_refresh_token = session.exec(statement).first()

    if not db_refresh_token:
        raise AuthenticationError("Invalid or expired refresh token")

    # Get the user
    user = session.get(User, db_refresh_token.user_id)
    if not user:
        raise AuthenticationError("User not found")

    # Revoke the old refresh token (rotation)
    db_refresh_token.is_revoked = True

    # Create new tokens
    new_access_token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })

    new_refresh_token = generate_refresh_token()
    new_hashed_refresh_token = hash_refresh_token(new_refresh_token)

    # Save new refresh token to database
    new_db_refresh_token = RefreshToken(
        hashed_token=new_hashed_refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30),
        replaced_by_id=None
    )

    # Link the old token to new one (for audit trail)
    db_refresh_token.replaced_by_id = new_db_refresh_token.id

    session.add(new_db_refresh_token)
    session.commit()

    # Set new cookies
    set_auth_cookies(response, new_access_token, new_refresh_token)

    logger.info(f"Token refreshed for user {user.id}")
    return user


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HTTP-only cookies for authentication"""
    # Set access token cookie (15 minutes)
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

# Role-based access control


def require_role(required_role: UserRole):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if required_role == UserRole.ADMIN:
            # Admin access
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        elif required_role == UserRole.INSTRUCTOR:
            # Instructor or Admin access
            if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Instructor access required"
                )
        # For STUDENT role, any authenticated user can access

        return current_user

    return role_checker


# Convenience dependencies
require_admin = require_role(UserRole.ADMIN)
require_instructor = require_role(UserRole.INSTRUCTOR)
require_student = require_role(UserRole.STUDENT)  # Any authenticated user
