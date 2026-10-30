# Day 2 - 8교시. Python + FastAPI + Ollama Local API 통합 실습

## 개요 — Terminal에서 쓰던 Local LLM을 우리 Web API에 연결하기

7교시에는 사람이 Terminal에서 Local Model에 질문하고 응답을 확인했습니다. 이제 **사람 대신 Backend Program이 Ollama에 질문을 보내도록** 바꿉니다. 수업의 성과는 Ollama 명령어를 더 외우는 것이 아니라 **FastAPI Endpoint가 실제 Local Model의 답변을 받아 Client에게 반환하는 하나의 작동하는 API**를 만드는 것입니다.

```text
[Client]               [우리가 작성하는 Python Backend]                 [기존 Ollama]
  POST /ai/chat ──→ FastAPI → Ollama Service → HTTP POST /api/chat ──→ Ollama Runtime
                  요청 검증       요청 생성·응답 처리                        Local Model
  JSON Response ←── FastAPI ←─ Ollama Service ←──── 생성 결과(JSON) ─────────┘
```

이미 학습한 부분은 간단히 연결합니다.

- **Day1 7교시:** Python에서 Cloud AI API를 호출하는 방법
- **Day1 8교시:** FastAPI Route, Pydantic Schema, AI Service 분리, HTTP 오류 처리
- **Day2 6교시:** Application Process와 Model Server Process의 분리
- **Day2 7교시:** Ollama 설치, 모델 다운로드, CLI 실행과 상태 확인

**이번 교시에 새로 할 일:** Backend의 Provider 통신 코드를 **OpenAI SDK 호출에서 Ollama Local HTTP API 호출로 바꾸고**, 양쪽 서버가 실제로 연결되는지 검증합니다. Day1의 Structured Output 구현은 다시 작성하지 않습니다. 이번 예제는 생성된 문자열을 `answer` 필드에 담는 간단한 API입니다.

> **실행 전제:** 교육장에 Ollama가 설치되어 있고, 7교시에서 다운로드·실행 검증을 마친 **정확한 모델 이름**이 있어야 합니다. 이 문서에는 임의의 모델 이름이나 버전을 실제 검증된 값처럼 기입하지 않습니다. 실제 Ollama의 API·CLI 지원 여부와 모델 접근 가능 여부는 수업 배포 전 강사가 해당 환경에서 확인합니다.

---

# 1. 실습 목표와 완료 기준

수업 종료 시 학생은 다음을 수행할 수 있어야 합니다.

1. 7교시의 Local Model이 준비되었는지 확인하고 모델 이름을 Backend 설정에 전달한다.
2. Ollama의 `/api/chat` Endpoint에 **Python `httpx`** 로 JSON Request를 보낸다.
3. 응답에서 `message.content`를 읽어 Python 문자열로 반환한다.
4. Provider 통신 코드를 FastAPI Route가 아닌 `ollama_service.py`에 둔다.
5. FastAPI에 `POST /ai/chat`을 구현하고 `ChatRequest`·`ChatResponse`를 적용한다.
6. `/docs`를 이용해 정상 요청·입력 오류·외부 서비스 오류를 구분한다.
7. Ollama가 없어도 실행 가능한 **모의 테스트**와 실제 모델을 사용하는 **통합 테스트**를 구분한다.
8. Day1 Cloud API와 현재 Local API의 **바뀐 부분과 그대로인 부분**을 코드 단위로 설명한다.

**완료 판정:** `POST /ai/chat`에 질문을 보내 `{"answer": "..."}` 형태의 응답을 받고, 공백 입력이 AI Provider에 전달되지 않으며, Ollama 장애가 발생해도 오류를 구분해 반환해야 합니다. 실제 모델 응답을 확인하기 전에는 ‘실제 Local AI 연동 검증 완료’로 판정하지 않습니다.

---

# 2. 이번 교시에서 변경되는 곳만 확인하기

Day1의 Cloud API 실습은 Route와 Service를 분리했습니다. 그 구조를 유지하면서 **AI Provider와 호출 방식만 교체**합니다.

| 계층 | Day1 8교시 | 이번 Day2 8교시 | 이번에 수정할 부분 |
|---|---|---|---|
| Client | FastAPI Endpoint 호출 | FastAPI Endpoint 호출 | API 요청 방식은 유지 |
| Route | `main.py` | `main.py` | `/ai/chat` 계약 작성 |
| Data Contract | Pydantic | Pydantic | `message` 입력과 `answer` 출력 정의 |
| AI Service | OpenAI SDK | `httpx` + Ollama API | **가장 큰 변경 지점** |
| Model 실행 위치 | Cloud Provider | 교육장 PC의 Ollama Runtime | 실행 위치 변경 |
| 응답 내용 | Structured AI 객체 | 자연어 문자열을 담은 JSON | 출력 계약의 차이 확인 |

이 표를 보고 다음 질문에 답할 수 있어야 합니다.

> FastAPI가 모델의 Weight 파일을 직접 읽어야 할까요?

아닙니다. 이번 구조에서는 **Ollama가 모델을 실행**합니다. FastAPI는 요청을 검증하고, Service를 통해 Ollama에 전달하고, 받은 결과를 우리 API 규격으로 바꿉니다.

---

# 3. 실습 전에 확보할 값과 상태

## 3.1 7교시에서 이어받을 값

Terminal에서 다음을 확인합니다.

```bash
ollama ls
```

강사는 결과에서 사용할 **모델 이름을 정확히 하나** 지정합니다. 모델이 목록에 없거나 7교시 실행이 실패했다면 **이 교시의 API 코드부터 고치지 말고 모델 준비 상태를 먼저 해결**합니다.

