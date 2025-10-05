# backend/app/routers/admin.py (create if doesn't exist)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.models.models import User, UserRole
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/users/{user_id}/promote-instructor")
async def promote_to_instructor(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Promote a user to instructor role (admin only)"""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = UserRole.INSTRUCTOR
    session.commit()

    return {"message": f"User {user.email} promoted to INSTRUCTOR"}
