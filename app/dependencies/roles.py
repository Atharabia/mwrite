from typing import Annotated

from fastapi import Cookie
from fastapi import Depends
from fastapi import HTTPException
from jose import jwt

from app.models.enums import Role
from app.settings import Settings


def _extract_roles(token: str | None) -> list[str]:
    if not token:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    try:
        payload = jwt.decode(
            token, Settings.JWT_SECRET_KEY,
            algorithms=[Settings.JWT_ALGORITHM]
        )
        return payload.get("roles", [])
    except Exception:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")


def require_roles(*roles: Role):
    async def _check(
        access_token: Annotated[str | None, Cookie()] = None,
    ) -> list[str]:
        user_roles = _extract_roles(access_token)
        if not set(roles) & set(user_roles):
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        return user_roles
    return Depends(_check)


require_super_admin = require_roles(Role.super_admin)
