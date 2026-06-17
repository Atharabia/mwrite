from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import WriterAuth
from app.models.enums import Role
from app.models.schemas import WriterPublic
from app.redis.settings import get_settings

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Writer Pages"])


@router.get("/settings", response_class=HTMLResponse, response_model=None)
async def settings_page(
    request: Request,
    writer: Annotated[WriterPublic | RedirectResponse,
                      Depends(WriterAuth.require_writer_page)],
) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, RedirectResponse):
        return writer
    if Role.super_admin not in writer.roles:
        return RedirectResponse(url="/writer", status_code=302)
    settings = await get_settings()
    return templates.TemplateResponse("writer/html/settings.html",
                                      {"request": request, "writer": writer,
                                       "settings": settings})
