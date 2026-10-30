from typing import Literal
from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    text: str = Field(min_length=10, max_length=5000)
    language: Literal["ko", "en"] = "ko"
    max_sentences: int = Field(default=3, ge=1, le=10)

request = SummaryRequest(text="FastAPI는 Python 기반 웹 프레임워크입니다.")
print(request)
