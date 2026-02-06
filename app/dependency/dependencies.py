# app/dependencies/core.py
from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from rich import status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import UserRole
from app.repository.comment_repository import CommentRepository
from app.service.comment_service import CommentService
from app.settings import Settings  # або де у вас Settings


def make_engine(settings: Settings):
    # Тут важливо, щоб URL був типу: postgresql+asyncpg://...
    return create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)


def make_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    engine = make_engine(settings)
    SessionLocal = make_sessionmaker(engine)

    async with SessionLocal() as session:
        yield session

# TODO: підключити реальний PhotoRepository коли він стане канонічним
class _PhotoRepoStub:
    async def get_by_id(self, photo_id: int):
        return None

def get_comment_repo(session: AsyncSession = Depends(get_session)) -> CommentRepository:
    return CommentRepository(session)

def get_comment_service(
    session: AsyncSession = Depends(get_session),
    comment_repo: CommentRepository = Depends(get_comment_repo),
):
    return CommentService(session=session, comment_repo=comment_repo, photo_repo=_PhotoRepoStub())

async def get_current_user_id() -> int:
    # TODO: replace with real JWT parsing
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth not wired")

async def get_current_user_role() -> UserRole:
    # TODO: replace with real JWT parsing
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth not wired")