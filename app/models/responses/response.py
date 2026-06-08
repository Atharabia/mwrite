from enum import Enum
from typing import Any

from pydantic import BaseModel


class Status(Enum):
    success = "SUCCESS"
    FAILURE = "FAILURE"


class Response(BaseModel):
    status: Status
    code: str | None = None
    data: Any | None = None
