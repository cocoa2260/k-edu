from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    return {"answer": f"fake answer: {request.question}"}

# 실행: uvicorn ai_boundary_fastapi:app --reload
