from datetime import datetime

from pydantic import BaseModel


class PhotoCreate(BaseModel):
    url: str
    description: str | None = None


class PhotoUpdateDescription(BaseModel):
    description: str | None = None


class PhotoRead(BaseModel):
    id: int
    owner_id: int
    url: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True
