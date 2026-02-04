from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.photos import PhotoRepository
from app.repository.users import UserRepository


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(session)


def get_photo_repository(
    session: AsyncSession = Depends(get_async_session),
) -> PhotoRepository:
    return PhotoRepository(session)
