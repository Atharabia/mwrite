import pytest
import pytest_asyncio

from app.models.enums import Role
from tests.conftest import make_token

_non_admin_token = lambda: make_token("user@test.com", [])


@pytest_asyncio.fixture(autouse=True, scope="module")
async def create_tables():
    from sqlmodel import SQLModel

    from app.database import engine
    async with engine.begin() as conn:
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