필요하면 같은 모델이 실제로 질문에 답하는지 7교시에서 사용한 방법으로 확인합니다. `ollama ps` 결과가 비어 있다는 사실만으로 고장으로 판정하지 않습니다. 모델이 현재 메모리에 올라와 있지 않을 수도 있기 때문입니다.

## 3.2 두 가지 실행 조건

| 실행 조건 | 확인할 값 | 만족해야 할 기준 |
|---|---|---|
| Ollama 측 | 모델 이름·Ollama Server 상태 | 모델이 준비되고 Local API로 호출할 수 있음 |
| Backend 측 | Python·FastAPI·httpx·실습 모델 설정 | `/health`, `/ai/chat`을 실행할 수 있음 |

**중요:** Ollama가 다른 PC에 설치되어 있다면 `localhost`는 그 다른 PC가 아니라 **FastAPI가 실행 중인 PC 자신**을 뜻합니다. 이번 기본 실습은 **Ollama와 FastAPI가 같은 PC**에 있다고 가정합니다. 별도 서버 연결, 네트워크 노출, 인증 정책의 상세 설계는 여기서 구현하지 않습니다.

---

# 4. 프로젝트 폴더와 Python 환경

Day1에서 이미 가상환경과 Python 패키지 설치를 배웠으므로, 이번에는 실행에 필요한 명령만 확인합니다. 새 폴더를 만들고 프로젝트 Root에서 진행합니다.

```text
day2_local_ai_api/
├── .venv/                 # 가상환경: 버전 관리에 포함하지 않음
├── app/
│   ├── __init__.py
│   ├── schemas.py          # 우리 API의 요청·응답 계약
│   ├── ollama_service.py   # Ollama API와의 통신
│   └── main.py             # FastAPI Endpoint
├── tests/
│   └── test_api.py         # Ollama 없이 확인하는 모의 테스트
├── test_ollama_service.py  # 실제 Ollama 연결 확인용
└── requirements.txt
```

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

패키지 설치:

```bash
python -m pip install fastapi uvicorn httpx pytest
```

`pydantic`은 FastAPI 환경에 함께 설치되지만, 코드에서는 직접 import하여 사용합니다. `pytest`는 **모의 테스트**에 사용합니다. 실제 수업의 `requirements.txt`에는 강사가 설치 및 실행 검증한 버전을 기록합니다. 아래는 **형식 설명용**이며 그대로 설치 명령에 사용하지 않습니다.

```text
fastapi==<수업에서 검증한 버전>
uvicorn==<수업에서 검증한 버전>
httpx==<수업에서 검증한 버전>
pytest==<수업에서 검증한 버전>
```

패키지 확인:

```bash
python -m pip show fastapi uvicorn httpx pydantic pytest
```

기존에 모델이 준비되었다면 이 Backend에 PyTorch나 Transformers를 새로 설치할 필요는 없습니다. **Python Backend는 Ollama HTTP API를 호출**하기 때문입니다.

---

# 5. Ollama 모델 이름을 코드 밖에서 설정하기

원본 예제의 `"<강사가_검증한_Model>"`는 자리표시자입니다. 이를 실제 모델 이름으로 바꾸지 않은 채 호출하면 해당 모델을 찾지 못합니다. 이번에는 모델 이름을 여러 파일에 복사하지 않고 **환경 변수 `OLLAMA_MODEL` 하나로 전달**합니다.

Windows PowerShell:

```powershell
$env:OLLAMA_MODEL="7교시에서_확정한_정확한_모델명"
```

macOS / Linux:

```bash
export OLLAMA_MODEL="7교시에서_확정한_정확한_모델명"
```

**위의 문구는 실제 모델 이름이 아닙니다.** 강사가 지정한 `ollama ls`의 모델 이름으로 바꿔 입력합니다. 실행한 Terminal 세션의 환경 변수가 이후 같은 Terminal에서 시작하는 Uvicorn 프로세스로 전달됩니다. 다른 Terminal에서 실행하면 설정을 다시 확인해야 합니다.

Ollama API는 이번 로컬 환경에서 기본 주소를 사용합니다.

```text
http://127.0.0.1:11434/api/chat
```

`127.0.0.1`과 `localhost`는 이번 로컬 실습에서 같은 PC를 가리키는 용도로 사용할 수 있습니다. 이번에는 설정할 항목을 줄이기 위해 기본 주소를 코드에 둡니다. **모델 이름은 환경 변수, 요청할 URL은 Service의 상수**로 구분합니다.

---

# 6. 실제 Ollama Chat Request와 우리가 받을 응답

Ollama의 Chat API에 보내는 Request는 원본 수업에서 소개한 다음 구조를 사용합니다.

```json
{
  "model": "<7교시에서_확정한_모델명>",
  "messages": [
    {
      "role": "user",
      "content": "로컬 모델을 API로 호출할 때 HTTP는 어떤 역할을 하나요?"
    }
  ],
  "stream": false
}
```

이 JSON의 `model` 값도 **표시를 위한 예시**입니다. 실제 코드에서는 환경 변수의 정확한 모델 이름을 넣습니다.

여기서 처음 구현에 꼭 필요한 사항은 세 가지입니다.

1. **`model`**: 어떤 Local Model에 요청할지 지정
2. **`messages`**: 역할(`role`)과 내용(`content`)을 가진 Message 목록
3. **`stream: false`**: 전체 응답을 하나의 JSON으로 받은 뒤 처리하기 위한 설정

이번에는 Streaming 응답을 이어 붙이는 코드를 만들지 않습니다. 관련 개념은 6교시에서 이미 배웠고, 이번 실습의 목표는 **한 번의 요청·한 번의 JSON 응답을 올바르게 전달하는 것**입니다.

정상적인 Non-streaming Chat 응답은 여러 Metadata를 포함할 수 있습니다. 이번 Service가 필요한 부분은 다음과 같습니다.

