from fastapi import APIRouter
from app.ui_routers.tags import router as ui_tags_router
from app.ui_routers.public import router as ui_public_router
from app.ui_routers.auth import router as ui_auth_router
from app.ui_routers.me import router as ui_me_router
from app.ui_routers.photos_actions import router as ui_photos_actions_router
from app.ui_routers.photo_extras import router as photo_extras_router
from app.ui_routers.admin import router as ui_admin_router

def build_ui_router() -> APIRouter:
    ui = APIRouter(prefix="/ui")

    # Тут централізовано підключаємо роутери
    ui.include_router(ui_public_router)
    ui.include_router(ui_auth_router)
    ui.include_router(ui_me_router)
    ui.include_router(ui_photos_actions_router)
    ui.include_router(photo_extras_router)
    ui.include_router(ui_tags_router)
    ui.include_router(ui_admin_router)

    return ui