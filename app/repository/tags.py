from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.models.photo import Photo
from app.models.photo_tags import PhotoTag


# move this to .env later?
MAX_TAGS_PER_PHOTO = 5


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def attach_tags_to_photo(
        self,
        photo: Photo,
        tag_names: Iterable[str],
    ) -> None:
        """
        Attach tags to photo.
        Creates tags if they do not exist.
        photo must be attached to the same AsyncSession.
        """

        # normalization + uniqueness
        normalized_names = {
            name.strip().lower()
            for name in tag_names
            if name.strip()
        }

        # limitation
        if len(normalized_names) > MAX_TAGS_PER_PHOTO:
            raise ValueError(f"Maximum {MAX_TAGS_PER_PHOTO} tags allowed")

        if not normalized_names:
            return

        # get existing tags with one request
        stmt = select(Tag).where(Tag.name.in_(normalized_names))
        result = await self.db.execute(stmt)
        existing_tags: List[Tag] = result.scalars().all()

        existing_by_name = {tag.name: tag for tag in existing_tags}

        # create missing tags
        new_tags: List[Tag] = []

        for name in normalized_names:
            if name not in existing_by_name:
                tag = Tag(name=name)
                self.db.add(tag)
                new_tags.append(tag)

        # needed to get IDs for new tags
        if new_tags:
            await self.db.flush()

        all_tags = existing_tags + new_tags

        # link to photo without duplicates
        existing_tag_ids = {pt.tag_id for pt in photo.photo_tags}

        for tag in all_tags:
            if tag.id not in existing_tag_ids:
                photo.photo_tags.append(
                    PhotoTag(photo=photo, tag=tag)
                )

    async def get_all(self) -> list[Tag]:
        stmt = select(Tag).order_by(Tag.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, tag_id: int) -> Tag | None:
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()