from fastapi import APIRouter

from . import blog
from . import image
from . import login


class RoutersRegistry:
    router = APIRouter(prefix="/writer")

    @classmethod
    def register_routers(cls) -> APIRouter:
        cls.router.include_router(login.router)
        cls.router.include_router(blog.router)
        cls.router.include_router(image.router)
        return cls.router
