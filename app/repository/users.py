from sqlalchemy import select, func, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreateSchema, UserReadSchema


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

    async def create_user(self, user: UserCreateSchema) -> User:
        query = insert(User).values(
            **user.model_dump()
        ).returning(User.id)
        
        async with self._session as session:
            user_id = (await session.execute(query)).scalar()
            await session.commit()
            return await self.get_user_by_id(user_id)
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        async with self._session as session:
            user = (await session.execute(query)).scalar_one_or_none()
        
        return user

    async def get_by_email(self, email: str) -> User | None:
        async with self._session.begin():
            res = await self._session.execute(select(User).where(User.email == email))
            return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        async with self._session.begin():
            res = await self._session.execute(select(User).where(User.id == user_id))
            return res.scalar_one_or_none()
    
    async def update_user_info(self, user_id: int, new_info_about_user: UserCreateSchema) -> User:
        query = update(User).where(User.id == user_id).values(
            **new_info_about_user.model_dump()
        )
        
        async with self._session as session:
            await session.execute(query)
            await session.commit()
            
        return await self.get_user_by_id(user_id=user_id)
