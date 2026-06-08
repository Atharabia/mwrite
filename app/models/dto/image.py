from datetime import datetime

from pydantic import BaseModel


class ImageDTO(BaseModel):
    id: str
    data: bytes
    mime_type: str
    created_at: datetime
