import json
from typing import List
from app.models.post_model import Post
from sqlalchemy.ext.asyncio import AsyncSession


async def save_post(db: AsyncSession, topic: str, content: str, summary: str, source_urls: List[str], posted: int = 0):
    post = Post(
        topic=topic,
        content=content,
        summary=summary,
        source_urls=json.dumps(source_urls),
        posted=posted
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)

    try:
        post.source_urls = json.loads(post.source_urls)
    except:
        post.source_urls = []

    return post


async def mark_post_as_posted(db: AsyncSession, post_id: int):
    post = await db.get(Post, post_id)
    if post:
        post.posted = 1
        await db.flush()
        await db.refresh(post)

        try:
            post.source_urls = json.loads(post.source_urls) if isinstance(post.source_urls, str) else post.source_urls
        except:
            post.source_urls = []

        return post
    return None


async def get_post_by_id(db: AsyncSession, post_id: int):
    post = await db.get(Post, post_id)
    if post:
        try:
            post.source_urls = json.loads(post.source_urls) if isinstance(post.source_urls, str) else post.source_urls
        except:
            post.source_urls = []
    return post