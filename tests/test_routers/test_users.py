import pytest

from app.models.user import User
from app.models.user import UserRole

from app.main import app as fastapi_app


@pytest.fixture
def app():
    return fastapi_app

@pytest.mark.asyncio
async def test_get_me(async_client, override_regular_user):
    response = await async_client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["username"] == override_regular_user.username

@pytest.mark.asyncio
async def test_get_public_profile_route(async_client, db_session):
    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    response = await async_client.get("/users/u1")

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_ban_user_route(async_client, override_admin_user, db_session):
    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    response = await async_client.patch(f"/users/{user.id}/ban")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

@pytest.mark.asyncio
async def test_unban_user_route(async_client, override_admin_user, db_session):
    user = User(
        username="u1",
        email="u1@test.com",
        password_hash="x",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()

    response = await async_client.patch(f"/users/{user.id}/unban")

    assert response.status_code == 200
    assert response.json()["is_active"] is True

@pytest.mark.asyncio
async def test_set_role_route(async_client, override_admin_user, db_session):
    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    response = await async_client.patch(
        f"/users/{user.id}/role?role=moderator"
    )

    assert response.status_code == 204

@pytest.mark.asyncio
async def test_update_me_route(async_client, db_session, app):
    # 1️⃣ створюємо користувача в БД
    user = User(
        username="u1",
        email="u1@test.com",
        password_hash="x",
        role=UserRole.user,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # 2️⃣ override dependency
    async def _override():
        return user

    from app.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = _override

    # 3️⃣ викликаємо endpoint
    response = await async_client.patch(
        "/users/me",
        json={"username": "newname"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "newname"

    app.dependency_overrides.clear()