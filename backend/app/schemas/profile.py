from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProfileCreate(BaseModel):
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None


class ProfileRead(BaseModel):
    id: str
    user_id: str
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
