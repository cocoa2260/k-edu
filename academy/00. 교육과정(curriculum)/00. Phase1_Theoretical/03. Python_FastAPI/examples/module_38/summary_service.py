from typing import Protocol

class TextClient(Protocol):
    def generate(self, prompt: str) -> str: ...

class FakeClient:
    def generate(self, prompt: str) -> str:
        return f"summary:{prompt[:20]}"

class SummaryService:
    def __init__(self, client: TextClient):
        self.client = client

    def summarize(self, text: str) -> str:
        prompt = f"다음 내용을 요약하세요.\n{text.strip()}"
        return self.client.generate(prompt)

print(SummaryService(FakeClient()).summarize("긴 문서 내용"))
