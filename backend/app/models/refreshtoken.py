from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid
from .base import TimestampMixin


class RefreshToken(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    hashed_token: str = Field(unique=True, index=True)
    is_revoked: bool = Field(default=False)
    expires_at: datetime
    user_id: str = Field(foreign_key="user.id")
    replaced_by_id: Optional[str] = Field(
        default=None, foreign_key="refreshtoken.id")

    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
