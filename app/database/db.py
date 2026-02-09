
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import Settings

def _get_database_url() -> str:
    database_url = Settings().database_url
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return database_url


_engine = None
_sessionmaker = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(_get_database_url(), echo=False)
    return _engine


def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _sessionmaker


async def get_async_session():
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
