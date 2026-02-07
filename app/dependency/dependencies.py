# app/dependencies.py
from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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
from app.service.photos_service import PhotoService
from app.service.tagging_service import TaggingService
from app.service.rating_service import RatingService
from app.service.comment_service import CommentService
from app.service.share_service import ShareService
from app.service.qr_service import QrService
from app.service.cloudinary_service import CloudinaryService

# auth canonical
from app.auth.service import AuthService
from app.settings import Settings


# --- Settings -----------------------------------------------------------------
def get_settings() -> Settings:
    return Settings()

# --- DB session  --------------------------------------------------------------

async def get_session() -> AsyncIterator[AsyncSession]:
    async for s in get_async_session():
        yield s

# --- Repositories --------------------------------------------------------------

def users_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)

def photos_repo(session: AsyncSession) -> PhotoRepository:
    return PhotoRepository(session)

def tags_repo(session: AsyncSession) -> TagRepository:
    return TagRepository(session)

def ratings_repo(session: AsyncSession) -> RatingRepository:
    return RatingRepository(session)

def comments_repo(session: AsyncSession) -> CommentRepository:
    return CommentRepository(session)

def public_links_repo(session: AsyncSession) -> PublicLinkRepository:
    return PublicLinkRepository(session)

def transformed_images_repo(session: AsyncSession) -> TransformedImageRepository:
    return TransformedImageRepository(session)

def token_blacklist_repo(session: AsyncSession) -> TokenBlacklistRepository:
    return TokenBlacklistRepository(session)


# --- Infra services (Cloudinary / QR) -----------------------------------------

def cloudinary_service(settings: Settings) -> CloudinaryService:
    # ВАЖЛИВО: CloudinaryService має працювати від settings (api_key/secret/cloud_name тощо)
    return CloudinaryService(settings)

CloudinaryServiceDep = Annotated[CloudinaryService, Depends(cloudinary_service)]


def qr_service() -> QrService:
    return QrService()

QrServiceDep = Annotated[QrService, Depends(qr_service)]


# --- Domain services -----------------------------------------------------------

def photo_service(
    session: AsyncSession,
    repo: PhotoRepository,
    cloud: CloudinaryServiceDep,
) -> PhotoService:
    return PhotoService(session=session, photos_repo=repo, cloudinary_client=cloud)

def tagging_service(
    session: AsyncSession,
    photo_repo: PhotoRepository,
    tag_repo: TagRepository,
) -> TaggingService:
    return TaggingService(session=session, photos_repo=photo_repo, tags_repo=tag_repo)


def rating_service(
    session: AsyncSession,
    ratings: RatingRepository,
    photos: PhotoRepository,
) -> RatingService:
    return RatingService(session=session, ratings_repo=ratings, photos_repo=photos)

def comment_service(
    session: AsyncSession,
    comments: CommentRepository,
    photos: PhotoRepository,
) -> CommentService:
    return CommentService(session=session, comment_repo=comments, photos_repo=photos)

def share_service(
    session: AsyncSession,
    photos: PhotoRepository,
    transformed: TransformedImageRepository,
    links: PublicLinkRepository,
    cloud: CloudinaryServiceDep,
    qr_maker: QrServiceDep,
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # поправ під твій роут

def auth_service(
    users: UserRepository,
    blacklist: TokenBlacklistRepository,
) -> AuthService:
    return AuthService(users=users, blacklist=blacklist)

