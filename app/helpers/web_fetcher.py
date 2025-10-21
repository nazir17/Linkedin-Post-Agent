import aiohttp
import feedparser
from typing import List, Dict
from bs4 import BeautifulSoup


async def fetch_news_rss(topic: str, max_items: int = 5) -> List[Dict]:
    try:
        url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                content = await response.text()
        
        feed = feedparser.parse(content)
        
        results = []
        for entry in feed.entries[:max_items]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", "")
            })
        
        return results
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []