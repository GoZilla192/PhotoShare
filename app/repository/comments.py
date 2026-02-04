from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment

class CommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, comment: Comment) -> Comment:
        self._session.add(comment)
        await self._session.commit()
        await self._session.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_photo_id(self, photo_id: int) -> list[Comment]:
        stmt = (select(Comment).where(Comment.photo_id == photo_id).order_by(Comment.created_at))
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def update_text(self, comment: Comment, text: str) -> Comment:
        comment.text = text
        await self._session.commit()
        await self._session.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self._session.delete(comment)
        await self._session.commit()
