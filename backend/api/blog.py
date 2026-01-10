from agents.llm import generate_answer

BLOG_PROMPT = """
You are a Senior DevOps Engineer writing a DAILY blog.

Rules:
- Real production experience
- Failures, trade-offs, scaling, cost
- Kubernetes, Linux, CI/CD, Cloud
- No beginner tutorials

Return format:
TITLE:
CONTENT:
"""

def generate_daily_blog():
    result = generate_answer(BLOG_PROMPT)

    lines = result.splitlines()
    title = lines[0].replace("TITLE:", "").strip()
    content = "\n".join(lines[1:]).replace("CONTENT:", "").strip()

    return title, content
