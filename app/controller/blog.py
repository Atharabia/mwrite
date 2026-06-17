from datetime import datetime, timezone
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import BlogTable
from app.database import session
from app.models.dto import BlogReaderDTO, BlogCreateDTO, BlogDTO, BlogUpdateDTO
from app.models.enums import BlogStatus


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BlogController:
    @staticmethod
    @session
    async def get_blogs(db: AsyncSession) -> list[BlogDTO]:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.deleted_at.is_(None))
            .order_by(BlogTable.created_at.desc()))
        rows = result.all()
        return [BlogDTO.model_validate(row, from_attributes=True) for row in rows]

    @staticmethod
    @session
    async def get_blog(db: AsyncSession, *, blog_id: int) -> BlogDTO | None:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.id == blog_id, BlogTable.deleted_at.is_(None)))
        row = result.first()
        if row is None:
            return None
        return BlogDTO.model_validate(row, from_attributes=True)

    @staticmethod
    @session
    async def get_published_blogs(db: AsyncSession) -> list[BlogReaderDTO]:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.status == BlogStatus.published,
                   BlogTable.deleted_at.is_(None))
            .order_by(BlogTable.created_at.desc()))
        rows = result.all()
        return [BlogReaderDTO(id=row.id, slug=row.slug, title=row.title,
                              content=row.content_html, views=row.views,
                              created_at=row.created_at)
                for row in rows]

    @staticmethod
    @session
    async def get_published_blogs_page(
        db: AsyncSession, *, page: int, size: int,
    ) -> tuple[list[BlogReaderDTO], int]:
        base = (select(BlogTable)
                .where(BlogTable.status == BlogStatus.published,
                       BlogTable.deleted_at.is_(None))
                .order_by(BlogTable.created_at.desc()))

        total = (await db.exec(
            select(func.count()).select_from(base.subquery())
        )).one()

        rows = (await db.exec(
            base.offset((page - 1) * size).limit(size))).all()

        blogs = [BlogReaderDTO(id=r.id, slug=r.slug, title=r.title,
                               content=r.content_html, views=r.views,
                               created_at=r.created_at)
                 for r in rows]
        return blogs, total

    @staticmethod
    @session
    async def get_published_blog(db: AsyncSession, *, slug: str) -> BlogReaderDTO | None:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.slug == slug,
                   BlogTable.status == BlogStatus.published,
                   BlogTable.deleted_at.is_(None)))
        row = result.first()
        if row is None:
            return None
        return BlogReaderDTO(id=row.id, slug=row.slug, title=row.title,
                             content=row.content_html, views=row.views,
                             created_at=row.created_at)

    @staticmethod
    @session
    async def publish_blog(db: AsyncSession, *, blog: BlogCreateDTO) -> BlogDTO:
        row = BlogTable(**blog.model_dump())
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return BlogDTO.model_validate(row, from_attributes=True)

    @staticmethod
    @session
    async def update_blog(
        db: AsyncSession, *, blog_id: int, update: BlogUpdateDTO
    ) -> BlogDTO | None:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.id == blog_id, BlogTable.deleted_at.is_(None)))
        row = result.first()
        if row is None:
            return None
        for field, value in update.model_dump(exclude_none=True).items():
            setattr(row, field, value)
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return BlogDTO.model_validate(row, from_attributes=True)

    @staticmethod
    @session
    async def soft_delete_blog(
        db: AsyncSession, *, blog_id: int, deleted_by: int
    ) -> bool:
        result = await db.exec(
            select(BlogTable)
            .where(BlogTable.id == blog_id, BlogTable.deleted_at.is_(None)))
        row = result.first()
        if row is None:
            return False
        row.deleted_at = _utc_now()
        row.deleted_by = deleted_by
        db.add(row)
        await db.commit()
        return True
