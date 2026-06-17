import functools
from collections.abc import Awaitable
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing_extensions import Concatenate
from typing_extensions import ParamSpec

from app.settings import Settings

from .tables import WriterTable
from .tables import BlogTable
from .tables import ImageTable
from .tables import SettingTable
from .tables import RoleTable
from .tables import WriterRoleTable


__all__ = [
    "WriterTable",
    "BlogTable",
    "ImageTable",
    "SettingTable",
    "RoleTable",
    "WriterRoleTable",
]


P = ParamSpec("P")
T = TypeVar("T")
engine: AsyncEngine = create_async_engine(Settings.DATABASE_URL,
                                          echo=Settings.APP_DEBUG)


async def create_database_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def session(
    func: Callable[Concatenate[AsyncSession, P], Awaitable[T]]
) -> Callable[P, Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        async with AsyncSession(engine) as session:
            result: T = await func(session, *args, **kwargs)
            return result
    return wrapper
