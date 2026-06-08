from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import Response

from app.controller import ImageController


router = APIRouter(tags=["General"])


@router.get("/images/{image_id}")
async def serve_image(image_id: str) -> Response:
    image = await ImageController.get_image(image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404)
    return Response(content=image.data, media_type=image.mime_type)
