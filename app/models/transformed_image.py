from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TransformedImage(Base):
    __tablename__ = "transformed_images"

    id = Column(Integer, primary_key=True)
    photo_id = Column(ForeignKey("photos.id"), nullable=False)

    transformation = Column(Text)
    image_url = Column(String(500), nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    photo = relationship("Photo", back_populates="transformed_images")
    public_links = relationship("PublicLink", back_populates="transformed_image")