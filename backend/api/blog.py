"""
Blog fetcher: pulls real articles from company RSS/Atom feeds,
embeds them into ChromaDB, and persists metadata in SQLite.
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from agents.llm import generate_answer
from api.models import DailyBlog
from core.company_profiles import get_profile, get_blog_feeds
from rag.embed_store import store_article

logger = logging.getLogger(__name__)

RSS_TIMEOUT = 15  # seconds per feed request


def _parse_feed(xml_text: str) -> list[dict]:
    """Parse RSS or Atom XML and return list of {title, content, url, published}."""
    articles = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # RSS 2.0
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            if title and (desc or link):
                articles.append({"title": title, "content": desc or title, "url": link, "published": pub})

        # Atom 1.0
        if not articles:
            for entry in root.findall("atom:entry", ns):
                title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                link_el = entry.find("atom:link", ns)
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()
                content_el = entry.find("{http://www.w3.org/2005/Atom}content")
                content = (content_el.text or summary or title).strip() if content_el is not None else summary
                published = (entry.findtext("atom:published", namespaces=ns) or "").strip()
                if title and content:
                    articles.append({"title": title, "content": content, "url": link, "published": published})

    except ET.ParseError as e:
        logger.warning(f"Feed parse error: {e}")

    return articles


def fetch_and_store_blogs(company: str = "NVIDIA", db: Session = None) -> int:
    """
    Fetch articles from all RSS feeds for the company.
    Embeds each article into ChromaDB and saves a DailyBlog record.
    Returns the number of new articles stored.
    """
    feeds = get_blog_feeds(company)
    stored = 0

    for feed_url in feeds:
        try:
            resp = requests.get(feed_url, timeout=RSS_TIMEOUT, headers={"User-Agent": "InterviewPrepBot/2.0"})
            resp.raise_for_status()
            articles = _parse_feed(resp.text)
        except Exception as e:
            logger.warning(f"Failed to fetch feed {feed_url}: {e}")
            continue

        for article in articles[:10]:  # cap per feed to avoid overload
            metadata = {
                "company": company,
                "url": article["url"],
                "published": article["published"],
                "source": "rss",
                "title": article["title"],
            }
            try:
                store_article(article["title"], article["content"], metadata)
            except Exception as e:
                logger.warning(f"Embed failed for '{article['title']}': {e}")
                continue

            if db is not None:
                db.add(DailyBlog(title=f"[{company}] {article['title']}", content=article["content"]))

            stored += 1

    if db is not None and stored:
        db.commit()

    logger.info(f"Stored {stored} articles for {company}")
    return stored


def get_blog_history(company: Optional[str] = None, db: Session = None) -> list:
    if db is None:
        return []
    query = db.query(DailyBlog).order_by(DailyBlog.created_at.desc())
    if company:
        query = query.filter(DailyBlog.title.like(f"[{company}]%"))
    blogs = query.limit(50).all()
    return [
        {
            "id": b.id,
            "title": b.title,
            "content": b.content[:500] + ("..." if len(b.content) > 500 else ""),
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in blogs
    ]


def generate_daily_blog_content(company: str = "NVIDIA") -> tuple[str, str]:
    """
    Fallback: ask the LLM to write a blog post when RSS fetch is unavailable.
    Used by the legacy /blog/daily endpoint.
    """
    profile = get_profile(company)
    focus = ", ".join(profile["focus_areas"][:5])
    prompt = f"""Write a senior-level technical blog post relevant to someone preparing for a {company} interview.
Focus on one of these areas: {focus}.
Make it practical, production-focused, and backed by real engineering trade-offs.
Include: the problem being solved, the solution approach, failure modes, and key takeaways.
Length: 400-600 words."""

    content = generate_answer(prompt)
    title = "Daily Tech Insight"
    if content and len(content.splitlines()) > 0:
        first_line = content.splitlines()[0].lstrip("#").strip()
        if first_line:
            title = first_line[:80]

    return title, content
