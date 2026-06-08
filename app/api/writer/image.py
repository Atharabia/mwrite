from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from app.controller import ImageController
from app.dependencies import WriterAuth
from app.models.responses import Response
from app.models.responses import Status
from app.models.schemas import WriterPublic
from app.models.schemas import ImageUpload


router = APIRouter(tags=["Writer"])


@router.post("/upload-image", response_model=Response)
async def upload_image(
        body: ImageUpload,
        writer: Annotated[WriterPublic,
                          Depends(WriterAuth.require_writer)]) -> Response:
    try:
        image_id = await ImageController.save_image(data_url=body.data_url)
    except ValueError as e:
        return Response(status=Status.FAILURE, code=str(e))
    return Response(status=Status.success,
                    data={"url": f"/images/{image_id}"})
