from sqlalchemy.orm import Session
from api.models import InterviewSession, QuestionResponse
from core.state_machine import InterviewStage
from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid
import json

class SessionManager:
    """Manages interview session lifecycle and state"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: str) -> str:
        """Create a new interview session"""
        session_id = str(uuid.uuid4())
        
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            current_stage=InterviewStage.WARMUP.value,
            stage_start_time=datetime.now(timezone.utc),
            difficulty_level=3,
            weak_areas=json.dumps([]),
            strong_areas=json.dumps([]),
            conversation_history=json.dumps([]),
            status="in_progress"
        )
        
        self.db.add(session)
        self.db.commit()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve session by ID"""
        return self.db.query(InterviewSession).filter_by(session_id=session_id).first()
    
    def update_stage(self, session_id: str, new_stage: InterviewStage):
        """Update session stage"""
        session = self.get_session(session_id)
        if session:
            session.current_stage = new_stage.value
            session.stage_start_time = datetime.now(timezone.utc)
            self.db.commit()
    
    def update_difficulty(self, session_id: str, new_difficulty: int):
        """Update session difficulty level"""
        session = self.get_session(session_id)
        if session:
            session.difficulty_level = new_difficulty
            self.db.commit()
    
    def add_weak_area(self, session_id: str, area: str):
        """Add identified weak area"""
        session = self.get_session(session_id)
        if session:
            weak_areas = json.loads(session.weak_areas or "[]")
            if area not in weak_areas:
                weak_areas.append(area)
                session.weak_areas = json.dumps(weak_areas)
                self.db.commit()
    
    def add_strong_area(self, session_id: str, area: str):
        """Add identified strong area"""
        session = self.get_session(session_id)
        if session:
            strong_areas = json.loads(session.strong_areas or "[]")
            if area not in strong_areas:
                strong_areas.append(area)
                session.strong_areas = json.dumps(strong_areas)
                self.db.commit()
    
    def add_to_conversation(self, session_id: str, question: str, answer: str):
        """Add Q&A to conversation history"""
        session = self.get_session(session_id)
        if session:
            history = json.loads(session.conversation_history or "[]")
            history.append({
                "question": question,
                "answer": answer,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            session.conversation_history = json.dumps(history)
            self.db.commit()
    
    def get_session_context(self, session_id: str) -> Dict:
        """Get full session context for agents"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Calculate time in current stage
        time_in_stage = 0
        if session.stage_start_time:
            # Make stage_start_time timezone-aware if it's naive
            stage_start = session.stage_start_time
            if stage_start.tzinfo is None:
                stage_start = stage_start.replace(tzinfo=timezone.utc)
            time_in_stage = int((datetime.now(timezone.utc) - stage_start).total_seconds())
        
        # Get responses in current stage
        responses = self.db.query(QuestionResponse).filter_by(
            session_id=session_id,
            stage=session.current_stage
        ).all()
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "current_stage": session.current_stage,
            "stage_start_time": session.stage_start_time.isoformat() if session.stage_start_time else None,
            "difficulty_level": session.difficulty_level,
            "weak_areas": json.dumps(json.loads(session.weak_areas or "[]")),
            "strong_areas": json.dumps(json.loads(session.strong_areas or "[]")),
            "conversation_history": json.dumps(json.loads(session.conversation_history or "[]")),
            "time_in_stage": time_in_stage,
            "questions_in_stage": len(responses)
        }
    
    def complete_session(self, session_id: str, overall_score: float):
        """Mark session as completed"""
        session = self.get_session(session_id)
        if session:
            session.status = "completed"
            session.overall_score = overall_score
            session.completed_at = datetime.now(timezone.utc)
            self.db.commit()
    
    def get_user_incomplete_sessions(self, user_id: str) -> List[InterviewSession]:
        """Get all incomplete sessions for a user"""
        return self.db.query(InterviewSession).filter_by(
            user_id=user_id,
            status="in_progress"
        ).all()
