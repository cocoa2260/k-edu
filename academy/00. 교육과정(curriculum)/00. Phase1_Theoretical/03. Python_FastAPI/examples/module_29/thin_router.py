from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

class ChatService:
    def answer(self, question: str) -> str:
        return question.strip().upper()

service = ChatService()

@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    return {"answer": service.answer(request.question)}
