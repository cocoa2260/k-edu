import os

import httpx

from app.config import required_env
from app.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUpstreamError,
)


class OllamaProvider:
    def __init__(self) -> None:
        self._model = required_env("OLLAMA_MODEL")
        self._base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, message: str) -> str:
        try:
            response = httpx.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "user", "content": message}
                    ],
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError() from exc
        except httpx.RequestError as exc:
            raise ProviderConnectionError() from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderUpstreamError() from exc

        try:
            content = response.json()["message"]["content"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderResponseError() from exc

        if not isinstance(content, str) or not content.strip():
            raise ProviderResponseError()
        return content
