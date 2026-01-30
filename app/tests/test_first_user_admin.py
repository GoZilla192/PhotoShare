import pytest
from models.roles import UserRole
from service import users as users_service

@pytest.mark.asyncio
async def test_first_user_becomes_admin(monkeypatch):
    async def fake_count_users(session):
        return 0

    async def fake_create_user(session, user):
        return user

    monkeypatch.setattr(users_service, "count_users", fake_count_users)
    monkeypatch.setattr(users_service, "create_user", fake_create_user)

    user = await users_service.register_user(
        session=None,
        username="first",
        email="first@test.com",
        password_hash="hash",
    )
    assert user.role == UserRole.admin

@pytest.mark.asyncio
async def test_next_users_become_user(monkeypatch):
    async def fake_count_users(session):
        return 5

    async def fake_create_user(session, user):
        return user

    monkeypatch.setattr(users_service, "count_users", fake_count_users)
    monkeypatch.setattr(users_service, "create_user", fake_create_user)

    user = await users_service.register_user(
        session=None,
        username="second",
        email="second@test.com",
        password_hash="hash",
    )
    assert user.role == UserRole.user
