from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    photo_id = Column(ForeignKey("photos.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    photo = relationship("Photo", back_populates="comments")
    user = relationship("User", back_populates="comments")