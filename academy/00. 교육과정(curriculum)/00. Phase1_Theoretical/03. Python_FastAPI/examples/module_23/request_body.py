from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    question: str
    temperature: float = 0.2

@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    return request.model_dump()
