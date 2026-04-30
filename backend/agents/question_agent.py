import json
from agents.llm import generate_answer
from core.company_profiles import get_focus_areas
from rag.retrieve import query_articles


def generate_interview_question(
    stage: str = "TECHNICAL_DEEP_DIVE",
    difficulty: int = 3,
    company: str = "NVIDIA",
    weak_areas: str = "[]",
) -> str:
    """
    Generate a context-aware interview question grounded in company profile
    and recent blog content from ChromaDB.
    """
    focus_areas = get_focus_areas(company)

    # Parse weak areas to steer question topics
    try:
        weak_list = json.loads(weak_areas) if isinstance(weak_areas, str) else weak_areas
    except (json.JSONDecodeError, TypeError):
        weak_list = []

    focus_hint = (
        f"Focus on the candidate's weak areas: {', '.join(weak_list[:3])}."
        if weak_list
        else f"Cover topics from: {', '.join(focus_areas[:4])}."
    )

    # Pull RAG context relevant to the company
    rag_query = f"{company} {' '.join(focus_areas[:3])} interview question"
    docs = query_articles(rag_query, k=2)
    rag_context = "\n".join(f"- {d['content'][:200]}" for d in docs) if docs else ""

    stage_instructions = {
        "WARMUP": "Ask a broad, approachable question to establish the candidate's background.",
        "TECHNICAL_DEEP_DIVE": "Ask a deep technical question requiring specific knowledge and trade-off reasoning.",
        "PROBLEM_SOLVING": "Present a system design or algorithmic challenge with realistic constraints.",
        "BEHAVIORAL": "Ask a behavioral question about past experience, ownership, and decision-making.",
        "WRAP_UP": "Ask the candidate what questions they have, or summarize key themes from the interview.",
    }

    stage_instruction = stage_instructions.get(stage, stage_instructions["TECHNICAL_DEEP_DIVE"])

    prompt = f"""You are a senior {company} engineer conducting a technical interview.

Stage: {stage} | Difficulty: {difficulty}/5
{stage_instruction}
{focus_hint}

{"Recent company tech context:\n" + rag_context if rag_context else ""}

Generate ONE clear, specific interview question. Do not provide the answer.
Question:"""

    return generate_answer(prompt)
