from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import WriterTable
from app.database import session
from app.models.dto import WriterDTO


class WriterController:
    @staticmethod
    @session
    async def get_writer(db: AsyncSession, *, email: str) -> WriterDTO | None:
        result = await db.exec(select(WriterTable)
                               .where(WriterTable.email == email))
        row = result.first()

        if row is None:
            return None

        return WriterDTO(id=row.id, email=row.email, password=row.password,
                         created_at=row.created_at, updated_at=row.updated_at)

    @staticmethod
    @session
    async def list_writers(db: AsyncSession) -> list[WriterDTO]:
        writers_result = await db.exec(select(WriterTable))
        writers = writers_result.all()

        return [
            WriterDTO(id=w.id, email=w.email, password=w.password,
                      created_at=w.created_at, updated_at=w.updated_at)
            for w in writers
        ]

    @staticmethod
    @session
    async def create_writer(
        db: AsyncSession,
        *,
        email: str,
        hashed_password: str,
    ) -> WriterDTO:
        writer = WriterTable(email=email, password=hashed_password)
        db.add(writer)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("EMAIL_ALREADY_EXISTS") from exc

        await db.refresh(writer)

        return WriterDTO(id=writer.id, email=writer.email,
                         password=writer.password,
                         created_at=writer.created_at,
                         updated_at=writer.updated_at)

    @staticmethod
    @session
    async def update_writer(
        db: AsyncSession,
        *,
        writer_id: int,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> WriterDTO | None:
        result = await db.exec(select(WriterTable)
                               .where(WriterTable.id == writer_id))
        writer = result.first()

        if writer is None:
            return None

        if email is not None:
            writer.email = email

        if hashed_password is not None:
            writer.password = hashed_password

        db.add(writer)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("EMAIL_ALREADY_EXISTS") from exc

        await db.refresh(writer)

        return WriterDTO(id=writer.id, email=writer.email,
                         password=writer.password,
                         created_at=writer.created_at,
                         updated_at=writer.updated_at)

    @staticmethod
    @session
    async def delete_writer(
        db: AsyncSession,
        *,
        writer_id: int,
    ) -> None:
        writer = (await db.exec(
            select(WriterTable).where(WriterTable.id == writer_id)
        )).first()
        if writer:
            await db.delete(writer)

        await db.commit()
