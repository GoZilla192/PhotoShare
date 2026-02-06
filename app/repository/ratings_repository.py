from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import Rating


class RatingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rating: Rating) -> Rating:
        self.session.add(rating)
        await self.session.commit()
        await self.session.refresh(rating)
        return rating

    async def get_by_id(self, rating_id: int) -> Rating | None:
        stmt = select(Rating).where(Rating.id == rating_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_photo_and_user(
        self,
        photo_id: int,
        user_id: int
    ) -> Rating | None:
        stmt = select(Rating).where(
            Rating.photo_id == photo_id,
            Rating.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_photo(self, photo_id: int) -> list[Rating]:
        stmt = select(Rating).where(Rating.photo_id == photo_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, rating: Rating) -> None:
        await self.session.delete(rating)
        await self.session.commit()

    async def get_rating_stats(self, photo_id: int) -> dict:
        stmt = select(
            func.avg(Rating.value),
            func.count(Rating.id)
        ).where(Rating.photo_id == photo_id)

        result = await self.session.execute(stmt)
        avg, count = result.one()

        return {
            "avg": float(avg) if avg is not None else None,
            "count": count
        }