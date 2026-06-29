from fastapi import FastAPI

from .general import RoutersRegistry as GeneralRegistry
from .reader import RoutersRegistry as ReaderRegistry
from .writer import RoutersRegistry as WriterRegistry


class RoutersRegistry:
    @staticmethod
    def register_routers(app: FastAPI) -> None:
        app.include_router(WriterRegistry.register_routers())
        app.include_router(ReaderRegistry.register_routers())
        app.include_router(GeneralRegistry.register_routers())
