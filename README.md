# 🧠 NVIDIA Interview AI Agent

An **agentic AI system** that simulates a real technical interview experience — including **multi-stage interview flow**, **adaptive difficulty**, **JWT authentication with multi-user support**, and **comprehensive evaluation metrics** — using a **Retrieval-Augmented Generation (RAG)** architecture and a **local LLM**.

This project is built as a **personal interview preparation platform**, focusing on:
- correctness over scale
- debuggability
- realistic interviewer behavior
- clean system design

---

## 🚀 What This Project Does

The system behaves like a **senior technical interviewer**:

- **Multi-stage interview progression** (WARMUP → TECHNICAL_DEEP_DIVE → PROBLEM_SOLVING → BEHAVIORAL → WRAP_UP)
- **Adaptive difficulty adjustment** (1-5 levels, scales based on performance)
- **Multi-dimensional evaluation** (technical accuracy, depth, communication, problem-solving)
- **User authentication & multi-user support** (JWT tokens, secure authentication)
- **Generates daily study plans** with technical context
- **Evaluates answers** using comprehensive rubric
- **Stores conversation history** and evaluation metrics
- **Tracks score trends** over time
- **Integrates with n8n** for dynamic content ingestion

All components run **locally**, end-to-end.

---

## 🧩 Core Features

### ✅ Multi-Stage Interview System
- **5 distinct stages** with specific requirements:
  - **WARMUP**: Introductory questions (2+ questions, 5 min minimum)
  - **TECHNICAL_DEEP_DIVE**: Core technical assessment (3+ questions, 15 min minimum)
  - **PROBLEM_SOLVING**: Algorithm & system design (2+ questions, 10 min minimum)
  - **BEHAVIORAL**: Communication & experience (2+ questions, 5 min minimum)
  - **WRAP_UP**: Final evaluation and feedback
- Stage transitions based on time, question count, and performance
- Automatic progression through interview stages

### ✅ Adaptive Difficulty System
- **5 difficulty levels** (1-5)
- Automatically adjusts based on performance:
  - Score < 40%: Decrease difficulty
  - Score > 80%: Increase difficulty
  - Difficulty resets per stage

### ✅ Multi-Dimensional Evaluation
- **Technical Accuracy**: Correctness of content
- **Depth of Understanding**: Demonstrates conceptual mastery
- **Communication Clarity**: Articulation and explanation quality
- **Problem-Solving Approach**: Methodology and logic

### ✅ JWT Authentication & Multi-User Support
- Secure user registration and login
- JWT tokens with 7-day expiration
- Email-based user identification
- Role-based access control
- Protected API endpoints

### ✅ RAG Architecture
- Technical content stored in vector database (ChromaDB)
- All responses grounded in retrieved context
- Reduced hallucination risk
- n8n integration for dynamic content updates

### ✅ Session Persistence
- User conversations and history stored in SQLite
- Session context maintained across requests
- Weak/strong area tracking
- Performance history per stage

### ✅ Clean Dark-Mode UI
- Built with Streamlit
- NVIDIA-style dark theme
- Real-time feedback and progress visualization

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
┌────────▼──────────┐
│  FastAPI Backend  │
│ ├─ Auth Endpoints │
│ ├─ Interview Flow │
│ └─ Content API    │
└────────┬──────────┘
         │
┌────────▼───────────────────────┐
│  Core Orchestration            │
│ ├─ State Machine               │
│ ├─ Session Manager             │
│ ├─ Content Manager             │
│ └─ Interview Orchestrator      │
└────────┬───────────────────────┘
         │
    ┌────┴────┬──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│Agents│  │ChromaDB│  │SQLite│
└───┬──┘  └───┬───┘  └────┬─┘
    │         │           │
┌───▼─────────▼───────────▼───┐
│  Ollama (Local LLM)         │
│  ├─ Question Generation     │
│  ├─ Answer Evaluation       │
│  └─ Interview Analysis      │
└─────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI |
| UI | Streamlit |
| LLM | Ollama (local) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Persistence | SQLite |
| Authentication | JWT (python-jose) |
| Hashing | bcrypt |
| Architecture | RAG + Agentic AI |
| Container | Docker & Docker Compose |
| Language | Python 3.9+ |

---

## 📁 Project Structure

