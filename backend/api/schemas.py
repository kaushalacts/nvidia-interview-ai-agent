from pydantic import BaseModel, EmailStr
from typing import Optional


class AskRequest(BaseModel):
    question: str


class EvalRequest(BaseModel):
    question: str
    answer: str


class BlogResponse(BaseModel):
    title: str
    content: str


# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    role: Optional[str] = None
    token: str
    expires_in: Optional[int] = None


# Interview flow
class InterviewStartRequest(BaseModel):
    company: Optional[str] = "NVIDIA"


class InterviewNextRequest(BaseModel):
    session_id: str
    company: Optional[str] = "NVIDIA"


class InterviewSubmitRequest(BaseModel):
    session_id: str
    question_id: str
    question: str
    answer: str
