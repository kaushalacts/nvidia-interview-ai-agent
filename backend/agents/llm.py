import time
import requests
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

MAX_RETRIES = 6
INITIAL_DELAY = 2  # seconds


def generate_answer(prompt: str) -> str:
    last_error = None
    delay = INITIAL_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()

            last_error = response.text

        except Exception as e:
            last_error = str(e)

        # 🟡 Ollama warming up → wait and retry
        time.sleep(delay)
        delay *= 2

    # ✅ Graceful fallback instead of crashing API
    return (
        "⚠️ AI engine is warming up.\n\n"
        "Please retry in a few seconds. "
        "This usually happens only after startup."
    )
