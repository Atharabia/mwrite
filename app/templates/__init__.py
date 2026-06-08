from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class StaticRegistry:
    @staticmethod
    def register_static(app: FastAPI) -> None:
        app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).resolve().parent),
            name="static",
        )
