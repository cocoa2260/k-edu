from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("공백만 있는 질문은 허용하지 않습니다.")
        return value.strip()


class ChatResponse(BaseModel):
    provider: str
    model: str
    answer: str
