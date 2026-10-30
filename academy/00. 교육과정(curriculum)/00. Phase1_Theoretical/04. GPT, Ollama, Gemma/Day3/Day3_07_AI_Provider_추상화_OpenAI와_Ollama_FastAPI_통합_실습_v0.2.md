# Day 3 - 7교시. AI Provider 추상화 — OpenAI와 Ollama를 하나의 FastAPI 구조로 통합하기 (강의용 v0.2)

## 개요 — 모델을 *또 호출*하는 시간이 아니라, 호출 코드를 *교체 가능하게* 만드는 시간

Day 1에는 OpenAI SDK를 이용한 Cloud 호출을, Day 2에는 Ollama Local API를 호출하는 FastAPI Backend를 만들었습니다. Day 3 - 6교시에는 Framework의 공통 Model Interface가 어떤 문제를 해결하는지 살펴보았습니다.

이제 같은 내용을 다시 구현하는 대신, **이미 존재하는 두 호출 방식을 하나의 변경 가능한 경계 뒤에 놓습니다.** 이번 교시의 변경 전후는 다음과 같습니다.

```text
변경 전
FastAPI Route → 특정 Ollama 호출 함수

변경 후
FastAPI Route → AIService → AIProvider 계약
                                  ├─ OpenAIProvider → OpenAI SDK
                                  └─ OllamaProvider → Ollama HTTP API
```

두 가지를 구별하세요.

- **호출을 통일한다:** Application이 `generate(message)`라는 하나의 계약을 사용합니다.
- **모델을 동일하게 만든다:** 이번 실습의 목적도 아니고, 추상화만으로 가능한 일도 아닙니다. 모델의 응답 내용·지원 기능·품질은 다를 수 있습니다.

이 교시가 끝나면 모델 선택 값을 바꾸고 Backend를 재시작해도 **Client의 URL·Request 필드·Response 필드를 고치지 않고** 같은 Chat 기능을 실행할 수 있어야 합니다.

> **학습 범위:** Python Backend 내부의 Provider Abstraction과 검증까지. React UI, CORS, Browser 취소, 전체 화면 상태 처리는 **다음 Day 3 - 8교시**의 고유 실습입니다.

---

# 1. 학습 목표와 완료 조건

수업 후 학생이 직접 제시해야 할 결과는 다음과 같습니다.

1. `AIProvider`를 Python `Protocol`로 정의하고 두 구현체가 같은 계약을 만족하게 한다.
2. OpenAI SDK 관련 코드는 `OpenAIProvider` 안에, Ollama HTTP 요청 코드는 `OllamaProvider` 안에만 둔다.
3. `Factory`가 설정에 따라 구현체를 만들고 `AIService`가 그 구현체를 주입받아 사용한다.
4. `POST /ai/chat`의 Request 구조를 **그대로 유지**하고 Response의 `provider`, `model`, `answer`를 일관되게 반환한다.
5. 선택하지 않은 Provider의 인증 정보까지 강제로 요구하지 않는다.
6. Provider 실패를 적절한 HTTP 응답으로 변환하되 비밀키나 내부 Traceback을 Client에 노출하지 않는다.
7. 실제 API 비용 없이 Mock Provider를 사용해 **같은 Client 계약으로 Provider 교체가 가능함**을 테스트한다.
8. 실행 오류가 설정·Provider·Service·Route 가운데 어디에서 시작됐는지 설명한다.

**완료 증거:** 작동하는 Backend 폴더, 선택된 Provider 응답, Mock 테스트 결과, 두 Provider를 교체했을 때 바뀌지 않은 API 계약에 대한 설명.

# 2. 선행 교시에서 가져오는 것과 이번에 새로 작성하는 것

| 구분 | 이미 배운 것 — 다시 가르치지 않음 | 이번에 새로 하는 일 |
|---|---|---|
| Day1 7교시 | OpenAI SDK·인증·`responses.create()` | SDK 호출을 전용 Provider로 격리 |
| Day1 8교시 | FastAPI·Schema·Structured Output | 기존 Route가 구현체를 몰라도 되도록 바꾸기 |
| Day2 8교시 | `httpx`·Ollama `/api/chat`·오류 처리 | 기존 Ollama 통신을 공통 Interface 구현으로 옮기기 |
| Day3 6교시 | Framework의 공통 Interface 역할 | **Framework 없이** 직접 `Protocol`과 Factory 구현 |
| Day3 8교시 | — | React·CORS·Frontend API 함수·취소·최종 통합은 미리 구현하지 않음 |

이번 교시에서는 FastAPI/Pydantic 기초나 OpenAI/Ollama 설치 방법을 다시 설명하지 않습니다. 이전 예제를 **어느 파일로 이동시키고, 무엇을 새로 연결할지**가 중심입니다.

# 3. 변경해야 하는 경계 찾기 — Route에서 Provider 분기를 없앤다

Day2 Backend에 OpenAI 호출을 단순히 추가한다면 다음과 같은 유혹이 생깁니다.

```python
# 이렇게 라우터에서 분기하는 방식은 이번 실습의 목표가 아닙니다.
if selected_provider == "openai":
    # OpenAI 전용 Request 생성 및 Response 처리
    ...
else:
    # Ollama 전용 JSON 생성 및 Response 처리
    ...
```

그렇게 되면 Route가 Provider 이름, URL, SDK, 응답 구조를 모두 알아야 합니다. Provider가 하나 더 추가될 때마다 Route가 수정됩니다.

수정 후에는 Route가 오직 **우리 Application의 Chat 기능**만 호출합니다.

