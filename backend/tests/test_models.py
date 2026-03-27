import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import User, InterviewSession
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

