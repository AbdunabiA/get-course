from datetime import datetime
from typing import Optional
from sqlmodel import Field


class TimestampMixin:
    """Reusable mixin for created_at and updated_at fields."""
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
