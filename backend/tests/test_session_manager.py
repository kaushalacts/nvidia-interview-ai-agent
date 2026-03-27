import pytest
from core.session_manager import SessionManager
from core.state_machine import InterviewStage
from api.database import Base
from api.models import User, InterviewSession, QuestionResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

@pytest.fixture(scope="function")
def test_db_engine():
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session_manager(test_db_engine):
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestSessionLocal()
    yield SessionManager(db)
    db.close()

def test_create_new_session(session_manager, test_db_engine):
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestSessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = session_manager.create_session("user1")
    
    assert session_id is not None
    session = session_manager.get_session(session_id)
    assert session.current_stage == InterviewStage.WARMUP.value
    assert session.difficulty_level == 3
    assert session.status == "in_progress"

def test_update_session_stage(session_manager, test_db_engine):
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestSessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = session_manager.create_session("user1")
    session_manager.update_stage(session_id, InterviewStage.TECHNICAL_DEEP_DIVE)
    
    session = session_manager.get_session(session_id)
    assert session.current_stage == InterviewStage.TECHNICAL_DEEP_DIVE.value

def test_add_weak_area(session_manager, test_db_engine):
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestSessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = session_manager.create_session("user1")
    session_manager.add_weak_area(session_id, "concurrency")
    session_manager.add_weak_area(session_id, "system design")
    
    session = session_manager.get_session(session_id)
    weak_areas = json.loads(session.weak_areas)
    assert "concurrency" in weak_areas
    assert "system design" in weak_areas

def test_get_session_context(session_manager, test_db_engine):
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestSessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = session_manager.create_session("user1")
    context = session_manager.get_session_context(session_id)
    
    assert context["session_id"] == session_id
    assert context["current_stage"] == InterviewStage.WARMUP.value
    assert context["difficulty_level"] == 3
    assert isinstance(context["weak_areas"], list)
    assert isinstance(context["conversation_history"], list)
