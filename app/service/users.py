from models.roles import UserRole
from models.user import User

async def count_users(session) -> int:
    raise NotImplementedError

async def create_user(session, user: User) -> User:
    raise NotImplementedError


async def register_user(session, username: str, email: str, password_hash: str) -> User:
    users_count = await count_users(session)
    role = UserRole.admin if users_count == 0 else UserRole.user

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
    )
    return await create_user(session, user)
