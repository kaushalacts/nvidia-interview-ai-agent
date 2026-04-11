from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import SessionLocal, engine
from api import models, schemas
from api.auth import hash_password, verify_password, create_access_token
from agents.interview_agent import answer_question
from agents.planner_agent import generate_daily_plan
from agents.evaluator_agent import evaluate_answer
from agents.question_agent import generate_interview_question
from api.blog import generate_daily_blog
import uuid
from datetime import datetime, timezone

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NVIDIA Interview AI Agent")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(request.password)
    
    new_user = models.User(
        user_id=user_id,
        email=request.email,
        password_hash=hashed_password,
        full_name=request.full_name,
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    token = create_access_token({
        "user_id": new_user.user_id,
        "email": new_user.email,
        "role": new_user.role
    })
    
    return {
        "user_id": new_user.user_id,
        "email": new_user.email,
        "token": token
    }


@app.post("/api/auth/login", response_model=schemas.AuthResponse, status_code=status.HTTP_200_OK)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Find user by email
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last_login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Generate JWT token
    token = create_access_token({
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role
    })
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "token": token,
        "expires_in": 604800  # 7 days in seconds
    }

@app.get("/interview/question")
def get_interview_question():
    return {"question": generate_interview_question()}

@app.get("/plan/today")
def plan_today():
    try:
        plan = generate_daily_plan()

        if not plan:
            return {"plan": "Plan generation returned empyt output"}

        return {"plan": plan}

    except Exception as e: 
        print ("ERROR in /plan/todya:", str(e))
        return {"plan": f"Failed to generate plan:{str(e)}"}

    #plan = generate_daily_plan()
    #return {
    #        "plan": plan or "Plan generation failed"
    #        }

@app.post("/ask")
def ask(req: schemas.AskRequest, db: Session = Depends(get_db)):
    answer = answer_question(req.question)
    db.add(models.ChatHistory(question=req.question, answer=answer))
    db.commit()
    return {"answer": answer}

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

@app.get("/history/chat")
def chat_history(db: Session = Depends(get_db)):
    return db.query(models.ChatHistory).all()

@app.get("/history/scores")
def score_history(db: Session = Depends(get_db)):
    return db.query(models.Evaluation).all()

@app.get("/blog/daily", response_model=schemas.BlogResponse)
def daily_blog(db: Session = Depends(get_db)):
    title, content = generate_daily_blog()
    db.add(models.DailyBlog(title=title, content=content))
    db.commit()
    return {"title": title, "content": content}

@app.get("/blog/history")
def blog_history(db: Session = Depends(get_db)):
    return db.query(models.DailyBlog).order_by(
        models.DailyBlog.created_at.desc()
    ).all()
