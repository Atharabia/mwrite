from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Annotated

import bcrypt
from fastapi import Cookie
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt

from app.controller import WriterController
from app.models.dto import WriterDTO
from app.models.schemas import WriterPublic
from app.settings import Settings


class WriterAuth:
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def create_token(data: dict, expires_minutes: int) -> str:
        payload = data.copy()
        payload["exp"] = (
            datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        )
        return jwt.encode(
            payload, Settings.JWT_SECRET_KEY, algorithm=Settings.JWT_ALGORITHM
        )

    @staticmethod
    async def _verify_token(
        token: str,
    ) -> tuple[WriterPublic | None, str | None]:
        try:
            payload = jwt.decode(
                token,
                Settings.JWT_SECRET_KEY,
                algorithms=[Settings.JWT_ALGORITHM],
            )
            email: str | None = payload.get("sub")
            expiration: int | None = payload.get("exp")

            if not email:
                return None, "INVALID_TOKEN"

            if expiration is None or (
                datetime.now(timezone.utc).timestamp() > expiration
            ):
                return None, "SESSION_EXPIRED"

        except Exception:
            return None, "INVALID_TOKEN"

        writer: WriterDTO | None = await WriterController.get_writer(
            email=email)

        if writer is None:
            return None, "INVALID_TOKEN"

        return WriterPublic(id=writer.id, email=writer.email), None

    @staticmethod
    async def require_writer(
        access_token: Annotated[str | None, Cookie()] = None,
    ) -> WriterPublic:
        if not access_token:
            raise HTTPException(status_code=401, detail="INVALID_TOKEN")
        writer, error = await WriterAuth._verify_token(access_token)
        if not writer:
            raise HTTPException(status_code=401, detail=error)
        return writer

    @staticmethod
    def _cleared_redirect() -> RedirectResponse:
        redirect = RedirectResponse(url="/writer/login", status_code=302)
        redirect.delete_cookie("access_token")
        return redirect

    @staticmethod
    async def require_writer_page(
        access_token: Annotated[str | None, Cookie()] = None,
    ) -> WriterPublic | RedirectResponse:
        if not access_token:
            return RedirectResponse(url="/writer/login", status_code=302)
        writer, _ = await WriterAuth._verify_token(access_token)
        if writer is None:
            return WriterAuth._cleared_redirect()
        return writer