```text
HTTP 요청 처리       FastAPI Route
업무 동작 조합       AIService
공통 호출 계약       AIProvider
Provider별 통신     OpenAIProvider / OllamaProvider
구현체 선택         Factory
```

**핵심 질문:** “OpenAI API의 Request 필드가 달라지면 `main.py`를 수정해야 할까?” 이 수업에서는 **Provider 내부만 수정**하는 것을 목표로 합니다. 단, 우리 API의 공통 계약 자체를 바꾸는 경우에는 Route/Schema 변경이 필요할 수 있습니다.

# 4. 교시가 끝날 때까지 지킬 API 계약

앞선 Backend의 Endpoint를 유지합니다.

| 항목 | 고정할 계약 | 이유 |
|---|---|---|
| Endpoint | `POST /ai/chat` | Client가 호출하는 주소 유지 |
| Request | `{"message": "..."}` | Provider 선택 값을 Client에서 받지 않음 |
| Response | `{"provider": "...", "model": "...", "answer": "..."}` | 실습에서 어떤 구현체가 동작했는지 관찰 |
| Provider 선택 | 서버 환경 변수 `AI_PROVIDER` | 선택 책임은 Backend에 있음 |
| 변경 시점 | 설정 변경 후 서버 재시작 | 한 요청 중간에 구현체가 임의로 바뀌지 않음 |

`provider`와 `model`은 **교실에서의 검증용 응답 필드**입니다. 운영 시스템에서 모델명을 공개할지는 별도 API 정책으로 결정할 수 있습니다. 본 교시에서는 비교 검증을 위해 유지합니다.

**이번 구현의 범위는 단일 문자열 메시지 → 문자열 응답입니다.** System Instruction, Tool Calling, Streaming, Multimodal처럼 Provider별 지원이 다른 기능은 이 계약에 무리하게 넣지 않습니다.

# 5. 실습 프로젝트 구조와 이전 코드의 이동 위치

Day2의 Ollama Service에서 출발해 다음 구조로 리팩터링합니다.

```text
day3_provider_abstraction/
├── app/
│   ├── __init__.py
│   ├── main.py                 # HTTP Route / Error Mapping
│   ├── schemas.py              # 우리 Client와 맺는 데이터 계약
│   ├── config.py               # 환경 변수 확인
│   ├── service.py              # AIProvider 계약에만 의존
│   └── providers/
│       ├── __init__.py
│       ├── base.py             # 공통 Protocol
│       ├── errors.py           # 공통 Provider 예외
│       ├── openai_provider.py  # OpenAI SDK 전용
│       ├── ollama_provider.py  # Ollama HTTP 전용
│       └── factory.py          # 구현체 선택
├── tests/
│   └── test_provider.py
├── .env.example
├── .env                       # 각자 로컬에서만 작성·Git 제외
└── requirements.txt
```

`__init__.py` 파일 두 개는 빈 파일로 생성해도 됩니다. Day2의 `ollama_service.py`에 있던 **모델명 설정·HTTP 호출·Response Parsing**은 이제 `OllamaProvider`의 책임입니다. `schemas.py`와 `/ai/chat`은 같은 역할을 유지합니다.

강사 점검: `main.py` 안에 `httpx.post(...)`나 `OpenAI(...).responses.create(...)`가 남아 있다면 리팩터링 목표를 달성하지 못한 것입니다.

# 6. 실습 환경과 설정 — 선택한 Provider만 준비하기

필요 패키지는 원본 강의 범위와 같습니다.

`requirements.txt`:

```text
fastapi
uvicorn[standard]
pydantic
httpx
openai
python-dotenv
pytest
```

`pytest`는 검증용 패키지입니다. 실제 배포와 검증을 분리한다면 별도 개발 의존성으로 관리할 수 있습니다.

기존 Python 가상환경을 사용하거나, 프로젝트 루트에서 다음을 실행합니다.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

`.env.example`:

```dotenv
AI_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

OPENAI_API_KEY=
OPENAI_MODEL=
```

`.env.example`을 `.env`로 복사한 다음 **실습에 사용할 Provider의 값만** 채웁니다. Day2에서 이미 준비한 Ollama 모델명을 재사용할 수 있습니다. OpenAI 실습에서는 유효한 API 사용 권한·비용 조건·Model ID가 필요합니다. **ChatGPT 사용 권한만으로 API 사용 가능 여부가 보장되지는 않습니다.**

`.env`를 Git에 올리지 않습니다. Model ID와 패키지 버전은 강사가 수업 환경에서 검증한 값을 사용하며 이 문서가 임의의 최신 모델명을 지정하지 않습니다. 학생 PC에서 사용한 설치 버전은 실습 기록에 남깁니다.

# 7. Python `Protocol` — Provider가 반드시 제공할 계약

`app/providers/base.py`:

```python
from typing import Protocol


class AIProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...

    @property
    def model_name(self) -> str:
        ...

    def generate(self, message: str) -> str:
        ...
```

`Protocol`은 여기서 **“AIService가 사용할 수 있는 객체의 구조”**를 선언합니다. `OpenAIProvider`가 반드시 `AIProvider`를 상속해야 하는 것은 아닙니다. 필요한 속성과 메서드를 만족하면 구조적 Typing 관점에서 계약을 구현할 수 있습니다.

| 계약 항목 | Service가 사용하는 이유 |
|---|---|
| `provider_name` | 어떤 구현체가 선택됐는지 응답에 표시 |
| `model_name` | 설정된 모델을 응답에 표시 |
| `generate(message)` | Provider와 관계없이 문자열 응답 받기 |

**중요한 한계:** `Protocol`을 선언했다고 런타임에서 자동으로 모든 Provider를 검사하거나, 출력 품질을 일치시키지는 않습니다. Type Checker와 테스트가 그 계약을 지키는 데 도움을 줍니다.

