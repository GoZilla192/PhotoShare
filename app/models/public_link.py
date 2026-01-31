from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PublicLink(Base):
    __tablename__ = "public_links"

    id = Column(Integer, primary_key=True)
    transformed_image_id = Column(
        ForeignKey("transformed_images.id"),
        nullable=False
    )

    uuid = Column(String(36), unique=True, nullable=False)
    qr_code_url = Column(String(500), nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    transformed_image = relationship("TransformedImage", back_populates="public_links")