from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path
from agents.interview_agent import answer_question
from agents.planner_agent import generate_daily_plan
from agents.evaluator_agent import evaluate_answer
from pydantic import BaseModel

from rag.embed_store import store_article

app = FastAPI()

DATA_DIR = Path("data/articles")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Article(BaseModel):
    title: str
    url: str
    content: str
    source: str = "nvidia"
    fetched_at: datetime | None = None

class EvaluationRequest(BaseModel):
    question: str
    answer: str

@app.post("/evaluate")
def evaluate(req: EvaluationRequest):
    feedback = evaluate_answer(req.question, req.answer)
    return {
        "question": req.question,
        "evaluation": feedback
    }
@app.get("/plan/today")
def daily_plan():
    plan = generate_daily_plan()
    return {
        "date": str(__import__("datetime").date.today()),
        "plan": plan
    }
@app.get("/ask")
def ask(question: str):
    answer = answer_question(question)
    return {
        "question": question,
        "answer": answer
    }
def root():
    return {"status": "NVIDIA Interview AI Agent running"}

@app.post("/ingest")
def ingest_article(article: Article):
    # 1️⃣ Save raw article to disk
    filename = article.title.replace(" ", "_").lower()[:50]
    filepath = DATA_DIR / f"{filename}.json"

    with open(filepath, "w") as f:
        json.dump(article.model_dump(), f, indent=2, default=str)

    # 2️⃣ Store in vector DB (RAG memory)
    # Ensure content is always a string
    content_text = (
        article.content
        if isinstance(article.content, str)
        else json.dumps(article.content, indent=2, default=str)
    )      

    store_article(
        title=article.title,
        content=content_text,
        metadata={
            "url": article.url,
            "source": article.source
        }
    )


    return {
        "message": "Article stored + embedded successfully",
        "file": str(filepath)
    }
from rag.retrieve import query_articles

@app.get("/search")
def search_articles(q: str):
    results = query_articles(q)
    return {
        "query": q,
        "results": results
    }

