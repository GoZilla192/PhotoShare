from __future__ import annotations

from sqlalchemy import select, delete
from app.models.transformed_image import TransformedImage
from app.repository.base_repository import BaseRepository


class TransformedImageRepository(BaseRepository):

    async def add(self, obj: TransformedImage) -> TransformedImage:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def create_for_photo(
        self,
        *,
        photo_id: int,
        image_url: str,
        transformation: str | None = None,
    ) -> TransformedImage:
        obj = TransformedImage(
            photo_id=photo_id,
            image_url=image_url,
            transformation=transformation,
        )
        return await self.add(obj)

    async def get_by_id(self, transformed_image_id: int) -> TransformedImage | None:
        return await self.session.get(TransformedImage, transformed_image_id)

    async def list_for_photo(
        self,
        photo_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TransformedImage]:
        stmt = (select(TransformedImage)
                .where(TransformedImage.photo_id == photo_id)
                .order_by(TransformedImage.created_at.desc())
                .limit(limit)
                .offset(offset))
        res = await self.session.execute(stmt)
        return list(res.scalars().unique().all())

    async def delete_by_id(self, transformed_image_id: int) -> bool:
        stmt = (delete(TransformedImage)
                .where(TransformedImage.id == transformed_image_id)
                .returning(TransformedImage.id))

        res = await self.session.execute(stmt)
        return bool(res.scalar_one_or_none())