import pytest
from datetime import datetime, UTC

from app.models.photo import Photo


@pytest.mark.asyncio
async def test_update_photo_description_forbidden(
    async_client,
    db_session,
    override_current_user,
):
    # arrange
    photo = Photo(
        id=1,
        user_id=1,  # not 999
        photo_unique_url="auth-test",
        cloudinary_public_id="dummy",
        description="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    async with db_session.begin():
        db_session.add(photo)

    # act
    response = await async_client.put(
        "/photos/1/description",
        json={"description": "Hacked"},
    )

    # assert
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_can_update_other_users_photo(
    async_client,
    db_session,
    override_admin_user,
):
    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="admin-test",
        cloudinary_public_id="dummy",
        description="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    async with db_session.begin():
        db_session.add(photo)

    response = await async_client.put(
        "/photos/1/description",
        json={"description": "Updated by admin"},
    )

    assert response.status_code == 200

    updated = await db_session.get(Photo, 1)
    assert updated.description == "Updated by admin"

@pytest.mark.asyncio
async def test_moderator_cannot_update_other_users_photo(
    async_client,
    db_session,
    override_moderator_user,
):
    photo = Photo(
        id=1,
        user_id=1,  # не 999
        photo_unique_url="mod-test",
        cloudinary_public_id="dummy",
        description="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    async with db_session.begin():
        db_session.add(photo)

    response = await async_client.put(
        "/photos/1/description",
        json={"description": "Moderator edit"},
    )

    assert response.status_code == 403