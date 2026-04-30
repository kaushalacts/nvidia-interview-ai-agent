# Interview Prep AI Platform

A fully local, agentic AI system that simulates real technical interviews for senior DevOps, SRE, MLOps, and AIOps roles at top tech companies — NVIDIA, Google, Meta, and Apple.

The platform runs end-to-end on your machine: no external API keys, no data leaving your system. Everything is powered by a local LLM via Ollama.

---

## What It Does

- **Conducts a real multi-stage mock interview** — the AI acts as a senior interviewer, asking increasingly difficult questions across five structured stages
- **Adapts difficulty in real time** based on how well you answer — scores above 80% push difficulty up, below 40% brings it down
- **Evaluates every answer across four dimensions** — technical accuracy, depth of understanding, communication clarity, and problem-solving approach
- **Fetches real engineering blog posts** from each company's RSS feed daily and lets you ask questions about them, grounded in actual content
- **Generates a tailored 2-hour prep plan** for whichever company you are targeting
- **Tracks your progress** over time with per-session scores and stage-level breakdowns

---

## Supported Companies

| Company | Focus Areas | Blog Source |
|---------|-------------|-------------|
| **NVIDIA** | CUDA, GPU architecture, Triton Inference Server, NCCL, DGX infra, MLOps, Kubernetes GPU scheduling | developer.nvidia.com |
| **Google** | Borg/Kubernetes internals, Spanner, SRE/SLO, Colossus, BeyondCorp, Pub/Sub | cloudblog.withgoogle.com |
| **Meta** | TAO graph store, Presto, Scuba, Tupperware, PyTorch distributed, AIOps | engineering.fb.com |
| **Apple** | Differential privacy, CoreML, APNs at scale, Darwin kernel, Secure Enclave | machinelearning.apple.com |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│   Plan · Ask AI · Interview · Progress · History · Blogs │
└───────────────────────┬──────────────────────────────────┘
                        │  REST + JWT Bearer