# 8. 공통 예외 — Provider별 라이브러리 오류를 Route까지 퍼뜨리지 않기

원본의 `main.py`는 `httpx.HTTPError`와 `OpenAIError`를 직접 알아야 했습니다. 이번에는 Provider 구현체가 내부 예외를 공통 오류로 변환하도록 보완합니다.

`app/providers/errors.py`:

```python
class AIProviderError(Exception):
    """외부 AI 호출에서 생긴 예외의 공통 부모 클래스."""


class ProviderConnectionError(AIProviderError):
    """Provider에 연결할 수 없음."""


class ProviderTimeoutError(AIProviderError):
    """Provider 응답 대기 시간 초과."""


class ProviderUpstreamError(AIProviderError):
    """Provider가 오류 상태를 반환함."""


class ProviderResponseError(AIProviderError):
    """성공 응답이라도 필요한 내용이 없거나 형식이 잘못됨."""
```

이것은 **Provider 교체 후에도 Route의 오류 처리 코드가 동일하도록** 만드는 추가 계약입니다. 연결 실패·시간 초과·원격 오류·응답 형식 오류의 차이는 Day2에서 배웠으므로 다시 정의하지 않고 코드에서 적용합니다.

# 9. `config.py` — 시작할 때 잘못된 설정을 발견하기

`app/config.py`:

```python
import os

from dotenv import load_dotenv


load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("<"):
        raise RuntimeError(f"설정이 필요합니다: {name}")
    return value
```

- 환경 변수를 읽고 비어 있는 값 또는 교재용 `<예시 값>`을 거부합니다.
- 오류 메시지에는 **환경 변수 이름만 표시**하고 API Key 내용은 넣지 않습니다.
- `OLLAMA_MODEL`이 없는 학생이 Ollama를 선택하면 시작 시 오류가 나야 합니다. 하지만 **Ollama를 선택했을 때 `OPENAI_API_KEY`가 비어 있는 것은 오류가 아닙니다.**

**수업 질문:** 두 Provider를 모두 실습하려면 모든 학생이 반드시 유료 Cloud API Key를 가져야 할까요? 아닙니다. Mock 테스트는 Key 없이 수행할 수 있고, Ollama만 호출하는 실습에서도 OpenAI Key는 요구하지 않습니다.

# 10. `OllamaProvider` — Day2의 HTTP 호출을 이사시키기

`app/providers/ollama_provider.py`:

```python
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
```

변경 전과 달리 Service는 `httpx`, Ollama의 URL, `message.content`라는 응답 경로를 몰라도 됩니다. **HTTP Payload 자체는 Day2 실습과 같습니다.** 단지 작성 책임이 이동했고, 외부로 노출되는 오류가 통일되었습니다.

주의: `stream: false`는 하나의 JSON Response를 받기 위한 기존 설정입니다. Streaming 구현은 이 교시의 범위가 아닙니다.

# 11. `OpenAIProvider` — SDK 호출을 같은 계약으로 감싸기

`app/providers/openai_provider.py`:

```python
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
```

Day1의 `responses.create()` 사용법을 다시 설명하는 교시가 아닙니다. **이번에 관찰할 것은** OpenAI 응답을 문자열로 바꾸는 작업을 끝내고, 동일한 `generate()` 계약으로 돌려보낸다는 점입니다.

`max_retries=0`은 오류 재현을 단순하게 하기 위한 *교육용 선택*입니다. 실제 운영에서는 재시도·제한 시간·사용량 정책을 검토해야 하지만 본 교시에서 재시도 체계를 구현하지 않습니다.

# 12. `Factory` — Provider 선택 분기는 한 곳에만 둔다

`app/providers/factory.py`:

```python
import os

from app.providers.base import AIProvider


def create_provider() -> AIProvider:
    provider_name = os.getenv(
        "AI_PROVIDER", "ollama"
    ).strip().lower()

    if provider_name == "ollama":
        from app.providers.ollama_provider import OllamaProvider
        return OllamaProvider()
    if provider_name == "openai":
        from app.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    raise RuntimeError(
        f"지원하지 않는 Provider 설정: {provider_name}"
    )
```

| 환경 변수 | 생성되는 구현체 | 이때 검증할 값 |
|---|---|---|
| `AI_PROVIDER=ollama` | `OllamaProvider` | `OLLAMA_MODEL` |
| `AI_PROVIDER=openai` | `OpenAIProvider` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| `AI_PROVIDER=unknown` | 생성 실패 | 설정 자체가 잘못됨 |

**이번 구현은 환경 변수에 따라 서버 시작 시 한 Provider를 선택합니다.** Factory는 선택한 Provider의 구현 모듈만 Import하므로, Ollama만 사용하는 동안 OpenAI SDK 모듈을 불러올 필요는 없습니다. 다만 전체 실습 환경은 `requirements.txt`에 나열된 패키지를 설치하는 것을 전제로 합니다. 요청마다 모델을 임의로 바꾸거나 Cloud 실패 시 Local로 자동 전환하는 기능은 없습니다. 그런 기능을 구현하지 않았는데 가능하다고 안내하지 마세요.

# 13. `AIService` — Concrete Provider를 모르는 업무 계층

`app/service.py`:

```python
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
```

`AIService`는 `OpenAIProvider`, `OllamaProvider`, `httpx`, `openai` 중 어느 것도 Import하지 않습니다. **이 Service 파일을 고치지 않고도 Provider를 교체할 수 있다는 것**이 이번 실습의 확인 지점입니다.

