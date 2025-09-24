from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserRead
from .category import CategoryRead


class CourseCreate(BaseModel):
    title: str
    description: str
    image: Optional[str] = None
    price: Optional[float] = 0.0
    is_published: bool = False
    category_id: Optional[str] = None


class CourseRead(BaseModel):
    id: str
    title: str
    description: str
    image: Optional[str] = None
    price: Optional[float]
    is_published: bool
    instructor_id: str
    category_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    instructor: Optional[UserRead] = None
    category: Optional[CategoryRead] = None
    lessons_count: Optional[int] = None
    enrollments_count: Optional[int] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    price: Optional[float] = None
    is_published: Optional[bool] = None
    category_id: Optional[str] = None
