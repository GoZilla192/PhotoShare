from fastapi import Depends

from app.dependency.repository import get_photo_repository
from app.models.user import User
from app.repository.photos_repository import PhotoRepository
from app.service.photos_service import PhotoService
from app.service.security import SecurityService


def get_security_service() -> SecurityService:
    return SecurityService()


async def get_current_user(
    security_service: SecurityService = Depends(get_security_service),
) -> User:
    return await security_service.get_current_user()


def get_photo_service(
    photo_repo: PhotoRepository = Depends(get_photo_repository),
) -> PhotoService:
    return PhotoService(photo_repo)
