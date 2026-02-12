from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, update, delete, func, and_
from app.models import PhotoTag, Tag, Rating
from app.models.photo import Photo
from app.repository.base_repository import BaseRepository


class PhotoRepository(BaseRepository):
    async def add(self, photo: Photo) -> Photo:
        self.session.add(photo)
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

    async def search(
            self,
            *,
            q: str | None = None,
            tag: str | None = None,
            min_rating: float | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
            sort: str = "newest",
            limit: int = 50,
            offset: int = 0,
    ) -> list[Photo]:
        """
        Search photos by:
        - keyword in description (ILIKE)
        - tag name
        - min avg rating
        - created_at range
        """
        stmt = select(Photo)

        # join tags if needed
        if tag:
            stmt = (
                stmt.join(PhotoTag, PhotoTag.photo_id == Photo.id)
                .join(Tag, Tag.id == PhotoTag.tag_id)
            )

        # ratings join for avg
        if min_rating is not None or sort in {"top", "low"}:
            stmt = stmt.outerjoin(Rating, Rating.photo_id == Photo.id)

        conditions = []
        if q:
            like = f"%{q.strip()}%"
            conditions.append(Photo.description.ilike(like))
        if tag:
            norm_tag = tag.strip().lower()
            conditions.append(Tag.name == norm_tag)
        if date_from:
            conditions.append(Photo.created_at >= date_from)
        if date_to:
            conditions.append(Photo.created_at <= date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # group/having for avg rating filter
        if min_rating is not None or sort in {"top", "low"}:
            avg_rating = func.coalesce(func.avg(Rating.value), 0.0)
            stmt = stmt.group_by(Photo.id)
            if min_rating is not None:
                stmt = stmt.having(avg_rating >= float(min_rating))

            # sorting by avg
            if sort == "top":
                stmt = stmt.order_by(avg_rating.desc(), Photo.created_at.desc())
            elif sort == "low":
                stmt = stmt.order_by(avg_rating.asc(), Photo.created_at.desc())
            elif sort == "oldest":
                stmt = stmt.order_by(Photo.created_at.asc())
            else:
                stmt = stmt.order_by(Photo.created_at.desc())
        else:
            # no ratings join
            if sort == "oldest":
                stmt = stmt.order_by(Photo.created_at.asc())
            else:
                stmt = stmt.order_by(Photo.created_at.desc())

        # important: distinct to avoid duplicates when joining tags
        stmt = stmt.order_by(Photo.created_at.desc()).limit(limit).offset(offset)

        res = await self.session.execute(stmt)
        return list(res.scalars().unique().all())

    async def count_search(
            self,
            *,
            q: str | None = None,
            tag: str | None = None,
            min_rating: float | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
    ) -> int:
        """
        Total count for search() with same filters.
        """
        stmt = select(func.count(func.distinct(Photo.id))).select_from(Photo)

        if tag:
            stmt = (
                stmt.join(PhotoTag, PhotoTag.photo_id == Photo.id)
                .join(Tag, Tag.id == PhotoTag.tag_id)
            )

        if min_rating is not None:
            stmt = stmt.outerjoin(Rating, Rating.photo_id == Photo.id)

        conditions = []
        if q:
            like = f"%{q.strip()}%"
            conditions.append(Photo.description.ilike(like))
        if tag:
            norm_tag = tag.strip().lower()
            conditions.append(Tag.name == norm_tag)
        if date_from:
            conditions.append(Photo.created_at >= date_from)
        if date_to:
            conditions.append(Photo.created_at <= date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        if min_rating is not None:
            # для having/group_by робимо надійний підзапит по photo.id
            avg_rating = func.coalesce(func.avg(Rating.value), 0.0)

            base = (
                select(Photo.id)
                .select_from(Photo)
            )
            if tag:
                base = (
                    base.join(PhotoTag, PhotoTag.photo_id == Photo.id)
                    .join(Tag, Tag.id == PhotoTag.tag_id)
                )
            base = base.outerjoin(Rating, Rating.photo_id == Photo.id)

            if conditions:
                base = base.where(and_(*conditions))

            base = base.group_by(Photo.id).having(avg_rating >= float(min_rating))

            subq = base.subquery()
            res = await self.session.execute(select(func.count()).select_from(subq))
            return int(res.scalar_one())

        res = await self.session.execute(stmt)
        return int(res.scalar_one())