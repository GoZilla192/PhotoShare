from fastapi import APIRouter, Depends, status

from app.dependency.comments import get_comment_service
from app.schemas.comments import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.service.comments import CommentService
from app.service.security import SecurityService
from app.models.user import User

router = APIRouter(prefix="/comments", tags=["comments"])
security = SecurityService()

@router.post("/photo/{photo_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(photo_id: int, data: CommentCreateRequest, service: CommentService = Depends(get_comment_service), current_user: User = Depends(security.get_current_user)):
    return await service.create_comment(
        photo_id=photo_id,
        user_id=current_user.id,
        text=data.text
    )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_own_comment(comment_id: int, data: CommentUpdateRequest, service: CommentService = Depends(get_comment_service), current_user: User = Depends(security.get_current_user)):
    return await service.update_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        text=data.text
    )

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, service: CommentService = Depends(get_comment_service), current_user: User = Depends(security.get_current_user)):
    await service.delete_comment(
        comment_id=comment_id,
        role=current_user.role
    )

@router.get("/photo/{photo_id}", response_model=list[CommentResponse])
async def get_comments_for_photo(photo_id: int, service: CommentService = Depends(get_comment_service)):
    return await service.get_comments_for_photo(photo_id)