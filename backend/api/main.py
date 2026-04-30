from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timezone
import uuid

from api.database import SessionLocal, engine
from api import models, schemas
from api.auth import hash_password, verify_password, create_access_token
from api.middleware import get_current_user
from api.blog import fetch_and_store_blogs, get_blog_history, generate_daily_blog_content
from agents.interview_agent import answer_question
from agents.planner_agent import generate_daily_plan
from agents.question_agent import generate_interview_question
from agents.enhanced_evaluator_agent import EnhancedEvaluatorAgent
from core.orchestrator import InterviewOrchestrator
from core.content_manager import ContentManager
from rag.embed_store import store_article
from rag.retrieve import query_articles
from agents.llm import generate_answer

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interview Prep AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    new_user = models.User(
        user_id=user_id,
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"user_id": new_user.user_id, "email": new_user.email, "role": new_user.role})
    return {"user_id": new_user.user_id, "email": new_user.email, "token": token}


@app.post("/api/auth/login", response_model=schemas.AuthResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({"user_id": user.user_id, "email": user.email, "role": user.role})
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "token": token,
        "expires_in": 604800,
    }


# ── Interview flow (orchestrated, auth-protected) ─────────────────────────────

@app.post("/api/interview/start")
def start_interview(
    request: schemas.InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    orchestrator = InterviewOrchestrator(db)
    session_id = orchestrator.start_interview(current_user["user_id"])
    return {"session_id": session_id, "stage": "WARMUP", "company": request.company}


@app.post("/api/interview/next")
def get_next_question(
    request: schemas.InterviewNextRequest,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    orchestrator = InterviewOrchestrator(db)
    action = orchestrator.get_next_action(request.session_id)

    if action["action"] == "complete_interview":
        result = orchestrator.complete_interview(request.session_id)
        return {"action": "complete", "result": result}

    if action["action"] == "transition_stage":
        orchestrator.transition_to_next_stage(request.session_id)

    context = orchestrator.session_manager.get_session_context(request.session_id)
    question = generate_interview_question(
        stage=context["current_stage"],
        difficulty=context["difficulty_level"],
        company=request.company or "NVIDIA",
        weak_areas=context.get("weak_areas", "[]"),
    )

    return {
        "action": "ask",
        "question_id": str(uuid.uuid4()),
        "question": question,
        "stage": context["current_stage"],
        "difficulty": context["difficulty_level"],
    }


@app.post("/api/interview/submit")
def submit_answer(
    request: schemas.InterviewSubmitRequest,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    orchestrator = InterviewOrchestrator(db)
    context = orchestrator.session_manager.get_session_context(request.session_id)

    evaluator = EnhancedEvaluatorAgent()
    evaluation = evaluator.evaluate_response(
        question=request.question,
        user_response=request.answer,
        expected_answer="",
        session_context=context,
    )

    orchestrator.record_response(
        session_id=request.session_id,
        question_id=request.question_id,
        user_response=request.answer,
        evaluation=evaluation,
    )

    return {
        "evaluation": evaluation,
        "stage": context["current_stage"],
        "difficulty": context["difficulty_level"],
    }


@app.get("/api/interview/session/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    orchestrator = InterviewOrchestrator(db)
    try:
        return orchestrator.session_manager.get_session_context(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Simple ask / plan (legacy, no auth required) ──────────────────────────────

@app.get("/interview/question")
def get_interview_question():
    return {"question": generate_interview_question()}


@app.post("/ask")
def ask(req: schemas.AskRequest, db: Session = Depends(get_db)):
    answer = answer_question(req.question)
    db.add(models.ChatHistory(question=req.question, answer=answer))
    db.commit()
    return {"answer": answer}


@app.get("/plan/today")
def plan_today(company: str = "NVIDIA"):
    try:
        plan = generate_daily_plan(company=company)
        return {"plan": plan or "Plan generation returned empty output"}
    except Exception as e:
        return {"plan": f"Failed to generate plan: {str(e)}"}


# ── Blogs ─────────────────────────────────────────────────────────────────────

@app.post("/api/blogs/fetch")
def fetch_blogs(company: str = "NVIDIA", db: Session = Depends(get_db)):
    """Pull latest articles from the company RSS feed into ChromaDB."""
    count = fetch_and_store_blogs(company=company, db=db)
    return {"fetched": count, "company": company}


@app.get("/api/blogs/history")
def blogs_history(company: str = None, db: Session = Depends(get_db)):
    return get_blog_history(company=company, db=db)


@app.post("/api/blogs/ask")
def ask_blog(
    req: schemas.AskRequest,
    company: str = "NVIDIA",
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    """RAG-powered Q&A grounded in fetched blog articles."""
    docs = query_articles(req.question, k=5)
    context = "\n\n".join(
        f"[{d['metadata'].get('title', 'Article')}]\n{d['content']}" for d in docs
    )

    prompt = f"""You are a technical expert helping someone prepare for a {company} interview.
Answer the question below using ONLY the provided article context.
If the context doesn't cover the question, say so honestly.

Context:
{context or "No relevant articles found yet. Try fetching blogs first."}

Question: {req.question}

Answer:"""

    answer = generate_answer(prompt)
    return {"answer": answer, "sources": [d["metadata"].get("title") for d in docs]}


# ── n8n webhooks ──────────────────────────────────────────────────────────────

@app.post("/api/ingest/blog")
def ingest_blog_from_n8n(payload: dict, db: Session = Depends(get_db)):
    """n8n webhook: receives a fetched blog article and embeds it."""
    company = payload.get("company", "NVIDIA")
    title = payload.get("title", "")
    content = payload.get("content", "")
    url = payload.get("url", "")
    published = payload.get("published", datetime.now(timezone.utc).isoformat())

    if not title or not content:
        raise HTTPException(status_code=400, detail="title and content required")

    store_article(title, content, {"company": company, "url": url, "published": published, "source": "n8n"})
    db.add(models.DailyBlog(title=f"[{company}] {title}", content=content))
    db.commit()
    return {"status": "stored", "title": title}


@app.post("/api/content/ingest")
def ingest_question(payload: dict, db: Session = Depends(get_db)):
    """n8n webhook: ingest interview questions into RAG + question bank."""
    return ContentManager().ingest_question(payload)


# ── History & scores ─────────────────────────────────────────────────────────

@app.get("/history/chat")
def chat_history(db: Session = Depends(get_db)):
    return db.query(models.ChatHistory).all()


@app.get("/history/scores")
def score_history(db: Session = Depends(get_db)):
    """Returns numeric scores from the orchestrated interview sessions."""
    responses = (
        db.query(models.QuestionResponse)
        .order_by(models.QuestionResponse.created_at)
        .all()
    )
    return [
        {
            "timestamp": r.created_at.isoformat(),
            "score": r.evaluation_score or 0,
            "stage": r.stage,
            "feedback": r.evaluation_feedback,
        }
        for r in responses
    ]


# ── Legacy blog endpoints (kept for UI backward compat) ───────────────────────

@app.get("/blog/daily")
def daily_blog(company: str = "NVIDIA", db: Session = Depends(get_db)):
    title, content = generate_daily_blog_content(company=company)
    db.add(models.DailyBlog(title=f"[{company}] {title}", content=content))
    db.commit()
    return {"title": title, "content": content}


@app.get("/blog/history")
def blog_history(db: Session = Depends(get_db)):
    return db.query(models.DailyBlog).order_by(models.DailyBlog.created_at.desc()).all()
