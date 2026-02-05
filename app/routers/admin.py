from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependency.roles import role_required
from app.dependency.service import get_current_user, get_photo_service
from app.exceptions import NotFoundError, PermissionDeniedError
from app.models.roles import UserRole
from app.models.user import User
from app.service.photos import PhotoService


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(role_required([UserRole.admin, UserRole.moderator]))],
)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
) -> Response:
    try:
        await photo_service.delete_photo(photo_id, current_user)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
