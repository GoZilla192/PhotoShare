from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import Photo
from app.models.tag import Tag
from app.models.photo_tags import PhotoTag


class PhotoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: int,
        photo_url: str,
        photo_unique_url: str,
        description: str | None = None,
    ) -> Photo:
        photo = Photo(
            user_id=user_id,
            photo_url=photo_url,
            photo_unique_url=photo_unique_url,
            description=description,
        )
        async with self._session.begin():
            self._session.add(photo)
        await self._session.refresh(photo)
        return photo

    async def get(self, photo_id: int) -> Photo | None:
        async with self._session.begin():
            return await self._session.get(Photo, photo_id)

    async def get_by_unique_url(self, photo_unique_url: str) -> Photo | None:
        async with self._session.begin():
            res = await self._session.execute(
                select(Photo).where(Photo.photo_unique_url == photo_unique_url)
            )
            return res.scalar_one_or_none()

    async def update_description(
        self,
        photo: Photo,
        description: str | None,
    ) -> Photo:
        async with self._session.begin():
            photo.description = description
        await self._session.refresh(photo)
        return photo

    async def delete(self, photo: Photo) -> None:
        async with self._session.begin():
            await self._session.delete(photo)

    async def list_by_user(self, user_id: int) -> list[Photo]:
        async with self._session.begin():
            res = await self._session.execute(
                select(Photo).where(Photo.user_id == user_id)
            )
            return list(res.scalars().all())
        
    async def get_photo_url_by_id(self, photo_id: int) -> str | None:
        async with self._session.begin():
            res = await self._session.execute(
                select(Photo.photo_url).where(Photo.id == photo_id)
            )
            return res.scalar_one_or_none()

    async def search(self, keyword: str | None = None, tag: str | None = None, user_id: int | None = None, date_order: str | None = None) -> list[Photo]:
        stmt = select(Photo)
        if keyword:
            stmt = stmt.where(Photo.description.ilike(f"%{keyword}%"))

        if tag:
            stmt = (stmt.join(Photo.photo_tags).join(PhotoTag.tag).where(Tag.name == tag))

        if user_id is not None:
            stmt = stmt.where(Photo.user_id == user_id)

        if date_order == "asc":
            stmt = stmt.order_by(Photo.created_at.asc())
        elif date_order == "desc":
            stmt = stmt.order_by(Photo.created_at.desc())

        res = await self._session.execute(stmt)
        return list(res.scalars().unique().all())