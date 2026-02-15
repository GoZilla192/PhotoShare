import pytest
from datetime import datetime, UTC
from types import SimpleNamespace

from app.models.photo import Photo
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.main import app as fastapi_app
from app.dependency.dependencies import photo_service
import app.auth.dependencies as auth_deps


@pytest.fixture
def app():
    return fastapi_app

@pytest.mark.asyncio
async def test_upload_photo_500(async_client, app):
    class FakeService:
        async def create_photo(self, **kwargs):
            raise RuntimeError("boom")

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photos import photo_service as get_photo_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_photo_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.post(
        "/photos",
        files={"file": ("test.jpg", b"data", "image/jpeg")},
    )

    assert response.status_code == 500

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_photo_by_id_not_found(async_client, app):
    class FakeService:
        async def get_photo(self, photo_id):
            raise NotFoundError("Not found")

    async def fake_user():
        return SimpleNamespace(id=1, role="user")

    from app.routers.photos import photo_service as get_photo_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_photo_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.get("/photos/1")

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_photo_by_id_forbidden(async_client, app):
    class FakeService:
        async def get_photo(self, photo_id):
            return SimpleNamespace(user_id=2)

        def ensure_owner_or_admin(self, user, owner_id):
            raise PermissionDeniedError("Forbidden")

        cloudinary = None

    async def fake_user():
        return SimpleNamespace(id=1, role="user")

    from app.routers.photos import photo_service as get_photo_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_photo_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.get("/photos/1")

    assert response.status_code == 403

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_photo_by_unique_url_not_found(async_client, app):
    class FakeService:
        async def get_photo_by_unique_url(self, slug):
            raise NotFoundError("Not found")

    from app.routers.photos import photo_service as get_photo_service

    app.dependency_overrides[get_photo_service] = lambda: FakeService()

    response = await async_client.get("/photos/by-unique/test")

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_photo_description_not_found(async_client, app):
    class FakeService:
        async def update_description(self, *args, **kwargs):
            raise NotFoundError("Not found")

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photos import photo_service as get_photo_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_photo_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.put(
        "/photos/1/description",
        json={"description": "new"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_photo_not_found(async_client, app):
    class FakeService:
        async def delete_photo(self, *args, **kwargs):
            raise NotFoundError("Not found")

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photos import photo_service as get_photo_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_photo_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.delete("/photos/1")

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_search_photos_success(async_client, app):

    class FakeService:
        async def search_photos(self, **kwargs):
            return (
                [
                    SimpleNamespace(
                        id=1,
                        photo_unique_url="x",
                        description="test",
                        user_id=1,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                        photo_url="https://example.com/image.jpg",
                    )
                ],
                1,
            )

    def fake_require_roles(*roles):
        async def _dep():
            return SimpleNamespace(id=1, role="admin", is_active=True)
        return _dep

    app.dependency_overrides[photo_service] = lambda: FakeService()
    app.dependency_overrides[auth_deps.require_roles] = fake_require_roles

    response = await async_client.get("/photos/search?q=test")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    app.dependency_overrides.clear()