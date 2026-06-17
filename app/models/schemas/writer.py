from pydantic import BaseModel
from pydantic import SecretStr


class LoginRequest(BaseModel):
    email: str
    password: SecretStr


class WriterPublic(BaseModel):
    id: int
    email: str
    roles: list[str] = []
