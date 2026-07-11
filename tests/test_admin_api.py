import pytest
import pytest_asyncio

from tests.conftest import make_token


@pytest.mark.asyncio
async def test_list_admins_requires_auth(client):
    r = await client.get("/api/writer/admins")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_admin_requires_auth(client):
    r = await client.post(
        "/api/writer/admins",
        json={"email": "x@x.com", "password": "pass"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_admin_requires_auth(client):
    r = await client.patch("/api/writer/admins/1", json={"email": "x@x.com"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_delete_admin_requires_auth(client):
    r = await client.delete("/api/writer/admins/1")
    assert r.status_code == 401


@pytest_asyncio.fixture(scope="module")
async def root_writer_id():
    from sqlmodel import select
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.database import WriterTable
    from app.database import engine

    async with AsyncSession(engine) as db:
        writer = (await db.exec(
            select(WriterTable).where(WriterTable.email == "root@test.com")
        )).first()
        if writer is None:
            writer = WriterTable(email="root@test.com", password="hash")
            db.add(writer)
            await db.commit()
            await db.refresh(writer)

        return writer.id


def _root_token(): return make_token("root@test.com")


@pytest.mark.asyncio
async def test_create_admin_duplicate_email(client, root_writer_id):
    payload = {"email": "dup@test.com", "password": "pass"}
    r = await client.post("/api/writer/admins", json=payload,
                          cookies={"access_token": _root_token()})
    assert r.json()["status"] == "SUCCESS"

    r = await client.post("/api/writer/admins", json=payload,
                          cookies={"access_token": _root_token()})
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_delete_self_blocked(client, root_writer_id):
    r = await client.delete(
        f"/api/writer/admins/{root_writer_id}",
        cookies={"access_token": _root_token()},
    )
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "CANNOT_DELETE_SELF"


@pytest.mark.asyncio
async def test_run_init_scripts_is_idempotent():
    from sqlmodel import select
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.database import WriterTable
    from app.database import engine
    from app.init import run_init_scripts
    from app.settings import Settings

    await run_init_scripts()
    await run_init_scripts()

    async with AsyncSession(engine) as db:
        writers = (await db.exec(
            select(WriterTable)
            .where(WriterTable.email == Settings.ADMIN_EMAIL)
        )).all()
    assert len(writers) == 1
