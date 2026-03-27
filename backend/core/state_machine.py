from enum import Enum
from typing import Optional, Dict


class InterviewStage(Enum):
    """Interview stage definitions"""
    WARMUP = "WARMUP"
    TECHNICAL_DEEP_DIVE = "TECHNICAL_DEEP_DIVE"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    BEHAVIORAL = "BEHAVIORAL"
    WRAP_UP = "WRAP_UP"


STAGE_ORDER = [
    InterviewStage.WARMUP,
    InterviewStage.TECHNICAL_DEEP_DIVE,
    InterviewStage.PROBLEM_SOLVING,
    InterviewStage.BEHAVIORAL,
    InterviewStage.WRAP_UP
]

STAGE_REQUIREMENTS = {
    InterviewStage.WARMUP: {
        "min_time_seconds": 300,  # 5 minutes
        "min_questions": 2,
        "description": "Introductory questions to establish baseline"
    },
    InterviewStage.TECHNICAL_DEEP_DIVE: {
        "min_time_seconds": 900,  # 15 minutes
        "min_questions": 3,
        "description": "Core technical assessment"
    },
    InterviewStage.PROBLEM_SOLVING: {
        "min_time_seconds": 600,  # 10 minutes
        "min_questions": 2,
        "description": "Algorithm and system design challenges"
    },
    InterviewStage.BEHAVIORAL: {
        "min_time_seconds": 300,  # 5 minutes
        "min_questions": 2,
        "description": "Communication and experience assessment"
    },
    InterviewStage.WRAP_UP: {
        "min_time_seconds": 0,  # Automatic
        "min_questions": 0,
        "description": "Final evaluation and feedback"
    }
}


def get_next_stage(current_stage: InterviewStage) -> Optional[InterviewStage]:
    """Get the next stage in the interview progression"""
    try:
        current_index = STAGE_ORDER.index(current_stage)
        if current_index < len(STAGE_ORDER) - 1:
            return STAGE_ORDER[current_index + 1]
        return None
    except ValueError:
        return None


def can_transition(
    stage: InterviewStage,
    time_in_stage: int,
    questions_answered: int,
    avg_score: float
) -> bool:
    """
    Determine if interview can transition to next stage.
    """
    requirements = STAGE_REQUIREMENTS[stage]
    
    # Check minimum time
    if time_in_stage < requirements["min_time_seconds"]:
        return False
    
    # Check minimum questions
    if questions_answered < requirements["min_questions"]:
        return False
    
    # Additional logic: extend stage if performing poorly
    if avg_score < 40 and questions_answered < requirements["min_questions"] + 2:
        return False
    
    return True


def get_stage_requirements(stage: InterviewStage) -> Dict:
    """Get requirements for a specific stage"""
    return STAGE_REQUIREMENTS[stage]


def adjust_difficulty_for_next_stage(current_stage_avg_score: float, current_difficulty: int) -> int:
    """
    Adjust difficulty level for next stage based on performance.
    """
    if current_stage_avg_score < 40:
        return max(1, current_difficulty - 1)
    elif current_stage_avg_score > 80:
        return min(5, current_difficulty + 1)
    return current_difficulty
