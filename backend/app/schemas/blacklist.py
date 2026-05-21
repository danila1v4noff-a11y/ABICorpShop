from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BlacklistCreate(BaseModel):
    user_id: int
    reason: str

class BlacklistResponse(BaseModel):
    blacklist_id: int
    user_id: int
    user_name: str
    reason: str
    created_at: datetime
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True