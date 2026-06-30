from datetime import datetime

from pydantic import BaseModel
from pydantic import SecretStr

from app.models.enums import Role


class LoginRequest(BaseModel):
    email: str
    password: SecretStr


class WriterPublic(BaseModel):
    id: int
    email: str
    roles: list[str] = []


class AdminPublic(BaseModel):
    id: int
    email: str
    roles: list[str] = []
    created_at: datetime


class AdminCreate(BaseModel):
    email: str
    password: SecretStr
    roles: list[Role] = []


class AdminUpdate(BaseModel):
    email: str | None = None
    password: SecretStr | None = None
    roles: list[Role] | None = None
