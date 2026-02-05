from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.comments import CommentRepository
from app.service.comments import CommentService


def get_comment_service(db: AsyncSession = Depends(get_async_session)) -> CommentService:
    repo = CommentRepository(db)
    return CommentService(repo)