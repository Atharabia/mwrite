from typing import Annotated

from fastapi import Cookie, HTTPException
from jose import jwt

from app.models.enums import Role
from app.settings import Settings


def _extract_roles(token: str | None) -> list[str]:
    if not token:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    try:
        payload = jwt.decode(token, Settings.JWT_SECRET_KEY,
                             algorithms=[Settings.JWT_ALGORITHM])
        return payload.get("roles", [])
    except Exception:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")


async def require_super_admin(
    access_token: Annotated[str | None, Cookie()] = None,
) -> list[str]:
    roles = _extract_roles(access_token)
    if Role.super_admin not in roles:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    return roles


async def require_editor_above(
    access_token: Annotated[str | None, Cookie()] = None,
) -> list[str]:
    roles = _extract_roles(access_token)
    if not {Role.super_admin, Role.editor} & set(roles):
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    return roles
