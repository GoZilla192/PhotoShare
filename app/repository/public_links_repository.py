from __future__ import annotations

from sqlalchemy import select
from app.models.public_link import PublicLink
from app.repository.base_repository import BaseRepository


class PublicLinkRepository(BaseRepository):
    async def add(self, link: PublicLink) -> PublicLink:
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_by_uuid(self, uuid: str) -> PublicLink | None:
        res = await self.session.execute(
            select(PublicLink).where(PublicLink.uuid == uuid)
        )
        return res.scalar_one_or_none()