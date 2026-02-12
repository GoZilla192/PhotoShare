from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status, File, Form, Query

from app.auth.dependencies import get_current_user
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.user import User
from app.schemas.photo_schema import PhotoRead, PhotoListResponse, PhotoUpdateDescriptionRequest
from app.service.photos_service import PhotoService
from app.dependency.dependencies import photo_service
from app.mappers.photo_mapper import map_photo_to_read


router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: bytes = File(...),
    description: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    photos: PhotoService = Depends(photo_service),
) -> PhotoRead:
    """
    Upload a new photo (multipart/form-data).
    description: optional
    tags: optional comma-separated string (ignored for now; service doesn't support tags yet)
    """
    # Сервіс очікує, що ми згенеруємо унікальний slug/URL і передамо його в create_photo()
    photo_unique_url = secrets.token_urlsafe(16)

    try:
        created = await photos.create_photo(
            user_id=current_user.id,
            file=file,
            photo_unique_url=photo_unique_url,
            description=description,
            tags=tags,
        )
        return PhotoRead.model_validate(created)
    except Exception as exc:
        # Якщо треба, можна деталізувати (наприклад, 400 для невалідного файлу).
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{photo_id}", response_model=PhotoRead)
async def get_photo_by_id(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    photos: PhotoService = Depends(photo_service),
) -> PhotoRead:
    """
    Private access to a photo by DB id:
    owner or admin only.
    """
    try:
        photo = await photos.get_photo(photo_id)
        photos.ensure_owner_or_admin(current_user, photo.user_id)
        return map_photo_to_read(photo, photos.cloudinary)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/by-unique/{photo_unique_url}", response_model=PhotoRead)
async def get_photo_by_unique_url(
    photo_unique_url: str,
    photos: PhotoService = Depends(photo_service),
) -> PhotoRead:
    """
    Public access by unique URL (share link).
    """
    # якщо потрібно auth-only — додамо Depends(get_current_user).
    try:
        photo = await photos.get_photo_by_unique_url(photo_unique_url)
        return map_photo_to_read(photo, photos.cloudinary)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Lists for UI
@router.get("", response_model=PhotoListResponse)
async def list_my_photos(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    photos: PhotoService = Depends(photo_service),
) -> PhotoListResponse:
    items = await photos.list_by_user(current_user.id, limit=limit, offset=offset)
    items = [map_photo_to_read(photo, photos.cloudinary) for photo in items]
    total = await photos.count_by_user(current_user.id)
    return PhotoListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/user/{user_id}/list", response_model=PhotoListResponse)
async def list_user_photos(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    photos: PhotoService = Depends(photo_service),
) -> PhotoListResponse:
    # Публічний список фото користувача для профілю (UI).
    items = await photos.list_by_user(user_id, limit=limit, offset=offset)
    items = [map_photo_to_read(photo, photos.cloudinary) for photo in items]
    total = await photos.count_by_user(user_id)
    return PhotoListResponse(items=items, total=total, limit=limit, offset=offset)


@router.put("/{photo_id}/description", response_model=PhotoRead)
async def update_photo_description(
    photo_id: int,
    payload: PhotoUpdateDescriptionRequest,
    current_user: User = Depends(get_current_user),
    photos: PhotoService = Depends(photo_service),
) -> PhotoRead:
    try:
        updated = await photos.update_description(photo_id, payload.description, current_user)

        return map_photo_to_read(updated, photos.cloudinary)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    photos: PhotoService = Depends(photo_service),
) -> Response:
    try:
        await photos.delete_photo(photo_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/search", response_model=PhotoListResponse)
async def search_photos(
    q: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    min_rating: float | None = Query(default=None, ge=1, le=5),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort: str = Query(default="newest", pattern="^(newest|oldest|top|low)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    photos: PhotoService = Depends(photo_service),
):
    items, total = await photos.search_photos(
        q=q, tag=tag, min_rating=min_rating,
        date_from=date_from, date_to=date_to,
        sort=sort, limit=limit, offset=offset,
    )
    return PhotoListResponse(
        items=[PhotoRead.model_validate(p, from_attributes=True) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )