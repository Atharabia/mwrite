from pathlib import Path

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.controller import BlogController
from app.redis.views import record_view

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.parent / "templates")

router = APIRouter(tags=["Reader Pages"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("reader/html/index.html",
                                      {"request": request})


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def post(
    request: Request,
    slug: str,
    background_tasks: BackgroundTasks,
) -> HTMLResponse:
    blog = await BlogController.get_published_blog(slug=slug)
    if blog:
        client_host = request.client.host if request.client else "0.0.0.0"
        ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or client_host
        )
        background_tasks.add_task(record_view, blog.id, ip)
    return templates.TemplateResponse("reader/html/post.html",
                                      {"request": request, "blog": blog})
