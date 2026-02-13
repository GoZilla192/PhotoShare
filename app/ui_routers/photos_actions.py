import uuid
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.ui_routers.deps import get_current_user_ui, get_templates

from app.service.photos_service import PhotoService
from app.service.comment_service import CommentService
from app.service.rating_service import RatingService
from app.service.tagging_service import TaggingService

from app.dependency.dependencies import photo_service, comment_service, rating_service, tagging_service

router = APIRouter(tags=["UI-Photo"])

def _parse_tags_csv(tags: str | None) -> list[str] | None:
    if not tags:
        return None
    items = [t.strip() for t in tags.split(",")]
    items = [t for t in items if t]
    return items[:5] or None

@router.get("/photos/upload")
async def ui_upload_form(request: Request, _=Depends(get_current_user_ui)):
    templates = get_templates(request)
    return templates.TemplateResponse(request, "pages/photos/upload.html")

@router.post("/photos/upload")
async def ui_upload_submit(
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    current_user=Depends(get_current_user_ui),
    photos: PhotoService = Depends(photo_service),
):
    content = await file.read()
    unique_url = str(uuid.uuid4())
    await photos.create_photo(
        user_id=current_user.id,
        file=content,
        photo_unique_url=unique_url,
        description=description,
        tags=_parse_tags_csv(tags),
    )
    return RedirectResponse(url="/ui/", status_code=303)

@router.post("/photos/{photo_id}/comment")
async def ui_add_comment(
    photo_id: int,
    text: str = Form(...),
    current_user=Depends(get_current_user_ui),
    comments: CommentService = Depends(comment_service),
):
    await comments.create(photo_id=photo_id, user_id=current_user.id, text=text)
    return RedirectResponse(url=f"/ui/photos/{photo_id}", status_code=303)

@router.post("/photos/{photo_id}/rate")
async def ui_rate_photo(
    photo_id: int,
    value: int = Form(...),
    current_user=Depends(get_current_user_ui),
    rating: RatingService = Depends(rating_service),
):
    await rating.set_rating(photo_id=photo_id, value=value, current_user=current_user)
    return await rating.get_stats(photo_id=photo_id)  # для AJAX

@router.post("/photos/{photo_id}/tags")
async def ui_update_tags(
    photo_id: int,
    tags: str = Form(...),
    current_user=Depends(get_current_user_ui),
    tagging: TaggingService = Depends(tagging_service),
):
    await tagging.set_photo_tags(photo_id=photo_id, tag_names=_parse_tags_csv(tags) or [], current_user=current_user)
    return RedirectResponse(url=f"/ui/photos/{photo_id}", status_code=303)

@router.post("/photos/{photo_id}/description")
async def ui_update_description(
    photo_id: int,
    description: str = Form(...),
    current_user=Depends(get_current_user_ui),
    photos: PhotoService = Depends(photo_service),
):
    await photos.update_description(photo_id=photo_id, description=description, current_user=current_user)
    return RedirectResponse(url=f"/ui/photos/{photo_id}", status_code=303)

@router.post("/photos/{photo_id}/delete")
async def ui_delete_photo(
    photo_id: int,
    current_user=Depends(get_current_user_ui),
    photos: PhotoService = Depends(photo_service),
):
    await photos.delete_photo(photo_id=photo_id, current_user=current_user)
    return RedirectResponse(url="/ui/", status_code=303)