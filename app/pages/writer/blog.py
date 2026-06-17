from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.controller import BlogController
from app.dependencies import WriterAuth
from app.models.schemas import WriterPublic
from app.redis.settings import get_settings

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Writer Pages"])


@router.get("/", response_class=HTMLResponse, response_model=None)
async def dashboard(request: Request,
                    writer: Annotated[WriterPublic | RedirectResponse,
                                      Depends(WriterAuth.require_writer_page)],
                    ) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, RedirectResponse):
        return writer
    settings = await get_settings()
    return templates.TemplateResponse("writer/html/index.html",
                                      {"request": request, "writer": writer,
                                       "settings": settings})


@router.get("/new", response_class=HTMLResponse, response_model=None)
async def new_post(request: Request,
                   writer: Annotated[WriterPublic | RedirectResponse,
                                     Depends(WriterAuth.require_writer_page)],
                   ) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, RedirectResponse):
        return writer
    settings = await get_settings()
    return templates.TemplateResponse("writer/html/new-post.html",
                                      {"request": request, "writer": writer,
                                       "settings": settings})


@router.get("/edit/{blog_id}",
            response_class=HTMLResponse,
            response_model=None)
async def edit_post(request: Request,
                    blog_id: int,
                    writer: Annotated[WriterPublic | RedirectResponse,
                                      Depends(WriterAuth.require_writer_page)],
                    ) -> HTMLResponse | RedirectResponse:
    if isinstance(writer, RedirectResponse):
        return writer
    blog = await BlogController.get_blog(blog_id=blog_id)
    if blog is None:
        return RedirectResponse(url="/writer", status_code=302)
    settings = await get_settings()
    return templates.TemplateResponse("writer/html/edit-post.html",
                                      {"request": request,
                                       "blog": blog.model_dump(mode="json"),
                                       "writer": writer,
                                       "settings": settings})
