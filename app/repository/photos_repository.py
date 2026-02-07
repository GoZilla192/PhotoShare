from __future__ import annotations

from sqlalchemy import select, update, delete, func
from app.models.photo import Photo
from app.repository.base_repository import BaseRepository


class PhotoRepository(BaseRepository):
    async def add(self, photo: Photo) -> Photo:
        self.session.add(photo)
        await self.session.flush()
        return photo

    async def get_by_id(self, photo_id: int) -> Photo | None:
        return await self.session.get(Photo, photo_id)

    async def get_by_unique_url(self, unique_url: str) -> Photo | None:
        res = await self.session.execute(
            select(Photo).where(Photo.photo_unique_url == unique_url)
        )
        return res.scalar_one_or_none()

    async def list_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> list[Photo]:
        stmt = (select(Photo)
                .where(Photo.user_id == user_id)
                .order_by(Photo.created_at.desc())
                .limit(limit).offset(offset))

        res = await self.session.execute(stmt)
        return list(res.scalars().unique().all())

    async def count_by_user(self, user_id: int) -> int:
        res = await self.session.execute(
            select(func.count(Photo.id)).where(Photo.user_id == user_id)
        )
        return int(res.scalar_one())

    async def update_description(self, photo_id: int, description: str) -> Photo | None:
        stmt = (update(Photo)
                .where(Photo.id == photo_id)
                .values(description=description)
                .returning(Photo))

        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_by_id(self, photo_id: int) -> bool:
        res = await self.session.execute(
            delete(Photo).where(Photo.id == photo_id).returning(Photo.id)
        )
        return res.scalar_one_or_none() is not None