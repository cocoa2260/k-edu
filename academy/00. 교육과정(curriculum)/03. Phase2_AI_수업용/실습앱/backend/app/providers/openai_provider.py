"""선택형 OpenAI Provider. API 사용료가 발생할 수 있습니다."""
from app.config import required_env
from app.providers.errors import (
    ProviderConnectionError, ProviderResponseError, ProviderTimeoutError, ProviderUpstreamError,
)


class OpenAIProvider:
    def __init__(self) -> None:
        from openai import OpenAI
        self._model = required_env('OPENAI_MODEL')
        self._client = OpenAI(api_key=required_env('OPENAI_API_KEY'), timeout=60.0, max_retries=0)

    @property
    def provider_name(self) -> str:
        return 'openai'

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, message: str) -> str:
        from openai import APIConnectionError, APITimeoutError, APIStatusError, OpenAIError
        try:
            response = self._client.responses.create(model=self._model, input=message)
        except APITimeoutError as exc:
            raise ProviderTimeoutError() from exc
        except APIConnectionError as exc:
            raise ProviderConnectionError() from exc
        except (APIStatusError, OpenAIError) as exc:
            raise ProviderUpstreamError() from exc
        answer = response.output_text
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderResponseError()
        return answer
