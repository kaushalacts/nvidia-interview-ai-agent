from agents.llm import generate_answer
from datetime import datetime

BLOG_PROMPT = """
Write a senior-level DevOps engineering blog.
Topic should be practical, production-focused, and concise.
"""

def generate_daily_blog():
    content = generate_answer(BLOG_PROMPT)

    title = "Daily DevOps Insight"
    if content and len(content.splitlines()) > 0:
        title = content.splitlines()[0][:80]

    return title, content
