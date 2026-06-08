import math
from typing import Annotated

from fastapi import APIRouter
from fastapi import Query

from app.controller import BlogController
from app.models.responses import Response
from app.models.responses import Status


router = APIRouter(tags=["Reader"])


@router.get("/get-blogs", response_model=Response)
async def get_blogs(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Response:
    blogs, total = await BlogController.get_published_blogs_page(page=page,
                                                                 size=size)
    return Response(status=Status.success, data={
        "items": blogs,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total else 0,
    })


@router.get("/get-blog/{slug}", response_model=Response)
async def get_blog(slug: str) -> Response:
    blog = await BlogController.get_published_blog(slug=slug)
    if blog is None:
        return Response(status=Status.FAILURE, code="BLOG_NOT_FOUND")
    return Response(status=Status.success, data=blog)
