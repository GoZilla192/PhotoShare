from __future__ import annotations

import json
import uuid as uuidlib
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import PublicLink
from app.repository.photos_repository import PhotoRepository
from app.repository.public_links_repository import PublicLinkRepository
from app.repository.transformed_images_repository import TransformedImageRepository
from app.service.cloudinary_service import CloudinaryService
from app.service.qr_service import QrService


class ShareService:
    def __init__(self,
                 session: AsyncSession,
                 photos_repo: PhotoRepository,
                 transformed_repo: TransformedImageRepository,
                 cloudinary: CloudinaryService,
                 public_links_repo: PublicLinkRepository,
                 qr_maker: QrService):
        self.session = session
        self.photos = photos_repo
        self.transformed = transformed_repo
        self.public_links = public_links_repo
        self.qr = qr_maker
        self.cloudinary = cloudinary

    async def create_share_link(self,
                                photo_id: int,
                                transform_params: dict,
                                current_user) -> str:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        # авторизацію тут “умовно пропускаємо”, але мінімум:
        # owner/admin (або будь-який залогінений — дискусійно)
        # if photo.user_id != current_user.id and current_user.role != UserRole.admin:
        #     raise PermissionDeniedError("Insufficient permissions")

        # сформувати URL трансформованого зображення (Cloudinary)
        transformed_url = self.cloudinary.build_transformed_url(
            public_id=photo.cloudinary_public_id,
            params=transform_params,
        )
        transformation_str = json.dumps(transform_params, ensure_ascii=False)

        public_uuid = str(uuidlib.uuid4())

        async with self.session.begin():
            ti = await self.transformed.create_for_photo(
                photo_id=photo.id,
                image_url=transformed_url,
                transformation=transformation_str,
            )

            link = PublicLink(
                uuid=public_uuid,
                transformed_image_id=ti.id,
            )
            await self.public_links.add(link)

        return public_uuid

    async def resolve_public(self, *, uuid: str) -> str:
        link = await self.public_links.get_by_uuid(uuid)
        if not link:
            raise NotFoundError("Public link not found")
        return link.transformed_image.url

    async def make_public_qr(self, *, uuid: str) -> str:
        url = f"/public/{uuid}"
        return self.qr.make_png_base64(url)
