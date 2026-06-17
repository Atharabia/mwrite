import bcrypt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.controller.setting import SETTING_DEFAULTS
from app.database import WriterTable, RoleTable, WriterRoleTable, SettingTable, engine
from app.models.enums import Role
from app.settings import Settings

ROLE_NAMES = [Role.super_admin, Role.editor, Role.writer]


async def _seed_roles(db: AsyncSession) -> None:
    for role_name in ROLE_NAMES:
        existing = await db.exec(
            select(RoleTable).where(RoleTable.name == role_name))
        if existing.first() is None:
            db.add(RoleTable(name=role_name))


async def _seed_setting_defaults(db: AsyncSession) -> None:
    for key, value in SETTING_DEFAULTS.items():
        existing = await db.exec(
            select(SettingTable).where(SettingTable.key == key))
        if existing.first() is None:
            db.add(SettingTable(key=key, value=value))


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
        await _seed_setting_defaults(db)
        await _create_default_writer(db)
        await db.commit()
