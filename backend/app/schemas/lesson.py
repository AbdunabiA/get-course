from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LessonCreate(BaseModel):
    title: str
    content: str
    video_url: Optional[str] = None
    order: int


class LessonRead(BaseModel):
    id: str
    course_id: str
    title: str
    content: str
    video_url: Optional[str] = None
    order: int
    created_at: datetime
    updated_at: datetime


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    order: Optional[int] = None
