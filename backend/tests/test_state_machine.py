import pytest
from core.state_machine import InterviewStage, get_next_stage, can_transition, get_stage_requirements, adjust_difficulty_for_next_stage


def test_interview_stages_defined():
    assert InterviewStage.WARMUP.value == "WARMUP"
    assert InterviewStage.TECHNICAL_DEEP_DIVE.value == "TECHNICAL_DEEP_DIVE"
    assert InterviewStage.PROBLEM_SOLVING.value == "PROBLEM_SOLVING"
    assert InterviewStage.BEHAVIORAL.value == "BEHAVIORAL"
    assert InterviewStage.WRAP_UP.value == "WRAP_UP"


def test_stage_progression():
    assert get_next_stage(InterviewStage.WARMUP) == InterviewStage.TECHNICAL_DEEP_DIVE
    assert get_next_stage(InterviewStage.TECHNICAL_DEEP_DIVE) == InterviewStage.PROBLEM_SOLVING
    assert get_next_stage(InterviewStage.PROBLEM_SOLVING) == InterviewStage.BEHAVIORAL
    assert get_next_stage(InterviewStage.BEHAVIORAL) == InterviewStage.WRAP_UP
    assert get_next_stage(InterviewStage.WRAP_UP) is None


def test_can_transition_time_based():
    # Warmup needs 5 minutes (300 seconds)
    assert can_transition(InterviewStage.WARMUP, time_in_stage=300, questions_answered=2, avg_score=70) == True
    assert can_transition(InterviewStage.WARMUP, time_in_stage=240, questions_answered=2, avg_score=70) == False


def test_can_transition_question_minimum():
    # Must meet minimum question requirement
    assert can_transition(InterviewStage.WARMUP, time_in_stage=300, questions_answered=1, avg_score=70) == False
    assert can_transition(InterviewStage.WARMUP, time_in_stage=300, questions_answered=3, avg_score=70) == True


def test_stage_requirements():
    warmup_req = get_stage_requirements(InterviewStage.WARMUP)
    assert warmup_req["min_time_seconds"] == 300
    assert warmup_req["min_questions"] == 2


def test_difficulty_adjustment():
    # Low score decreases difficulty
    assert adjust_difficulty_for_next_stage(current_stage_avg_score=30, current_difficulty=3) == 2
    # High score increases difficulty
    assert adjust_difficulty_for_next_stage(current_stage_avg_score=85, current_difficulty=3) == 4
    # Medium score maintains difficulty
    assert adjust_difficulty_for_next_stage(current_stage_avg_score=60, current_difficulty=3) == 3
