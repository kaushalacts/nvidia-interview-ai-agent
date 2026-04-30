import time
from datetime import datetime
from zoneinfo import ZoneInfo

from agents.llm import generate_answer
from core.company_profiles import get_profile
from rag.retrieve import query_articles

_FALLBACK = """
Time-Boxed Interview Prep Plan

- 00:00-00:15  Systems Warm-up       Refresh one critical concept and its production implications
- 00:15-00:45  Core Platform Topic   Deep dive: internals, design decisions, failure modes
- 00:45-01:15  Performance & Reliability  Bottlenecks, SLOs, alerting, cost vs performance
- 01:15-01:40  Hands-on Scenario     Debug or design a real production problem
- 01:40-02:00  Senior Interview Q    Open-ended architectural reasoning question
"""


def generate_daily_plan(company: str = "NVIDIA") -> str:
    profile = get_profile(company)
    focus = ", ".join(profile["focus_areas"][:6])
    sre_focus = ", ".join(profile.get("sre_focus", []))
    display = profile["display_name"]

    tz = ZoneInfo("Asia/Kolkata")
    today = datetime.now(tz).strftime("%A, %d %B %Y")

    # Pull RAG context
    rag_query = f"{company} GPU infrastructure Kubernetes performance optimization DevOps MLOps SRE"
    try:
        docs = query_articles(rag_query, k=3)
        context = "\n".join(f"- {d.get('content', '')[:150]}" for d in docs)
    except Exception:
        context = ""

    prompt = f"""You are preparing a senior DevOps/SRE engineer for a {display} interview.

Date: {today}
Company: {display}
Key focus areas: {focus}
SRE emphasis: {sre_focus}

{"Recent tech context:\n" + context if context else ""}

Create a 2-hour interview preparation plan. Return STRICTLY in this format:

Time-Boxed {display} Interview Prep Plan

- 00:00-00:15  Systems Warm-up
  Refresh ONE critical concept from: {focus.split(",")[0].strip()} or related area
  Why it matters at {display} scale

- 00:15-00:45  Core Platform Topic
  Deep dive into ONE area (internals, design decisions, failure modes)
  Include: architecture, trade-offs, and what breaks at scale

- 00:45-01:15  Performance & Reliability
  Bottlenecks, metrics, SLOs, debugging approach
  Cost vs performance trade-offs specific to {display}

- 01:15-01:40  Hands-on Scenario
  Design or debug a realistic {display} production scenario
  Constraints: scale, latency, cost, privacy

- 01:40-02:00  Senior Interview Question
  One open-ended architectural question from {display}'s domain
  Expect the interviewer to challenge every assumption

Rules: Think like an owner. No buzzwords. Show reasoning and trade-offs."""

    try:
        start = time.time()
        result = generate_answer(prompt)
        print(f"Planner LLM took {time.time() - start:.1f}s")
        return result or _FALLBACK
    except Exception as e:
        print(f"Planner LLM failed: {e}")
        return _FALLBACK
