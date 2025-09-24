from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid


class Category(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(unique=True, index=True)

    courses: List["Course"] = Relationship(back_populates="category")
