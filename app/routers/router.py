from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.photos import router as photos_router
from app.routers import tags


def build_api_router() -> APIRouter:
    api = APIRouter()

    # Тут централізовано підключаємо роутери
    api.include_router(tags.router)
    api.include_router(photos_router)
    api.include_router(auth_router)

    return api