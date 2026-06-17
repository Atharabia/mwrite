from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import SettingTable
from app.database import session
from app.models.dto import SettingDTO
from app.models.enums import SettingKey


SETTING_DEFAULTS: dict[str, str] = {
    SettingKey.blog_name: "Mwrite",
    SettingKey.blog_description: "",
    SettingKey.blog_author: "",
    SettingKey.blog_tagline: "",
    SettingKey.footer_text: "",
    SettingKey.posts_per_page: "10",
    SettingKey.allow_indexing: "true",
    SettingKey.og_image_id: "",
}

KNOWN_KEYS = set(k.value for k in SettingKey)


class SettingController:
    @staticmethod
    @session
    async def get(db: AsyncSession, *, key: str) -> str | None:
        result = await db.exec(
            select(SettingTable).where(SettingTable.key == key))
        row = result.first()
        return row.value if row else None

    @staticmethod
    @session
    async def set(db: AsyncSession, *, key: str, value: str) -> None:
        result = await db.exec(
            select(SettingTable).where(SettingTable.key == key))
        row = result.first()
        if row:
            row.value = value
            db.add(row)
        else:
            db.add(SettingTable(key=key, value=value))
        await db.commit()

    @staticmethod
    @session
    async def get_all(db: AsyncSession) -> dict[str, str]:
        result = await db.exec(select(SettingTable))
        rows = result.all()
        settings = dict(SETTING_DEFAULTS)
        for row in rows:
            if row.key in KNOWN_KEYS:
                settings[row.key] = row.value
        return settings
