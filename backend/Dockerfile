# =========================
# BUILDER
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libstdc++6 \
    libgomp1 \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --prefix=/install \
    -r requirements.txt


# =========================
# RUNTIME
# =========================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# ---- System runtime libs ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    libgomp1 \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

# ---- Create user ----
RUN useradd -m appuser

# ---- Create dirs & set permissions (AS ROOT) ----
RUN mkdir -p /data /app/rag/chroma_db \
 && chown -R appuser:appuser /data /app

# ---- Copy deps ----
COPY --from=builder /install /usr/local

# ---- Copy app code (still ROOT, but owned already) ----
COPY api ./api
COPY agents ./agents
COPY rag ./rag

# ---- Drop privileges (FINAL STEP) ----
USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000", "--workers=2"]
