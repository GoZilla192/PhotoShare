from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.db import get_async_session as get_session  # якщо поки так

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(session: AsyncSession = Depends(get_session)):
    # DB check
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
