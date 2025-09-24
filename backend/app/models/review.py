from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from .base import TimestampMixin


class Review(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    rating: int = Field(ge=1, le=5)
    comment: str

    student_id: str = Field(foreign_key="user.id")
    course_id: str = Field(foreign_key="course.id")

    student: Optional["User"] = Relationship(back_populates="reviews")
    course: Optional["Course"] = Relationship(back_populates="reviews")

    __table_args__ = ({"sqlite_autoincrement": True},)
