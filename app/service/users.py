from models.roles import UserRole
from models.user import User
from repository.users import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def count_users(self) -> int:
        return await self._user_repo.count_users()

    async def create_user(self, user: User) -> User:
        return await self._user_repo.create_user(user)

    async def register_user(
        self,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        users_count = await self.count_users()
        role = UserRole.admin if users_count == 0 else UserRole.user

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        return await self.create_user(user)
