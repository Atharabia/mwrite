from fastapi import APIRouter

from . import images


class RoutersRegistry:
    router = APIRouter()

    @classmethod
    def register_routers(cls) -> APIRouter:
        cls.router.include_router(images.router)
        return cls.router
