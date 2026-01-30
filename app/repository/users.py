from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

async def count_users(session: AsyncSession) -> int:
    res = await session.execute(select(func.count(User.id)))
    return res.scalar_one()

async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user