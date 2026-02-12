import os
from dotenv import load_dotenv
from types import SimpleNamespace

load_dotenv(".env.test")
os.environ["ENV"] = "test"

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.main import app
from app.models.base import Base
from app.dependency.dependencies import get_session
from app.service.photos_service import PhotoService
from app.repository.photos_repository import PhotoRepository
from app.auth.dependencies import get_current_user
from app.models.user import UserRole


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def async_session_maker(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def db_session(engine, async_session_maker) -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class DummyCloudinary:
    pass

class DummyTagsRepository:
    pass

@pytest.fixture
def dummy_cloudinary():
    return DummyCloudinary()

@pytest.fixture
def dummy_tags_repo():
    return DummyTagsRepository()

@pytest.fixture
def photo_service_factory(db_session, dummy_cloudinary, dummy_tags_repo):
    """
    photos_repo may be different
    """
    def _factory(photos_repo=None):
        if photos_repo is None:
            photos_repo = PhotoRepository(db_session)

        return PhotoService(
            session=db_session,
            photos_repo=photos_repo,
            cloudinary_client=dummy_cloudinary,
            tags_repo=dummy_tags_repo,
        )

    return _factory

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

@pytest.fixture(autouse=True)
def override_get_session(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def override_current_user():
    fake_user = SimpleNamespace(
        id=999,
        role="user",
        is_active=True
    )

    async def _override():
        return fake_user

    app.dependency_overrides[get_current_user] = _override
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def override_admin_user():
    fake_user = SimpleNamespace(
        id=999,
        role=UserRole.admin,
        is_active=True,
    )

    async def _override():
        return fake_user

    app.dependency_overrides[get_current_user] = _override
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def override_moderator_user():
    fake_user = SimpleNamespace(
        id=999,
        role=UserRole.moderator,
        is_active=True,
    )

    async def _override():
        return fake_user

    app.dependency_overrides[get_current_user] = _override
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def override_moderator_user():
    fake_user = SimpleNamespace(
        id=999,
        role=UserRole.moderator,
        is_active=True,
    )

    async def _override():
        return fake_user

    app.dependency_overrides[get_current_user] = _override
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)