from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.qr import qr as qr_router
from app.routers.photos import router as photos_router
from app.routers.tags import tags as tags_router


def build_api_router() -> APIRouter:
    api = APIRouter()

    # Here we connect routers
    api.include_router(auth_router)
    app.include_router(qr_router)
    api.include_router(photos_router)
    api.include_router(tags_router)

    return api