from fastapi import APIRouter, Depends, HTTPException, Response, status

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
        owner_id=current_user.id,
        url=payload.url,
        description=payload.description,
    )
    return photo


@router.get("/by-url/{url}", response_model=PhotoRead)
async def get_photo_by_url(
    url: str,
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    try:
        return await photo_service.get_photo_by_url(url)
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
