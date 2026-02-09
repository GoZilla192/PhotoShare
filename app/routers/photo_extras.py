from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.auth.dependencies import get_current_user
from app.dependency.dependencies import (
    tagging_service as get_tagging_service,
    rating_service as get_rating_service,
    share_service as get_share_service,
)
from app.legacy.service import get_photo_service
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.schemas.rating_schema import RatingResponse, RatingSetRequest
from app.schemas.share_schema import ShareCreateRequest, ShareCreateResponse, TransformRequest
from app.schemas.tag_schema import PhotoTagsReadResponse, PhotoTagsSetRequest
from app.service.cloudinary_service import CloudinaryService
from app.service.photos_service import PhotoService

from app.service.tagging_service import TaggingService
from app.service.rating_service import RatingService
from app.service.share_service import ShareService

router = APIRouter(tags=["Photo Extras"])

# ---------------------------------------------------------------------------
# Tags (поки залежить від наявних методів TaggingService)
# ---------------------------------------------------------------------------


@router.get("/photos/{photo_id}/tags", response_model=PhotoTagsReadResponse)
async def get_photo_tags(
    photo_id: int,
    svc: TaggingService = Depends(get_tagging_service),
) -> PhotoTagsReadResponse:
    try:
        tags = await svc.get_photo_tags(photo_id=photo_id)
        return PhotoTagsReadResponse(photo_id=photo_id, tags=tags)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/photos/{photo_id}/tags", response_model=PhotoTagsReadResponse)
async def set_photo_tags(
    photo_id: int,
    body: PhotoTagsSetRequest,
    current_user=Depends(get_current_user),
    svc: TaggingService = Depends(get_tagging_service),
) -> PhotoTagsReadResponse:
    try:
        tags = await svc.set_photo_tags(photo_id=photo_id, tag_names=body.tags, current_user=current_user)
        return PhotoTagsReadResponse(photo_id=photo_id, tags=tags)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Share link + public open + QR
# ---------------------------------------------------------------------------

@router.post("/photos/{photo_id}/share", response_model=ShareCreateResponse)
async def create_share_link(
    photo_id: int,
    body: ShareCreateRequest,
    current_user=Depends(get_current_user),
    svc: ShareService = Depends(get_share_service),
) -> ShareCreateResponse:
    try:
        uuid = await svc.create_share_link(
            photo_id=photo_id,
            transform_params=body.transform_params,
            current_user=current_user,
        )
        return ShareCreateResponse(uuid=uuid)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/public/{uuid}")
async def open_public(
    uuid: str,
    svc: ShareService = Depends(get_share_service),
):
    try:
        url = await svc.resolve_public(uuid=uuid)
        return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/public/{uuid}/qr")
async def get_public_qr(
    uuid: str,
    svc: ShareService = Depends(get_share_service),
):
    try:
        b64 = await svc.make_public_qr(uuid=uuid)
        return {"png_base64": b64}
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Rating
# ---------------------------------------------------------------------------

@router.get("/photos/{photo_id}/rating", response_model=RatingResponse)
async def get_photo_rating(
    photo_id: int,
    svc: RatingService = Depends(get_rating_service),
) -> RatingResponse:
    try:
        stats = await svc.get_stats(photo_id=photo_id)
        return RatingResponse(avg=stats["avg"], count=stats["count"])
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/photos/{photo_id}/rating", response_model=RatingResponse)
async def set_photo_rating(
    photo_id: int,
    body: RatingSetRequest,
    current_user=Depends(get_current_user),
    svc: RatingService = Depends(get_rating_service),
) -> RatingResponse:
    try:
        await svc.set_rating(photo_id=photo_id, value=body.value, current_user=current_user)
        stats = await svc.get_stats(photo_id=photo_id)
        return RatingResponse(avg=stats["avg"], count=stats["count"])
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Optional transform endpoint (якщо потрібен окремо від share)
# ---------------------------------------------------------------------------

@router.post("/photos/{photo_id}/transform")
async def transform_photo(
    photo_id: int,
    body: TransformRequest,
    current_user=Depends(get_current_user),
    photos: PhotoService = Depends(get_photo_service),
    cloud: CloudinaryService = Depends(get_cloudinary_service),
):
    photo = await photos.get_photo_row(photo_id)  # ORM з cloudinary_public_id
    if photo.user_id != current_user.id:
        raise HTTPException(403, "Only owner can transform preview")

    params = build_transform_params(body)
    url = cloud.build_transformed_url(photo.cloudinary_public_id, params)
    return {"url": url, "params": params}
