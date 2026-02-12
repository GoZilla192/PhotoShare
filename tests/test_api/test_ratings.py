import pytest
from datetime import datetime, UTC

from app.models.photo import Photo
from app.models.rating import Rating

@pytest.mark.asyncio
async def test_user_can_add_rating(
    async_client,
    db_session,
    override_current_user,  # role=user
):
    # creating photo of another user
    photo = Photo(
        id=1,
        user_id=1,  # not 999
        photo_unique_url="rating-test",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    response = await async_client.post(
        "/ratings/photos/1",
        json={"value": 5},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["photo_id"] == 1
    assert data["avg_rating"] == 5.0
    assert data["ratings_count"] == 1

@pytest.mark.asyncio
async def test_user_cannot_rate_own_photo(
    async_client,
    db_session,
    override_current_user,
):
    # user 999 is owner
    photo = Photo(
        id=1,
        user_id=999,
        photo_unique_url="own-photo",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    response = await async_client.post(
        "/ratings/photos/1",
        json={"value": 5},
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_user_cannot_rate_same_photo_twice(
    async_client,
    db_session,
    override_current_user,
):
    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="double-rate",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    # first rating
    await async_client.post(
        "/ratings/photos/1",
        json={"value": 5},
    )

    # second rating
    response = await async_client.post(
        "/ratings/photos/1",
        json={"value": 4},
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_user_cannot_delete_rating(
    async_client,
    db_session,
    override_current_user,
):
    rating = Rating(
        id=1,
        photo_id=1,
        user_id=1,
        value=5,
    )

    db_session.add(rating)
    await db_session.flush()

    response = await async_client.delete("/ratings/1")

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_moderator_can_delete_rating(
    async_client,
    db_session,
    override_moderator_user,
):
    rating = Rating(
        id=1,
        photo_id=1,
        user_id=1,
        value=5,
    )

    db_session.add(rating)
    await db_session.flush()

    response = await async_client.delete("/ratings/1")

    assert response.status_code == 204