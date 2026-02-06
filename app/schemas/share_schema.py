from pydantic import BaseModel, Field


class ShareCreateRequest(BaseModel):
    transformation: str | None = Field(default=None, description="Transformation preset or params string")


class ShareCreateResponse(BaseModel):
    uuid: str
    public_url: str
    qr_code_url: str | None = None
    transformed_image_url: str | None = None