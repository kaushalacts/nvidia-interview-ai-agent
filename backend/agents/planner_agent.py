from datetime import datetime
from zoneinfo import ZoneInfo

from rag.retrieve import query_articles
from agents.llm import generate_answer

SYSTEM_PROMPT = """
You are a Principal DevOps / Platform Engineer interviewing at NVIDIA.

Your responsibility:
- Design a DAILY interview-prep plan for a SENIOR DevOps Engineer (₹40 LPA+)
- Focus on ownership, systems thinking, and production trade-offs
- Assume strong Linux, networking, cloud, and Kubernetes fundamentals

Core evaluation dimensions at this level:
- Distributed systems design
- Reliability, scalability, and performance
- GPU-aware infrastructure & CI/CD
- Failure handling & cost optimization
- Clear reasoning under constraints

This is NOT entry-level DevOps.
"""

def generate_daily_plan():
    # 🇮🇳 India timezone
    tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(tz)

    today = now.strftime("%A, %d %B %Y")

    # Pull RAG context focused on GPU infra + DevOps
    docs = query_articles(
        query=(
            "NVIDIA GPU infrastructure Kubernetes CUDA "
            "performance optimization DevOps MLOps SRE"
        ),
        k=3
    )

    context = "\n".join(
        f"- {d.get('content', '')[:500]}" for d in docs
    ) or "No specific reference context available."

    prompt = f"""
{SYSTEM_PROMPT}

Date: {today}

Reference Context (optional background):
{context}

TASK:
Create a **2-hour senior DevOps interview preparation plan**.

Return STRICTLY in the format below.

🕒 Time-Boxed Senior DevOps Plan

- 00:00–00:15 → Systems Warm-up
  • Refresh ONE critical concept (e.g., Linux I/O, networking, containers, scheduling)
  • Why it matters at scale

- 00:15–00:45 → Core Platform Topic
  • Example areas:
    - Kubernetes internals (scheduler, CNI, CSI)
    - GPU scheduling & device plugins
    - CI/CD design for large monorepos
    - Infrastructure as Code trade-offs
  • Include design decisions & failure modes

- 00:45–01:15 → Deep Dive (Performance / Reliability)
  • Bottlenecks, metrics, and tuning
  • SLOs, alerts, and production debugging
  • Cost vs performance trade-offs

- 01:15–01:40 → Hands-on / Thought Exercise
  • Design or debug a real production scenario
  • Constraints: scale, latency, cost, security
  • Explain decisions clearly

- 01:40–02:00 → Senior Interview Question
  • Open-ended, real-world question
  • Expect architectural reasoning
  • No trivia or definitions

Rules:
- Think like an OWNER, not an operator
- Avoid generic DevOps buzzwords
- Assume interviewer challenges every decision
- Prioritize reasoning, trade-offs, and impact
"""

    return generate_answer(prompt)

