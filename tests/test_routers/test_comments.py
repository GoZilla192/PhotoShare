import pytest
from datetime import datetime, UTC

from app.models.comment import Comment
from types import SimpleNamespace
from app.auth.dependencies import get_current_user
from app.dependency.dependencies import comment_service as get_comment_service
from app.main import app as fastapi_app


@pytest.fixture
def app():
    return fastapi_app

@pytest.mark.asyncio
async def test_list_comments_for_photo(async_client, app):
    class FakeService:
        async def list_for_photo(self, photo_id, limit, offset):
            return [
                    Comment(
                        id=1,
                        photo_id=photo_id,
                        user_id=1,
                        text="hello",
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    ]

    app.dependency_overrides[get_comment_service] = lambda: FakeService()

    response = await async_client.get("/photos/1/comments")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["text"] == "hello"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_comment_not_found(async_client, app):
    class FakeService:
        async def update_text(self, **kwargs):
            raise ValueError("Comment not found")

    async def fake_user():
        return SimpleNamespace(id=1)

    app.dependency_overrides[get_comment_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.patch(
        "/comments/1",
        json={"text": "new"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_comment_route(async_client, app):
    class FakeService:
        async def create(self, photo_id, user_id, text):
            return Comment(
                        id=1,
                        photo_id=photo_id,
                        user_id=1,
                        text="hello",
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )

    async def fake_user():
        return SimpleNamespace(id=1)

    app.dependency_overrides[get_comment_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.post(
        "/photos/1/comments",
        json={"text": "hello"},
    )

    assert response.status_code == 201
    assert response.json()["text"] == "hello"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_comment_forbidden(async_client, app):
    class FakeService:
        async def update_text(self, **kwargs):
            raise PermissionError("Forbidden")

    async def fake_user():
        return SimpleNamespace(id=1)

    app.dependency_overrides[get_comment_service] = lambda: FakeService()
    app.dependency_overrides[get_current_user] = fake_user

    response = await async_client.patch(
        "/comments/1",
        json={"text": "new"},
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()