┌───────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                          │
│                                                          │
│  /api/auth/*          JWT register & login               │
│  /api/interview/*     Orchestrated interview flow        │
│  /api/blogs/*         RSS fetch, history, RAG Q&A        │
│  /api/ingest/*        n8n webhook receivers              │
│  /plan/today          Daily prep plan                    │
│  /ask                 RAG-grounded free-form Q&A         │
└──────┬──────────────────────────┬────────────────────────┘
       │                          │
┌──────▼──────────┐   ┌──────────▼──────────────────────┐
│ Interview       │   │ RAG Engine                       │
│ Orchestrator    │   │                                  │
│                 │   │  ChromaDB  ←  RSS blog articles  │
│ ┌─────────────┐ │   │            ←  n8n webhook        │
│ │ State       │ │   │            ←  /api/content/ingest│
│ │ Machine     │ │   │                                  │
│ │             │ │   │  embed_store.py  (HuggingFace)   │
│ │ WARMUP      │ │   │  retrieve.py     (similarity)    │
│ │ TECHNICAL   │ │   └──────────────────────────────────┘
│ │ PROBLEM     │ │
│ │ BEHAVIORAL  │ │   ┌──────────────────────────────────┐
│ │ WRAP_UP     │ │   │ Agents                           │
│ └─────────────┘ │   │                                  │
│                 │   │  question_agent   (generates Qs) │
│ SessionManager  │   │  enhanced_evaluator (scores ans) │
│ (SQLite)        │   │  planner_agent    (daily plan)   │
└─────────────────┘   │  interview_agent  (RAG Q&A)      │
                      └────────────┬─────────────────────┘
                                   │
                      ┌────────────▼─────────────────────┐
                      │  Ollama  (local LLM)              │
                      │  default model: llama3.2          │
                      └──────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  n8n  (workflow automation)  — localhost:5678            │
│                                                          │
│  Schedule: 6:00 AM IST daily                            │
│  → HTTP POST /api/blogs/fetch?company=NVIDIA            │
│    (repeat per company)                                  │
└──────────────────────────────────────────────────────────┘
```

---

## Interview Flow

```
Register / Login
      │
      ▼
 Select Company  (NVIDIA / Google / Meta / Apple)
      │
      ▼
 POST /api/interview/start   →  session_id returned
      │
      ▼
 POST /api/interview/next    →  question + stage + difficulty
      │
      ▼
 User answers
      │
      ▼
 POST /api/interview/submit  →  4-dimension evaluation + feedback
      │
      ▼
 Repeat until stage requirements met, then auto-advance
      │
      ▼
 WARMUP → TECHNICAL_DEEP_DIVE → PROBLEM_SOLVING → BEHAVIORAL → WRAP_UP
      │
      ▼
 Overall score + weak/strong area report
```

### Stage Requirements

| Stage | Min Time | Min Questions | Purpose |
|-------|----------|---------------|---------|
| WARMUP | 5 min | 2 | Establish baseline, background |
| TECHNICAL_DEEP_DIVE | 15 min | 3 | Core technical depth |
| PROBLEM_SOLVING | 10 min | 2 | System design, algorithms |
| BEHAVIORAL | 5 min | 2 | Ownership, past experience |
| WRAP_UP | — | — | Final report, overall score |

### Adaptive Difficulty

| Score | Action |
|-------|--------|
| > 80% | Difficulty increases (+1, max 5) |
| 40–80% | Difficulty stays the same |
| < 40% | Difficulty decreases (−1, min 1) |

### Evaluation Dimensions

Every answer is scored across four dimensions and combined into an overall score:

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Technical Accuracy | 40% | Correctness of facts, terminology, concepts |
| Depth of Understanding | 30% | The "why" behind the "what" |
| Communication Clarity | 15% | Structure, examples, ease of explanation |
| Problem-Solving Approach | 15% | Trade-off reasoning, edge cases, methodology |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Local LLM | Ollama (llama3.2 default) |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| ORM & DB | SQLAlchemy + SQLite |
| Authentication | JWT (python-jose) + bcrypt |
| Automation | n8n (self-hosted) |
| Containers | Docker + Docker Compose |
| Language | Python 3.11 |

---

## Project Structure

```
interview-prep-ai/
│
├── backend/
│   ├── api/
│   │   ├── main.py            # FastAPI app, all routes
│   │   ├── auth.py            # JWT creation and verification
│   │   ├── middleware.py      # get_current_user dependency
│   │   ├── database.py        # SQLAlchemy engine (reads DATABASE_URL env)
│   │   ├── models.py          # ORM models (User, Session, Response, Blog)
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   └── blog.py            # RSS fetcher + blog history
│   │
│   ├── core/
│   │   ├── state_machine.py   # Stage definitions and transition logic
│   │   ├── orchestrator.py    # Coordinates state machine + session + agents
│   │   ├── session_manager.py # CRUD for interview sessions in SQLite
│   │   └── company_profiles.py# NVIDIA/Google/Meta/Apple topic configs + RSS feeds
│   │
│   ├── agents/
│   │   ├── llm.py                    # Ollama HTTP client with retry
│   │   ├── question_agent.py         # Generates stage/company/difficulty-aware questions
│   │   ├── enhanced_evaluator_agent.py # Multi-dimension JSON scoring
│   │   ├── evaluator_agent.py        # Simple evaluator (legacy, kept for reference)
│   │   ├── interview_agent.py        # RAG-grounded free-form Q&A
│   │   └── planner_agent.py          # Company-specific 2-hour prep plan
│   │
│   ├── rag/
│   │   ├── embed_store.py     # Store articles into ChromaDB
│   │   └── retrieve.py        # Similarity search over ChromaDB
│   │
│   ├── tests/                 # pytest suite (unit + integration + e2e)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── ui/
│   │   └── app.py             # Streamlit UI (6 tabs)
│   ├── Dockerfile.ui
│   └── ui/requirements.txt
│
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── TESTING.md
│
├── docker-compose.yml
└── .env                       # Root env — picked up by Docker Compose
```

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- 8 GB RAM minimum (Ollama + model + services)

### 1. Clone and configure

```bash
git clone https://github.com/kaushalacts/interview-prep-ai.git
cd interview-prep-ai

# Edit the .env file — set a strong JWT_SECRET before exposing publicly
nano .env
```

The `.env` file at the root looks like this:

```env
OLLAMA_MODEL=llama3.2
JWT_SECRET=change-me-to-a-random-32-char-string-before-deploy
N8N_USER=admin
N8N_PASSWORD=changeme
```

### 2. Start all services

```bash
docker-compose up --build -d
```

This starts four containers:

| Container | Port | Purpose |
|-----------|------|---------|
| `ollama` | — | Local LLM runtime |
| `interview-backend` | 8000 | FastAPI API |
| `interview-ui` | 8501 | Streamlit frontend |
| `n8n` | 5678 | Workflow automation |

### 3. Pull the LLM model

Do this once after the first `up`. The model is ~2 GB.

```bash
docker exec ollama ollama pull llama3.2
```

To use a smaller/faster model instead:

```bash
docker exec ollama ollama pull phi3:mini
# then set OLLAMA_MODEL=phi3:mini in .env and restart backend
```

### 4. Open the app

```
http://localhost:8501
```

Register an account, pick your target company in the sidebar, and start an interview.

---

## n8n Blog Automation Setup

n8n automates the daily 6 AM blog fetch from each company's engineering blog. This only needs to be set up once.

### Step 1 — Open n8n

```
http://localhost:5678
```

Login with the credentials from your `.env` (`N8N_USER` / `N8N_PASSWORD`).

### Step 2 — Create a workflow for each company

For each company (NVIDIA, Google, Meta, Apple):

1. Add a **Schedule Trigger** node — set to `0 6 * * *` (6:00 AM daily), timezone `Asia/Kolkata`
2. Add an **HTTP Request** node:
   - Method: `POST`
   - URL: `http://backend:8000/api/blogs/fetch?company=NVIDIA`
   - (replace `NVIDIA` with the target company)
3. Activate the workflow

Fetched articles are embedded into ChromaDB and appear in the **Blogs** tab of the UI automatically.

### Manual fetch (any time)

You can also trigger a fetch on-demand from the Blogs tab in the UI, or directly:

```bash
curl -X POST "http://localhost:8000/api/blogs/fetch?company=NVIDIA"
```

---

## API Reference

All interview endpoints require a JWT token in the `Authorization: Bearer <token>` header. Obtain the token from `/api/auth/login`.

### Authentication

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | `{email, password, full_name}` | Create account, returns token |
| POST | `/api/auth/login` | `{email, password}` | Returns JWT token (7-day expiry) |

### Interview Flow

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/api/interview/start` | `{company}` | Start session, returns `session_id` |
| POST | `/api/interview/next` | `{session_id, company}` | Get next question (or completion report) |
| POST | `/api/interview/submit` | `{session_id, question_id, question, answer}` | Submit answer, get evaluation |
| GET | `/api/interview/session/{session_id}` | — | Get current session context |

### Blogs

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| POST | `/api/blogs/fetch` | `?company=NVIDIA` | Pull latest articles from RSS |
| GET | `/api/blogs/history` | `?company=NVIDIA` | List stored articles |
| POST | `/api/blogs/ask` | `{question}` + `?company=NVIDIA` | RAG Q&A over fetched articles |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/plan/today` | `?company=NVIDIA` — Generate 2-hour prep plan |
| POST | `/ask` | `{question}` — Free-form RAG-grounded Q&A |
| GET | `/history/scores` | Numeric score history for progress chart |
| GET | `/health` | Health check |

### n8n Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ingest/blog` | Receive a blog article from n8n and embed it |
| POST | `/api/content/ingest` | Receive an interview question from n8n |

---

## UI Tabs

| Tab | What It Does |
|-----|-------------|
| **Plan** | Generates a company-specific 2-hour prep plan using RAG context |
| **Ask AI** | Free-form Q&A — answers grounded in ChromaDB articles |
| **Interview** | Full mock interview loop: start → question → answer → evaluation → repeat |
| **Progress** | Line chart of scores over time + bar chart by stage |
| **History** | Current session Q&A + persistent chat history |
| **Blogs** | Fetch real articles, browse them, ask questions via RAG |

---

## Running Tests

Tests use an in-memory SQLite database — no running services needed.

```bash
cd backend

# Full test suite
pytest tests/ -v

# End-to-end interview flow only
pytest tests/test_e2e_interview.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

The test suite covers:
- User registration and login flow
- JWT token creation and verification
- Interview session lifecycle
- Stage transitions through all 5 stages
- Adaptive difficulty adjustment
- Session persistence across requests
- Multi-user isolation
- Enhanced evaluator scoring logic

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | *(required)* | Secret key for signing JWT tokens — change before deploying |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama endpoint (Docker internal) |
| `DATABASE_URL` | `sqlite:////data/interview_ai.db` | SQLAlchemy database URL |
| `N8N_USER` | `admin` | n8n basic auth username |
| `N8N_PASSWORD` | `changeme` | n8n basic auth password |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Local Development (without Docker)

```bash
# 1. Start Ollama separately
ollama serve
ollama pull llama3.2

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Set environment variables
export OLLAMA_HOST=http://localhost:11434
export DATABASE_URL=sqlite:///./interview_ai.db
export JWT_SECRET=dev-secret-key

# 4. Run the API
uvicorn api.main:app --reload --port 8000

# 5. In a separate terminal, run the frontend
cd frontend/ui
pip install -r requirements.txt
API=http://localhost:8000 streamlit run app.py
```

---

## Design Decisions

**Why local LLM (Ollama)?**
No API costs, no data leaving your machine, works offline. The trade-off is slower inference compared to hosted APIs.

**Why SQLite?**
Sufficient for a single-user or small-team tool. Trivial to swap for PostgreSQL by changing `DATABASE_URL`.

**Why ChromaDB for RAG?**
Runs embedded alongside the backend with zero infrastructure. The same DB volume persists between restarts.

**Why n8n for blog automation?**
Visual workflow editor makes it easy to add new data sources, transformations, or notification steps without writing code.

**Why the state machine pattern?**
Interview stages have explicit entry/exit conditions (time, question count, performance). A state machine makes those rules testable and auditable rather than buried in if-else chains.

**Why EnhancedEvaluatorAgent over a simple scorer?**
The LLM returns structured JSON with four independent dimension scores. This makes the scores chartable, comparable across sessions, and usable to steer the next question's difficulty — none of which is possible with a free-text score string.

---

## Roadmap

- [ ] Add more companies (Amazon, Microsoft, OpenAI)
- [ ] Spaced-repetition mode — surfaces weak areas from past sessions
- [ ] Voice input support (Whisper integration)
- [ ] PDF report export after each interview session
- [ ] PostgreSQL support for multi-user production deployment
- [ ] Webhook-triggered model warm-up on container start
