from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.comments_schema import CommentCreateSchema, CommentUpdateSchema, CommentReadSchema
from app.models import UserRole

# TODO: замінити на реальні DI функції вашого проекту:
def get_comment_service():
    raise NotImplementedError("Wire CommentService dependency")

async def get_actor_user_id():
    raise NotImplementedError("Wire auth dependency to extract current user id")

async def get_actor_role():
    raise NotImplementedError("Wire auth dependency to extract current user role")


router = APIRouter(tags=["Comments"])


@router.get("/photos/{photo_id}/comments", response_model=list[CommentReadSchema])
async def list_comments_for_photo(
    photo_id: int,
    limit: int = 50,
    offset: int = 0,
    service=Depends(get_comment_service),
):
    try:
        comments = await service.list_for_photo(photo_id=photo_id, limit=limit, offset=offset)
        return [CommentReadSchema.model_validate(c, from_attributes=True) for c in comments]
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/photos/{photo_id}/comments", response_model=CommentReadSchema)
async def create_comment(
    photo_id: int,
    body: CommentCreateSchema,
    service=Depends(get_comment_service),
    actor_user_id: int = Depends(get_actor_user_id),
):
    try:
        c = await service.create(photo_id=photo_id, user_id=actor_user_id, text=body.text)
        return CommentReadSchema.model_validate(c, from_attributes=True)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/comments/{comment_id}", response_model=CommentReadSchema)
async def update_comment_text(
    comment_id: int,
    body: CommentUpdateSchema,
    service=Depends(get_comment_service),
    actor_user_id: int = Depends(get_actor_user_id),
):
    try:
        c = await service.update_text(comment_id=comment_id, actor_user_id=actor_user_id, new_text=body.text)
        return CommentReadSchema.model_validate(c, from_attributes=True)
    except ValueError:
        raise HTTPException(status_code=404, detail="Comment not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service=Depends(get_comment_service),
    actor_role: UserRole = Depends(get_actor_role),
):
    try:
        await service.delete(comment_id=comment_id, actor_role=actor_role)
        return
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Not implemented")
