from datetime import datetime

from pydantic import BaseModel
from pydantic import SecretStr


class LoginRequest(BaseModel):
    email: str
    password: SecretStr


class WriterPublic(BaseModel):
    id: int
    email: str


class AdminPublic(BaseModel):
    id: int
    email: str
    created_at: datetime


class AdminCreate(BaseModel):
    email: str
    password: SecretStr


class AdminUpdate(BaseModel):
    email: str | None = None
    password: SecretStr | None = None
