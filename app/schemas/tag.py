from pydantic import BaseModel, Field, ConfigDict


class TagOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PhotoTagsReadResponse(BaseModel):
    photo_id: int
    tags: list[str]


class PhotoTagsSetRequest(BaseModel):
    tags: list[str] = Field(default_factory=list,
                            description="Up to 5 tag names (case-insensitive)")
