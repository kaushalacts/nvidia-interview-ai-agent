from rag.retrieve import query_articles
from agents.llm import generate_answer
from datetime import date

SYSTEM_PROMPT = """
You are an expert NVIDIA interview coach.
Create a focused, high-impact daily study plan.
Prioritize GPU systems, CUDA, performance, and design thinking.
"""

def generate_daily_plan():
    today = date.today().isoformat()

    # Retrieve relevant NVIDIA context
    docs = query_articles("CUDA GPU performance NVIDIA", k=3)

    context = "\n\n".join(
        f"- {d['content']}" for d in docs
    ) or "No specific documents found."

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Task:
Create a structured study plan for today ({today}) with:
1. Core concept to study
2. One deep-dive topic
3. One hands-on or thinking exercise
4. One interview-style question

Keep it concise and actionable.
"""

    return generate_answer(prompt)

