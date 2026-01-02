from rag.retrieve import query_articles
from agents.llm import generate_answer
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

SYSTEM_PROMPT = """
You are an expert NVIDIA interview coach.
Create a focused, high-impact daily study plan.
Prioritize GPU systems, CUDA, performance, and design thinking.
"""

def generate_daily_plan():
    # Explicit timezone (India)
    tz = ZoneInfo("Asia/Kolkata")
    today = datetime.now(tz).strftime("%Y-%m-%d")

    docs = query_articles("CUDA GPU performance NVIDIA", k=3)

    context = "\n\n".join(
        f"- {d['content']}" for d in docs
    ) or "No specific documents found."

    prompt = f"""
{SYSTEM_PROMPT}

Date: {today}

Context:
{context}

Task:
Create a structured study plan for today with:
1. Core concept
2. Deep dive topic
3. Hands-on or thinking exercise
4. Interview-style question

Keep it concise and actionable.
"""

    return generate_answer(prompt)