```
nvidia-interview-ai-agent/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app & endpoints
│   │   ├── auth.py              # JWT & password hashing
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── middleware.py        # Auth middleware
│   │   └── blog.py              # Daily blog generation
│   ├── core/
│   │   ├── state_machine.py     # Interview state management
│   │   ├── orchestrator.py      # Interview orchestration
│   │   ├── session_manager.py   # Session persistence
│   │   └── content_manager.py   # Content ingestion
│   ├── agents/
│   │   ├── interview_agent.py   # Interview logic
│   │   ├── evaluator_agent.py   # Answer evaluation
│   │   ├── question_agent.py    # Question generation
│   │   ├── planner_agent.py     # Daily plan generation
│   │   └── llm.py               # LLM interactions
│   ├── rag/
│   │   ├── embed_store.py       # Vector store management
│   │   └── retrieve.py          # Content retrieval
│   ├── tests/
│   │   ├── test_api_auth.py
│   │   ├── test_auth.py
│   │   ├── test_orchestrator.py
│   │   ├── test_e2e_interview.py
│   │   └── ...
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── ui/
│   │   └── app.py               # Streamlit app
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── API.md                   # API documentation
│   ├── SETUP.md                 # Setup guide
│   └── TESTING.md               # Testing guide
├── docker-compose.yml
└── README.md
```

---

## 🔐 Authentication & API

### Authentication Flow

1. **Register**: Create new user account
   ```bash
   POST /api/auth/register
   ```

2. **Login**: Get JWT token
   ```bash
   POST /api/auth/login
   ```

3. **Protected Endpoints**: Use Bearer token in Authorization header
   ```
   Authorization: Bearer <jwt-token>
   ```

### Key API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| POST | `/api/interview/plan` | Start interview session |
| POST | `/api/interview/ask` | Get next question |
| POST | `/api/interview/evaluate` | Submit answer and get evaluation |
| GET | `/api/interview/session` | Get session context |
| POST | `/api/content/ingest` | Ingest question from n8n (webhook) |
| GET | `/health` | Health check |

See [docs/API.md](docs/API.md) for complete documentation.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.9+, Ollama

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/kaushalacts/nvidia-interview-ai-agent.git
cd nvidia-interview-ai-agent

# Copy environment file
cp backend/.env.example backend/.env

# Start all services
docker-compose up -d

# Access frontend
open http://localhost:8501
```

### Option 2: Local Development

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

---

## 📋 Usage Guide

### 1. Register & Login
```
Register a new account → Receive JWT token → Use token for subsequent requests
```

### 2. Start Interview Session
```
POST /api/interview/plan → Session created → Interview begins at WARMUP stage
```

### 3. Answer Questions
```
GET current question → POST answer → Receive evaluation → Move to next question
```

### 4. Stage Progression
```
WARMUP (intro) → TECHNICAL_DEEP_DIVE → PROBLEM_SOLVING → BEHAVIORAL → WRAP_UP
```

Each stage has requirements for time, question count, and performance metrics.

### 5. Review Results
```
See multi-dimensional evaluation (technical, depth, communication, problem-solving)
```

---

## 🧪 Testing

Run the full test suite:

```bash
# Unit tests
pytest backend/tests/ -v

# Integration tests
pytest backend/tests/test_e2e_interview.py -v

# With coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

See [docs/TESTING.md](docs/TESTING.md) for more details.

---

## 🛠️ Configuration

Create `backend/.env` file:

```env
JWT_SECRET=your-secret-key-change-in-production-min-32-chars
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
DATABASE_PATH=./interview_ai.db
LOG_LEVEL=INFO
```

---

## ⚖️ Design Decisions

- **Multi-stage architecture**: Simulates real interview progression
- **Adaptive difficulty**: Personalizes experience based on performance
- **JWT authentication**: Enables multi-user support
- **State machine pattern**: Clear, testable interview flow
- **Session persistence**: Complete history maintained
- **Modular agents**: Interview, evaluator, question, planner agents
- **RAG architecture**: Context-grounded responses
- **Docker deployment**: Reproducible, isolated environments

---

## 📚 Documentation

- **[API Documentation](docs/API.md)** - Complete API reference with examples
- **[Setup Guide](docs/SETUP.md)** - Step-by-step setup instructions
- **[Testing Guide](docs/TESTING.md)** - Testing structure and practices

---

## 🎯 Interview Context

This project demonstrates:

* Agentic AI design patterns
* Retrieval-augmented generation
* State machine architecture
* Multi-user system design
* JWT authentication
* Adaptive algorithms
* Clean API design
* Production-ready deployment

It reflects **system-level thinking** expected at **NVIDIA**.
