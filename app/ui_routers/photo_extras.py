from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.ui_routers.deps import get_templates, get_current_user_ui
from app.dependency.dependencies import share_service, cloudinary_service, photo_service
from app.service.share_service import ShareService
from app.service.cloudinary_service import CloudinaryService, build_transform_params
from app.service.photos_service import PhotoService
from app.schemas.share_schema import TransformRequest, ShareCreateRequest, \
    TransformPreset  # якщо є; інакше зберемо вручну

router = APIRouter(tags=["UI-PhotoExtras"])

@router.post("/photos/{photo_id}/share")
async def ui_create_share(
    photo_id: int,
    current_user=Depends(get_current_user_ui),
    svc: ShareService = Depends(share_service),
    transform_params_json: str | None = Form(default=None),
):
    import json

    transform_params: dict = {}
    if transform_params_json:
        transform_params = json.loads(transform_params_json)

    uuid = await svc.create_share_link(
        photo_id=photo_id,
        transform_params=transform_params,
        current_user=current_user,
    )

    return RedirectResponse(url=f"/ui/photos/{photo_id}?share_uuid={uuid}", status_code=303)


@router.get("/photos/{photo_id}/share/qr")
async def ui_share_qr(
    request: Request,
    photo_id: int,
    uuid: str,
    svc: ShareService = Depends(share_service),
):
    png_b64 = await svc.make_public_qr(uuid=uuid)
    templates = get_templates(request)
    return templates.TemplateResponse(
        request,
        "pages/photos/share_qr.html",
        {"photo_id": photo_id, "uuid": uuid, "png_base64": png_b64},
    )


@router.post("/photos/{photo_id}/transform")
async def ui_transform_preview(
    request: Request,
    photo_id: int,
    current_user=Depends(get_current_user_ui),
    photos: PhotoService = Depends(photo_service),
    cloud: CloudinaryService = Depends(cloudinary_service),

    preset: str = Form(...),                     # REQUIRED
    width: int | None = Form(default=None),
    height: int | None = Form(default=None),
    blur: int | None = Form(default=None),       # for blur preset
    angle: int | None = Form(default=None),      # for rotate preset
    crop: str | None = Form(default=None),
    quality: str | None = Form(default=None),
    effect: str | None = Form(default=None),
):
    photo = await photos.get_photo(photo_id)
    if photo.user_id != current_user.id:
        raise HTTPException(403, "Only owner can transform preview")

    body = TransformRequest(
        preset=TransformPreset(preset),
        width=width,
        height=height,
        blur=blur,
        angle=angle,
        crop=crop,
        quality=quality,
        effect=effect,
    )

    params = build_transform_params(body)
    url = cloud.build_transformed_url(public_id=photo.cloudinary_public_id, params=params)

    templates = get_templates(request)
    return templates.TemplateResponse(
        request,
        "pages/photos/transform_preview.html",
        {"photo": photo, "url": url, "params": params},
    )