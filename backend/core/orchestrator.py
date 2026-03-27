from sqlalchemy.orm import Session
from core.session_manager import SessionManager
from core.state_machine import InterviewStage, get_next_stage, can_transition, adjust_difficulty_for_next_stage
from api.models import QuestionResponse
from typing import Dict
import statistics


class InterviewOrchestrator:
    """Central orchestrator managing interview flow and agent coordination"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session_manager = SessionManager(db)
    
    def start_interview(self, user_id: str) -> str:
        """Start a new interview session"""
        session_id = self.session_manager.create_session(user_id)
        return session_id
    
    def get_next_action(self, session_id: str) -> Dict:
        """
        Determine next action in interview flow.
        Returns: {"action": "ask_question" | "transition_stage" | "complete_interview"}
        """
        context = self.session_manager.get_session_context(session_id)
        current_stage = InterviewStage(context["current_stage"])
        
        # Check if interview should be completed
        if current_stage == InterviewStage.WRAP_UP:
            return {"action": "complete_interview"}
        
        # Check if stage should transition
        if self.should_transition_stage(session_id):
            next_stage = get_next_stage(current_stage)
            return {"action": "transition_stage", "next_stage": next_stage.value}
        
        # Default: ask next question
        return {"action": "ask_question", "stage": current_stage.value}
    
    def should_transition_stage(self, session_id: str) -> bool:
        """Determine if current stage should transition to next"""
        context = self.session_manager.get_session_context(session_id)
        current_stage = InterviewStage(context["current_stage"])
        
        # TODO: Architecture deviation - Direct DB access for QuestionResponse queries
        # Spec requires all session persistence through SessionManager
        # Current implementation directly queries QuestionResponse at lines 47-50, 72-75, 134
        # Future refactoring: Move response queries to SessionManager methods
        
        # Get average score in current stage
        responses = self.db.query(QuestionResponse).filter_by(
            session_id=session_id,
            stage=current_stage.value
        ).all()
        
        avg_score = 0
        if responses:
            scores = [r.evaluation_score for r in responses if r.evaluation_score is not None]
            avg_score = statistics.mean(scores) if scores else 0
        
        return can_transition(
            stage=current_stage,
            time_in_stage=context["time_in_stage"],
            questions_answered=context["questions_in_stage"],
            avg_score=avg_score
        )
    
    def transition_to_next_stage(self, session_id: str):
        """Transition interview to next stage"""
        context = self.session_manager.get_session_context(session_id)
        current_stage = InterviewStage(context["current_stage"])
        next_stage = get_next_stage(current_stage)
        
        if next_stage:
            # Calculate average score in current stage for difficulty adjustment
            responses = self.db.query(QuestionResponse).filter_by(
                session_id=session_id,
                stage=current_stage.value
            ).all()
            
            avg_score = 0
            if responses:
                scores = [r.evaluation_score for r in responses if r.evaluation_score is not None]
                avg_score = statistics.mean(scores) if scores else 0
            
            # Adjust difficulty for next stage
            new_difficulty = adjust_difficulty_for_next_stage(avg_score, context["difficulty_level"])
            
            # Update session
            self.session_manager.update_stage(session_id, next_stage)
            self.session_manager.update_difficulty(session_id, new_difficulty)
    
    def record_response(
        self,
        session_id: str,
        question_id: str,
        user_response: str,
        evaluation: Dict
    ):
        """Record user response and evaluation"""
        import uuid
        from datetime import datetime
        
        context = self.session_manager.get_session_context(session_id)
        
        response = QuestionResponse(
            response_id=str(uuid.uuid4()),
            session_id=session_id,
            question_text=question_id,
            user_answer=user_response,
            evaluation_score=evaluation.get("overall_score", 0),
            evaluation_feedback=evaluation.get("feedback", ""),
            technical_accuracy=evaluation.get("technical_accuracy", 0),
            depth_score=evaluation.get("depth_of_understanding", 0),
            clarity_score=evaluation.get("communication_clarity", 0),
            time_taken=evaluation.get("time_taken", 0),
            stage=context["current_stage"]
        )
        
        self.db.add(response)
        self.db.commit()
        
        # Update conversation history
        self.session_manager.add_to_conversation(session_id, question_id, user_response)
        
        # Update weak/strong areas
        if "identified_weak_areas" in evaluation:
            for area in evaluation["identified_weak_areas"]:
                self.session_manager.add_weak_area(session_id, area)
        
        if "identified_strong_areas" in evaluation:
            for area in evaluation["identified_strong_areas"]:
                self.session_manager.add_strong_area(session_id, area)
    
    def complete_interview(self, session_id: str) -> Dict:
        """Complete interview and generate final evaluation"""
        # Calculate overall score
        responses = self.db.query(QuestionResponse).filter_by(session_id=session_id).all()
        
        if responses:
            scores = [r.evaluation_score for r in responses if r.evaluation_score is not None]
            overall_score = statistics.mean(scores) if scores else 0
        else:
            overall_score = 0
        
        self.session_manager.complete_session(session_id, overall_score)
        
        context = self.session_manager.get_session_context(session_id)
        
        return {
            "overall_score": overall_score,
            "weak_areas": context["weak_areas"],
            "strong_areas": context["strong_areas"],
            "total_questions": len(responses)
        }