```json
{
  "message": {
    "role": "assistant",
    "content": "HTTP는 Backend와 Ollama 서버가 요청과 응답을 주고받도록 합니다."
  }
}
```

위 JSON은 **필요한 필드만 발췌한 학습용 예시**입니다. 실제 전체 Provider 응답과 동일하다고 주장하는 출력은 아닙니다. 우리 API는 `message.content`만 읽고 나머지 Provider Metadata는 Client에게 그대로 전달하지 않습니다.

**질문:** Ollama의 원시 Response와 우리 서비스의 Response가 반드시 같은 구조여야 할까요?

**답:** 아닙니다. `Ollama Response → Python 문자열 → ChatResponse`로 변환합니다. 이를 통해 Client는 Provider의 내부 Field를 알 필요가 없습니다.

---

# 7. `app/schemas.py` — 우리 API의 계약

Day1 8교시에서 Pydantic의 의미를 배웠으므로 이론 정의를 반복하지 않고 **이번 요청에서 무엇을 차단하는지** 확인합니다.

`app/schemas.py` 전체 코드:

```python
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("질문에 공백만 입력할 수 없습니다.")
        return cleaned


class ChatResponse(BaseModel):
    answer: str
```

`min_length=1`만으로는 `"   "`와 같은 **공백만 있는 입력**을 막지 못합니다. 그래서 `field_validator`에서 앞뒤 공백을 제거한 뒤 내용이 비어 있는지 확인합니다. `max_length=2000`은 이 실습의 단순한 입력 길이 제한일 뿐 **토큰 수나 모델 Context 제한을 대신하지 않습니다**.

| Request Body | 결과 | Ollama 호출 여부 |
|---|---|---|
| `{"message":"로컬 API란?"}` | 유효 | 호출 진행 |
| `{"message":""}` | `422` | 호출하지 않음 |
| `{"message":"   "}` | `422` | 호출하지 않음 |
| `{"message":123}` | `422` | 호출하지 않음 |
| `{"message":"a"}` | 유효 | 호출 진행 |

`ChatResponse`는 **AI가 작성한 문장의 진실성**을 증명하는 기능이 아닙니다. 이번 코드에서 검사하는 것은 `answer`가 문자열이라는 **API 형식**입니다. 내용 정확도 평가는 별개의 문제입니다.

---

# 8. `app/ollama_service.py` — Ollama와 통신하는 완성 코드

이번 교시의 핵심 파일입니다. Day1에 사용한 OpenAI SDK 대신 일반 HTTP Client인 `httpx`를 사용합니다. Service는 FastAPI의 `HTTPException`을 직접 만들지 않고, **Provider 통신에서 무엇이 실패했는지만 구분해 상위 Route에 알립니다.**

```python
import os

import httpx


OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"


class OllamaConfigurationError(Exception):
    """실습 모델 이름이 설정되지 않았을 때 사용합니다."""


class OllamaConnectionError(Exception):
    """Ollama Server와 연결할 수 없을 때 사용합니다."""


class OllamaTimeoutError(Exception):
    """Ollama 응답을 기다리다가 제한 시간을 넘겼을 때 사용합니다."""


class OllamaResponseError(Exception):
    """Provider가 오류 또는 해석할 수 없는 응답을 보냈을 때 사용합니다."""


def ask_ollama(message: str) -> str:
    model_name = os.getenv("OLLAMA_MODEL", "").strip()
    if not model_name:
        raise OllamaConfigurationError("OLLAMA_MODEL이 설정되지 않았습니다.")

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": message},
        ],
        "stream": False,
    }

    try:
        response = httpx.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException as error:
        raise OllamaTimeoutError("Ollama 응답 시간이 초과되었습니다.") from error
    except httpx.ConnectError as error:
        raise OllamaConnectionError("Ollama에 연결할 수 없습니다.") from error
    except httpx.HTTPError as error:
        raise OllamaResponseError("Ollama 요청이 실패했습니다.") from error

    try:
        data = response.json()
        answer = data["message"]["content"]
    except (ValueError, KeyError, TypeError) as error:
        raise OllamaResponseError("Ollama 응답 구조를 읽을 수 없습니다.") from error

    if not isinstance(answer, str) or not answer.strip():
        raise OllamaResponseError("Ollama가 유효한 답변 문자열을 반환하지 않았습니다.")

    return answer
```

## 8.1 코드를 실제 HTTP Request와 대응시키기

| 코드 | 동작 | 학생이 확인할 내용 |
|---|---|---|
| `os.getenv("OLLAMA_MODEL")` | 실행 환경의 모델 이름 읽기 | 7교시의 모델 이름과 같은가? |
| `payload["messages"]` | Model에 보낼 User Message 준비 | Client의 `message`가 들어가는가? |
| `"stream": False` | 하나의 JSON Response 요청 | 응답을 한 번에 파싱할 수 있는가? |
| `httpx.post(...)` | Ollama 서버에 HTTP 요청 | 서버가 켜져 있는가? |
| `response.raise_for_status()` | HTTP 오류 상태 감지 | 잘못된 모델 이름 등을 구분할 수 있는가? |
| `response.json()` | 응답 JSON 읽기 | `message.content`가 존재하는가? |
| `return answer` | 필요한 문자열만 상위 계층으로 전달 | Provider Metadata를 넘기지 않는가? |

## 8.2 HTTP 응답이 성공이어도 검사할 것이 남아 있다

HTTP `200`이라고 해서 항상 우리가 원하는 `message.content`가 들어 있다는 보장은 없습니다. 따라서 이 코드는 **상태 코드 확인과 응답 구조 확인을 별도로** 수행합니다.

- 연결에 실패하면 **OllamaConnectionError**
- 응답 제한 시간을 넘기면 **OllamaTimeoutError**
- Ollama가 오류 Status를 보내거나 JSON 구조가 예상과 다르면 **OllamaResponseError**
- 모델 이름이 설정되지 않으면 **OllamaConfigurationError**

