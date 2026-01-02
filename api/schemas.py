from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str

class EvalRequest(BaseModel):
    question: str
    answer: str