현재 Service의 기능은 작습니다. 목적은 새 Business Logic을 억지로 추가하는 것이 아니라, Provider의 교체 가능한 의존성을 **주입받는 구조**를 눈으로 확인하는 것입니다.

# 14. `schemas.py` — Client 계약 유지

`app/schemas.py`:

```python
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("공백만 있는 질문은 허용하지 않습니다.")
        return value.strip()


class ChatResponse(BaseModel):
    provider: str
    model: str
    answer: str
```

Day2에서 이미 다룬 입력 검증은 그대로 가져옵니다. 이번 차이는 **Response에 선택된 Provider와 Model 식별 정보를 포함한다는 것**입니다.

- 잘못된 `message`는 Provider 호출 전에 `422`로 거부합니다.
- `provider`를 Request 필드에 넣지 않습니다. Provider 선택은 이번 수업에서 Backend 설정 책임입니다.
- `answer`는 Provider별 내부 응답 JSON이 아닌 우리 Application의 문자열입니다.

# 15. `main.py` — 기존 Route를 유지하면서 의존성을 연결하기

`app/main.py`:

```python
from fastapi import FastAPI, HTTPException

from app.providers.base import AIProvider
from app.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUpstreamError,
)
from app.providers.factory import create_provider
from app.schemas import ChatRequest, ChatResponse
from app.service import AIService


def create_app(provider: AIProvider | None = None) -> FastAPI:
    # 테스트에서는 Mock을 주입하고, 일반 실행에서는 Factory를 사용합니다.
    selected = provider if provider is not None else create_provider()
    service = AIService(selected)
    api = FastAPI(title="AI Provider Abstraction")

    @api.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "provider": selected.provider_name,
            "model": selected.model_name,
        }

    @api.post("/ai/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        try:
            result = service.chat(request.message)
        except ProviderConnectionError as exc:
            raise HTTPException(503, "AI Provider 연결 실패") from exc
        except ProviderTimeoutError as exc:
            raise HTTPException(504, "AI Provider 응답 시간 초과") from exc
        except (ProviderUpstreamError, ProviderResponseError) as exc:
            raise HTTPException(502, "AI Provider 응답 오류") from exc

        return ChatResponse(
            provider=result.provider,
            model=result.model,
            answer=result.answer,
        )

    return api


app = create_app()
```

여기서 **새로 확인할 내용은 `create_app(provider=...)`를 통한 의존성 주입**입니다. 일반 실행은 Factory에서 가져온 Provider로 시작하고, 자동 테스트에서는 외부 API가 필요 없는 Mock을 직접 넘길 수 있습니다.

`app = create_app()`은 모듈을 불러올 때 Provider 설정을 검사합니다. `.env`의 모델명이나 Key가 누락되면 서버가 시작하지 않는 것이 정상입니다. **설정 오류가 있는 상태를 200 Health로 위장하지 않습니다.**

`/health`는 현재 **Backend 프로세스가 살아 있고 선택된 설정이 무엇인지** 보여 줍니다. 외부 OpenAI 또는 Ollama의 실제 정상 동작을 검사하지 않습니다.

# 16. 코드의 의존 방향을 실제로 확인하기

구현 후 Python Import를 보고 다음 질문에 답하게 합니다.

```text
main.py
  └── AIService + 공통 Provider Error

service.py
  └── AIProvider (Protocol)

factory.py
  ├── OpenAIProvider
  └── OllamaProvider

openai_provider.py
  └── OpenAI SDK

ollama_provider.py
  └── httpx
```

**판정 기준**

- `main.py`가 `OpenAI`나 `httpx`의 Provider별 Exception을 직접 처리하지 않는다.
- `service.py`는 Provider 선택 분기를 가지지 않는다.
- `factory.py`에만 `AI_PROVIDER`에 따른 분기가 있다.
- 두 Provider는 각자의 API 호출·Response Parsing을 책임진다.
- `ChatRequest`와 `ChatResponse`의 구조는 선택한 Provider와 관계없이 같다.

이것이 원본에서 말한 *Dependency Inversion*을 이번 프로젝트 범위에서 구현한 모습입니다. 거대한 추상화 Framework를 도입하는 것이 목표는 아닙니다.

# 17. Mock Provider — API 비용이나 Local Model 없이 교체를 검증한다

모델 품질을 비교하는 시험이 아닙니다. **Application이 계약만으로 Provider를 사용하는지 확인하는 시험**입니다.

아래 테스트 파일을 작성합니다. `tests/test_provider.py`:

