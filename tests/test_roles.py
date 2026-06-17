import pytest
from fastapi import HTTPException
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_require_super_admin_passes_with_correct_role():
    from app.dependencies.roles import require_super_admin
    token = make_token("admin@test.com", ["super_admin"])
    roles = await require_super_admin(access_token=token)
    assert "super_admin" in roles


@pytest.mark.asyncio
async def test_require_super_admin_raises_403_for_editor():
    from app.dependencies.roles import require_super_admin
    token = make_token("editor@test.com", ["editor"])
    with pytest.raises(HTTPException) as exc:
        await require_super_admin(access_token=token)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_super_admin_raises_401_without_token():
    from app.dependencies.roles import require_super_admin
    with pytest.raises(HTTPException) as exc:
        await require_super_admin(access_token=None)
    assert exc.value.status_code == 401
