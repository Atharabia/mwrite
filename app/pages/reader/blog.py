from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.controller import BlogController
from app.redis.settings import get_settings
from app.redis.views import record_view

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Reader Pages"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    settings = await get_settings()
    return templates.TemplateResponse("reader/html/index.html",
                                      {"request": request, "settings": settings})


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def post(
    request: Request,
    slug: str,
    background_tasks: BackgroundTasks,
) -> HTMLResponse:
    blog = await BlogController.get_published_blog(slug=slug)
    if blog:
        ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.client.host
        )
        background_tasks.add_task(record_view, blog.id, ip)
    settings = await get_settings()
    return templates.TemplateResponse("reader/html/post.html",
                                      {"request": request, "blog": blog,
                                       "settings": settings})
