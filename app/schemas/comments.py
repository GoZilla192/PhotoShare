from datetime import datetime
from pydantic import BaseModel, Field

class CommentCreateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class CommentUpdateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(BaseModel):
    id: int
    photo_id: int
    user_id: int
    text: str
    created_at: datetime
    updated_at: datetime