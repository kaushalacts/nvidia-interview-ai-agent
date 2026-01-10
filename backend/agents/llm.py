import os
import requests
import time

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

OLLAMA_GENERATE_URL = f"{OLLAMA_HOST}/api/generate"

SESSION = requests.Session()  # reuse connection


def generate_answer(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 2048,      # VERY IMPORTANT (reduce memory)
            "num_predict": 512,   # cap output
            "temperature": 0.7,
        },
    }

    last_error = None

    for attempt in range(1, 6):  # more retries
        try:
            resp = SESSION.post(
                OLLAMA_GENERATE_URL,
                json=payload,
                timeout=180,
            )

            # Ollama returns 404 while runner is warming — retry
            if resp.status_code == 404:
                raise RuntimeError("Ollama runner warming up")

            resp.raise_for_status()
            data = resp.json()

            if "response" not in data:
                raise RuntimeError(f"Invalid Ollama response: {data}")

            return data["response"]

        except Exception as e:
            last_error = e
            time.sleep(3 * attempt)  # exponential backoff

    raise RuntimeError(f"Ollama generation failed after retries: {last_error}")

