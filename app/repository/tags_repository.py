from __future__ import annotations

from sqlalchemy import select, delete, func
from app.models.tag import Tag
from app.models.photo_tags import PhotoTag
from app.repository.base_repository import BaseRepository


def _normalize_tag(name: str) -> str:
    # однакова логіка для всього проекту
    return name.strip().lower()


class TagRepository(BaseRepository):
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Tag]:
        res = await self.session.execute(
            select(Tag).order_by(Tag.name.asc()).limit(limit).offset(offset)
        )
        return list(res.scalars().unique().all())

    async def get_by_id(self, tag_id: int) -> Tag | None:
        return await self.session.get(Tag, tag_id)

    async def get_by_names(self, names: list[str]) -> list[Tag]:
        norm = [_normalize_tag(n) for n in names if n and n.strip()]
        norm = list(dict.fromkeys(norm))  # unique preserve order
        if not norm:
            return []

        res = await self.session.execute(select(Tag).where(Tag.name.in_(norm)))
        return list(res.scalars().unique().all())

    async def get_or_create_by_names(self, names: list[str]) -> list[Tag]:
        """
        Returns Tag objects for provided names. Creates missing tags.
        Does NOT create links to photos.
        """
        norm = [_normalize_tag(n) for n in names if n and n.strip()]
        norm = list(dict.fromkeys(norm))
        if not norm:
            return []

        existing = await self.get_by_names(norm)
        existing_map = {t.name: t for t in existing}

        missing = [n for n in norm if n not in existing_map]
        for name in missing:
            tag = Tag(name=name)
            self.session.add(tag)

        if missing:
            await self.session.flush()  # so new tags get ids
            # re-read all to have consistent objects
            res = await self.session.execute(select(Tag).where(Tag.name.in_(norm)))
            return list(res.scalars().all())

        return existing

    async def set_tags_for_photo(self, photo_id: int, tag_names: list[str], *, max_tags: int = 5) -> list[str]:
        """
        Overwrites tags for the given photo (set semantics).
        Returns normalized tag names actually attached.
        """
        norm = [_normalize_tag(n) for n in tag_names if n and n.strip()]
        norm = list(dict.fromkeys(norm))[:max_tags]

        # clear old links
        await self.session.execute(delete(PhotoTag).where(PhotoTag.photo_id == photo_id))

        if not norm:
            return []

        tags = await self.get_or_create_by_names(norm)

        # attach
        for tag in tags:
            self.session.add(PhotoTag(photo_id=photo_id, tag_id=tag.id))

        await self.session.flush()
        return [t.name for t in tags]

    async def list_tag_names_for_photo(self, photo_id: int) -> list[str]:
        res = await self.session.execute(
            select(Tag.name)
            .join(PhotoTag, PhotoTag.tag_id == Tag.id)
            .where(PhotoTag.photo_id == photo_id)
            .order_by(Tag.name.asc())
        )
        return [row[0] for row in res.all()]

    async def list_cloud(self, *, limit: int = 50, offset: int = 0) -> list[tuple[str, int]]:
        """
        Returns list of (tag_name, photo_count), sorted by photo_count desc then name asc.
        Includes only tags that are attached to at least one photo.
        """
        stmt = (select(Tag.name,func.count(PhotoTag.photo_id)
                     .label("cnt"),)
                .select_from(Tag)
                .join(PhotoTag, PhotoTag.tag_id == Tag.id)
                .group_by(Tag.id, Tag.name)
                .order_by(func.count(PhotoTag.photo_id).desc(), Tag.name.asc())
                .limit(limit)
                .offset(offset))
        res = await self.session.execute(stmt)
        return [(row[0], int(row[1])) for row in res.all()]