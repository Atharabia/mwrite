from pathlib import Path
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import WriterAuth
from app.models.schemas import WriterPublic

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Writer Pages"])


@router.get("/login", response_class=HTMLResponse, response_model=None)
async def login_page(
    request: Request,
    writer: Annotated[WriterPublic | RedirectResponse,
                      Depends(WriterAuth.require_writer_page)],
) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, WriterPublic):
        return RedirectResponse(url="/writer", status_code=302)
    response = templates.TemplateResponse("writer/html/login.html",
                                          {"request": request})
    response.delete_cookie("access_token")
    return response