```python
import os
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

# app.main에서 기본 app을 만들기 전에 테스트 설정을 지정합니다.
os.environ["AI_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "test-local-model"

from app.main import create_app  # noqa: E402
from app.providers.errors import (  # noqa: E402
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class MockProvider:
    provider_name = "mock"
    model_name = "fixed-test-model"

    def generate(self, message: str) -> str:
        return f"테스트 응답: {message}"


def test_contract_is_independent_of_real_api():
    with TestClient(create_app(MockProvider())) as client:
        res = client.post("/ai/chat", json={"message": "회의 일정 정리"})
    assert res.status_code == 200
    assert res.json() == {
        "provider": "mock",
        "model": "fixed-test-model",
        "answer": "테스트 응답: 회의 일정 정리",
    }


def test_input_validation_prevents_provider_call():
    class ExplodingProvider(MockProvider):
        def generate(self, message: str) -> str:
            raise AssertionError("Provider는 호출되면 안 됩니다")

    with TestClient(create_app(ExplodingProvider())) as client:
        res = client.post("/ai/chat", json={"message": "   "})
    assert res.status_code == 422


def test_health_does_not_call_model():
    with TestClient(create_app(MockProvider())) as client:
        res = client.get("/health")
    assert res.json() == {
        "status": "ok",
        "provider": "mock",
        "model": "fixed-test-model",
    }


def test_provider_errors_have_stable_http_mapping():
    errors = [
        (ProviderConnectionError(), 503),
        (ProviderTimeoutError(), 504),
        (ProviderResponseError(), 502),
    ]
    for error, expected_status in errors:
        class BrokenProvider(MockProvider):
            def generate(self, message: str) -> str:
                raise error

        with TestClient(create_app(BrokenProvider())) as client:
            res = client.post("/ai/chat", json={"message": "확인"})
        assert res.status_code == expected_status
        assert "Traceback" not in res.text


def test_factory_selects_only_configured_provider(monkeypatch):
    from app.providers.factory import create_provider

    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "course-local")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = create_provider()
    assert provider.provider_name == "ollama"
    assert provider.model_name == "course-local"

    monkeypatch.setenv("AI_PROVIDER", "unsupported")
    try:
        create_provider()
    except RuntimeError:
        pass
    else:
        raise AssertionError("지원하지 않는 Provider를 수락했습니다")


def test_ollama_provider_parses_response_without_network(monkeypatch):
    from app.providers.ollama_provider import OllamaProvider

    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    def fake_post(url, *, json, timeout):
        assert url.endswith("/api/chat")
        assert json["model"] == "test-model"
        assert json["stream"] is False
        assert json["messages"][0]["content"] == "기록 확인"
        return httpx.Response(
            200,
            json={"message": {"content": "정상 생성"}},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    assert OllamaProvider().generate("기록 확인") == "정상 생성"


def test_openai_provider_uses_same_interface_without_network(monkeypatch):
    from app.providers import openai_provider

    class FakeResponses:
        def create(self, *, model, input):
            assert model == "course-cloud-model"
            assert input == "기록 확인"
            return SimpleNamespace(output_text="Cloud 테스트 응답")

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "course-cloud-model")
    monkeypatch.setattr(
        openai_provider, "OpenAI", lambda **kwargs: FakeClient()
    )
    provider = openai_provider.OpenAIProvider()
    assert provider.provider_name == "openai"
    assert provider.generate("기록 확인") == "Cloud 테스트 응답"
```

**왜 Mock이 필요한가?** 이전 교시에서는 Ollama 연결 여부를 확인했지만, 지금은 **Ollama의 작동 여부가 아니라 Provider 추상화가 지켜지는지** 확인해야 하기 때문입니다. 외부 응답이 바뀌어도 `MockProvider`의 결과는 고정됩니다.

# 18. 테스트 실행 및 판독

프로젝트 루트에서 실행합니다.

```bash
python -m pytest -q tests/test_provider.py
```

확인할 결과는 성공 개수뿐 아니라 **실패한 경계**입니다.

| 테스트 | 증명하는 내용 | 증명하지 않는 내용 |
|---|---|---|
| Mock Chat Response | Route와 Service가 공통 계약을 사용함 | 실제 AI의 정확도 |
| 빈 입력 | Provider 호출 전에 Request를 차단함 | Model의 안전성 |
| Health | 모델 생성 없이 Backend 정보 반환 | Provider 접속 가능 여부 |
| 오류 Mapping | 구현체 종류와 무관하게 HTTP Error 유지 | 모든 실서비스 장애 처리 |
| Factory | 선택한 Provider 설정만 검사 | 모델 품질·실행 성능 |
| Ollama Mock | HTTP Body와 Response Parsing 흐름 | 실제 Ollama/Local 모델 정상 |
| OpenAI Mock | SDK 호출과 Response Parsing 흐름 | 실제 Cloud 인증·과금·모델 정상 |

주의: Mock이 전부 통과해도 실제 Ollama와 OpenAI의 **네트워크·인증·모델 사용 가능 상태**는 별도로 확인해야 합니다.

# 19. 실제 Provider 호출 — 동일 Endpoint, 설정만 변경하기

모의 테스트가 통과한 뒤 강사가 검증한 환경에서만 실제 호출합니다.

**실습 A — Ollama**

1. `.env`에 `AI_PROVIDER=ollama`, `OLLAMA_MODEL=Day2에서_검증한_이름`을 설정합니다.
2. Ollama가 동작하고 해당 모델이 존재하는지 Day2에서 배운 방법으로 확인합니다.
3. `python -m uvicorn app.main:app --reload`로 Backend를 실행합니다.
4. FastAPI `/docs`에서 `POST /ai/chat`을 호출합니다.
5. Request에 `{"message": "프로젝트 회의에서 확인해야 할 위험 요소 두 가지를 알려줘."}`를 입력합니다.
6. Response의 `provider`, `model`, `answer`를 기록합니다.

**실습 B — OpenAI (계정과 비용 조건이 충족되는 경우에만)**

1. Backend를 종료합니다.
2. `.env`에서 `AI_PROVIDER=openai`, `OPENAI_MODEL=강사가_검증한_모델_ID`, `OPENAI_API_KEY=본인의_유효한_Key`를 설정합니다.
3. Backend를 재시작하고 **같은 `/ai/chat` Endpoint와 같은 Request Body**를 호출합니다.
4. `provider`, `model`, `answer`를 다시 기록합니다.
5. `main.py`, `service.py`, `schemas.py` 및 Client 요청은 수정하지 않았는지 확인합니다.

**판독:** 응답 텍스트가 같아야 성공하는 실습이 아닙니다. **같은 Client 계약으로 다른 Provider가 호출되는지**가 성공 조건입니다.

Cloud API 접근 권한이나 예산이 없으면 OpenAI 호출을 생략하고, 17교시의 Fake Client 테스트로 **코드 구조 검증**만 수행합니다. 이 경우 **실제 Cloud 전환 성공**이라고 기록하지 않습니다.

# 20. Provider를 바꿨을 때 변해야 할 것과 변하면 안 되는 것

| 확인 대상 | Ollama → OpenAI 교체 시 | 판정 |
|---|---|---|
| `AI_PROVIDER` 등 설정 | 변경됨 | 정상 |
| Factory에서 생성한 객체 | 변경됨 | 정상 |
| Provider 통신 메커니즘 | `httpx` → OpenAI SDK | 정상 |
| AI 응답 문장 | 달라질 수 있음 | 정상 |
| `/ai/chat` URL | 동일 | 필수 |
| Request의 `message` 필드 | 동일 | 필수 |
| Response의 `provider`, `model`, `answer` 필드 | 동일 | 필수 |
| Service에서 호출하는 `generate(message)` | 동일 | 필수 |
| FastAPI Route의 Provider별 분기 | **없어야 함** | 필수 |

**오해 방지:** Provider 교체는 **설정만 바꾸면 즉시 무중단 전환되는 기능**이 아닙니다. 이번 코드는 Server 시작 시 Provider를 결정하므로 재시작이 필요합니다.

# 21. 실패 실습 — 어디까지 내려갔는지 찾아보기

이번 교시에서는 **Provider 오류가 공통 형태로 올라오는 경로**를 관찰합니다.

| 실패 상황 | 처음 막힌 계층 | 확인 결과 |
|---|---|---|
| `AI_PROVIDER=unknown` | Factory / 설정 | 앱 시작 실패; Route 실행 전 문제 |
| `OLLAMA_MODEL` 누락 | OllamaProvider 초기화 | 앱 시작 실패 |
| 공백만 있는 `message` | FastAPI / Pydantic | `422`, Provider 미호출 |
| Ollama 연결 불가 | OllamaProvider / Network | `503` |
| Provider 응답 대기 초과 | Provider 내부 | `504` |
| Ollama HTTP 오류 또는 Provider 오류 상태 | Provider 내부 | `502` |
| 성공 HTTP인데 `message.content` 없음 | OllamaProvider 응답 검사 | `502` |
| `GET /health`는 정상인데 모델 호출 실패 | Backend / Provider는 별개 | `/health` 성공만으로 추론 정상 보장 불가 |

HTTP `503/504/502` 구분은 **이번 강의용 Application에서 정의한 오류 정책**입니다. 서비스 특성에 따라 다른 정책을 설계할 수 있습니다. 중요한 것은 Route가 Provider별 원본 Exception을 알 필요가 없다는 점입니다.

학생에게는 **오류 원문 전체를 공개 답변에 출력하는 방식** 대신 실패 지점과 일반화된 메시지를 기록하도록 안내합니다. Credential, 사용자 입력 전문, 내부 시스템 경로는 진단 기록에서도 취급에 주의합니다.

# 22. 새로운 Provider 추가 — 무엇만 수정하면 되는가?

원본의 응용 과제를 이번 구조에 맞춰 생각해봅니다. 새로운 Provider가 다음을 구현한다고 가정합니다.

```python
class ExampleProvider:
    @property
    def provider_name(self) -> str:
        return "example"

    @property
    def model_name(self) -> str:
        return "example-model"

    def generate(self, message: str) -> str:
        return f"예제: {message}"
```

실제 추가 시 필요한 변경은 대체로 다음과 같습니다.

- 새 Provider 클래스와 그 내부 설정·오류 변환 작성
- Factory에 새 선택 분기 추가
- 해당 Provider 테스트 추가

**원칙적으로 변경하지 않아도 되는 것:** `AIService.chat`, `/ai/chat` Route, `ChatRequest`, `ChatResponse`.

단, 새 Provider가 공통 `generate(message) -> str` 계약을 만족하지 못한다면 무리하게 연결하지 말고 별도 기능 계약을 설계해야 합니다. 모든 Provider의 고유 기능을 한 Interface에 넣으면 다시 복잡해집니다.

# 23. 왜 Framework 대신 직접 추상화하는가?

6교시에서 LangChain의 공통 Model Interface가 제공하는 편의를 배웠습니다. 하지만 지금은 **Framework의 많은 기능이 필요한 상황이 아니라, 두 Provider 호출이 Application에 퍼지지 않도록 분리하는 상황**입니다.

이번 실습의 설계 선택에는 분명한 경계가 있습니다.

| 지금 직접 구현한 것 | 아직 구현하지 않은 것 |
|---|---|
| 두 Provider에 대한 공통 문자열 입력·출력 | Multi-turn 대화 이력 저장 |
| Provider Factory | 자동 Fallback·Load Balancing |
| 간단한 공통 예외 처리 | 복잡한 Retry·Circuit Breaker |
| 고정 선택과 테스트 주입 | 요청 단위 Provider 교체 |
| Test Double로 계약 검증 | 모든 Provider-specific Capability 추상화 |

강사는 **추상화가 꼭 복잡해야 좋은 설계는 아니라는 점**을 강조합니다. 이번 두 Provider 사례에서 추가한 Interface와 Factory가 어떤 파일의 변경을 막아 주는지 설명할 수 있다면 목표를 달성한 것입니다.

# 24. 학생 활동 A — 코드의 책임을 찾는다

아래 변경 요청을 읽고 **어느 파일을 먼저 수정할지** 기록합니다.

| 변경 요청 | 학생 답안(파일명) | 강사 확인 기준 |
|---|---|---|
| Ollama의 응답 JSON 경로가 변경됨 | | `ollama_provider.py` |
| OpenAI API 호출 옵션이 바뀜 | | `openai_provider.py` |
| 새로운 Provider 이름을 선택 가능하게 함 | | `factory.py`와 새 구현체 |
| `/ai/chat`의 Response 필드를 추가함 | | `schemas.py`, `main.py` 및 Client 계약 검토 |
| 새로운 Provider-specific Timeout 처리 | | Provider 및 공통 Error 정책 검토 |
| `AIService`에 Provider 이름 조건문이 생김 | | 책임 분리 위반 여부 검토 |

*제출 기준:* 단순 파일명 외에 “왜 다른 파일을 고치지 않아도 되는지” 한 문장을 덧붙입니다.

# 25. 학생 활동 B — 설정의 독립성을 반례로 확인한다

다음 조건에서 **서버가 시작해야 하는지** 판단합니다.

| 조건 | 예상 판정 | 이유 |
|---|---|---|
| `ollama` 선택, Ollama 모델명 존재, OpenAI Key 없음 | 시작 가능 | 선택하지 않은 Cloud Provider는 초기화하지 않음 |
| `openai` 선택, 모델명만 있고 Key 없음 | 시작 실패 | 선택한 Provider 필수 값 누락 |
| `ollama` 선택, 모델명 빈 문자열 | 시작 실패 | `required_env()` 검사 |
| `unknown` 선택 | 시작 실패 | Factory에서 거부 |
| 테스트에서 Mock 객체 직접 전달 | 시작 가능 | Factory 선택을 우회하고 테스트 객체를 사용 |

시작 성공과 **실제 모델 응답 성공은 다릅니다.** 이 표의 첫 행도 Ollama Server가 꺼져 있으면 요청 시 실패할 수 있습니다.

# 26. 학생 활동 C — 교체 전후의 계약 유지 증빙

다음 기록표를 작성합니다.

| 항목 | Ollama 실행/Mock | OpenAI 실행/Mock |
|---|---|---|
| `AI_PROVIDER` 설정 | | |
| 생성된 Provider | | |
| `POST /ai/chat` Request | | |
| Response Key 3개 | | |
| 모델 호출 성공 여부 | | |
| 실패 시 상태 코드 | | |
| `main.py` 변경 여부 | | |
| `service.py` 변경 여부 | | |

학생이 **실제 실행한 결과**와 **Mock으로 확인한 결과**를 혼동해 기록하지 않는 것이 중요합니다. OpenAI API 사용 권한이 없다면 Mock 결과만 작성해도 수업의 추상화 목표는 검증할 수 있습니다.

# 27. 학생 활동 D — 일부러 추상화를 무너뜨려 본다

다음 문장을 검토하고 반박합니다.

> “Provider가 두 개뿐이니 `AIService` 안에서 `if provider == 'openai'`로 분기하면 된다. 어차피 동작은 같다.”

답안에는 다음 요소를 포함합니다.

1. 이 방식에서 Provider-specific SDK·HTTP 정보가 어느 Layer로 퍼지는가?
2. 새 Provider를 추가하면 무엇을 수정해야 하는가?
3. 현재 설계에서는 어떤 파일을 건드리지 않아도 되는가?
4. **직접 추상화가 오히려 불필요한 단순 프로그램**은 어떤 경우인가?

이 활동의 목표는 인터페이스를 무조건 사용하라는 것이 아니라, **도입 비용과 유지보수상의 이익을 구분**하는 것입니다.

# 28. 강사 진행 순서 — 코드 해설보다 변경 지점 확인에 시간 배분하기

| 순서 | 강사 시연 | 학생 확인 질문 |
|---|---|---|
| 1 | Day2 Route에서 Ollama 호출 위치 찾기 | Provider가 변경되면 어디를 고쳐야 하나? |
| 2 | `Protocol` 작성 | 서비스가 꼭 알아야 하는 기능 세 개는? |
| 3 | 두 구현체 작성 | 같은 메서드 뒤에서 달라지는 것은? |
| 4 | Factory와 Service 연결 | 선택하지 않은 Provider의 Key가 필요한가? |
| 5 | Route의 Provider별 코드 제거 | Route가 `httpx`를 Import하는가? |
| 6 | Mock Test 실행 | 모델 없이도 무엇을 검증할 수 있는가? |
| 7 | 선택적 실제 호출 및 오류 실습 | 성공 범위와 미검증 범위는? |

개별 Provider의 설치·사용법을 다시 길게 설명하지 말고, **어떤 의존성이 어디로 이동했는지**에 시간을 사용합니다.

# 29. 자주 발생하는 오해 — 코드의 실제 동작으로 판정

**오해 A — `Protocol`을 상속하지 않으면 공통 Provider가 아니다.** 구조적 Typing에서는 필요한 속성과 메서드를 구현하는 방식으로 계약을 만족시킬 수 있습니다. 그렇다고 자동 런타임 검증이 되는 것은 아닙니다.

**오해 B — Factory가 두 Provider를 모두 실행한다.** Factory는 **설정에 따라 하나를 생성**합니다. 각각의 실제 API를 호출해 상태를 검사하는 기능이 아닙니다.

**오해 C — Cloud Provider를 선택하려면 Local Model도 실행해야 한다.** 해당 Provider를 호출하는 데 필요한 환경만 준비하면 됩니다.

**오해 D — 두 Provider로 바꾸어도 답변이 똑같아야 성공이다.** 추상화가 통일하는 것은 호출 계약이지 언어 모델의 결과가 아닙니다.

**오해 E — `/health`가 200이면 Model도 정상이다.** 현재 구현은 Model Inference를 Health 요청에서 실행하지 않습니다.

