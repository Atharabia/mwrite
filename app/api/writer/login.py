from fastapi import APIRouter
from fastapi import Request
from fastapi import Response as HTTPResponse

from app.dependencies.admin_auth import WriterAuth
from app.middleware.rate_limiter import limiter
from app.models.responses import Response
from app.models.responses import Status
from app.models.schemas import LoginRequest
from app.controller import WriterController
from app.settings import Settings


router = APIRouter(tags=["Writer"])


@router.post("/login", response_model=Response)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest,
                http_response: HTTPResponse) -> Response:
    writer = await WriterController.get_writer(email=body.email)

    password = body.password.get_secret_value()
    if not writer or not WriterAuth.verify_password(password, writer.password):
        return Response(status=Status.FAILURE, code="INVALID_LOGIN")

    token_data = {"sub": writer.email}

    access_token = WriterAuth.create_token(
        token_data, Settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    http_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=Settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return Response(status=Status.success)


@router.post("/logout")
async def logout(http_response: HTTPResponse) -> Response:
    http_response.delete_cookie("access_token", path="/", samesite="lax")
    return Response(status=Status.success)
