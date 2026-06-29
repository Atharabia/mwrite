from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from slugify import slugify

from app.controller import BlogController
from app.dependencies import WriterAuth
from app.models.dto import BlogCreateDTO
from app.models.dto import BlogUpdateDTO
from app.models.responses import Response
from app.models.responses import Status
from app.models.schemas import BlogCreate
from app.models.schemas import BlogPublic
from app.models.schemas import BlogUpdate
from app.models.schemas import WriterPublic
from app.redis.views import get_buffered_views_many

router = APIRouter(tags=["Writer"])


@router.get("/get-blogs", response_model=Response)
async def get_blogs(
        writer: Annotated[WriterPublic,
                          Depends(WriterAuth.require_writer)]) -> Response:
    blogs = await BlogController.get_blogs()
    buffered = await get_buffered_views_many([b.id for b in blogs])
    return Response(status=Status.success,
                    data=[BlogPublic.model_validate(
                        {**b.model_dump(),
                         "views": b.views + buffered.get(b.id, 0)}
                    ) for b in blogs])


@router.post("/publish-blog", response_model=Response)
async def publish_blog(
        blog: BlogCreate,
        writer: Annotated[WriterPublic,
                          Depends(WriterAuth.require_writer)]) -> Response:
    created = await BlogController.publish_blog(
        blog=BlogCreateDTO(
            slug=slugify(blog.title),
            title=blog.title,
            content_delta=blog.content_delta,
            content_html=blog.content_html,
            content_text=blog.content_text,
            status=blog.status,
        ))
    return Response(status=Status.success,
                    data=BlogPublic.model_validate(created.model_dump()))


@router.patch("/update-blog/{blog_id}", response_model=Response)
async def update_blog(
        blog_id: int,
        update: BlogUpdate,
        writer: Annotated[WriterPublic,
                          Depends(WriterAuth.require_writer)]) -> Response:
    blog = await BlogController.update_blog(
        blog_id=blog_id,
        update=BlogUpdateDTO.model_validate(update.model_dump()))
    if blog is None:
        return Response(status=Status.FAILURE, code="BLOG_NOT_FOUND")
    return Response(status=Status.success,
                    data=BlogPublic.model_validate(blog.model_dump()))
