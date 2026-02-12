import pytest

from app.models.user import UserRole
from app.auth.service import AuthService
from app.repository.users_repository import UserRepository
from app.repository.token_repository import TokenBlacklistRepository
from app.core.settings import Settings


@pytest.mark.asyncio
async def test_first_registered_user_becomes_admin(db_session):
    users_repo = UserRepository(db_session)
    blacklist_repo = TokenBlacklistRepository(db_session)
    settings = Settings()

    auth_service = AuthService(
        session=db_session,
        users=users_repo,
        blacklist=blacklist_repo,
        settings=settings,
    )

    token = await auth_service.register(
        username="first",
        email="first@example.com",
        password="password123",
    )

    user = await users_repo.get_by_email("first@example.com")

    assert user.role == UserRole.admin

@pytest.mark.asyncio
async def test_second_registered_user_is_regular_user(db_session):
    users_repo = UserRepository(db_session)
    blacklist_repo = TokenBlacklistRepository(db_session)
    settings = Settings()

    auth_service = AuthService(
        session=db_session,
        users=users_repo,
        blacklist=blacklist_repo,
        settings=settings,
    )

    # first user
    await auth_service.register(
        username="first",
        email="first@example.com",
        password="password123",
    )

    # second user
    await auth_service.register(
        username="second",
        email="second@example.com",
        password="password123",
    )

    second_user = await users_repo.get_by_email("second@example.com")

    assert second_user.role == UserRole.user
