from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from app.controller.writer import WriterController
from app.dependencies import WriterAuth
from app.models.responses import Response
from app.models.responses import Status
from app.models.schemas import AdminCreate
from app.models.schemas import AdminPublic
from app.models.schemas import AdminUpdate
from app.models.schemas import WriterPublic

router = APIRouter(
    prefix="/admins",
    tags=["Writer"],
    dependencies=[Depends(WriterAuth.require_writer)],
)


@router.get("", response_model=Response)
async def list_admins() -> Response:
    writers = await WriterController.list_writers()
    data = [AdminPublic(id=w.id, email=w.email,
                        created_at=w.created_at).model_dump(mode="json")
            for w in writers]
    return Response(status=Status.success, data=data)


@router.post("", response_model=Response)
async def create_admin(body: AdminCreate) -> Response:
    try:
        writer = await WriterController.create_writer(
            email=body.email,
            hashed_password=WriterAuth.hash_password(
                body.password.get_secret_value()
            ),
        )
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    return Response(
        status=Status.success,
        data=AdminPublic(
            id=writer.id, email=writer.email,
            created_at=writer.created_at,
        ).model_dump(mode="json"),
    )


@router.patch("/{writer_id}", response_model=Response)
async def update_admin(
    writer_id: int,
    body: AdminUpdate,
) -> Response:
    hashed_password = (
        WriterAuth.hash_password(body.password.get_secret_value())
        if body.password else None
    )
    try:
        writer = await WriterController.update_writer(
            writer_id=writer_id,
            email=body.email,
            hashed_password=hashed_password,
        )
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    if writer is None:
        return Response(status=Status.FAILURE, code="WRITER_NOT_FOUND")
    return Response(
        status=Status.success,
        data=AdminPublic(
            id=writer.id, email=writer.email,
            created_at=writer.created_at,
        ).model_dump(mode="json"),
    )


@router.delete("/{writer_id}", response_model=Response)
async def delete_admin(
    writer_id: int,
    current_writer: Annotated[
        WriterPublic, Depends(WriterAuth.require_writer)
    ],
) -> Response:
    try:
        if writer_id == current_writer.id:
            raise ValueError("CANNOT_DELETE_SELF")

        await WriterController.delete_writer(writer_id=writer_id)
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    return Response(status=Status.success)
