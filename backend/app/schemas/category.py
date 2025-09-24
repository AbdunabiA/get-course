from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: str
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
