from pydantic import BaseModel, model_validator

class GenerationRequest(BaseModel):
    min_tokens: int = 10
    max_tokens: int = 100

    @model_validator(mode="after")
    def validate_range(self):
        if self.min_tokens > self.max_tokens:
            raise ValueError("min_tokens는 max_tokens보다 클 수 없습니다.")
        return self

print(GenerationRequest(min_tokens=20, max_tokens=50))
