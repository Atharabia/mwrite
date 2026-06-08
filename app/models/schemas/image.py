from pydantic import BaseModel
from pydantic import Field


class ImageUpload(BaseModel):
    data_url: str = Field(max_length=14_000_000)  # ~10 MB after base64 decode
