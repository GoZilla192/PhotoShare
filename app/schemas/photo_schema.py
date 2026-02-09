from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PhotoUploadRequest(BaseModel):
    """
    Payload for upload endpoint (metadata only).
    Сам файл йде як multipart UploadFile, не через Pydantic.
    """
    description: str | None = Field(default=None, max_length=500)


class PhotoUpdateDescriptionRequest(BaseModel):
    description: str | None = Field(default=None, max_length=500)


class PhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    # Публічний унікальний ідентифікатор/slug для шарингу
    photo_unique_url: str

    # Готовий URL (Cloudinary)
    photo_url: str

    description: str | None = None
    created_at: datetime
    updated_at: datetime


class PhotoListResponse(BaseModel):
    """
    Опційно, можно віддавати total для пагінації.
    Якщо не треба — можна не використовувати.
    """
    items: list[PhotoRead]
    total: int | None = None
    limit: int | None = None
    offset: int| None = None