실제 Provider의 HTTP 오류에는 모델 이름 불일치, 지원되지 않는 요청, 실행 환경 문제 등 여러 원인이 있을 수 있습니다. 이 실습에서는 상세 Provider 오류를 Client에게 그대로 노출하지 않고 **일관된 HTTP 오류**로 바꿉니다.

## 8.3 `timeout=60.0`의 의미

이 값은 예제의 제한 시간일 뿐 모든 Local Model에 적합한 값은 아닙니다. 큰 모델을 처음 로드할 때는 시간이 더 걸릴 수 있습니다. 무조건 Timeout 값을 크게 늘리기 전에 **Ollama 상태, 모델 준비 여부, 환경 자원**을 확인하는 것이 먼저입니다. 상세 성능 튜닝은 본 교시의 범위가 아닙니다.

---

# 9. 실제 Provider에 연결하기 전에 Service만 확인하기

이제 `app/__init__.py`를 빈 파일로 만들고, 프로젝트 Root에 다음 파일을 작성합니다.

`test_ollama_service.py`:

```python
from app.ollama_service import ask_ollama


def main() -> None:
    answer = ask_ollama(
        "로컬 모델을 API로 호출할 때 HTTP는 어떤 역할을 하나요?"
    )
    print(answer)


if __name__ == "__main__":
    main()
```

```bash
python test_ollama_service.py
```

이 테스트는 **실제 Ollama가 실행되고, `OLLAMA_MODEL`이 설정되어 있고, 모델이 요청을 처리할 때만 성공**합니다. 예를 들어 이 단계에서 연결 오류가 발생한다면 **FastAPI Route는 아직 작성하지 않았으므로**, 우선 Ollama Server·모델 준비·환경 변수부터 확인합니다.

이 분리는 오류가 생겼을 때 원인을 좁히기 위한 것입니다. 실제 Ollama가 아직 준비되지 않은 교육장에서는 **13장의 모의 테스트를 먼저 실행**할 수 있습니다.

---

# 10. `app/main.py` — Backend Endpoint 연결

Day1의 FastAPI 기초 설명은 생략하고, 앞에서 만든 Service를 호출하는 **최종 완성 코드**만 사용합니다.

```python
from fastapi import FastAPI, HTTPException

from app.ollama_service import (
    OllamaConfigurationError,
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
    ask_ollama,
)
from app.schemas import ChatRequest, ChatResponse


app = FastAPI(title="AIKOS Local AI API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ai/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer = ask_ollama(request.message)
    except OllamaConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail="Local AI 모델 이름이 설정되지 않았습니다.",
        ) from error
    except OllamaConnectionError as error:
        raise HTTPException(
            status_code=503,
            detail="Local AI 서비스에 연결할 수 없습니다.",
        ) from error
    except OllamaTimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="Local AI 응답 시간이 초과되었습니다.",
        ) from error
    except OllamaResponseError as error:
        raise HTTPException(
            status_code=502,
            detail="Local AI 서비스 응답을 처리할 수 없습니다.",
        ) from error

    return ChatResponse(answer=answer)
```

**왜 `def`인가?** 이번 Service는 동기 방식의 `httpx.post()`를 호출합니다. Day1의 동기/비동기 설명을 반복하지 않고, 여기서는 두 함수의 호출 방식이 일치한다는 점만 확인합니다.

**왜 `/health`를 분리했는가?** 이 Endpoint는 FastAPI 프로세스가 HTTP 요청을 받는지만 확인합니다. **Ollama 모델 실행의 정상 여부까지 보장하지 않습니다.** AI 상태를 추가로 점검하는 별도 API 설계는 응용 과제로 남깁니다.

## 10.1 실패 원인과 HTTP 상태 코드를 연결하기

| 상황 | 감지 위치 | 우리 API 응답 | Ollama 호출 여부 |
|---|---|---|---|
| 빈 문자열·공백·잘못된 타입 | Pydantic | `422 Unprocessable Entity` | 호출 전 차단 |
| `OLLAMA_MODEL` 누락 | Ollama Service 설정 | `503 Service Unavailable` | 호출하지 않음 |
| Ollama 서버 연결 불가 | HTTP Client | `503 Service Unavailable` | 접속 실패 |
| Ollama 응답 Timeout | HTTP Client | `504 Gateway Timeout` | 요청 또는 대기 중 실패 |
| Ollama가 오류 Status를 반환 | HTTP Client | `502 Bad Gateway` | Provider 응답 오류 |
| 응답에 `message.content`가 없음 | Service 응답 해석 | `502 Bad Gateway` | Provider 응답 형식 불일치 |
| 정상 응답 | Route | `200 OK` | 정상 처리 |

이 상태 코드 매핑은 **교육용 간단한 설계**입니다. 실제 서비스에서는 모델이 없는 경우와 서버가 다운된 경우를 더 구분하거나 Retry 정책을 적용할 수 있습니다. 단, 사용자의 요청이 잘못된 상황과 Provider 장애를 **모두 `500` 하나로 처리하지 않는 것**이 이번 수업의 핵심입니다.

---

# 11. 두 서버를 실행하고 `/docs`에서 호출하기

Ollama Server와 FastAPI Server는 서로 다른 프로세스입니다. **둘 다 준비**되어야 `/ai/chat`이 실제 AI 답변을 받을 수 있습니다.

먼저 Ollama 쪽 준비가 끝난 것을 확인한 뒤, **`OLLAMA_MODEL`을 설정한 동일한 Terminal에서** 프로젝트 Root로 이동하여 FastAPI를 시작합니다.

```bash
python -m uvicorn app.main:app --reload
```

정상 시작하면 기본 주소에서 다음을 확인합니다.

