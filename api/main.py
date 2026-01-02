from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api.database import SessionLocal, engine
from api import models, schemas
from agents.interview_agent import answer_question
from agents.planner_agent import generate_daily_plan
from agents.evaluator_agent import evaluate_answer
from agents.question_agent import generate_interview_question


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/interview/question")
def get_interview_question():
    return {"question": generate_interview_question()}
# -------------------------
# Planner
# -------------------------
@app.get("/plan/today")
def plan_today():
    return {"plan": generate_daily_plan()}

# -------------------------
# Interview AI
# -------------------------
@app.post("/ask")
def ask(req: schemas.AskRequest, db: Session = Depends(get_db)):
    answer = answer_question(req.question)

    db.add(models.ChatHistory(
        question=req.question,
        answer=answer
    ))
    db.commit()

    return {"answer": answer}

# -------------------------
# Evaluation
# -------------------------
@app.post("/evaluate")
def evaluate(req: schemas.EvalRequest, db: Session = Depends(get_db)):
    feedback = evaluate_answer(req.question, req.answer)

    score = next(
        (line for line in feedback.splitlines() if "score" in line.lower()),
        "Score not found"
    )

    db.add(models.Evaluation(
        question=req.question,
        score=score,
        feedback=feedback
    ))
    db.commit()

    return {"evaluation": feedback}

# -------------------------
# History / Progress
# -------------------------
@app.get("/history/chat")
def chat_history(db: Session = Depends(get_db)):
    return db.query(models.ChatHistory).all()

@app.get("/history/scores")
def score_history(db: Session = Depends(get_db)):
    return db.query(models.Evaluation).all()

