from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from .base import TimestampMixin


class Profile(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    user_id: str = Field(foreign_key="user.id", unique=True)

    user: Optional["User"] = Relationship(back_populates="profile")
