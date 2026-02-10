from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.dependency.dependencies import get_settings, get_session
from app.routers.router import build_api_router
from app.ui_routers.ui_router import build_ui_router
from fastapi import Request, HTTPException
from fastapi.exception_handlers import http_exception_handler as fastapi_http_exception_handler
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

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
        version="0.1.5",
    )

    # --- UI: templates + static ---
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
    app.mount("/js", StaticFiles(directory="app/web/js"), name="js")
    templates = Jinja2Templates(directory="app/web/templates")
    app.state.templates = templates

    # Роутери
    app.include_router(build_api_router())
    app.include_router(build_ui_router())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Для API/Swagger лишаємо стандартну JSON-відповідь
        if request.url.path.startswith(("/docs", "/openapi", "/health")):
            return await fastapi_http_exception_handler(request, exc)

        # Для UI віддаємо HTML-шаблони
        if exc.status_code in (403, 404):
            return app.state.templates.TemplateResponse(
                f"errors/{exc.status_code}.html",
                {"request": request, "detail": exc.detail},
                status_code=exc.status_code,
            )

        # Інші HTTP помилки — стандартно
        return await fastapi_http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Валідація для API — як зазвичай
        if request.url.path.startswith(("/docs", "/openapi", "/health")):
            return await request_validation_exception_handler(request, exc)

        # Для UI можна показати 403 або окремий шаблон 422 (як захочеш)
        return app.state.templates.TemplateResponse(
            "errors/403.html",
            {"request": request, "detail": "Validation error"},
            status_code=403,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        if request.url.path.startswith(("/docs", "/openapi", "/health")):
            raise exc  # щоб API не “ховав” 500
        return app.state.templates.TemplateResponse(
            "errors/500.html",
            {"request": request},
            status_code=500,
        )

    # lifespan підключаємо після створення app:
    # FastAPI приймає lifespan тільки в конструктор, тому робимо так:
    app.router.lifespan_context = lifespan  # type: ignore[assignment]

    return app