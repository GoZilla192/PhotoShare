import pytest
from unittest.mock import patch

from app.database import db


def test_get_database_url_success():
    with patch("app.database.db.Settings") as mock_settings:
        mock_settings.return_value.database_url = "postgresql+asyncpg://user:pass@localhost/db"

        url = db._get_database_url()

        assert url == "postgresql+asyncpg://user:pass@localhost/db"

def test_get_database_url_raises():
    with patch("app.database.db.Settings") as mock_settings:
        mock_settings.return_value.database_url = None

        with pytest.raises(RuntimeError, match="DATABASE_URL is not set"):
            db._get_database_url()

from unittest.mock import patch, MagicMock


def test_get_engine_creates_once():
    db._engine = None  # reset

    fake_engine = MagicMock()

    with patch("app.database.db.create_async_engine", return_value=fake_engine) as mock_create:
        with patch("app.database.db._get_database_url", return_value="postgresql://test"):

            engine1 = db.get_engine()
            engine2 = db.get_engine()

            mock_create.assert_called_once()
            assert engine1 is fake_engine
            assert engine2 is fake_engine

def test_get_sessionmaker_creates_once():
    db._sessionmaker = None  # reset

    fake_engine = MagicMock()
    fake_sessionmaker = MagicMock()

    with patch("app.database.db.get_engine", return_value=fake_engine):
        with patch("app.database.db.async_sessionmaker", return_value=fake_sessionmaker) as mock_sm:

            sm1 = db.get_sessionmaker()
            sm2 = db.get_sessionmaker()

            mock_sm.assert_called_once_with(
                fake_engine,
                expire_on_commit=False,
                class_=db.AsyncSession,
            )

            assert sm1 is fake_sessionmaker
            assert sm2 is fake_sessionmaker

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_get_async_session_yields_session():
    fake_session = AsyncMock()

    # створюємо mock sessionmaker, який повертає async context manager
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = fake_session
    mock_context_manager.__aexit__.return_value = None

    mock_sessionmaker = MagicMock(return_value=mock_context_manager)

    with patch("app.database.db.get_sessionmaker", return_value=mock_sessionmaker):

        generator = db.get_async_session()

        session = None
        async for s in generator:
            session = s

        assert session is fake_session