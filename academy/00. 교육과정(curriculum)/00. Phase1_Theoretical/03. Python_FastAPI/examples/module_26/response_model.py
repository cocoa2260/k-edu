from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatResponse(BaseModel):
    answer: str
    model: str

@app.get("/sample", response_model=ChatResponse)
def sample() -> ChatResponse:
    return ChatResponse(answer="hello", model="fake")
