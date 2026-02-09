from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.dependency.dependencies import get_settings, get_session
from app.routers.router import build_api_router


def setup_logging() -> None:
    """
    Мінімальна конфігурація логів (без dictConfig),
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def db_healthcheck() -> None:
    """
    Проста перевірка, що DB піднімається і приймає запити.
    Не тримаємо engine/session в app.state — у нас DI вже є через get_async_session().
    """
    async for session in get_session():
        await session.execute(text("SELECT 1"))
        return


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = app
    settings = get_settings()
    logger = logging.getLogger("photoshare")

    logger.info("Starting %s ...", settings.APP_NAME)

    # --- startup: DB check ---
    try:
        await db_healthcheck()
        logger.info("DB connection: OK")
    except Exception:
        logger.exception("DB connection: FAILED")
        # якщо виришимо падати при старті — піднімаємо виняток
        raise

    yield

    # --- shutdown ---
    logger.info("Shutting down %s ...", settings.APP_NAME)


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.4",
    )

    # Роутери
    app.include_router(build_api_router())

    # lifespan підключаємо після створення app:
    # FastAPI приймає lifespan тільки в конструктор, тому робимо так:
    app.router.lifespan_context = lifespan  # type: ignore[assignment]

    return app