```text
GET http://127.0.0.1:8000/health
```

예상 응답:

```json
{
  "status": "ok"
}
```

그다음 Browser에서 다음으로 이동합니다.

```text
http://127.0.0.1:8000/docs
```

Swagger UI의 `POST /ai/chat`에서 **Try it out**을 선택하여 다음 JSON을 입력합니다.

```json
{
  "message": "로컬 모델을 API로 호출할 때 HTTP는 어떤 역할을 하나요?"
}
```

정상 응답의 **형태**:

```json
{
  "answer": "HTTP는 Backend와 Ollama가 요청과 응답을 주고받도록 합니다."
}
```

위 답변은 **구조를 이해하기 위한 예시**입니다. 실제 모델은 같은 의미를 다르게 표현할 수 있고 내용이 정확하지 않을 수도 있습니다. 실습의 첫 번째 성공 조건은 **우리가 정의한 `answer: str` 계약을 만족하는 것**입니다.

## 11.1 실제 통합 요청 한 번에서 일어나는 일

1. Client가 `/ai/chat`에 JSON Request를 보냅니다.
2. `ChatRequest`가 메시지를 검증하고 공백을 정리합니다.
3. FastAPI Route가 `ask_ollama()`을 호출합니다.
4. Service가 환경 변수에서 모델 이름을 읽고 `/api/chat` 요청을 만듭니다.
5. `httpx`가 Ollama Server에 HTTP POST를 보냅니다.
6. Ollama가 Local Model을 사용해 응답을 생성합니다.
7. Service가 `response.json()`에서 `message.content`를 꺼냅니다.
8. FastAPI가 `ChatResponse` 형태의 JSON을 Client에 반환합니다.

학생이 직접 작성한 Python 코드의 **실행 지점과 반환 지점**을 찾아 표시하게 합니다. 흐름도를 다시 길게 암기하는 활동이 아니라, 각 단계가 어느 파일에 있는지 찾는 활동입니다.

---

# 12. 먼저 실패시키기 — 입력 문제와 Provider 문제를 구분하자

정상 동작만 확인하면 문제 발생 시 어느 프로그램에서 실패했는지 판단하기 어렵습니다. 다음 순서대로 실험합니다.

## 실험 A. 빈 입력·공백 입력

```json
{
  "message": "   "
}
```

**예상:** FastAPI가 `422`를 반환하고 Ollama에 요청하지 않습니다. 이때 Ollama를 재설치할 이유는 없습니다. 같은 방식으로 빈 문자열(`""`)과 잘못된 타입을 확인합니다.

## 실험 B. 모델 이름이 설정되지 않은 경우

Uvicorn을 중지하고, 테스트용 Terminal에서 `OLLAMA_MODEL`을 비워 새로 실행합니다. 원래 모델 이름은 실습 기록표에 보존합니다.

Windows PowerShell:

```powershell
$env:OLLAMA_MODEL=""
```

macOS / Linux:

```bash
export OLLAMA_MODEL=""
```

**예상:** `/health`는 `200`을 반환할 수 있지만 `/ai/chat`은 `503`입니다. **Backend가 기동하는 것과 실제 AI Provider를 사용할 수 있는 것은 다른 조건**이라는 사실을 확인합니다. 실험이 끝나면 정확한 모델 이름으로 다시 설정합니다.

## 실험 C. Ollama에 연결할 수 없는 경우

강사의 통제하에 Ollama 연결이 불가능한 상태를 만들거나 모의 테스트로 재현합니다. 운영체제의 서비스나 다른 학생이 사용하는 Ollama를 무분별하게 종료하지 않습니다.

**예상:** FastAPI는 `503`을 반환합니다. Ollama 연결 실패를 관찰하는 데 **모의 테스트로도 충분한 부분**과 **실제로 서버를 중지해야 확인할 수 있는 부분**을 구분합니다.

## 실험 D. Provider 응답이 예상 구조와 다른 경우

실제 모델 동작을 망가뜨리는 대신 13장의 테스트에서 `message.content`가 없는 가짜 응답을 반환하도록 합니다.

**예상:** Service가 `OllamaResponseError`를 발생시키고 FastAPI가 `502`를 반환합니다.

---

# 13. Ollama 없이 확인하는 자동 테스트

실제 Ollama 서버나 Model을 실행하지 않고도 **입력 검증, Route와 Service 분리, 상태 코드, HTTP Payload, Response 파싱**을 검사할 수 있습니다. 단, 이것은 **모의 테스트**이며, 실제 Local Model의 응답 속도·정확도·모델 접근 가능성까지 검증하지 않습니다.

`tests/test_api.py` 전체 코드:

