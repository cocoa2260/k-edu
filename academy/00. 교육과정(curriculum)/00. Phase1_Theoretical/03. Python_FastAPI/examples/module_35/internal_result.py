from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class AIResult:
    text: str

class AIClient(Protocol):
    def generate(self, prompt: str) -> AIResult: ...

class FakeClient:
    def generate(self, prompt: str) -> AIResult:
        return AIResult(text=f"fake:{prompt}")

client: AIClient = FakeClient()
print(client.generate("boundary"))
