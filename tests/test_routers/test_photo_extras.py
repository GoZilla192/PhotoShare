import pytest
from datetime import datetime, UTC
from types import SimpleNamespace

from app.models.photo import Photo
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.main import app as fastapi_app


@pytest.fixture
def app():
    return fastapi_app

@pytest.mark.asyncio
async def test_get_photo_tags_success(async_client, app):
    class FakeService:
        async def get_photo_tags(self, photo_id):
            return ["a", "b"]

    from app.routers.photo_extras import get_tagging_service

    app.dependency_overrides[get_tagging_service] = lambda: FakeService()

    response = await async_client.get("/photos/1/tags")

    assert response.status_code == 200
    assert response.json()["tags"] == ["a", "b"]

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_photo_tags_not_found(async_client, app):
    class FakeService:
        async def get_photo_tags(self, photo_id):
            raise NotFoundError("Photo not found")

    from app.routers.photo_extras import get_tagging_service

    app.dependency_overrides[get_tagging_service] = lambda: FakeService()

    response = await async_client.get("/photos/1/tags")

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_set_photo_tags_success(async_client, app):
    class FakeService:
        async def set_photo_tags(self, photo_id, tag_names, current_user):
            return tag_names

    async def fake_user():
        return SimpleNamespace(id=1, role="user")

    from app.routers.photo_extras import get_tagging_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_tagging_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.put(
        "/photos/1/tags",
        json={"tags": ["a", "b"]},
    )

    assert response.status_code == 200
    assert response.json()["tags"] == ["a", "b"]

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_set_photo_tags_forbidden(async_client, app):
    class FakeService:
        async def set_photo_tags(self, *args, **kwargs):
            raise PermissionDeniedError("Forbidden")

    async def fake_user():
        return SimpleNamespace(id=2, role="user")

    from app.routers.photo_extras import get_tagging_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_tagging_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.put(
        "/photos/1/tags",
        json={"tags": ["a"]},
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_share_link_success(async_client, app):
    class FakeService:
        async def create_share_link(self, **kwargs):
            return "uuid123"

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photo_extras import get_share_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_share_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.post(
        "/photos/1/share",
        json={"transform_params": {}},
    )

    assert response.status_code == 200
    assert response.json()["uuid"] == "uuid123"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_open_public_redirect(async_client, app):
    class FakeService:
        async def resolve_public(self, uuid):
            return "https://example.com/img.jpg"

    from app.routers.photo_extras import get_share_service

    app.dependency_overrides[get_share_service] = lambda: FakeService()

    response = await async_client.get("/public/abc")

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/img.jpg"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_public_qr(async_client, app):
    class FakeService:
        async def make_public_qr(self, uuid):
            return "base64data"

    from app.routers.photo_extras import get_share_service

    app.dependency_overrides[get_share_service] = lambda: FakeService()

    response = await async_client.get("/public/abc/qr")

    assert response.status_code == 200
    assert response.json()["png_base64"] == "base64data"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_photo_rating(async_client, app):
    class FakeService:
        async def get_stats(self, photo_id):
            return {
                "photo_id": photo_id,
                "avg_rating": 4.5,
                "ratings_count": 2,
            }

    from app.routers.photo_extras import get_rating_service

    app.dependency_overrides[get_rating_service] = lambda: FakeService()

    response = await async_client.get("/photos/1/rating")

    assert response.status_code == 200
    assert response.json()["avg_rating"] == 4.5
    assert response.json()["ratings_count"] == 2

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_set_photo_rating(async_client, app):
    class FakeService:
        async def set_rating(self, **kwargs):
            return

        async def get_stats(self, photo_id):
            return {
                "photo_id": photo_id,
                "avg_rating": 5.0,
                "ratings_count": 1,
            }

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photo_extras import get_rating_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_rating_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.put(
        "/photos/1/rating",
        json={"value": 5},
    )

    assert response.status_code == 200
    assert response.json()["avg_rating"] == 5.0
    assert response.json()["ratings_count"] == 1

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_transform_photo_success(async_client, app):
    class FakePhotoService:
        async def get_photo(self, photo_id):
            return SimpleNamespace(
                id=1,
                user_id=1,
                cloudinary_public_id="abc",
            )

    class FakeCloud:
        def build_transformed_url(self, public_id, params):
            return "https://example.com/transformed.jpg"

    async def fake_user():
        return SimpleNamespace(id=1)

    from app.routers.photo_extras import photo_service, cloudinary_service
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[photo_service] = lambda: FakePhotoService()
    app.dependency_overrides[cloudinary_service] = lambda: FakeCloud()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.post(
        "/photos/1/transform",
        json={"preset": "thumb"},
    )

    assert response.status_code == 200
    assert "url" in response.json()

    app.dependency_overrides.clear()