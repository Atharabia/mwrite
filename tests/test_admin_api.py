import pytest
import pytest_asyncio
from app.models.enums import Role


@pytest_asyncio.fixture(autouse=True, scope="module")
async def create_tables():
    from app.database import engine
    from sqlmodel import SQLModel
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_get_writer_roles_returns_empty_for_unknown_writer():
    from app.controller.writer import WriterController
    roles = await WriterController.get_writer_roles(writer_id=99999)
    assert roles == []
