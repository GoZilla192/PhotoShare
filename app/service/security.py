from datetime import datetime, timedelta
from typing import List

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.users import UserRepository
from app.models.roles import UserRole
from app.models.user import User
from app.settings import Settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    def __init__(self) -> None:
        self._settings = Settings()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self._settings.SECRET_KEY, algorithm=self._settings.ALGORITHM)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        try:
            payload = jwt.decode(
                token,
                self._settings.SECRET_KEY,
                algorithms=[self._settings.ALGORITHM],
            )
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User = Depends(lambda: security_service.get_current_user())) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        return current_user

security_service = SecurityService()

def require_roles(allowed_roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(security_service.get_current_active_user),) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return role_checker