```python
import os
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ollama_service import (
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
    ask_ollama,
)


client = TestClient(app)


def test_health_is_independent_of_ollama() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_or_blank_input_is_rejected_before_provider() -> None:
    with patch("app.main.ask_ollama") as mocked_service:
        for value in ("", "   "):
            response = client.post("/ai/chat", json={"message": value})
            assert response.status_code == 422
        mocked_service.assert_not_called()


def test_successful_response_uses_our_schema() -> None:
    with patch("app.main.ask_ollama", return_value="로컬 AI 답변") as mocked:
        response = client.post("/ai/chat", json={"message": " 질문 "})
    assert response.status_code == 200
    assert response.json() == {"answer": "로컬 AI 답변"}
    mocked.assert_called_once_with("질문")


def test_missing_model_configuration() -> None:
    with patch.dict(os.environ, {"OLLAMA_MODEL": ""}):
        response = client.post("/ai/chat", json={"message": "질문"})
    assert response.status_code == 503


@pytest.mark.parametrize(
    ("failure", "expected_status"),
    [
        (OllamaConnectionError("연결 실패"), 503),
        (OllamaTimeoutError("시간 초과"), 504),
        (OllamaResponseError("형식 오류"), 502),
    ],
)
def test_provider_failure_mapping(failure: Exception, expected_status: int) -> None:
    with patch("app.main.ask_ollama", side_effect=failure):
        response = client.post("/ai/chat", json={"message": "질문"})
    assert response.status_code == expected_status


def test_real_service_builds_the_ollama_payload() -> None:
    fake_response = httpx.Response(
        200,
        json={"message": {"role": "assistant", "content": "모의 답변"}},
        request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
    )
    with patch.dict(os.environ, {"OLLAMA_MODEL": "class-model"}):
        with patch("app.ollama_service.httpx.post", return_value=fake_response) as post:
            answer = ask_ollama("질문")
    assert answer == "모의 답변"
    assert post.call_args.kwargs["json"] == {
        "model": "class-model",
        "messages": [{"role": "user", "content": "질문"}],
        "stream": False,
    }


def test_provider_response_without_content_is_rejected() -> None:
    fake_response = httpx.Response(
        200,
        json={"message": {"role": "assistant"}},
        request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
    )
    with patch.dict(os.environ, {"OLLAMA_MODEL": "class-model"}):
        with patch("app.ollama_service.httpx.post", return_value=fake_response):
            with pytest.raises(OllamaResponseError):
                ask_ollama("질문")
```

프로젝트 Root에서 실행합니다.

```bash
python -m pytest -q
```

시험 결과가 통과해도 의미를 정확히 표현해야 합니다.

| 검증 대상 | 위 테스트로 확인 가능? | 별도 조건 |
|---|---|---|
| FastAPI `/health` 응답 | 가능 | Python 테스트 환경 |
| 입력 `422`와 Provider 호출 차단 | 가능 | Mock Service |
| Service의 요청 Payload | 가능 | Mock HTTP Response |
| `503`·`504`·`502` 변환 | 가능 | Mock Exception |
| Ollama Server 실제 작동 | **불가능** | 설치된 Ollama 서버 필요 |
| Local Model의 실제 생성 문장 | **불가능** | 교육장 Local Model 필요 |
| 모델 성능·정확도 | **불가능** | 별도 평가 설계 필요 |

### 강사 확인 포인트

- `test_successful_response_uses_our_schema`는 **FastAPI Route 계약**을 검사합니다.
- `test_real_service_builds_the_ollama_payload`는 **Service가 올바른 Ollama Request를 만드는지** 검사합니다.
- 단위·모의 테스트를 모두 통과한 뒤에도 **실제 모델 연결 테스트**를 반드시 분리해 수행합니다.

---

# 14. Day1과 같은 부분, 실제로 바뀐 부분을 코드에서 찾기

아래 질문은 **Day1에서 배운 내용을 다시 서술하라는 문제**가 아닙니다. 학생이 만든 실제 코드의 위치를 찾아 차이를 설명하게 합니다.

| 질문 | 확인 파일 | 답의 핵심 |
|---|---|---|
| HTTP Endpoint는 누가 제공하나요? | `app/main.py` | FastAPI |
| Client의 잘못된 입력은 어디서 막나요? | `app/schemas.py` | `ChatRequest` |
| Ollama 모델 이름은 어디에서 바꾸나요? | 실행 환경 + `app/ollama_service.py` | `OLLAMA_MODEL` |
| Provider HTTP 요청은 어디에서 발생하나요? | `app/ollama_service.py` | `httpx.post()` |
| Provider JSON에서 필요한 값을 고르는 위치는? | `app/ollama_service.py` | `data["message"]["content"]` |
| HTTP 오류 Status를 결정하는 곳은? | `app/main.py` | `HTTPException` |
| AI Model Weight를 실제로 실행하는 프로그램은? | 우리 코드 외부 | Ollama Runtime |

Cloud와 Local 양쪽 코드가 외형상 비슷해도 **API Request 및 Response 구조가 같다고 가정하지 않습니다.** 예를 들어 Day1의 `response.output_parsed`와 이번 Ollama의 `message.content`는 **같은 필드가 아닙니다.** 그래서 Provider와 통신하는 코드가 별도로 필요합니다.

---

# 15. 학생 실습 — 실행 결과를 제출할 수 있게 정리하기

## 활동 1. 동일한 Endpoint로 서로 다른 질문 보내기

`/docs`에서 다음 질문을 각각 요청합니다.

```text
A. Local Model을 HTTP로 호출한다는 것은 무슨 뜻인가요?
B. Ollama가 응답하지 않는다면 사용자는 무엇을 보게 되나요?
```

학생은 Request Body와 HTTP Status, `answer` 필드의 존재 여부를 기록합니다. **답변이 사실에 맞는지**는 강의 개념과 비교해 별도로 점검합니다.

## 활동 2. 입력이 빈 경우 Ollama가 호출되는지 확인하기

`""`와 `"   "`를 전송합니다. 상태 코드 `422`를 확인하고 **13장의 모의 테스트**에서 실제 Service가 호출되지 않았음을 함께 확인합니다.

## 활동 3. 모델 이름 설정을 일부러 빼보기

모델 환경 변수만 비운 뒤 FastAPI를 재시작합니다. `/health=200`, `/ai/chat=503`을 확인합니다. **Backend 자체가 실행되고 있어도 AI 기능이 준비되지 않았을 수 있다**는 것을 학생이 자신의 말로 설명하도록 합니다.

## 활동 4. Service와 Route 실패를 분리하기

Service 단독 테스트에서 성공했는데 `/ai/chat`이 실패하는 상황, 반대로 `/health`는 정상인데 Service가 실패하는 상황을 비교합니다. 오류 화면 전체를 암기하지 말고 **처음 실패한 파일과 함수**를 기록합니다.

## 활동 5. 클라이언트가 Ollama 내부 구조를 알 필요가 있을까?

