from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import Photo


class PhotoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        owner_id: int,
        url: str,
        description: str | None = None,
    ) -> Photo:
        photo = Photo(
            owner_id=owner_id,
            url=url,
            description=description,
        )
        async with self._session.begin():
            self._session.add(photo)
        await self._session.refresh(photo)
        return photo

    async def get(self, photo_id: int) -> Photo | None:
        async with self._session.begin():
            return await self._session.get(Photo, photo_id)

    async def get_by_url(self, url: str) -> Photo | None:
        async with self._session.begin():
            res = await self._session.execute(
                select(Photo).where(Photo.url == url)
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

    async def list_by_user(self, owner_id: int) -> list[Photo]:
        async with self._session.begin():
            res = await self._session.execute(
                select(Photo).where(Photo.owner_id == owner_id)
            )
            return list(res.scalars().all())
