# =========================
# BUILDER STAGE
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

# Minimal build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps into virtual env-style path
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =========================
# RUNTIME STAGE
# =========================
FROM python:3.11-slim

# Runtime hygiene
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only installed deps from builder
COPY --from=builder /install /usr/local

# App code
COPY api ./api
COPY agents ./agents
COPY rag ./rag

# Runtime dirs
RUN mkdir -p /data /app/rag/chroma_db

ENV PYTHONPATH=/app
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
