from fastapi import FastAPI

from .writer import RoutersRegistry as WriterRegistry
from .reader import RoutersRegistry as ReaderRegistry
from .general import RoutersRegistry as GeneralRegistry


class RoutersRegistry:
    @staticmethod
    def register_routers(app: FastAPI) -> None:
        app.include_router(WriterRegistry.register_routers())
        app.include_router(ReaderRegistry.register_routers())
        app.include_router(GeneralRegistry.register_routers())
