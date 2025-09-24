from pydantic import BaseModel
from datetime import datetime


class RefreshTokenCreate(BaseModel):
    user_id: str
    hashed_token: str
    is_revoked: bool = False
    expires_at: datetime


class RefreshTokenRead(BaseModel):
    id: str
    user_id: str
    hashed_token: str
    is_revoked: bool
    expires_at: datetime
    created_at: datetime
