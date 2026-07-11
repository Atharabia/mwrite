import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import WriterTable
from app.database import engine
from app.settings import Settings


async def _create_default_writer(db: AsyncSession) -> None:
    if not Settings.ADMIN_EMAIL or not Settings.ADMIN_PASSWORD:
        return

    result = await db.exec(
        select(WriterTable).where(WriterTable.email == Settings.ADMIN_EMAIL))
    writer = result.first()

    if writer is None:
        hashed = bcrypt.hashpw(
            Settings.ADMIN_PASSWORD.encode(), bcrypt.gensalt()
        ).decode()
        writer = WriterTable(email=Settings.ADMIN_EMAIL, password=hashed)
        try:
            async with db.begin_nested():
                db.add(writer)
        except IntegrityError:
            pass


async def run_init_scripts() -> None:
    async with AsyncSession(engine) as db:
        await _create_default_writer(db)
        await db.commit()
