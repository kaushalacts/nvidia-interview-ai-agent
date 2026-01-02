## 🚀 Project Status

This project builds an **AI-powered interview preparation agent** focused on NVIDIA-level system and GPU concepts.

### ✅ Completed Milestones

- [x] FastAPI backend foundation
- [x] Automated ingestion via n8n
- [x] Persistent article storage (JSON)
- [x] ChromaDB vector database
- [x] RAG-based semantic retrieval
- [x] Data-quality safe ingestion pipeline
- [x] Local LLM integration using Ollama
- [x] **Interview AI Agent (RAG + LLM)** ✅

---

## 🧠 System Architecture

n8n (Automation / Scraping)
↓
FastAPI (/ingest)
↓
Persistent Storage (JSON)
↓
ChromaDB (Vector Memory)
↓
RAG Retrieval
↓
Ollama (Local LLM)
↓
Interview AI Agent (/ask)


[200~
---

## 🔍 Example Usage

### Ask an Interview Question

```bash
curl --get \
  --data-urlencode "question=Explain CUDA optimization techniques" \
  http://localhost:8000/ask

