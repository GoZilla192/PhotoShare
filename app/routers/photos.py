from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependency.service import get_current_user, get_photo_service
from app.exceptions import NotFoundError, PermissionDeniedError
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoRead, PhotoUpdateDescription
from app.service.photos import PhotoService


router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    payload: PhotoCreate,
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    photo = await photo_service.create_photo(
        user_id=current_user.id,
        photo_url=payload.photo_url,
        photo_unique_url=payload.photo_unique_url,
        description=payload.description,
    )
    return photo


@router.get("/by-unique/{photo_unique_url}", response_model=PhotoRead)
async def get_photo_by_unique_url(
    photo_unique_url: str,
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    try:
        return await photo_service.get_photo_by_unique_url(photo_unique_url)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{photo_id}/description", response_model=PhotoRead)
async def update_photo_description(
    photo_id: int,
    payload: PhotoUpdateDescription,
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    try:
        return await photo_service.update_description(
            photo_id=photo_id,
            description=payload.description,
            current_user=current_user,
        )
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


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
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

@router.get("/search", response_model=list[PhotoRead])
async def search_photo(
        keyword: str | None = Query(default=None),
        tag: str | None = Query(default=None),
        user_id: int | None = Query(default=None),
        date_from: datetime | None = Query(default=None),
        date_to: datetime | None = Query(default=None),
        rating_from: float | None = Query(default=None, ge=1.0, le=5.0),
        rating_to: float | None = Query(default=None, ge=1.0, le=5.0),
        date_order: str | None = Query(default=None, regex="^(asc|desc)$"),
        current_user: User = Depends(get_current_user),
        service: PhotoService = Depends(get_photo_service)
):
    return await service.search_photos(
       current_user=current_user,
        keyword=keyword,
        tag=tag,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        rating_from=rating_from,
        rating_to=rating_to,
        date_order=date_order
    )
