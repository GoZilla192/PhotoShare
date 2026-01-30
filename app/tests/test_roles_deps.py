import pytest
from models.roles import UserRole
from tests.conftest import FakeUser

@pytest.mark.asyncio
async def test_admin_only_allows_admin(client):
    async for ac in client(FakeUser(UserRole.admin)):
        r = await ac.get("/admin-only")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_admin_only_forbids_moderator(client):
    async for ac in client(FakeUser(UserRole.moderator)):
        r = await ac.get("/admin-only")
        assert r.status_code == 403

@pytest.mark.asyncio
async def test_admin_only_forbids_user(client):
    async for ac in client(FakeUser(UserRole.user)):
        r = await ac.get("/admin-only")
        assert r.status_code == 403

@pytest.mark.asyncio
async def test_mod_or_admin_allows_moderator(client):
    async for ac in client(FakeUser(UserRole.moderator)):
        r = await ac.get("/mod-or-admin")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_mod_or_admin_allows_admin(client):
    async for ac in client(FakeUser(UserRole.admin)):
        r = await ac.get("/mod-or-admin")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_mod_or_admin_forbids_user(client):
    async for ac in client(FakeUser(UserRole.user)):
        r = await ac.get("/mod-or-admin")
        assert r.status_code == 403

@pytest.mark.asyncio
async def test_inactive_user_forbidden_everywhere(client):
    async for ac in client(FakeUser(UserRole.admin, is_active=False)):
        r1 = await ac.get("/admin-only")
        r2 = await ac.get("/mod-or-admin")
        assert r1.status_code == 403
        assert r2.status_code == 403
