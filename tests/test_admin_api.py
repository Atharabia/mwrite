import pytest
import pytest_asyncio

from app.models.enums import Role
from tests.conftest import make_token


def _non_admin_token(): return make_token("user@test.com", [])


@pytest_asyncio.fixture(autouse=True, scope="module")
async def create_tables():
    from sqlmodel import SQLModel

    from app.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_get_writer_roles_returns_empty_for_unknown_writer():
    from app.controller.writer import WriterController
    roles = await WriterController.get_writer_roles(writer_id=99999)
    assert roles == []


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


@pytest.mark.asyncio
async def test_list_admins_requires_super_admin_role(client):
    token = _non_admin_token()
    r = await client.get("/api/writer/admins", cookies={"access_token": token})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_admin_requires_super_admin_role(client):
    token = _non_admin_token()
    r = await client.post(
        "/api/writer/admins",
        json={"email": "x@x.com", "password": "pass"},
        cookies={"access_token": token},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_admin_requires_super_admin_role(client):
    token = _non_admin_token()
    r = await client.patch(
        "/api/writer/admins/1",
        json={"email": "x@x.com"},
        cookies={"access_token": token},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_admin_requires_super_admin_role(client):
    token = _non_admin_token()
    r = await client.delete(
        "/api/writer/admins/1",
        cookies={"access_token": token},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_admin_rejects_invalid_role(client):
    token = make_token("admin@test.com", [Role.super_admin])
    r = await client.post(
        "/api/writer/admins",
        json={"email": "x@x.com", "password": "pass", "roles": ["hacker"]},
        cookies={"access_token": token},
    )
    assert r.status_code == 422


@pytest_asyncio.fixture(scope="module")
async def super_admin_id(create_tables):
    from sqlmodel import select
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.database import RoleTable
    from app.database import WriterRoleTable
    from app.database import WriterTable
    from app.database import engine

    async with AsyncSession(engine) as db:
        role = (await db.exec(
            select(RoleTable).where(RoleTable.name == Role.super_admin)
        )).first()
        if role is None:
            role = RoleTable(name=Role.super_admin)
            db.add(role)
            await db.flush()

        writer = (await db.exec(
            select(WriterTable).where(WriterTable.email == "root@test.com")
        )).first()
        if writer is None:
            writer = WriterTable(email="root@test.com", password="hash")
            db.add(writer)
            await db.flush()

        assignment = (await db.exec(
            select(WriterRoleTable).where(
                WriterRoleTable.writer_id == writer.id,
                WriterRoleTable.role_id == role.id,
            )
        )).first()
        if assignment is None:
            db.add(WriterRoleTable(writer_id=writer.id, role_id=role.id))

        writer_id = writer.id
        await db.commit()
        return writer_id


def _root_token(): return make_token("root@test.com", [Role.super_admin])


@pytest.mark.asyncio
async def test_create_admin_duplicate_email(client, super_admin_id):
    payload = {"email": "dup@test.com", "password": "pass"}
    r = await client.post("/api/writer/admins", json=payload,
                          cookies={"access_token": _root_token()})
    assert r.json()["status"] == "SUCCESS"

    r = await client.post("/api/writer/admins", json=payload,
                          cookies={"access_token": _root_token()})
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_delete_self_blocked(client, super_admin_id):
    r = await client.delete(
        f"/api/writer/admins/{super_admin_id}",
        cookies={"access_token": _root_token()},
    )
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "CANNOT_DELETE_SELF"


@pytest.mark.asyncio
async def test_delete_last_super_admin_blocked(client, super_admin_id):
    r = await client.post(
        "/api/writer/admins",
        json={"email": "other@test.com", "password": "pass", "roles": []},
        cookies={"access_token": _root_token()},
    )
    assert r.json()["status"] == "SUCCESS"

    other_token = make_token("other@test.com", [Role.super_admin])
    r = await client.delete(
        f"/api/writer/admins/{super_admin_id}",
        cookies={"access_token": other_token},
    )
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "CANNOT_DELETE_LAST_SUPER_ADMIN"


@pytest.mark.asyncio
async def test_remove_last_super_admin_role_blocked(client, super_admin_id):
    r = await client.patch(
        f"/api/writer/admins/{super_admin_id}",
        json={"roles": []},
        cookies={"access_token": _root_token()},
    )
    assert r.json()["status"] == "FAILURE"
    assert r.json()["code"] == "CANNOT_REMOVE_LAST_SUPER_ADMIN"


@pytest.mark.asyncio
async def test_run_init_scripts_is_idempotent(super_admin_id):
    from sqlmodel import select
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.database import RoleTable
    from app.database import engine
    from app.init import run_init_scripts

    await run_init_scripts()
    await run_init_scripts()

    async with AsyncSession(engine) as db:
        names = (await db.exec(select(RoleTable.name))).all()
    assert sorted(names) == sorted(r.value for r in Role)
