from models.roles import UserRole
from models.user import User
from repository.users import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

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
