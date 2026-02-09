from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.users_repository import UserRepository
from app.legacy.auth import AuthService

def get_auth_service(db: AsyncSession = Depends(get_async_session)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)