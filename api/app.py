# api/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "NVIDIA Interview AI Agent running"}

