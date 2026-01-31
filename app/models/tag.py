from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.photo_tags import photo_tags


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    photos = relationship(
        "Photo",
        secondary=photo_tags,
        back_populates="tags"
    )