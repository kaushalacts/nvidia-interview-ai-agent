# =========================
# BUILDER STAGE
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

# ---- System deps required for sentence-transformers / numpy / torch ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libstdc++6 \
    libgomp1 \
    libgl1 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Python deps ----
COPY requirements.txt .

# Upgrade pip (important for py311 wheels)
RUN pip install --upgrade pip

# Install into isolated prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# =========================
# RUNTIME STAGE
# =========================
FROM python:3.11-slim

# ---- Runtime hygiene ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# ---- Runtime system deps (REQUIRED) ----
# These are needed at runtime for sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    libgomp1 \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

# ---- Copy Python deps ----
COPY --from=builder /install /usr/local

# ---- App code ----
COPY api ./api
COPY agents ./agents
COPY rag ./rag

# ---- Runtime dirs ----
RUN mkdir -p /data /app/rag/chroma_db

EXPOSE 8000

# ---- Start FastAPI ----
CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
