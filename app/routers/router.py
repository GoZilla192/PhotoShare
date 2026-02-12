from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.photos import router as photos_router
from app.routers.users import router as users_router
from app.routers.comments import router as comments_router
from app.routers.photo_extras import router as photo_extras_router
from app.routers.health import router as health_router
from app.routers.tags import router as tags_router
from app.routers.ratings import router as ratings_router


def build_api_router() -> APIRouter:
    api = APIRouter()

    # Тут централізовано підключаємо роутери
    api.include_router(users_router)
    api.include_router(photos_router)
    api.include_router(photo_extras_router)
    api.include_router(comments_router)
    api.include_router(tags_router)
    api.include_router(auth_router)
    api.include_router(health_router)
    api.include_router(ratings_router)

    return api