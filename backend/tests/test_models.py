import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import User, InterviewSession, QuestionResponse, QuestionBank
from api.database import Base
import json


@pytest.fixture(scope="function")
def test_db():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False)
    yield SessionLocal
    Base.metadata.drop_all(bind=engine)


def test_user_model_creation(test_db):
    db = test_db()
    
    user = User(
        user_id="test-uuid",
        email="test@example.com",
        password_hash="hashed_pw",
        full_name="Test User",
        role="user"
    )
    db.add(user)
    db.commit()
    
    retrieved = db.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.full_name == "Test User"
    assert retrieved.role == "user"
    db.close()


def test_interview_session_model(test_db):
    db = test_db()
    
    user = User(user_id="user1", email="user1@test.com", password_hash="hash", full_name="User One")
    db.add(user)
    db.commit()
    
    session = InterviewSession(
        session_id="session1",
        user_id="user1",
        current_stage="WARMUP",
        difficulty_level=3,
        weak_areas=json.dumps(["concurrency"]),
        strong_areas=json.dumps(["algorithms"]),
        conversation_history=json.dumps([]),
        status="in_progress"
    )
    db.add(session)
    db.commit()
    
    retrieved = db.query(InterviewSession).filter_by(session_id="session1").first()
    assert retrieved.current_stage == "WARMUP"
    assert retrieved.difficulty_level == 3
    assert retrieved.user.email == "user1@test.com"
    db.close()


def test_question_response_model(test_db):
    db = test_db()
    
    user = User(user_id="user1", email="user1@test.com", password_hash="hash")
    session = InterviewSession(session_id="sess1", user_id="user1", current_stage="WARMUP", status="in_progress")
    db.add_all([user, session])
    db.commit()
    
    response = QuestionResponse(
        response_id="resp1",
        session_id="sess1",
        question_text="What is Python GIL?",
        user_answer="Global Interpreter Lock...",
        evaluation_score=85.0,
        evaluation_feedback="Good answer",
        technical_accuracy=90.0,
        depth_score=80.0,
        clarity_score=85.0,
        time_taken=120,
        stage="WARMUP"
    )
    db.add(response)
    db.commit()
    
    retrieved = db.query(QuestionResponse).filter_by(response_id="resp1").first()
    assert retrieved.evaluation_score == 85.0
    assert retrieved.stage == "WARMUP"
    assert retrieved.session.session_id == "sess1"
    db.close()


def test_question_bank_model(test_db):
    db = test_db()
    
    question = QuestionBank(
        question_id="q1",
        question_text="Explain async/await in Python",
        expected_answer="Async/await enables...",
        topic_tags=json.dumps(["python", "concurrency"]),
        difficulty_level=3,
        stage_suitable="technical",
        source_url="https://example.com",
        usage_count=5,
        avg_user_score=75.5,
        is_active=True
    )
    db.add(question)
    db.commit()
    
    retrieved = db.query(QuestionBank).filter_by(question_id="q1").first()
    assert retrieved.difficulty_level == 3
    assert retrieved.stage_suitable == "technical"
    assert retrieved.is_active == True
    db.close()

