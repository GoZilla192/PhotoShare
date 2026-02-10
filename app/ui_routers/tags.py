from __future__ import annotations

from fastapi import APIRouter, Depends
from app.dependency.dependencies import tagging_service
from app.service.tagging_service import TaggingService

router = APIRouter(tags=["UI-Tags"])

@router.get("/tags/cloud")
async def ui_tag_cloud(
    limit: int = 50,
    offset: int = 0,
    svc: TaggingService = Depends(tagging_service),
):
    return await svc.get_tag_cloud(limit=limit, offset=offset)