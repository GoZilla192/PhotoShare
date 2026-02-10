from __future__ import annotations

from sqlalchemy import select, update
from app.models import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_first_user_id(self) -> int | None:
        res = await self.session.execute(
            select(User.id).order_by(User.id.asc()).limit(1)
        )
        return res.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        res = await self.session.execute(
            select(User).where(User.username == username)
        )
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(
            select(User).where(User.email == email)
        )
        return res.scalar_one_or_none()

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_profile_fields(
            self,
            user_id: int,
            *,
            username: str | None = None,
            email: str | None = None,
    ) -> User | None:
        values: dict = {}
        if username is not None:
            values["username"] = username
        if email is not None:
            values["email"] = email

        if not values:
            return await self.get_by_id(user_id)

        stmt = (update(User)
                .where(User.id == user_id)
                .values(**values)
                .returning(User))

        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()
        return row

    async def set_is_active(self, user_id: int, is_active: bool) -> bool:
        stmt = (update(User)
                .where(User.id == user_id)
                .values(is_active=is_active)
                .returning(User.id))

        res = await self.session.execute(stmt)
        return bool(res.scalar_one_or_none())

    async def exists_any(self) -> bool:
        res = await self.session.execute(select(User.id).limit(1))
        return bool(res.scalar_one_or_none())

    async def list_users(self, *, limit: int = 200, offset: int = 0) -> list[User]:
        res = await self.session.execute(
            select(User)
            .order_by(User.id.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars().unique().all())



