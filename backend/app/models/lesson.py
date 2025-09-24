from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from .base import TimestampMixin


class Lesson(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    content: str
    video_url: Optional[str] = None
    order: int = Field(ge=1)
    course_id: str = Field(foreign_key="course.id")

    course: Optional["Course"] = Relationship(back_populates="lessons")
