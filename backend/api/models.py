from sqlalchemy import Column, Integer, Text, DateTime, String, Float, Boolean, ForeignKey
from datetime import datetime
from api.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255))
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    sessions = relationship("InterviewSession", back_populates="user")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    session_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    current_stage = Column(String(50), nullable=False)
    stage_start_time = Column(DateTime)
    difficulty_level = Column(Integer, default=3)
    weak_areas = Column(Text)  # JSON array
    strong_areas = Column(Text)  # JSON array
    conversation_history = Column(Text)  # JSON array
    overall_score = Column(Float)
    status = Column(String(20), default="in_progress")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    user = relationship("User", back_populates="sessions")
    responses = relationship("QuestionResponse", back_populates="session")


class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    response_id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    evaluation_score = Column(Float)
    evaluation_feedback = Column(Text)
    technical_accuracy = Column(Float)
    depth_score = Column(Float)
    clarity_score = Column(Float)
    time_taken = Column(Integer)  # seconds
    stage = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="responses")


class QuestionBank(Base):
    __tablename__ = "question_bank"
    
    question_id = Column(String(36), primary_key=True)
    question_text = Column(Text, nullable=False)
    expected_answer = Column(Text)
    topic_tags = Column(Text)  # JSON array
    difficulty_level = Column(Integer)
    stage_suitable = Column(String(50))
    source_url = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    avg_user_score = Column(Float)
    is_active = Column(Boolean, default=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    score = Column(Text)
    feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DailyBlog(Base):
    __tablename__ = "daily_blogs"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

