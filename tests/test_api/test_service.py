import pytest
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace

from app.auth.service import (
    AuthService,
    ConflictError,
    InvalidCredentialsError,
    InactiveUserError,
)

@pytest.fixture
def auth_service():
    session = AsyncMock()
    users = AsyncMock()
    blacklist = AsyncMock()

    settings = SimpleNamespace(
        SECRET_KEY="test",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
    )

    return AuthService(session, users, blacklist, settings), session, users, blacklist

@pytest.mark.asyncio
async def test_register_email_conflict(auth_service):
    service, _, users, _ = auth_service

    users.get_by_email.return_value = object()

    with pytest.raises(ConflictError):
        await service.register(
            username="u",
            email="e@mail.com",
            password="pass",
        )

@pytest.mark.asyncio
async def test_register_username_conflict(auth_service):
    service, _, users, _ = auth_service

    users.get_by_email.return_value = None
    users.get_by_username.return_value = object()

    with pytest.raises(ConflictError):
        await service.register(
            username="u",
            email="e@mail.com",
            password="pass",
        )

from app.models import UserRole
from unittest.mock import patch


@pytest.mark.asyncio
async def test_register_first_user_is_admin(auth_service):
    service, session, users, _ = auth_service

    users.get_by_email.return_value = None
    users.get_by_username.return_value = None
    users.exists_any.return_value = False

    fake_user = MagicMock(id=1, role=UserRole.admin)
    users.add.return_value = fake_user

    with patch("app.auth.service.create_access_token", return_value="token"):
        token = await service.register(
            username="u",
            email="e@mail.com",
            password="pass",
        )

    assert token == "token"
    session.flush.assert_awaited_once()

@pytest.mark.asyncio
async def test_register_regular_user(auth_service):
    service, _, users, _ = auth_service

    users.get_by_email.return_value = None
    users.get_by_username.return_value = None
    users.exists_any.return_value = True

    fake_user = MagicMock(id=2)
    users.add.return_value = fake_user

    with patch("app.auth.service.create_access_token", return_value="token"):
        token = await service.register(
            username="u2",
            email="e2@mail.com",
            password="pass",
        )

    assert token == "token"

@pytest.mark.asyncio
async def test_login_user_not_found(auth_service):
    service, _, users, _ = auth_service

    users.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await service.login(email="e@mail.com", password="pass")

@pytest.mark.asyncio
async def test_login_inactive_user(auth_service):
    service, _, users, _ = auth_service

    fake_user = MagicMock(is_active=False)
    users.get_by_email.return_value = fake_user

    with pytest.raises(InactiveUserError):
        await service.login(email="e@mail.com", password="pass")

from unittest.mock import patch


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service):
    service, _, users, _ = auth_service

    fake_user = MagicMock(is_active=True, password_hash="hash")
    users.get_by_email.return_value = fake_user

    with patch("app.auth.service.verify_password", return_value=False):
        with pytest.raises(InvalidCredentialsError):
            await service.login(email="e@mail.com", password="pass")

@pytest.mark.asyncio
async def test_login_success(auth_service):
    service, _, users, _ = auth_service

    fake_user = MagicMock(
        id=1,
        is_active=True,
        password_hash="hash",
        role="admin",
    )
    users.get_by_email.return_value = fake_user

    with patch("app.auth.service.verify_password", return_value=True):
        with patch("app.auth.service.create_access_token", return_value="token"):
            token = await service.login(email="e@mail.com", password="pass")

    assert token == "token"

@pytest.mark.asyncio
async def test_logout_invalid_payload(auth_service):
    service, _, _, _ = auth_service

    with patch("app.auth.service.decode_token", return_value={}):
        with pytest.raises(ValueError):
            await service.logout("token")

@pytest.mark.asyncio
async def test_logout_success(auth_service):
    service, session, _, blacklist = auth_service

    payload = {"jti": "123", "sub": "1", "exp": 9999999999}

    with patch("app.auth.service.decode_token", return_value=payload):
        await service.logout("token")

    blacklist.add.assert_awaited_once()
    session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_logout_rollback_on_error(auth_service):
    service, session, _, blacklist = auth_service

    payload = {"jti": "123", "sub": "1", "exp": 9999999999}

    blacklist.add.side_effect = Exception("DB error")

    with patch("app.auth.service.decode_token", return_value=payload):
        with pytest.raises(Exception):
            await service.logout("token")

    session.rollback.assert_awaited_once()