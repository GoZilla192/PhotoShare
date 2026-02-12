from __future__ import annotations

from sqlalchemy import select, func
from app.models.rating import Rating


class RatingRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_photo_and_user(self, photo_id: int, user_id: int):
        stmt = select(Rating).where(
            Rating.photo_id == photo_id,
            Rating.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, rating_id: int):
        stmt = select(Rating).where(Rating.id == rating_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, rating: Rating):
        self.session.add(rating)
        await self.session.flush()
        return rating

    async def delete(self, rating: Rating):
        await self.session.delete(rating)
        await self.session.flush()

    async def get_rating_stats(self, photo_id: int):
        stmt = select(
            func.count(Rating.id),
            func.avg(Rating.value),
        ).where(Rating.photo_id == photo_id)

        result = await self.session.execute(stmt)
        count, avg = result.one()

        return {
            "photo_id": photo_id,
            "avg_rating": float(avg) if avg is not None else None,
            "ratings_count": count or 0,
        }