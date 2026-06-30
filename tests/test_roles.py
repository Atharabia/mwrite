import pytest
from fastapi import HTTPException

from app.dependencies.roles import require_roles
from app.models.enums import Role
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_require_super_admin_passes_with_correct_role():
    token = make_token("admin@test.com", ["super_admin"])
    roles = await require_roles(Role.super_admin).dependency(
        access_token=token
    )
    assert "super_admin" in roles


@pytest.mark.asyncio
async def test_require_super_admin_raises_403_for_editor():
    token = make_token("editor@test.com", ["editor"])
    with pytest.raises(HTTPException) as exc:
        await require_roles(Role.super_admin).dependency(
            access_token=token
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_super_admin_raises_401_without_token():
    with pytest.raises(HTTPException) as exc:
        await require_roles(Role.super_admin).dependency(access_token=None)
    assert exc.value.status_code == 401
