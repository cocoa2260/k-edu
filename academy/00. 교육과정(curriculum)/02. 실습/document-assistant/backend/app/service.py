from dataclasses import dataclass

from app.providers.base import AIProvider


@dataclass(frozen=True)
class ChatResult:
    provider: str
    model: str
    answer: str


class AIService:
    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def chat(self, message: str) -> ChatResult:
        return ChatResult(
            provider=self._provider.provider_name,
            model=self._provider.model_name,
            answer=self._provider.generate(message),
        )
