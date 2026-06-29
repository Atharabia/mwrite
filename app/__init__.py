import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import RoutersRegistry
from app.database import create_database_tables
from app.init import run_init_scripts
from app.middleware import MiddlewareRegistry
from app.pages import PagesRegistry
from app.redis.views import flush_views_loop
from app.settings import Settings
from app.templates import StaticRegistry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_database_tables()
    await run_init_scripts()
    task = asyncio.create_task(flush_views_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=Settings.APP_NAME,
    version=Settings.APP_VERSION,
    debug=Settings.APP_DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if Settings.APP_DEBUG else None,
    redoc_url="/redoc" if Settings.APP_DEBUG else None,
    openapi_url="/openapi.json" if Settings.APP_DEBUG else None,
)

MiddlewareRegistry.register_middlewares(app)
RoutersRegistry.register_routers(app)
PagesRegistry.register_routers(app)
StaticRegistry.register_static(app)