다음 구조 중 Client가 알아야 하는 것과 Backend가 감춰야 하는 것을 나눕니다.

```text
/ai/chat
ChatRequest.message
ChatResponse.answer
OLLAMA_MODEL
Ollama /api/chat
Ollama message.content
```

정답 방향: 일반 Client는 **우리 API의 URL·요청·응답 계약**을 알면 됩니다. 모델 이름과 Ollama API의 세부 계약은 Backend가 관리할 수 있습니다.

---

# 16. 선택 응용 과제 — 기본 통합을 끝낸 학생만 진행

다음 과제는 원본 교육과정의 확장 활동입니다. **기본 `/ai/chat`이 먼저 정상 작동한 학생**에게만 진행합니다.

## 16.1 System Message 추가하기

기존 Payload의 `messages`를 다음처럼 변경해 봅니다.

```python
messages = [
    {
        "role": "system",
        "content": "당신은 AI 입문 교육을 돕는 강사입니다.",
    },
    {
        "role": "user",
        "content": message,
    },
]
```

코드의 다른 부분을 바꾸지 않고 메시지 목록만 변경한 뒤 응답을 관찰합니다. Model이 해당 역할 메시지를 어떻게 사용하는지는 모델마다 다를 수 있습니다. **Prompt Engineering 원리나 모델별 Chat Template을 새 단원으로 가르치지는 않습니다.**

## 16.2 모델 이름을 우리 Response에 포함시키기

원본 과제의 핵심은 Client가 사용된 모델을 구분할 수 있도록 만드는 것입니다. `ChatResponse`에 `model: str` 필드를 추가하고, Route가 실제 사용한 모델 이름과 답변을 함께 반환하도록 개선해 봅니다. 단, `main.py`와 `ollama_service.py`가 **동일한 설정값을 읽도록** 설계해야 합니다. 이름만 다른 임의의 상수를 하나 더 만들지 않습니다.

예상 응답의 **형태**:

```json
{
  "model": "<7교시에서_확정한_모델명>",
  "answer": "..."
}
```

## 16.3 Ollama 상태 확인용 Endpoint 설계하기

현재 `/health`는 FastAPI만 확인합니다. 별도의 `GET /health/ai`에서 **Ollama 연결 상태를 확인하는 방법**을 설계합니다. 단순한 상태 확인에 **매번 실제 긴 답변을 생성하지 않도록** 하는 것이 조건입니다. 실제 API와 서버 상태 확인 방식은 교육장 Ollama 환경에 맞춰 검증 후 구현합니다.

## 16.4 Document Summary API 설계하기

원본의 추가 과제처럼 **문서 요약 기능**으로 전환해 봅니다.

```json
{
  "text": "요약할 문서의 본문입니다."
}
```

```json
{
  "summary": "문서의 핵심 내용입니다."
}
```

제출할 설계에는 `Request Schema`, `Response Schema`, `Service 함수`, `Ollama Chat Request`, `입력 길이 제한`, `Provider 오류 처리`를 포함합니다. 여기서 Document Retrieval, Embedding, RAG, 문서 업로드 처리 등의 추가 시스템을 **미리 구현하지 않습니다.**

---

# 17. 실습 오류 진단표 — 먼저 실패한 경계를 찾자

| 관찰한 현상 | 먼저 확인할 위치 | 가능한 원인 | 첫 대응 |
|---|---|---|---|
| `uvicorn` 명령 실행 불가 | Python 환경 | 패키지/가상환경 문제 | `python -m pip show uvicorn` |
| `/docs`에 `/ai/chat`이 없음 | FastAPI | 잘못된 모듈/Route 실행 | `app.main:app` 확인 |
| `/health` 성공, `/ai/chat` 503 | 설정·Ollama 연결 | 모델 변수 없음 / Server 중단 | 환경 변수와 Ollama 상태 확인 |
| `/ai/chat` 422 | `schemas.py` | 빈 값, 공백, 타입/길이 문제 | Request Body 확인 |
| `/ai/chat` 502 | `ollama_service.py` | 모델 이름 불일치 등 Provider HTTP 오류 또는 응답 구조 오류 | Ollama 상태·응답·로그 확인 |
| `/ai/chat` 504 | `httpx` 호출 | 응답 대기 시간 초과 | Model 실행·자원·Timeout 확인 |
| 응답 `answer`가 있으나 설명이 부정확함 | Model 생성 결과 | 모델의 응답 품질 문제 | 출력 내용을 별도 평가 |
| `/health` 성공, 실제 Ollama는 실패 | Endpoint 설계 | `/health`가 FastAPI만 확인 | Health 범위 구분 |

이 표의 핵심은 **상태 코드 하나만으로 원인을 단정하지 않고, 어느 단계까지 정상 실행됐는지 확인하는 것**입니다. Provider가 돌려준 내부 오류나 Secret을 Client에게 그대로 노출하지 않으며, 서버 로그 확인 시에도 민감한 내용이 기록되지 않도록 주의합니다.

---

# 18. 수업 결과 확인표와 제출 기준

수업 종료 시 다음 항목을 체크합니다.

- [ ] 7교시에서 확정한 Ollama 모델 이름을 기록했다.
- [ ] `OLLAMA_MODEL`을 설정했고, Uvicorn 프로세스가 해당 설정을 사용한다.
- [ ] `app/schemas.py`, `app/ollama_service.py`, `app/main.py`를 분리했다.
- [ ] `POST /api/chat` Payload에 `model`, `messages`, `stream: false`가 포함된다.
- [ ] `response.raise_for_status()`와 응답 구조 검사를 구분했다.
- [ ] `/health` 및 `/docs`를 확인했다.
- [ ] `/ai/chat`의 정상 응답을 `{"answer": "..."}` 형태로 받았다.
- [ ] `""`·`"   "` 입력이 `422`로 차단된다.
- [ ] 모델 이름 미설정/연결 실패·Timeout·Provider 응답 오류를 구분했다.
- [ ] Ollama를 사용하지 않는 모의 테스트를 실행했다.
- [ ] **실제 Ollama Model을 이용한 API 호출**을 별도로 확인했다.
- [ ] 같은 Web API 구조에서 Cloud와 Local의 Provider 연결 방식만 어떻게 달라지는지 설명할 수 있다.

