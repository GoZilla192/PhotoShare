from __future__ import annotations

from sqlalchemy import select

from app.models.token_blacklist import TokenBlacklist
from app.repository.base_repository import BaseRepository


class TokenBlacklistRepository(BaseRepository):

    async def add(self, entry: TokenBlacklist) -> TokenBlacklist:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def is_revoked(self, jti: str) -> bool:
        res = await self.session.execute(select(TokenBlacklist.id).where(TokenBlacklist.jti == jti))
        return bool(res.scalar_one_or_none())