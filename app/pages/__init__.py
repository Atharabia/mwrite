from fastapi import FastAPI

from .reader import PagesRegistry as ReaderRegistry
from .writer import PagesRegistry as WriterRegistry


class PagesRegistry:
    @staticmethod
    def register_routers(app: FastAPI) -> None:
        app.include_router(WriterRegistry.register_routers())
        app.include_router(ReaderRegistry.register_routers())
