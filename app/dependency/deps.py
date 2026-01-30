from fastapi import Depends, HTTPException, status

from models.roles import UserRole
from models.user import User
from service.security import SecurityService


def get_security_service() -> SecurityService:
    return SecurityService()


async def get_current_user(
    security_service: SecurityService = Depends(get_security_service),
) -> User:
    return await security_service.get_current_user()


def require_role(required_role: UserRole):
    def dep(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dep


def require_roles(*allowed_roles: UserRole):
    def dep(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dep
