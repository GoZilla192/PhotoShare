from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models import UserRole


class UserPublicSchema(BaseModel):
    """Мінімальна інформація про автора для UI."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    # avatar_url: str | None = None

class CommentCreateSchema(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentUpdateSchema(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    user_id: int
    text: str
    created_at: datetime
    updated_at: datetime | None = None

    # author підтягнеться, якщо в ORM comment.user завантажено
    user: UserPublicSchema | None = None
