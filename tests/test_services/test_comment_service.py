import pytest

from app.service.comment_service import CommentService
from app.repository.comment_repository import CommentRepository
from app.repository.photos_repository import PhotoRepository
from app.models.comment import Comment
from app.models.roles import UserRole


@pytest.mark.asyncio
async def test_comment_create(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    c = await service.create(photo_id=1, user_id=1, text="hello")

    assert c.id is not None
    assert c.text == "hello"

@pytest.mark.asyncio
async def test_update_comment_not_found(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    with pytest.raises(ValueError):
        await service.update_text(comment_id=999, actor_user_id=1, new_text="x")

@pytest.mark.asyncio
async def test_update_comment_not_owner(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comment = Comment(photo_id=1, user_id=1, text="old")
    db_session.add(comment)
    await db_session.flush()

    with pytest.raises(PermissionError):
        await service.update_text(comment.id, actor_user_id=2, new_text="new")

@pytest.mark.asyncio
async def test_update_comment_success(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comment = Comment(photo_id=1, user_id=1, text="old")
    db_session.add(comment)
    await db_session.flush()

    updated = await service.update_text(comment.id, actor_user_id=1, new_text="new")

    assert updated.text == "new"

@pytest.mark.asyncio
async def test_delete_comment_not_found(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    await service.delete(comment_id=999, actor_role=UserRole.admin)

@pytest.mark.asyncio
async def test_delete_comment_not_allowed(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comment = Comment(photo_id=1, user_id=1, text="test")
    db_session.add(comment)
    await db_session.flush()

    with pytest.raises(PermissionError):
        await service.delete(comment.id, actor_role=UserRole.user)

@pytest.mark.asyncio
async def test_delete_comment_success(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comment = Comment(photo_id=1, user_id=1, text="test")
    db_session.add(comment)
    await db_session.flush()

    await service.delete(comment.id, actor_role=UserRole.admin)

    deleted = await comment_repo.get_by_id(comment.id)
    assert deleted is None

@pytest.mark.asyncio
async def test_list_for_user_public(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comments = await service.list_for_user(
        target_user_id=1,
        actor_user_id=None,
        actor_role=None,
        is_public=True,
    )

    assert isinstance(comments, list)

@pytest.mark.asyncio
async def test_list_for_user_private_denied(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    with pytest.raises(PermissionError):
        await service.list_for_user(
            target_user_id=1,
            actor_user_id=2,
            actor_role=UserRole.user,
            is_public=False,
        )

@pytest.mark.asyncio
async def test_list_for_user_private_owner(db_session):
    comment_repo = CommentRepository(db_session)
    photos_repo = PhotoRepository(db_session)
    service = CommentService(db_session, comment_repo, photos_repo)

    comments = await service.list_for_user(
        target_user_id=1,
        actor_user_id=1,
        actor_role=UserRole.user,
        is_public=False,
    )

    assert isinstance(comments, list)