from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_users(self) -> int:
        async with self._session.begin():
            res = await self._session.execute(select(func.count(User.id)))
            return res.scalar_one()

    async def get_first_user_id(self) -> int | None:
        async with self._session.begin():
            res = await self._session.execute(select(func.min(User.id)))
            return res.scalar_one()

    async def create_user(self, user: User) -> User:
        async with self._session.begin():
            self._session.add(user)
        await self._session.refresh(user)
        return user
