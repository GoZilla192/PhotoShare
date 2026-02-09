from __future__ import annotations

from sqlalchemy import select, delete, func
from app.models.rating import Rating
from app.repository.base_repository import BaseRepository


class RatingRepository(BaseRepository):
    async def upsert(self, *, photo_id: int, user_id: int, rating: int) -> Rating:
        """
        Set/update rating by (photo_id, user_id). Uses ORM merge-like pattern.
        (Unique constraint in DB enforces single rating.)
        """
        res = await self.session.execute(
            select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user_id)
        )
        obj = res.scalar_one_or_none()
        if obj is None:
            obj = Rating(photo_id=photo_id, user_id=user_id, value=rating)
            self.session.add(obj)
        else:
            obj.value = rating

        await self.session.flush()
        return obj

    async def delete_for_user(self, *, photo_id: int, user_id: int) -> bool:
        res = await self.session.execute(
            delete(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user_id).returning(Rating.id)
        )
        return res.scalar_one_or_none() is not None

    async def get_aggregate(self, photo_id: int) -> tuple[float, int]:
        res = await self.session.execute(
            select(func.avg(Rating.value), func.count(Rating.id)).where(Rating.photo_id == photo_id)
        )
        avg, cnt = res.one()
        return float(avg or 0.0), int(cnt or 0)

    async def get_for_user(self, *, photo_id: int, user_id: int) -> int | None:
        res = await self.session.execute(
            select(Rating.value).where(Rating.photo_id == photo_id, Rating.user_id == user_id)
        )
        return res.scalar_one_or_none()
