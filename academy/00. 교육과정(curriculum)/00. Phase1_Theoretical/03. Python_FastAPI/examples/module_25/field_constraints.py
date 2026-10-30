from pydantic import BaseModel, Field, ValidationError

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=100)
    top_k: int = Field(default=3, ge=1, le=10)

for payload in [{"question": "FastAPI?"}, {"question": "", "top_k": 99}]:
    try:
        print(ChatRequest.model_validate(payload))
    except ValidationError as error:
        print(error.errors())
