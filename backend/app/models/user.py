from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from .base import TimestampMixin
from .enums import UserRole


class User(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.STUDENT)

    profile: Optional["Profile"] = Relationship(back_populates="user")
    courses: List["Course"] = Relationship(back_populates="instructor")
    enrollments: List["Enrollment"] = Relationship(back_populates="student")
    reviews: List["Review"] = Relationship(back_populates="student")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
