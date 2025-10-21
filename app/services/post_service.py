import asyncio
import hashlib
from app.helpers.web_fetcher import fetch_news_rss
from app.services.genai_service import generate_linkedin_post
from app.services.embedding_service import embed_texts
from app.helpers.pinecone_helper import upsert_vectors
from app.helpers.db_helper import save_post, mark_post_as_posted, get_post_by_id
from app.configs.database import AsyncSessionLocal
from app.helpers.linkedin_poster import post_to_linkedin


async def create_post_flow(topic: str, length: str = "short", auto_post: bool = False):
    
    news = await fetch_news_rss(topic, max_items=5)
    snippets = [(n.get("title", "") + " - " + n.get("summary", "")) for n in news]
    
    if not snippets:
        snippets = [f"Latest insights about {topic}"]

    loop = asyncio.get_event_loop()
    gen_result = await loop.run_in_executor(None, generate_linkedin_post, topic, snippets, length)
    
    content = gen_result["content"]
    summary = gen_result.get("summary") or (snippets[0] if snippets else "")

    if not isinstance(content, str):
        content = str(content)
    if not isinstance(summary, str):
        summary = str(summary)

    embeddings = await embed_texts([content])
    embedding = embeddings[0]
    
    if not isinstance(embedding, list):
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        else:
            embedding = list(embedding)
    
    embedding = [float(x) for x in embedding]

    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    post_id = f"post-{content_hash[:16]}"
    
    vecs_to_upsert = [(post_id, embedding, {"topic": topic})]
    await loop.run_in_executor(None, upsert_vectors, vecs_to_upsert)

    async with AsyncSessionLocal() as db:
        try:
            post = await save_post(
                db, topic, content, summary,
                [n.get("link") for n in news if n.get("link")],
                posted=0
            )
            
            if auto_post:
                resp = await loop.run_in_executor(None, post_to_linkedin, content)
                if resp and resp.get('success'):
                    await mark_post_as_posted(db, post.id)
                    post.posted = 1
            
            await db.commit()
            await db.refresh(post)
            
            return post
            
        except Exception as e:
            await db.rollback()
            raise


async def publish_existing_post(post_id: int):
    
    async with AsyncSessionLocal() as db:
        try:
            post = await get_post_by_id(db, post_id)
            if not post:
                raise ValueError('post not found')
            
            content = post.content
            if not isinstance(content, str):
                content = str(content)

            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, post_to_linkedin, content)
            
            if resp and resp.get('success'):
                await mark_post_as_posted(db, post.id)
                await db.commit()
                await db.refresh(post)
                return True
            else:
                return False
                
        except Exception as e:
            await db.rollback()
            raise