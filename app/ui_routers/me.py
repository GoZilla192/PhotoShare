from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.ui_routers.deps import get_templates, get_current_user_ui
from app.dependency.dependencies import user_service
from app.service.users_service import UserService

router = APIRouter(tags=["UI-User"])

@router.get("/me")
async def ui_me(
    request: Request,
    current_user=Depends(get_current_user_ui),
    users: UserService = Depends(user_service),
):
    profile = await users.get_me(current_user)  # :contentReference[oaicite:10]{index=10}
    templates = get_templates(request)
    return templates.TemplateResponse(
        request,
        "pages/me.html",
        {"profile": profile, "current_user": current_user},
    )