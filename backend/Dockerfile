FROM python:3.11-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian12
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages

COPY api ./api
COPY agents ./agents
COPY rag ./rag

USER root
RUN mkdir -p /data /app/rag/chroma_db \
 && chown -R nonroot:nonroot /data /app

USER nonroot
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["-m", "uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
