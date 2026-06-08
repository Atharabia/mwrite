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
