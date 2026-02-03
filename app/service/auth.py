from fastapi import HTTPException, status
from app.models.roles import UserRole
from app.models.user import User
from app.repository.users import UserRepository
from app.service.security import SecurityService
from app.exceptions import InactiveUserError, InvalidCredentialsError


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo
        self._security = SecurityService()

    async def register_user(
        self,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        first_user_id = await self._user_repo.get_first_user_id()

        role = UserRole.admin if first_user_id is None else UserRole.user

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )

        return await self._user_repo.create_user(user)

    async def login_user(self, email: str, password: str) -> User:
        user = await self._user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        if not self._security.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        return user
