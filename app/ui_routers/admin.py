from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.ui_routers.deps import get_templates, require_admin_ui
from app.dependency.dependencies import user_service
from app.service.users_service import UserService

router = APIRouter(prefix="/admin", tags=["UI-Admin"])

@router.get("/users")
async def ui_admin_users(
    request: Request,
    admin=Depends(require_admin_ui),
    users: UserService = Depends(user_service),
):
    items = await users.list_users(limit=200, offset=0, current_user=admin)
    templates = get_templates(request)
    return templates.TemplateResponse(
        request,
        "pages/admin/users.html",
        {"users": items, "current_user": admin},
    )

@router.post("/users/{user_id}/ban")
async def ui_ban_user(
    user_id: int,
    admin=Depends(require_admin_ui),
    users: UserService = Depends(user_service),
):
    await users.ban_user(target_user_id=user_id, current_user=admin)
    return RedirectResponse(url="/ui/admin/users", status_code=303)

@router.post("/users/{user_id}/unban")
async def ui_unban_user(
    user_id: int,
    admin=Depends(require_admin_ui),
    users: UserService = Depends(user_service),
):
    await users.unban_user(target_user_id=user_id, current_user=admin)
    return RedirectResponse(url="/ui/admin/users", status_code=303)