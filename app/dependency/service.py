from fastapi import Depends

from models.user import User
from service.security import SecurityService


def get_security_service() -> SecurityService:
    return SecurityService()


async def get_current_user(
    security_service: SecurityService = Depends(get_security_service),
) -> User:
    return await security_service.get_current_user()
