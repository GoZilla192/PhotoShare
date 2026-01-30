from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.roles import UserRole
from repository.users import count_users, create_user

async def register_user(
    session: AsyncSession,
    username: str,
    email: str,
    password_hash: str,
) -> User:
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
