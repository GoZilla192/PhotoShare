from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from app.ui_routers.deps import get_templates, get_optional_user_ui

from app.service.photos_service import PhotoService
from app.service.tagging_service import TaggingService
from app.service.rating_service import RatingService
from app.service.comment_service import CommentService
from app.service.users_service import UserService

from app.dependency.dependencies import photo_service, tagging_service, rating_service, comment_service, user_service  # :contentReference[oaicite:12]{index=12}


router = APIRouter(tags=["UI-Public"])

@router.get("/")
async def ui_index(
    request: Request,
    q: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort: str = Query(default="newest"),
    page: int = Query(default=1, ge=1),
    current_user=Depends(get_optional_user_ui),
    photos: PhotoService = Depends(photo_service),
    tagging: TaggingService = Depends(tagging_service),
):
    limit = 20
    offset = (page - 1) * limit

    items, total = await photos.search_photos(q=q, tag=tag, sort=sort, limit=limit, offset=offset)
    cloud = await tagging.get_tag_cloud(limit=50, offset=0)

    templates = get_templates(request)
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "tag_cloud": cloud,
            "current_user": current_user,
            "filters": {"q": q, "tag": tag, "sort": sort, "page": page},
        },
    )

@router.get("/photos/{photo_id}")
async def ui_photo_detail(
    request: Request,
    photo_id: int,

    photos: PhotoService = Depends(photo_service),
    tagging: TaggingService = Depends(tagging_service),
    rating: RatingService = Depends(rating_service),
    comments: CommentService = Depends(comment_service),
):
    photo = await photos.get_photo(photo_id)
    tags = await tagging.get_photo_tags(photo_id=photo_id)
    rating_stats = await rating.get_stats(photo_id=photo_id)
    comment_items = await comments.list_for_photo(photo_id=photo_id, limit=50, offset=0)
    share_uuid = request.query_params.get("share_uuid")

    templates = get_templates(request)
    return templates.TemplateResponse(
        "pages/photos/detail.html",
        {
            "request": request,
            "photo": photo,
            "tags": tags,
            "rating": rating_stats,
            "comments": comment_items,
            "share_uuid": share_uuid,
        },
    )

@router.get("/users/{username}")
async def ui_user_public(
    request: Request,
    username: str,
    users: UserService = Depends(user_service),
    photos: PhotoService = Depends(photo_service),
):
    profile = await users.get_public_profile_by_username(username)
    user_photos = await photos.list_by_user(profile.id, limit=20, offset=0)

    templates = get_templates(request)
    return templates.TemplateResponse(
        "pages/users/public.html",
        {
            "request": request,
            "profile": profile,
            "photos": user_photos,
        },
    )