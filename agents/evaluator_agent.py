from agents.llm import generate_answer

EVALUATION_PROMPT = """
You are a senior NVIDIA interviewer evaluating a candidate's answer.

Evaluate on:
1. Technical correctness
2. Depth of understanding
3. System-level thinking
4. Clarity and structure

Give:
- A score out of 10
- What was done well
- What is missing or weak
- Specific suggestions to improve

Be honest, concise, and professional.
"""

def evaluate_answer(question: str, answer: str) -> str:
    prompt = f"""
{EVALUATION_PROMPT}

Interview Question:
{question}

Candidate Answer:
{answer}

Provide evaluation now.
"""
    return generate_answer(prompt)

