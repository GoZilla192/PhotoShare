from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File, Form, Query

import uuid
from app.legacy.service import get_current_user, get_photo_service
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.user import User
from app.schemas.photo_schema import PhotoCreate, PhotoRead, PhotoUpdateDescription, PhotoListResponse
from app.service.photos_service import PhotoService


router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    photo_unique_url = uuid.uuid4().hex
    try:
        return await photo_service.create_photo(
            user_id=current_user.id,
            file=file,
            photo_unique_url=photo_unique_url,
            description=description,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{photo_id}", response_model=PhotoRead)
async def get_photo_by_id(
    photo_id: int,
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoRead:
    try:
        return await photo_service.get_photo(photo_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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

# --- Lists for UI -------------------------------------------------------------


@router.get("/me/list", response_model=PhotoListResponse)
async def list_my_photos(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoListResponse:
    items = await photo_service.list_by_user(current_user.id, limit=limit, offset=offset)
    total = await photo_service.count_by_user(current_user.id)
    return PhotoListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/user/{user_id}/list", response_model=PhotoListResponse)
async def list_user_photos(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    photo_service: PhotoService = Depends(get_photo_service),
) -> PhotoListResponse:
    # Публічний список фото користувача для профілю (UI).
    items = await photo_service.list_by_user(user_id, limit=limit, offset=offset)
    total = await photo_service.count_by_user(user_id)
    return PhotoListResponse(items=items, total=total, limit=limit, offset=offset)


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
