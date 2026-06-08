from fastapi import APIRouter

from . import blog, login, image


class RoutersRegistry:
    router = APIRouter(prefix="/writer")

    @classmethod
    def register_routers(cls) -> APIRouter:
        cls.router.include_router(login.router)
        cls.router.include_router(blog.router)
        cls.router.include_router(image.router)
        return cls.router
