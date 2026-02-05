from app.models.comment import Comment
from app.models.roles import UserRole
from app.repository.comments import CommentRepository
from app.exceptions import PermissionDeniedError, CommentNotFoundError

class CommentService:
    def __init__(self, comment_repo: CommentRepository) -> None:
        self._comment_repo = comment_repo

    async def create_comment(self, photo_id: int, user_id: int, text: str) -> Comment:
        comment = Comment(
            photo_id=photo_id,
            user_id=user_id,
            text=text
        )
        return await self._comment_repo.create(comment)

    async def update_comment(self, comment_id: int, user_id: int, text: str) -> Comment:
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError()

        if comment.user_id != user_id:
            raise PermissionDeniedError()

        return await self._comment_repo.update_text(comment, text)

    async def delete_comment(self, comment_id: int, role: UserRole) -> None:
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError()

        if role not in (UserRole.admin, UserRole.moderator):
            raise PermissionDeniedError()

        await self._comment_repo.delete(comment)

    async def get_comments_for_photo(self, photo_id: int) -> list[Comment]:
        return await self._comment_repo.get_by_photo_id(photo_id)