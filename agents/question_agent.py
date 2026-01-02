from agents.llm import generate_answer

QUESTION_PROMPT = """
You are a senior NVIDIA interviewer.
Generate ONE clear, technical interview question.
Focus on CUDA, GPU architecture, performance, or system design.
Do not provide the answer.
"""

def generate_interview_question():
    return generate_answer(QUESTION_PROMPT)

