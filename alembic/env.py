import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context
from app.database import BlogTable
from app.database import ImageTable
from app.database import SettingTable
from app.database import WriterTable
from app.settings import Settings

all_tables = [
    WriterTable,
    BlogTable,
    ImageTable,
    SettingTable,
]

config = context.config
config.set_main_option("sqlalchemy.url", Settings.DATABASE_URL)
target_metadata = SQLModel.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def compare_type(context, inspected_column, metadata_column,
                 inspected_type, metadata_type):
    # Dialects reflect generic types as their own concrete subtype (e.g.
    # MySQL always reports a LargeBinary column back as MEDIUMBLOB). Treat
    # same-family types as equal so this doesn't show up as a diff forever.
    if inspected_type._type_affinity is metadata_type._type_affinity:
        return False
    return None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
