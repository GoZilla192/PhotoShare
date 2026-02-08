from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import UserRole


class UserPublicProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    created_at: datetime | None = None
    photos_count: int = 0               # по ТЗ треба


class UserMeProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime | None = None
    photos_count: int = 0


class UserMeUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    # якщо дозволяєте змінювати email:
    email: EmailStr | None = None
    # можна додати сюди інші редаговані поля профілю (bio, avatar_url...), якщо є


class UserBanResponse(BaseModel):
    user_id: int
    is_active: bool
