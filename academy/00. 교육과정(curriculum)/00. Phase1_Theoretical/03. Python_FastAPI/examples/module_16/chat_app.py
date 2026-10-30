from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    text: str

@app.post("/questions")
async def create_question(question: Question) -> dict[str, str]:
    return {"answer": f"received: {question.text}"}
