from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.auth.dependencies import get_current_user
from app.dependency.dependencies import comment_service as get_comment_service
from app.schemas.comments_schema import CommentCreateSchema, CommentUpdateSchema, CommentReadSchema
from app.service.comment_service import CommentService


router = APIRouter(tags=["Comments"])


@router.get("/photos/{photo_id}/comments", response_model=list[CommentReadSchema])
async def list_comments_for_photo(
    photo_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: CommentService = Depends(get_comment_service),
):
    comments = await svc.list_for_photo(photo_id=photo_id, limit=limit, offset=offset)
    return [CommentReadSchema.model_validate(c, from_attributes=True) for c in comments]


@router.post("/photos/{photo_id}/comments", response_model=CommentReadSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    photo_id: int,
    body: CommentCreateSchema,
    current_user=Depends(get_current_user),
    svc: CommentService = Depends(get_comment_service),
):
    c = await svc.create(photo_id=photo_id, user_id=current_user.id, text=body.text)
    return CommentReadSchema.model_validate(c, from_attributes=True)


@router.patch("/comments/{comment_id}", response_model=CommentReadSchema)
async def update_comment_text(
    comment_id: int,
    body: CommentUpdateSchema,
    current_user=Depends(get_current_user),
    svc: CommentService = Depends(get_comment_service),
):
    try:
        c = await svc.update_text(comment_id=comment_id, actor_user_id=current_user.id, new_text=body.text)
        return CommentReadSchema.model_validate(c, from_attributes=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_user),
    svc: CommentService = Depends(get_comment_service),
):
    try:
        await svc.delete(comment_id=comment_id, actor_role=current_user.role)
        return
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
