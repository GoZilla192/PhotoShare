from fastapi import Depends, HTTPException, status

from dependency.service import get_current_user
from models.roles import UserRole
from models.user import User


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
