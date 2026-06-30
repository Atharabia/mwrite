from fastapi import APIRouter

from . import admin as admin_users
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
        cls.router.include_router(admin_users.router)
        return cls.router
