from datetime import datetime

from pydantic import BaseModel


class WriterDTO(BaseModel):
    id: int
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
