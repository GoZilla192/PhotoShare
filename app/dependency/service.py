from fastapi import Depends

from app.models.user import User
from app.service.security import SecurityService


def get_security_service() -> SecurityService:
    return SecurityService()


async def get_current_user(
    security_service: SecurityService = Depends(get_security_service),
) -> User:
    return await security_service.get_current_user()
