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


def test_transition_to_next_stage(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    
    # Verify initial stage
    context = orchestrator.session_manager.get_session_context(session_id)
    assert context["current_stage"] == InterviewStage.WARMUP.value
    
    # Transition to next stage
    orchestrator.transition_to_next_stage(session_id)
    
    # Verify stage changed
    context = orchestrator.session_manager.get_session_context(session_id)
    assert context["current_stage"] == InterviewStage.TECHNICAL_DEEP_DIVE.value


def test_record_response(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    
    # Record a response
    evaluation = {
        "overall_score": 8.5,
        "feedback": "Good answer",
        "technical_accuracy": 9.0,
        "depth_of_understanding": 8.0,
        "communication_clarity": 8.5,
        "time_taken": 120,
        "identified_weak_areas": ["concurrency"],
        "identified_strong_areas": ["algorithms"]
    }
    
    orchestrator.record_response(
        session_id=session_id,
        question_id="q1",
        user_response="My answer to the question",
        evaluation=evaluation
    )
    
    # Verify response was recorded in DB
    from api.models import QuestionResponse
    db_session = SessionLocal()
    response = db_session.query(QuestionResponse).filter_by(session_id=session_id).first()
    assert response is not None
    assert response.evaluation_score == 8.5
    assert response.technical_accuracy == 9.0
    
    # Verify conversation history updated
    context = orchestrator.session_manager.get_session_context(session_id)
    assert len(context["conversation_history"]) > 0
    
    # Verify weak/strong areas updated
    assert "concurrency" in context["weak_areas"]
    assert "algorithms" in context["strong_areas"]
    
    db_session.close()


def test_complete_interview(orchestrator, test_db):
    SessionLocal = sessionmaker(bind=test_db)
    db = SessionLocal()
    user = User(user_id="user1", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.close()
    
    session_id = orchestrator.start_interview("user1")
    
    # Record some responses
    evaluation1 = {
        "overall_score": 8.0,
        "feedback": "Good",
        "technical_accuracy": 8.0,
        "depth_of_understanding": 7.5,
        "communication_clarity": 8.5,
        "identified_weak_areas": ["memory management"],
        "identified_strong_areas": ["data structures"]
    }
    
    evaluation2 = {
        "overall_score": 9.0,
        "feedback": "Excellent",
        "technical_accuracy": 9.5,
        "depth_of_understanding": 8.5,
        "communication_clarity": 9.0,
        "identified_weak_areas": [],
        "identified_strong_areas": ["problem solving"]
    }
    
    orchestrator.record_response(
        session_id=session_id,
        question_id="q1",
        user_response="Answer 1",
        evaluation=evaluation1
    )
    
    orchestrator.record_response(
        session_id=session_id,
        question_id="q2",
        user_response="Answer 2",
        evaluation=evaluation2
    )
    
    # Complete interview
    result = orchestrator.complete_interview(session_id)
    
    # Verify results
    assert result["overall_score"] == 8.5  # Average of 8.0 and 9.0
    assert result["total_questions"] == 2
    assert "memory management" in result["weak_areas"]
    assert "data structures" in result["strong_areas"]
    assert "problem solving" in result["strong_areas"]
    
    # Verify session marked as completed by checking directly from DB
    session = orchestrator.session_manager.get_session(session_id)
    assert session.status == "completed"
    assert session.overall_score == 8.5
