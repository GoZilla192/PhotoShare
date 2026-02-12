import pytest
from app.models.photo import Photo


@pytest.mark.asyncio
async def test_get_photo_by_unique_url_not_found(async_client):
    response = await async_client.get(
        "/photos/by-unique/non-existent-url"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_photo_by_unique_url_ok(async_client, db_session):
    # arrange: create a photo in the test DB
    photo = Photo(
        user_id=1,
        photo_unique_url="api-test-url",
        cloudinary_public_id="dummy",
        description="API test photo",
    )

    async with db_session.begin():
        db_session.add(photo)

    # act: call API
    response = await async_client.get(
        "/photos/by-unique/api-test-url"
    )

    # assert: status and minimum contract response
    assert response.status_code == 200

    data = response.json()
    assert data["photo_unique_url"] == "api-test-url"
