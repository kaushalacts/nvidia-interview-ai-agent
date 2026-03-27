import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.orchestrator import InterviewOrchestrator
from core.state_machine import InterviewStage
from api.database import Base
from api.models import User


@pytest.fixture(scope="function")
def test_db():
    # Use in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def orchestrator(test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    yield InterviewOrchestrator(db)
    db.close()


def test_start_interview(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    assert session_id is not None
    
    context = orchestrator.session_manager.get_session_context(session_id)
    assert context["current_stage"] == InterviewStage.WARMUP.value


def test_should_transition_stage(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    
    # Should not transition immediately (not enough time/questions)
    should_transition = orchestrator.should_transition_stage(session_id)
    assert should_transition == False


def test_get_next_action(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    action = orchestrator.get_next_action(session_id)
    
    assert action["action"] in ["ask_question", "transition_stage", "complete_interview"]
