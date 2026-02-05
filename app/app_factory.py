from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers.router import build_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup. також синглтон setting тут або в create_app
    # тут згодом: init db, health checks, cloudinary client, etc.
    yield
    # shutdown
    # тут згодом: close connections, cleanup resources


def create_app() -> FastAPI:
    app = FastAPI(
        title="PhotoShare",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(build_api_router())

    return app