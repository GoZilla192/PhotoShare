import pytest

from app.models.user import User
from app.core.exceptions import ConflictError, InvalidCredentialsError, InactiveUserError
from app.main import app as fastapi_app


@pytest.fixture
def app():
    return fastapi_app

@pytest.mark.asyncio
async def test_register_success(async_client, app):
    class FakeAuth:
        async def register(self, **kwargs):
            return "token123"

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/register",
        json={
            "username": "usr1",
            "email": "u1@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json()["access_token"] == "token123"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_conflict(async_client, app):
    class FakeAuth:
        async def register(self, **kwargs):
            raise ConflictError("Email already exists")

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/register",
        json={
            "username": "usr1",
            "email": "u1@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_success(async_client, app):
    class FakeAuth:
        async def login(self, email, password):
            return "token456"

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/login",
        json={"email": "u1@test.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token456"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_invalid(async_client, app):
    class FakeAuth:
        async def login(self, email, password):
            raise InvalidCredentialsError()

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/login",
        json={"email": "u1@test.com", "password": "wrong1"},
    )

    assert response.status_code == 401

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_inactive(async_client, app):
    class FakeAuth:
        async def login(self, email, password):
            raise InactiveUserError()

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/login",
        json={"email": "u1@test.com", "password": "password123"},
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_logout(async_client, app):
    class FakeAuth:
        async def logout(self, token):
            return

    async def fake_user():
        return User(id=1, username="usr1", email="u1@test.com", password_hash="x")

    async def fake_token():
        return "token123"

    from app.auth.dependencies import get_current_user, oauth2_scheme
    from app.dependency.dependencies import auth_service

    app.dependency_overrides[get_current_user] = fake_user
    app.dependency_overrides[oauth2_scheme] = fake_token
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post("/auth/logout")

    assert response.status_code == 204

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_token_success(async_client, app):
    class FakeAuth:
        async def login(self, email, password):
            return "token789"

    from app.dependency.dependencies import auth_service
    app.dependency_overrides[auth_service] = lambda: FakeAuth()

    response = await async_client.post(
        "/auth/token",
        data={"username": "u1@test.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token789"

    app.dependency_overrides.clear()