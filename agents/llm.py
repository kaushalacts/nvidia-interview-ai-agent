import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"

def generate_answer(prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()["response"]

