from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .course import CourseRead


class EnrollmentCreate(BaseModel):
    course_id: str


class EnrollmentRead(BaseModel):
    id: str
    student_id: str
    course_id: str
    progress: float
    created_at: datetime
    updated_at: datetime

    course: Optional[CourseRead] = None


class EnrollmentUpdate(BaseModel):
    progress: Optional[float] = None
