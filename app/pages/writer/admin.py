from pathlib import Path
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import WriterAuth
from app.models.enums import Role
from app.models.schemas import WriterPublic
from app.settings import Settings

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Writer Pages"])


@router.get("/admins", response_class=HTMLResponse, response_model=None)
async def admins_page(
    request: Request,
    writer: Annotated[WriterPublic | RedirectResponse,
                      Depends(WriterAuth.require_writer_page)],
) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, RedirectResponse):
        return writer
    if Role.super_admin not in writer.roles:
        return RedirectResponse(url="/writer", status_code=302)
    return templates.TemplateResponse("writer/html/admins.html",
                                      {"request": request, "writer": writer,
                                       "settings": Settings})
