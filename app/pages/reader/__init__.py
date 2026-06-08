from fastapi import APIRouter

from . import blog


class PagesRegistry:
    router = APIRouter()

    @classmethod
    def register_routers(cls) -> APIRouter:
        cls.router.include_router(blog.router)
        return cls.router
