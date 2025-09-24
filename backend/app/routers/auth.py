from app.models.models import User, UserRole
from fastapi import Depends, HTTPException, status, Request
from fastapi import Response
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.models import (
    User, Profile, RefreshToken,
    UserCreate, UserRead,
    UserRole
)
from app.auth.utils import (
    hash_password, verify_password, create_access_token,
    generate_refresh_token, hash_refresh_token
)
from app.auth.dependencies import (
    get_current_user, set_auth_cookies, clear_auth_cookies,
    AuthenticationError
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register(
    user_data: UserCreate,
    response: Response,
    session: Session = Depends(get_session)
):
    """Register a new user. Creates user + profile in a single transaction, sets tokens as secure httpOnly cookies."""

    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Use a transaction so user and profile are created atomically
        with session.begin():
            hashed_password = hash_password(user_data.password)
            new_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                role=user_data.role if hasattr(
                    user_data, 'role') else UserRole.STUDENT
            )
            session.add(new_user)
            session.flush()  # ensure new_user.id is available

            new_profile = Profile(
                name=user_data.name,
                user_id=new_user.id
            )
            session.add(new_profile)

        # Refresh objects
        session.refresh(new_user)

        # Create tokens
        access_token = create_access_token({
            "sub": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role
        })

        refresh_token = generate_refresh_token()
        hashed_refresh_token = hash_refresh_token(refresh_token)

        # Save refresh token to DB (outside transaction to avoid re-using session.begin complexity)
        db_refresh_token = RefreshToken(
            hashed_token=hashed_refresh_token,
            user_id=new_user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session.add(db_refresh_token)
        session.commit()
        session.refresh(db_refresh_token)

        # Set cookies
        set_auth_cookies(response, access_token, refresh_token)

        logger.info(f"New user registered: {new_user.email}")

        return UserRead(
            id=new_user.id,
            email=new_user.email,
            role=new_user.role,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )

    except Exception as e:
        session.rollback()
        logger.exception("Error while registering user")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=dict)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login user and set access + refresh tokens in secure httpOnly cookies."""

    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    try:
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        })

        refresh_token = generate_refresh_token()
        hashed_refresh_token = hash_refresh_token(refresh_token)

        db_refresh_token = RefreshToken(
            hashed_token=hashed_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session.add(db_refresh_token)
        session.commit()
        session.refresh(db_refresh_token)

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

    except Exception as e:
        session.rollback()
        logger.exception("Error during login")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):
    """Refresh access token using refresh token (rotation + revocation)."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    hashed_token = hash_refresh_token(refresh_token)

    statement = select(RefreshToken).where(
        RefreshToken.hashed_token == hashed_token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    )
    db_refresh_token = session.exec(statement).first()

    if not db_refresh_token:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = session.get(User, db_refresh_token.user_id)
    if not user:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    try:
        # Revoke old token
        db_refresh_token.is_revoked = True
        session.add(db_refresh_token)

        # Create new tokens
        new_access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        })
        new_refresh_token = generate_refresh_token()
        new_hashed_refresh_token = hash_refresh_token(new_refresh_token)

        new_db_refresh_token = RefreshToken(
            hashed_token=new_hashed_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

        session.add(new_db_refresh_token)
        session.commit()
        session.refresh(new_db_refresh_token)

        # Link old to new AFTER new token has an id
        db_refresh_token.replaced_by_id = new_db_refresh_token.id
        session.add(db_refresh_token)
        session.commit()

        # Set new cookies
        set_auth_cookies(response, new_access_token, new_refresh_token)

        logger.info(f"Token refreshed for user {user.id}")

        return {"message": "Token refreshed successfully"}

    except Exception as e:
        session.rollback()
        logger.exception("Error during token refresh")
        clear_auth_cookies(response)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Logout user and revoke refresh token from this device."""
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            hashed_token = hash_refresh_token(refresh_token)

            statement = select(RefreshToken).where(
                RefreshToken.hashed_token == hashed_token,
                RefreshToken.user_id == current_user.id
            )
            db_refresh_token = session.exec(statement).first()

            if db_refresh_token:
                db_refresh_token.is_revoked = True
                session.add(db_refresh_token)
                session.commit()

        except Exception as e:
            session.rollback()
            logger.warning(f"Error during logout: {e}")

    clear_auth_cookies(response)
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logout successful"}


@router.post("/logout-all", response_model=dict)
async def logout_all(
    response: Response,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Revoke all refresh tokens for the current user."""
    try:
        statement = select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False
        )
        refresh_tokens = session.exec(statement).all()

        for token in refresh_tokens:
            token.is_revoked = True
            session.add(token)

        session.commit()
        clear_auth_cookies(response)
        logger.info(f"All sessions revoked for user: {current_user.email}")
        return {"message": "Logged out from all devices"}

    except Exception as e:
        session.rollback()
        logger.exception("Error during logout-all")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
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


@router.get("/test-protected")
async def test_protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "This is a protected route!",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role
        }
    }

