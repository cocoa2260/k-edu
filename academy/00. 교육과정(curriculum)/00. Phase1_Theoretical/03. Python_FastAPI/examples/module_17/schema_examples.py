from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class ChatRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"question": "FastAPI란?"}
    })
    question: str

@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    return {"answer": request.question}
