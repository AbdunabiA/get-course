from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from .base import TimestampMixin


class Course(SQLModel, TimestampMixin, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(index=True)
    description: str
    image: Optional[str] = None
    price: Optional[float] = Field(default=0.0, ge=0)
    is_published: bool = Field(default=False)

    instructor_id: str = Field(foreign_key="user.id")
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")

    instructor: Optional["User"] = Relationship(back_populates="courses")
    category: Optional["Category"] = Relationship(back_populates="courses")
    lessons: List["Lesson"] = Relationship(
        back_populates="course", cascade_delete=True)
    enrollments: List["Enrollment"] = Relationship(back_populates="course")
    reviews: List["Review"] = Relationship(back_populates="course")
