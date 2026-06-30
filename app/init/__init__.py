import bcrypt
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import RoleTable
from app.database import WriterRoleTable
from app.database import WriterTable
from app.database import engine
from app.models.enums import Role
from app.settings import Settings

ROLE_NAMES = [Role.super_admin, Role.editor, Role.writer]


async def _seed_roles(db: AsyncSession) -> None:
    await db.execute(
        mysql_insert(RoleTable)
        .values([{"name": r} for r in ROLE_NAMES])
        .prefix_with("IGNORE")
    )


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
        db.add(writer)
        await db.flush()

    super_admin_role = await db.exec(
        select(RoleTable).where(RoleTable.name == Role.super_admin))
    role = super_admin_role.first()
    if role is None:
        return

    existing_assignment = await db.exec(
        select(WriterRoleTable).where(
            WriterRoleTable.writer_id == writer.id,
            WriterRoleTable.role_id == role.id,
        ))
    if existing_assignment.first() is None:
        db.add(WriterRoleTable(writer_id=writer.id, role_id=role.id))


async def run_init_scripts() -> None:
    async with AsyncSession(engine) as db:
        await _seed_roles(db)
        await db.flush()
        await _create_default_writer(db)
        await db.commit()
