import uuid
from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import Text
from sqlmodel import Field
from sqlmodel import SQLModel

from app.models.enums import BlogStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoleTable(SQLModel, table=True):
    __tablename__ = "role"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class WriterRoleTable(SQLModel, table=True):
    __tablename__ = "writer_role"
    writer_id: int = Field(foreign_key="writer.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)


class SettingTable(SQLModel, table=True):
    __tablename__ = "setting"
    key: str = Field(primary_key=True)
    value: str = Field()


class WriterTable(SQLModel, table=True):
    __tablename__ = "writer"

    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str = Field()

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now,
                                 sa_column_kwargs={"onupdate": utc_now})


class ImageTable(SQLModel, table=True):
    __tablename__ = "image"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                    primary_key=True)
    data: bytes = Field(
        sa_column=Column(LargeBinary(length=16_777_215), nullable=False),
    )
    mime_type: str = Field()

    created_at: datetime = Field(default_factory=utc_now)


class BlogTable(SQLModel, table=True):
    __tablename__ = "blog"

    id: int = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, unique=True, index=True)
    title: str = Field()
    content_delta: str = Field(default="", sa_type=Text)
    content_html: str = Field(default="", sa_type=Text)
    content_text: str = Field(default="", sa_type=Text)
    status: BlogStatus = Field(
        default=BlogStatus.draft,
        sa_column=Column(String(length=255), nullable=False),
    )
    views: int = Field(default=0)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now,
                                 sa_column_kwargs={"onupdate": utc_now})
