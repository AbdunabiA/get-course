# backend/app/routers/auth.py - SIMPLIFIED VERSION
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import (
    User, Profile, RefreshToken,
    UserRole
)
from app.schemas import UserCreate
from app.auth.utils import (
    hash_password, verify_password, create_access_token,
    generate_refresh_token, hash_refresh_token
)
from app.auth.dependencies import (
    get_current_user, set_auth_cookies, clear_auth_cookies,
    AuthenticationError
)
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    response: Response,
    session: Session = Depends(get_session)
):
    """Register a new user"""

    try:
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role if hasattr(
                user_data, 'role') else UserRole.STUDENT
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Create user profile
        new_profile = Profile(
            name=user_data.name,
            user_id=new_user.id
        )
        session.add(new_profile)
        session.commit()

        # Create tokens
        access_token = create_access_token({
            "sub": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        })

        refresh_token = generate_refresh_token()
        hashed_refresh_token = hash_refresh_token(refresh_token)

        # Save refresh token to database
        db_refresh_token = RefreshToken(
            hashed_token=hashed_refresh_token,
            user_id=new_user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session.add(db_refresh_token)
        session.commit()

        # Set cookies
        set_auth_cookies(response, access_token, refresh_token)

        logger.info(f"New user registered: {new_user.email}")

        return {
            "message": "Registration successful",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error while registering user: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=dict)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login user with email and password"""

    # Find user by email
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create tokens
    access_token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })

    refresh_token = generate_refresh_token()
    hashed_refresh_token = hash_refresh_token(refresh_token)

    # Save refresh token to database
    db_refresh_token = RefreshToken(
        hashed_token=hashed_refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    session.add(db_refresh_token)
    session.commit()

    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)

    logger.info(f"User logged in: {user.email}")

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):
    """Refresh access token using refresh token - SIMPLIFIED VERSION"""

    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

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
        clear_auth_cookies(response)  # Clear invalid cookies
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get the user
    user = session.get(User, db_refresh_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

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
        expires_at=datetime.utcnow() + timedelta(days=30)
    )

    # Link the old token to new one (for audit trail)
    db_refresh_token.replaced_by_id = new_db_refresh_token.id

    session.add(new_db_refresh_token)
    session.commit()

    # Set new cookies
    set_auth_cookies(response, new_access_token, new_refresh_token)

    logger.info(f"Token refreshed for user {user.id}")

    return {
        "message": "Token refreshed successfully"
    }


@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Logout user and revoke refresh token - SIMPLIFIED VERSION"""

    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            hashed_token = hash_refresh_token(refresh_token)

            # Find and revoke the refresh token
            statement = select(RefreshToken).where(
                RefreshToken.hashed_token == hashed_token,
                RefreshToken.user_id == current_user.id
            )
            db_refresh_token = session.exec(statement).first()

            if db_refresh_token:
                db_refresh_token.is_revoked = True
                session.commit()

        except Exception as e:
            logger.warning(f"Error during logout: {e}")

    # Clear cookies regardless of refresh token status
    clear_auth_cookies(response)

    logger.info(f"User logged out: {current_user.email}")

    return {"message": "Logout successful"}


@router.post("/logout-all", response_model=dict)
async def logout_all(
    response: Response,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Logout from all devices (revoke all refresh tokens)"""

    # Revoke all refresh tokens for this user
    statement = select(RefreshToken).where(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    )
    refresh_tokens = session.exec(statement).all()

    for token in refresh_tokens:
        token.is_revoked = True

    session.commit()

    # Clear cookies
    clear_auth_cookies(response)

    logger.info(f"All sessions revoked for user: {current_user.email}")

    return {"message": "Logged out from all devices"}


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current user information"""

    # Get user profile
    statement = select(Profile).where(Profile.user_id == current_user.id)
    profile = session.exec(statement).first()

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        },
        "profile": {
            "name": profile.name if profile else None,
            "bio": profile.bio if profile else None,
            "avatar": profile.avatar if profile else None
        } if profile else None
    }

# Development endpoint - remove in production


@router.get("/test-protected")
async def test_protected_route(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify authentication is working"""
    return {
        "message": "This is a protected route!",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role
        }
    }
