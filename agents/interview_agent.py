from rag.retrieve import query_articles
from agents.llm import generate_answer

SYSTEM_PROMPT = """
You are a senior NVIDIA engineer conducting a technical interview.
Answer concisely, deeply, and with system-level thinking.
If context is provided, ground your answer in it.
"""

def answer_question(question: str) -> str:
    # Retrieve top-k relevant docs
    docs = query_articles(question, k=3)

    context = "\n\n".join(
        f"- {d['content']}" for d in docs
    ) or "No relevant documents found."

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer as an NVIDIA interviewer would expect.
"""

    return generate_answer(prompt)

