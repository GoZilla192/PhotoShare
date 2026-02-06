from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.tags import TagRepository
from app.schemas.tag import TagOut

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.get("/", response_model=List[TagOut])
async def get_tags(
    db: AsyncSession = Depends(get_async_session),
):
    repo = TagRepository(db)
    return await repo.get_all()


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    repo = TagRepository(db)
    tag = await repo.get_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag