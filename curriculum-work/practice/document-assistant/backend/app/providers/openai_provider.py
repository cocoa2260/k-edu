from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    OpenAI,
    OpenAIError,
)

from app.config import required_env
from app.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUpstreamError,
)


class OpenAIProvider:
    def __init__(self) -> None:
        api_key = required_env("OPENAI_API_KEY")
        self._model = required_env("OPENAI_MODEL")
        self._client = OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=0,  # 수업의 오류 경로를 관찰하기 위한 설정
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, message: str) -> str:
        try:
            response = self._client.responses.create(
                model=self._model,
                input=message,
            )
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