**오해 F — Mock 테스트가 통과했으니 실제 OpenAI와 Ollama 연결을 검증한 것이다.** Mock은 구조·호출·응답 파싱·오류 처리만 확인합니다. 라이브 호출은 따로 진행해야 합니다.

**오해 G — 이 구조만으로 Provider 자동 Fallback이 된다.** Factory에서 정해진 단일 Provider를 사용하는 구조이며 자동 대체는 구현하지 않았습니다.

# 30. 확인 질문과 예상 답안

**Q1. `AIService`가 왜 `OpenAIProvider`를 직접 Import하지 않나요?**

특정 구현이 아니라 `AIProvider` 계약에 의존하게 해 Provider 교체 시 Service 수정 범위를 줄이기 위해서입니다.

**Q2. OpenAI 사용 시 Ollama 모델 이름이 왜 필요하지 않나요?**

Factory가 OpenAIProvider만 생성하고 그 Provider가 필요한 환경 설정만 검사하기 때문입니다.

**Q3. Provider별 네트워크 오류를 Provider 안에서 공통 예외로 바꾸는 이유는?**

FastAPI Route가 SDK별 예외 종류를 몰라도 같은 오류 계약을 유지하기 위해서입니다.

**Q4. `POST /ai/chat`에 `provider`를 Request 필드로 추가해야 하나요?**

이번 실습에서는 아닙니다. Provider 선택은 서버 환경 변수로 고정합니다. 요청 단위 선택은 별도의 요구사항과 권한 통제 설계가 필요한 주제입니다.

**Q5. `create_app(MockProvider())`를 호출하면 어떤 장점이 있나요?**

실제 모델·API Key·네트워크 없이도 Route와 Service의 계약 및 오류 처리를 반복해서 검증할 수 있습니다.

# 31. 수업 완료 체크리스트와 제출물

- [ ] `main.py`의 Route에 Provider별 SDK·HTTP 호출이 남아 있지 않다.
- [ ] `AIService`는 공통 `AIProvider`만 사용한다.
- [ ] `OpenAIProvider`와 `OllamaProvider`가 모두 `generate(message) -> str` 계약을 만족한다.
- [ ] Factory가 선택한 Provider의 설정만 검사한다.
- [ ] `message`가 공백인 요청은 Provider를 호출하지 않고 `422`로 거부한다.
- [ ] 정상 Response의 `provider`, `model`, `answer`가 유지된다.
- [ ] Provider 실패의 `503`, `504`, `502` 처리 경로를 확인했다.
- [ ] Mock 자동 테스트를 실행하고 실제 실행 여부를 구분해 기록했다.
- [ ] Provider 교체 시 `main.py`와 `service.py`를 수정하지 않았다.
- [ ] `.env` 및 API Key가 제출물이나 Git에 포함되지 않았다.

**최종 제출물:** Backend 프로젝트 폴더(Secret 제외), 자동 테스트 결과, Provider 전환 또는 Mock 전환 비교표, 이번 리팩터링으로 변경 책임이 분리된 위치에 대한 설명.

# 32. 이번 교시 결론과 Day3 8교시 연결

이번 실습의 핵심은 새로운 Model을 더 잘 실행하는 것이 아닙니다. **동일한 Application 기능을 구현하는 Provider-specific Code가 업무 계층과 HTTP Route로 새어나가지 않도록 경계를 만드는 것**입니다.

```text
Client  ── (고정) ── POST /ai/chat
                            ↓
                         AIService
                            ↓
                   AIProvider.generate()
                       ├─ OpenAI
                       └─ Ollama
```

이 교시에서 보존한 Client Contract는 다음과 같습니다.

```json
{
  "message": "사용자 질문"
}
```

```json
{
  "provider": "ollama",
  "model": "수업에서 검증한 모델명",
  "answer": "생성된 응답"
}
```

**다음 Day3 8교시에서는** 이 Backend Contract를 React에서 호출해 Loading·Error·취소·화면 상태 등 *Browser에서만 확인할 수 있는 문제*를 다룹니다. **이 교시에서 React 화면이나 CORS 코드를 미리 작성하지 않습니다.**

---

# 참고자료 — 유일한 교육과정 원본에 기재된 범위

- OpenAI API / Responses API 및 Python SDK 공식 문서
- Ollama API / Chat 공식 문서
- FastAPI 공식 문서
- Python `typing.Protocol` 문서
- Pydantic 문서

위 자료명은 원본 교육과정에 포함된 참고자료 목록입니다. **이번 개편에서는 ZIP 밖의 문서를 교육내용 출처로 사용하거나, 최신 SDK 호환성을 외부에서 검증하지 않았습니다.** 실제 교육장에서 사용 중인 패키지·Model ID·API 권한과 버전은 강사 측에서 확인해야 합니다.

# 관련 Wiki Link

`[[AI Provider]]` · `[[Provider Abstraction]]` · `[[Dependency Inversion]]` · `[[Protocol]]` · `[[OpenAI SDK]]` · `[[Ollama]]` · `[[FastAPI]]` · `[[AI Service Architecture]]` · `[[HTTP]]` · `[[Provider Error]]` · `[[Mock Provider]]`

# 저장 위치 제안 — 원본 기준

```text
Academy/
└── 03. 실습/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day3_07교시_AI_Provider_추상화_OpenAI와_Ollama_FastAPI_통합_실습.md
```

> **수정·검증 상태:** v0.2 강의용 Working Copy. 실제 OpenAI API·Ollama Live Inference와 최신 SDK/Model 조합은 별도 현장 검증 대상입니다. 원본 파일을 덮어쓰지 않습니다.
