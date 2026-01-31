from sqlalchemy import Column, ForeignKey, Table
from app.database import Base

photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", ForeignKey("photos.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)