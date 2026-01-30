import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pytest_asyncio
from pathlib import Path
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from models.roles import UserRole
from service.deps import require_role, require_roles

class FakeUser:
    def __init__(self, role: UserRole, is_active: bool = True):
        self.role = role
        self.is_active = is_active


@pytest.fixture
def make_app():

    def _make_app(current_user: FakeUser) -> FastAPI:
        app = FastAPI()

        async def override_get_current_user():
            return current_user

        @app.get("/admin-only")
        async def admin_only(user=Depends(require_role(UserRole.admin))):
            return {"ok": True}

        @app.get("/mod-or-admin")
        async def mod_or_admin(user=Depends(require_roles(UserRole.moderator, UserRole.admin))):
            return {"ok": True}
        from service import deps as deps_module
        app.dependency_overrides[deps_module.get_current_user] = override_get_current_user
        return app
    return _make_app


@pytest_asyncio.fixture
async def client(make_app):
    async def _client(current_user: FakeUser):
        app = make_app(current_user)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    return _client
