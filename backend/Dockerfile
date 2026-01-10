# =========================
# BUILDER
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
 && rm -rf /root/.cache/pip \
 && find /usr/local/lib/python3.11/site-packages \
    -type d \( -name "tests" -o -name "__pycache__" \) -exec rm -rf {} + \
 && find /usr/local/lib/python3.11/site-packages \
    -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

RUN mkdir -p /runtime/app/rag/chroma_db /runtime/data

# =========================
# RUNTIME
# =========================
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages

COPY api ./api
COPY agents ./agents
COPY rag ./rag

COPY --from=builder /runtime/data /data
COPY --from=builder /runtime/app/rag/chroma_db /app/rag/chroma_db

ENV PYTHONPATH=/app
USER nonroot
EXPOSE 8000

CMD ["-m", "uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
