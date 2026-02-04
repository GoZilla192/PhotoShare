from datetime import datetime

from pydantic import BaseModel


class PhotoCreate(BaseModel):
    photo_url: str
    photo_unique_url: str
    description: str | None = None


class PhotoUpdateDescription(BaseModel):
    description: str | None = None


class PhotoRead(BaseModel):
    id: int
    user_id: int
    photo_unique_url: str
    photo_url: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
