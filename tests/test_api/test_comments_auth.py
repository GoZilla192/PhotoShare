import pytest
from app.models.comment import Comment
from datetime import datetime, UTC

@pytest.mark.asyncio
async def test_user_cannot_delete_other_users_comment(
    async_client,
    db_session,
    override_current_user,  # role = user
):
    comment = Comment(
        id=1,
        user_id=1,  # не 999
        photo_id=1,
        text="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    async with db_session.begin():
        db_session.add(comment)

    response = await async_client.delete("/comments/1")

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_moderator_can_delete_other_users_comment(
    async_client,
    db_session,
    override_moderator_user,
):
    comment = Comment(
        id=1,
        user_id=1,
        photo_id=1,
        text="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(comment)
    await db_session.flush()

    response = await async_client.delete("/comments/1")

    assert response.status_code == 204

    deleted = await db_session.get(Comment, 1)
    assert deleted is None

@pytest.mark.asyncio
async def test_admin_can_delete_other_users_comment(
    async_client,
    db_session,
    override_admin_user,
):
    comment = Comment(
        id=1,
        user_id=1,
        photo_id=1,
        text="Original",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(comment)
    await db_session.flush()

    response = await async_client.delete("/comments/1")

    assert response.status_code == 204

    deleted = await db_session.get(Comment, 1)
    assert deleted is None