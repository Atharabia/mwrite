from fastapi import APIRouter

from . import admin as admin_pages
from . import blog
from . import login


class PagesRegistry:
    router = APIRouter(prefix="/writer")

    @classmethod
    def register_routers(cls) -> APIRouter:
        cls.router.include_router(login.router)
        cls.router.include_router(blog.router)
        cls.router.include_router(admin_pages.router)
        return cls.router
