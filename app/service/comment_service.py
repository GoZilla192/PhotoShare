from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.roles import UserRole
from app.repository.comment_repository import CommentRepository
from app.repository.photos_repository import PhotoRepository


class CommentService:
    def __init__(self, session: AsyncSession,
                 comment_repo: CommentRepository,
                 photo_repo: PhotoRepository):
        self.session = session
        self.comments = comment_repo
        self.photos = photo_repo

    async def create(self, photo_id: int, user_id: int, text: str) -> Comment:
        # (опційно) перевірити що фото існує через photo_repo
        c = Comment(photo_id=photo_id, user_id=user_id, text=text)
        async with self.session.begin():
            await self.comments.add(c)
        return c

    async def update_text(self, comment_id: int, actor_user_id: int, new_text: str) -> Comment:
        c = await self.comments.get_by_id(comment_id)
        if not c:
            raise ValueError("Comment not found")
        if c.user_id != actor_user_id:
            raise PermissionError("Only owner can edit comment")
        c.text = new_text
        async with self.session.begin():
            await self.session.flush()
        return c

    async def delete(self, comment_id: int, actor_role: UserRole) -> None:
        c = await self.comments.get_by_id(comment_id)
        if not c:
            return
        if actor_role not in {UserRole.admin, UserRole.moderator}:
            raise PermissionError("Only admin/moderator can delete comments")
        async with self.session.begin():
            await self.comments.delete(c)

    async def list_for_photo(self, photo_id: int, limit: int = 50, offset: int = 0) -> list[Comment]:
        # Опційно: перевірка існування фото
        # photo = await self.photos.get_by_id(photo_id)
        # if not photo:
        #     raise ValueError("Photo not found")

        return await self.comments.list_for_photo(photo_id=photo_id, limit=limit, offset=offset)

    async def list_for_user(
            self,
            target_user_id: int,
            actor_user_id: int | None = None,
            actor_role: UserRole | None = None,
            limit: int = 50,
            offset: int = 0,
            is_public: bool = True,
    ) -> list[Comment]:
        if not is_public:
            # приватний режим: тільки власник або admin/moder
            if actor_user_id != target_user_id and actor_role not in {UserRole.admin, UserRole.moderator}:
                raise PermissionError("Not allowed to view user's comments")

        return await self.comments.list_for_user(user_id=target_user_id, limit=limit, offset=offset)