from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserRead(BaseModel):
    id: str
    email: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
