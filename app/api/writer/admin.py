from typing import Annotated

from fastapi import APIRouter, Depends

from app.controller.writer import WriterController
from app.dependencies import require_super_admin, WriterAuth
from app.models.responses import Response, Status
from app.models.schemas import AdminCreate, AdminUpdate, AdminPublic, WriterPublic


router = APIRouter(
    prefix="/admins",
    tags=["Writer"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("", response_model=Response)
async def list_admins() -> Response:
    writers = await WriterController.list_writers()
    data = [AdminPublic(id=w.id, email=w.email, roles=w.roles,
                        created_at=w.created_at).model_dump(mode="json")
            for w in writers]
    return Response(status=Status.success, data=data)


@router.post("", response_model=Response)
async def create_admin(body: AdminCreate) -> Response:
    try:
        writer = await WriterController.create_writer(
            email=body.email,
            plain_password=body.password.get_secret_value(),
            role_names=body.roles,
        )
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    return Response(status=Status.success,
                    data=AdminPublic(id=writer.id, email=writer.email,
                                    roles=writer.roles,
                                    created_at=writer.created_at).model_dump(mode="json"))


@router.patch("/{writer_id}", response_model=Response)
async def update_admin(
    writer_id: int,
    body: AdminUpdate,
) -> Response:
    try:
        writer = await WriterController.update_writer(
            writer_id=writer_id,
            email=body.email,
            plain_password=body.password.get_secret_value() if body.password else None,
            role_names=body.roles,
        )
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    if writer is None:
        return Response(status=Status.FAILURE, code="WRITER_NOT_FOUND")
    return Response(status=Status.success,
                    data=AdminPublic(id=writer.id, email=writer.email,
                                    roles=writer.roles,
                                    created_at=writer.created_at).model_dump(mode="json"))


@router.delete("/{writer_id}", response_model=Response)
async def delete_admin(
    writer_id: int,
    current_writer: Annotated[WriterPublic, Depends(WriterAuth.require_writer)],
) -> Response:
    try:
        await WriterController.delete_writer(
            writer_id=writer_id,
            current_writer_id=current_writer.id,
        )
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    return Response(status=Status.success)