### 학생 제출 예시

| 항목 | 학생 기록 |
|---|---|
| 사용 Ollama Model 이름 | |
| Python / FastAPI / httpx 버전 | |
| `/health` 응답 | |
| 정상 `/ai/chat` 요청과 Status | |
| 정상 응답의 `answer` 일부 | |
| 공백 요청 Status | |
| Ollama 연결 실패 시 Status | |
| 모의 테스트 통과 결과 | |
| 실제 모델 호출 여부 및 결과 | |
| 어려웠던 오류와 해결한 위치 | |

실제 Ollama 실행을 하지 못한 학생은 모의 테스트 통과만으로 전체 실습을 완료했다고 표시하지 않습니다. **`모의 테스트 통과`와 `실제 Local Model 통합 성공`은 서로 다른 검증 상태**입니다.

---

# 19. Day2 최종 결과 — 코드로 비교하는 세 가지 실행 구조

Day2에서 새로 얻게 된 성과는 **Ollama를 실행하는 방법을 안다**는 데서 끝나지 않습니다. 이제 학생은 다음 세 가지의 **호출 위치**가 다르다는 사실을 실제 코드를 근거로 설명할 수 있습니다.

| 방법 | Application의 AI 호출 지점 | Model을 실행하는 주체 | 해당 수업 |
|---|---|---|---|
| Cloud API | OpenAI SDK 호출 | Cloud AI Provider | Day1 7~8교시 |
| Python 직접 실행 | `model.generate()` | Python Process의 Transformers/PyTorch | Day2 5교시 |
| Local API | `httpx.post(.../api/chat)` | 별도 Ollama Runtime | **Day2 8교시** |

세 가지 모두 모델에서 결과를 얻을 수 있지만, **모델을 직접 실행하는 프로그램과 Application 사이의 경계**가 다릅니다. 지금 학생이 구현한 것은 세 번째 방법입니다.

여기까지 완료하면 Day2의 수업 실습 흐름은 다음처럼 연결됩니다.

```text
7교시: 사람 → Ollama CLI → Local Model
                      ↓
8교시: Client → FastAPI → Python Service → Ollama API → Local Model
```

그다음 생각할 질문은 다음과 같습니다.

> 같은 기능을 여러 모델 중 어느 모델로 제공할지, 실행 환경과 제약 조건을 무엇으로 판단할 것인가?

이 질문은 **Day3의 모델 선택·실행 환경·운영 판단**으로 넘깁니다. 본 교시에서는 Model Family·Parameter 규모·Quantization·성능 최적화·Provider 추상화 Framework 등을 미리 가르치지 않습니다.

---

# 20. 이번 교시 핵심 정리 및 다음 교시 연결

이번 교시에서 바뀐 것은 Web API 기술 전체가 아니라 **Backend가 결과를 얻는 마지막 연결 방식**입니다.

1. Client는 우리 FastAPI의 `/ai/chat`만 호출합니다.
2. FastAPI는 입력을 검증하고 Provider 통신 코드를 Service에 맡깁니다.
3. Ollama Service는 Local HTTP API에 JSON Request를 보내고 `message.content`를 읽습니다.
4. Ollama Runtime이 학습된 Local Model을 실행합니다.
5. FastAPI는 응답을 `ChatResponse(answer=...)` 형태로 반환합니다.
6. Client 입력 오류, 설정 문제, Provider 연결 문제, 응답 구조 문제를 구분합니다.

**가장 중요한 문장:**

> **Cloud API와 Local API를 사용할 때 Web API의 기본 구조는 유지할 수 있지만, Provider별 요청·응답 계약과 실행 주체는 달라집니다. 이번 실습에서는 그 차이를 Ollama Service 코드로 직접 구현했습니다.**

다음 Day3에서는 이 Local Model을 무조건 선택하기보다 **모델별 실행 조건과 선택 근거를 판단하는 방법**을 학습합니다. 그 상세 개념은 이번 교시의 학습 목표에 포함하지 않습니다.

---

# 참고자료 — 원본 강의에서 안내한 목록

- Ollama 공식 API 문서
- Ollama 공식 Chat API 문서
- FastAPI 공식 문서
- HTTPX 공식 문서
- Pydantic 공식 문서

> 이 목록은 **원본 강의에 있던 참고자료 이름을 보존**한 것입니다. 이번 수정 과정에서 해당 사이트를 외부 검색하여 최신 인터페이스를 확인한 것은 아닙니다. Ollama·FastAPI·HTTPX 버전과 API 세부 동작은 **실제 교육장 환경에서 추가 검증 필요**입니다.

# 관련 Wiki Link

- [[Ollama]]
- [[Local AI]]
- [[FastAPI]]
- [[Pydantic]]
- [[HTTPX]]
- [[API]]
- [[Model Serving]]
- [[AI Provider]]
- [[Provider Abstraction]]
- [[AI Service Architecture]]

# 저장 위치 제안 — 원본 기준

```text
Academy/
└── 03. 실습/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day2_08교시_Python_FastAPI_Ollama_Local_API_통합_실습.md
```

> **편집 상태:** 교육과정 원본과 별도로 생성한 `v0.2` 수정본입니다. 원본 파일과 Google Drive 자료는 변경하지 않았습니다. **실제 Ollama Local Model 통합 실행 및 최종 수업 검수는 별도 확인 사항**입니다.
