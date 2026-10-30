from typing import Protocol

class Client(Protocol):
    def name(self) -> str: ...

class FakeClient:
    def name(self) -> str:
        return "fake"

class OpenAIClient:
    def name(self) -> str:
        return "openai"

def create_client(provider: str) -> Client:
    if provider == "fake":
        return FakeClient()
    if provider == "openai":
        return OpenAIClient()
    raise ValueError(f"unsupported provider: {provider}")

print(create_client("fake").name())
