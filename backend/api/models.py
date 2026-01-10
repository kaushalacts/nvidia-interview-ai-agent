from sqlalchemy import Column, Integer, Text, DateTime, String
from datetime import datetime
from api.database import Base

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
