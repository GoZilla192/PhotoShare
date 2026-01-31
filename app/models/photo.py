from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.photo_tags import photo_tags


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    image_url = Column(String(500), nullable=False)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="photos")
    comments = relationship("Comment", back_populates="photo")
    ratings = relationship("Rating", back_populates="photo")
    transformed_images = relationship("TransformedImage", back_populates="photo")

    tags = relationship(
        "Tag",
        secondary=photo_tags,
        back_populates="photos"
    )