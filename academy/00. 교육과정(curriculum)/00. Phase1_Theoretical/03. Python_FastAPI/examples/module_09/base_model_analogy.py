class RequestModel:
    def validate_text(self, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("빈 문자열은 허용하지 않습니다.")
        return normalized

class ChatRequest(RequestModel):
    def __init__(self, question: str):
        self.question = self.validate_text(question)

print(ChatRequest("  상속이란?  ").question)
