from typing import Protocol

class TextClient(Protocol):
    def generate(self, text: str) -> str: ...

class FakeTextClient:
    def generate(self, text: str) -> str:
        return text.upper()

class SummaryService:
    def __init__(self, client: TextClient):
        self.client = client

    def summarize(self, text: str) -> str:
        return self.client.generate(text)

def router_handler(text: str, service: SummaryService) -> dict[str, str]:
    return {"summary": service.summarize(text)}

print(router_handler("layered", SummaryService(FakeTextClient())))
