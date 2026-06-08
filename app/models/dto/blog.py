from datetime import datetime

from pydantic import BaseModel

from app.models.enums import BlogStatus


class BlogCreateDTO(BaseModel):
    slug: str
    title: str
    content_delta: str
    content_html: str
    content_text: str
    status: BlogStatus = BlogStatus.published


class BlogUpdateDTO(BaseModel):
    title: str | None = None
    content_delta: str | None = None
    content_html: str | None = None
    content_text: str | None = None
    status: BlogStatus | None = None


class BlogDTO(BaseModel):
    id: int
    slug: str | None
    title: str
    content_delta: str
    content_html: str
    content_text: str
    status: BlogStatus
    views: int
    created_at: datetime
    updated_at: datetime


class BlogReaderDTO(BaseModel):
    id: int
    slug: str | None
    title: str
    content: str
    views: int
    created_at: datetime
