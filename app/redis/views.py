import asyncio

from sqlalchemy import update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import BlogTable
from app.database import engine
from app.redis import client
from app.settings import Settings


async def record_view(blog_id: int, ip: str) -> None:
    seen_key = f"blog:view:seen:{blog_id}:{ip}"
    is_new = await client.set(
        seen_key, 1, nx=True, ex=Settings.REDIS_VIEW_FLUSH_INTERVAL
    )
    if is_new:
        await client.incr(f"blog:views:{blog_id}")


async def get_buffered_views(blog_id: int) -> int:
    val = await client.get(f"blog:views:{blog_id}")
    return int(val) if val else 0


async def get_buffered_views_many(blog_ids: list[int]) -> dict[int, int]:
    if not blog_ids:
        return {}
    keys = [f"blog:views:{bid}" for bid in blog_ids]
    values = await client.mget(*keys)
    return {bid: int(val) if val else 0 for bid, val in zip(blog_ids, values)}


async def _flush() -> None:
    async with AsyncSession(engine) as db:
        async for key in client.scan_iter("blog:views:*"):
            flushed = await client.getdel(key)
            if not flushed:
                continue
            blog_id = int(key.split(":")[-1])
            await db.exec(
                update(BlogTable)
                .where(BlogTable.id == blog_id)
                .values(views=BlogTable.views + int(flushed))
            )
        await db.commit()


async def flush_views_loop() -> None:
    while True:
        await asyncio.sleep(Settings.REDIS_VIEW_FLUSH_INTERVAL)
        await _flush()
