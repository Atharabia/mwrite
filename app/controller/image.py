import base64
import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import ImageTable
from app.database import session
from app.models.dto import ImageDTO


class ImageController:
    @staticmethod
    @session
    async def save_image(db: AsyncSession, *, data_url: str) -> str:
        try:
            header, encoded = data_url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            data = base64.b64decode(encoded)
        except Exception as exc:
            raise ValueError("Invalid image data") from exc
        image_id = str(uuid.uuid4())
        row = ImageTable(id=image_id, data=data, mime_type=mime_type)
        db.add(row)
        await db.commit()
        return image_id

    @staticmethod
    @session
    async def get_image(db: AsyncSession, *, image_id: str) -> ImageDTO | None:
        result = await db.exec(
            select(ImageTable).where(ImageTable.id == image_id))
        row = result.first()
        if row is None:
            return None
        return ImageDTO.model_validate(row, from_attributes=True)
