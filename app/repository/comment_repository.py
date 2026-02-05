from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User
from app.models.comment import Comment
from app.repository.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    async def get_by_id(self, comment_id: int) -> Comment | None:
        res = await self.session.execute(select(Comment).where(Comment.id == comment_id))
        return res.scalar_one_or_none()

    async def list_for_photo(self, photo_id: int, limit: int = 50, offset: int = 0) -> list[Comment]:
        res = await self.session.execute(
            select(Comment)
            .join(Comment.user)  # JOIN users
            .where(
                Comment.photo_id == photo_id,
                User.is_active.is_(True),  # фільтр бану
            )
            .options(selectinload(Comment.user))  # підвантажили автора
            .order_by(Comment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars().unique().all())

    async def list_for_user(self, user_id: int, limit: int = 50, offset: int = 0) -> list[Comment]:
        stmt = (select(Comment)
                .join(Comment.user)
                .where(  # JOIN users
                Comment.user_id == user_id,
                User.is_active.is_(True))   # фільтр бану
                .options(selectinload(Comment.user))    # підвантажили автора
                .order_by(Comment.created_at.desc())
                .limit(limit).offset(offset))

        res = await self.session.execute(stmt)
        return list(res.scalars().unique().all())

    async def add(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()      # comment.id стає доступним
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.session.delete(comment)
