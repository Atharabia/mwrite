from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.models.enums import BlogStatus


class BlogCreate(BaseModel):
    title: str = Field(max_length=300)
    content_delta: str = Field(max_length=500_000)
    content_html: str = Field(max_length=500_000)
    content_text: str = Field(max_length=500_000)
    status: BlogStatus = BlogStatus.published


class BlogUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    content_delta: str | None = Field(default=None, max_length=500_000)
    content_html: str | None = Field(default=None, max_length=500_000)
    content_text: str | None = Field(default=None, max_length=500_000)
    status: BlogStatus | None = None


class BlogPublic(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    slug: str | None
    title: str
    content_delta: str
    content_html: str
    content_text: str
    status: BlogStatus
    views: int
    created_by: int | None = None
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime


class BlogPublicReader(BaseModel):
    id: int
    slug: str | None
    title: str
    content: str
    views: int
    created_at: datetime
