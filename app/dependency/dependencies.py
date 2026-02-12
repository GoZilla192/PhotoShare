from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.repository.comment_repository import CommentRepository
from app.repository.photos_repository import PhotoRepository
from app.repository.public_links_repository import PublicLinkRepository
from app.repository.ratings_repository import RatingRepository
from app.repository.tags_repository import TagRepository
from app.repository.token_repository import TokenBlacklistRepository
from app.repository.transformed_images_repository import TransformedImageRepository
from app.repository.users_repository import UserRepository

# services (domain)
from app.service.users_service import UserService
from app.service.photos_service import PhotoService
from app.service.tagging_service import TaggingService
from app.service.rating_service import RatingService
from app.service.comment_service import CommentService
from app.service.share_service import ShareService
from app.service.qr_service import QrService
from app.service.cloudinary_service import CloudinaryService

# auth canonical
from app.auth.service import AuthService

from app.core.settings import Settings


# --- Settings -----------------------------------------------------------------
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# --- DB session  --------------------------------------------------------------

async def get_session() -> AsyncIterator[AsyncSession]:
    async for s in get_async_session():
        yield s

# --- Repositories --------------------------------------------------------------

def users_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

def photos_repo(session: AsyncSession = Depends(get_session)) -> PhotoRepository:
    return PhotoRepository(session)

def tags_repo(session: AsyncSession = Depends(get_session)) -> TagRepository:
    return TagRepository(session)

def ratings_repo(session: AsyncSession = Depends(get_session)) -> RatingRepository:
    return RatingRepository(session)

def comments_repo(session: AsyncSession = Depends(get_session)) -> CommentRepository:
    return CommentRepository(session)

def public_links_repo(session: AsyncSession = Depends(get_session)) -> PublicLinkRepository:
    return PublicLinkRepository(session)

def transformed_images_repo(session: AsyncSession = Depends(get_session)) -> TransformedImageRepository:
    return TransformedImageRepository(session)

def token_blacklist_repo(session: AsyncSession = Depends(get_session)) -> TokenBlacklistRepository:
    return TokenBlacklistRepository(session)


# --- Infra services (Cloudinary / QR) -----------------------------------------

def cloudinary_service(settings: Settings = Depends(get_settings)) -> CloudinaryService:
    # ВАЖЛИВО: CloudinaryService має працювати від settings (api_key/secret/cloud_name тощо)
    return CloudinaryService(settings)

def qr_service() -> QrService:
    return QrService()

# --- Domain services -----------------------------------------------------------
def user_service(
    session: AsyncSession = Depends(get_session),
    user_repo: UserRepository = Depends(users_repo),
    photo_repo: PhotoRepository = Depends(photos_repo),
) -> UserService:
    return UserService(session=session, photos_repo=photo_repo, users_repo=user_repo)

def photo_service(
    session: AsyncSession = Depends(get_session),
    repo: PhotoRepository = Depends(photos_repo),
    cloud: CloudinaryService = Depends(cloudinary_service),
    tag_repo: TagRepository = Depends(tags_repo),
) -> PhotoService:
    return PhotoService(session=session, photos_repo=repo, cloudinary_client=cloud, tags_repo=tag_repo)

def tagging_service(
    session: AsyncSession = Depends(get_session),
    photo_repo: PhotoRepository = Depends(photos_repo),
    tag_repo: TagRepository = Depends(tags_repo),
) -> TaggingService:
    return TaggingService(session=session, photos_repo=photo_repo, tags_repo=tag_repo)

def rating_service(
    session: AsyncSession = Depends(get_session)
) -> RatingService:
    ratings_repo = RatingRepository(session)
    photos_repo = PhotoRepository(session)
    return RatingService(session=session, ratings_repo=ratings_repo, photos_repo=photos_repo)

def comment_service(
    session: AsyncSession = Depends(get_session),
    comments: CommentRepository = Depends(comments_repo),
    photos: PhotoRepository = Depends(photos_repo),
) -> CommentService:
    return CommentService(session=session, comment_repo=comments, photos_repo=photos)

def share_service(
    session: AsyncSession = Depends(get_session),
    photos: PhotoRepository = Depends(photos_repo),
    transformed: TransformedImageRepository = Depends(transformed_images_repo),
    links: PublicLinkRepository = Depends(public_links_repo),
    cloud: CloudinaryService = Depends(cloudinary_service),
    qr_maker: QrService = Depends(qr_service),
) -> ShareService:
    return ShareService(
        session=session,
        photos_repo=photos,
        transformed_repo=transformed,
        public_links_repo=links,
        cloudinary=cloud,
        qr_maker=qr_maker,
    )

# --- Auth (canonical: app/auth/* only) ----------------------------------------

def auth_service(
    session: AsyncSession = Depends(get_session),
    users: UserRepository = Depends(users_repo),
    blacklist: TokenBlacklistRepository = Depends(token_blacklist_repo),
    settings: Settings = Depends(get_settings)
) -> AuthService:
    return AuthService(session=session, users=users, blacklist=blacklist, settings=settings)