# 🧠 NVIDIA Interview AI Agent

An **agentic AI system** that simulates a real technical interview experience — including **daily preparation plans**, **interviewer-led questioning**, **answer evaluation**, and **progress tracking** — using a **Retrieval-Augmented Generation (RAG)** architecture and a **local LLM**.

This project is built as a **personal interview preparation platform**, focusing on:
- correctness over scale
- debuggability
- realistic interviewer behavior
- clean system design

---

## 🚀 What This Project Does

The system behaves like a **senior technical interviewer**:

- Generates a **daily study plan**
- Asks **technical interview questions**
- Evaluates answers using an interview rubric
- Runs multi-round interview sessions
- Stores **date-wise chat history**
- Tracks **evaluation scores over time**
- Visualizes progress via charts

All components run **locally**, end-to-end.

---

## 🧩 Core Features

### ✅ Agent-Led Interview Mode
- AI controls the interview flow
- AI asks the questions
- User only answers
- Multi-question interview sessions supported

### ✅ Daily Interview Preparation Planner
- Generates a focused daily plan
- Uses NVIDIA-relevant technical context
- Timezone-safe (Asia/Kolkata)

### ✅ Retrieval-Augmented Generation (RAG)
- Technical content stored in a vector database
- All responses grounded in retrieved context
- Reduced hallucination risk

### ✅ Persistent History & Progress Tracking
- Date-wise interview chat history
- Stored evaluations with timestamps
- Score trend visualization

### ✅ Clean Dark-Mode UI
- Built with Streamlit
- NVIDIA-style dark theme
- Lightweight and inspectable

---

## 🏗️ System Architecture

```

Streamlit UI
↓
FastAPI Backend
↓
Interview / Planner / Evaluator Agents
↓
ChromaDB (Vector Memory)
↓
Ollama (Local LLM)

```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-----|-----------|
| Backend API | FastAPI |
| UI | Streamlit |
| LLM | Ollama (local) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Persistence | SQLite |
| Architecture | RAG + Agentic AI |
| Language | Python |

---

## 📁 Project Structure
  

nvidia-interview-ai-agent/
├── api/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ └── schemas.py
│
├── agents/
│ ├── llm.py
│ ├── interview_agent.py
│ ├── planner_agent.py
│ ├── evaluator_agent.py
│ └── question_agent.py
│
├── rag/
│ ├── embed_store.py
│ └── retrieve.py
│
├── ui/
│ └── app.py
│
├── .streamlit/
│ └── config.toml
│
├── requirements.txt
└── README.md

 

---

## ▶️ Run Locally

### 1️⃣ Setup Environment

```bash
git clone https://github.com/kaushalacts/nvidia-interview-ai-agent.git
cd nvidia-interview-ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

---

### 2️⃣ Start Ollama

```bash
ollama pull llama3.1
ollama serve
```

---

### 3️⃣ Start Backend

```bash
uvicorn api.main:app --reload
```

---

### 4️⃣ Start UI

```bash
streamlit run ui/app.py
```

---

## 🧪 Usage

### Daily Plan

* Click **Generate Plan** to get today’s interview focus

### Interview Mode

* Start interview session
* Answer AI-generated questions
* Receive evaluation feedback
* Continue with next questions

### History & Progress

* Review date-wise interview history
* Track improvement via score charts

---

## ⚖️ Design Decisions

* Single-user, local-first design
* No authentication (intentional)
* Correctness and reasoning prioritized
* Fast iteration over premature optimization

This system is designed as an **internal engineering tool**, not a SaaS product.

---

## 🔮 Future Enhancements

* Adaptive questioning based on weak areas
* Structured numeric scoring
* Topic-specific interview sessions
* Export history reports
* Cloud deployment (model-agnostic)

---
Added dockerfile with docker compose -produciton grade. 
----

---

## 🎯 Interview Context

This project demonstrates:

* Agentic AI design
* Retrieval-augmented generation
* Feedback loops for skill improvement
* Practical UI integration
* Engineering trade-off reasoning

It reflects system-level thinking expected at **NVIDIA**.

 
 
