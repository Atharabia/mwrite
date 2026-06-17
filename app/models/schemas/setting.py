from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic import SecretStr

from app.models.enums import Role


class SettingsUpdate(BaseModel):
    blog_name: str | None = Field(default=None, max_length=200)
    blog_description: str | None = Field(default=None, max_length=500)
    blog_author: str | None = Field(default=None, max_length=200)
    blog_tagline: str | None = Field(default=None, max_length=200)
    footer_text: str | None = Field(default=None, max_length=500)
    posts_per_page: int | None = Field(default=None, ge=1, le=100)
    allow_indexing: bool | None = None
    og_image_id: str | None = Field(default=None, max_length=36)


class SettingsPublic(BaseModel):
    blog_name: str
    blog_description: str
    blog_author: str
    blog_tagline: str
    footer_text: str
    posts_per_page: int
    allow_indexing: bool
    og_image_id: str

    @field_validator("posts_per_page", mode="before")
    @classmethod
    def coerce_posts_per_page(cls, v: object) -> int:
        return int(v)

    @field_validator("allow_indexing", mode="before")
    @classmethod
    def coerce_allow_indexing(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)


class AdminCreate(BaseModel):
    email: EmailStr
    password: SecretStr
    roles: list[Role] = Field(min_length=1)


class AdminUpdate(BaseModel):
    email: EmailStr | None = None
    password: SecretStr | None = None
    roles: list[Role] | None = None


class AdminPublic(BaseModel):
    id: int
    email: str
    roles: list[str]
    created_at: datetime
