from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from .base import TimestampMixin


class Enrollment(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    student_id: str = Field(foreign_key="user.id")
    course_id: str = Field(foreign_key="course.id")

    student: Optional["User"] = Relationship(back_populates="enrollments")
    course: Optional["Course"] = Relationship(back_populates="enrollments")

    __table_args__ = ({"sqlite_autoincrement": True},)
