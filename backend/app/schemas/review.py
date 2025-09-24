from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserRead


class ReviewCreate(BaseModel):
    course_id: str
    rating: int
    comment: str


class ReviewRead(BaseModel):
    id: str
    student_id: str
    course_id: str
    rating: int
    comment: str
    created_at: datetime

    student: Optional[UserRead] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
