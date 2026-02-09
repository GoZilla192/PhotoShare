from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependency.dependencies import tags_repo as get_tags_repo
from app.repository.tags_repository import TagRepository
from app.schemas.tag_schema import TagOut

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagOut])
async def list_tags(
    repo: TagRepository = Depends(get_tags_repo),
) -> list[TagOut]:
    tags = await repo.list_all()
    return [TagOut.model_validate(t, from_attributes=True) for t in tags]


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag_id(
    tag_id: int,
    repo: TagRepository = Depends(get_tags_repo),
) -> TagOut:
    tag = await repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return TagOut.model_validate(tag, from_attributes=True)