# Day 1 - 8교시. FastAPI와 AI 통합 - Structured Output 실습

## 개요 — Python의 AI 호출을 Web API로 확장하기

7교시에는 Python 코드에서 `OpenAI()`와 `client.responses.create()`를 사용하여 Cloud AI에 요청을 보내고 텍스트 응답을 확인했습니다. 이번 교시의 출발점은 그 코드를 다시 따라 치는 것이 아니라, **다른 프로그램이 사용할 수 있는 HTTP API로 감싸고 AI 결과를 일정한 데이터 구조로 받는 것**입니다.

이번에 완성할 기능은 **AI 용어 설명 API**입니다. 클라이언트가 `"Inference"` 같은 용어를 보내면, Backend가 AI 설명을 생성하고 다음 필드를 가진 JSON 응답을 돌려줍니다.

```text
Client → FastAPI(요청 검증) → AI Service → OpenAI SDK → Cloud AI
                                                 ↓
Client ← JSON Response ← Pydantic 모델 ← 구조화된 AI 결과
```

**오늘의 새로운 학습 성과**는 세 가지입니다.

1. `Request Schema`와 `AI Output Schema`를 별도로 만들어 입력과 출력을 검증합니다.
2. HTTP 처리(FastAPI)와 AI 요청(Service)을 나누고, **실패한 위치에 따라 응답을 다르게** 만듭니다.
3. AI가 생성한 데이터를 그대로 믿지 않고, **형식 검증과 내용 검증이 다르다**는 점을 확인합니다.

이 문서는 바로 실행할 수 있도록 파일별 최종 코드를 **한 번씩만** 제공합니다. 코드 중간에 조금씩 수정한 조각을 반복해 보여주는 대신, 완성본을 만들고 해당 줄의 역할을 함께 분석합니다.

> **실행 조건:** 원본에 등장하는 OpenAI `responses.parse()`와 모델 ID는 교육장 계정·SDK·모델 지원 범위에 따라 실제 호출 결과가 달라질 수 있습니다. 여기서는 원본 ZIP의 인터페이스를 바탕으로 구성했으며, 외부 API 및 모델 호환성은 실제 수업 환경에서 별도로 확인해야 합니다. 실제 호출 결과를 실행 검증 완료라고 미리 표시하지 않습니다.

---

# 1. 실습 목표와 완료 기준

이번 교시가 끝나면 학생은 다음을 수행할 수 있어야 합니다.

1. `POST /ai/explain`으로 용어를 보내고 JSON 결과를 받는다.
2. FastAPI와 Pydantic이 **사용자 요청을 검증하는 시점**을 설명한다.
3. Pydantic 모델을 OpenAI Structured Output의 목표 형식으로 전달한다.
4. `app/main.py`, `app/ai_service.py`, `app/schemas.py`의 책임을 구분한다.
5. 정상 요청, 잘못된 요청, Provider 실패를 각각 다른 결과로 확인한다.
6. API Key를 브라우저 코드나 Git 저장소에 넣지 않는다.
7. 자동 테스트에서 실제 AI 호출 없이 Request/Response 계약을 검증한다.
8. 다음 Day 2에서 Cloud Model을 Local Model로 바꾼다면 무엇을 변경해야 하는지 설명한다.

**완료 판정은 두 단계**로 구분합니다.

| 검증 범위 | 완료 기준 | 실제 Cloud API 필요 여부 |
|---|---|---|
| 오프라인 API 계약 검증 | `/health`, 요청 오류, 모의 AI 응답, 실패 응답 테스트 통과 | 필요 없음 |
| 실제 AI 연동 검증 | 사용 가능한 Model ID와 API Key로 `POST /ai/explain` 정상 호출 | 필요함 |

오프라인 테스트만 성공했다고 ‘실제 AI 연동까지 완료’라고 표시하지 않습니다.

---

# 2. 먼저 완성할 API 계약 보기

웹 API를 구현할 때는 먼저 **클라이언트가 무엇을 보내고 무엇을 받을지** 정합니다. 예제에서 요청자는 React일 수도 있고, Swagger UI나 다른 HTTP Client일 수도 있습니다.

**Endpoint:** `POST /ai/explain`

요청 예시:

```json
{
  "term": "Inference"
}
```

정상 응답 예시(실제 모델 실행 결과가 아닌 설명용 샘플):

```json
{
  "term": "Inference",
  "definition": "학습된 모델을 새로운 입력에 사용하여 결과를 얻는 과정입니다.",
  "easy_explanation": "공부를 마친 모델에게 새 문제를 풀게 하는 단계라고 생각할 수 있습니다.",
  "practical_position": "AI 서비스를 실행할 때 모델이나 외부 AI API로 입력을 보내는 과정에서 사용합니다."
}
```

| Field | 자료형 | 의미 |
|---|---|---|
| `term` | `str` | 클라이언트가 요청한 AI 용어 |
| `definition` | `str` | 용어의 핵심 의미 |
| `easy_explanation` | `str` | 초보자를 위한 쉬운 설명 |
| `practical_position` | `str` | 실제 개발 과정에서 만나는 위치 |

이 네 필드는 클라이언트에게 전달하기로 약속한 **데이터 계약(Data Contract)**입니다. 설명 문장은 생성할 때마다 바뀔 수 있지만 필드 이름과 자료형은 일관되게 관리해야 합니다. **필드 구조가 맞는 것과 설명이 사실에 맞는 것은 별개**입니다.

---

# 3. 환경과 프로젝트 준비

## 3.1 필요한 프로그램

원본 강의의 권장 조건은 Python 3.11 이상, 가상환경, FastAPI, Uvicorn, Pydantic, OpenAI Python SDK, 인터넷 연결, 사용할 수 있는 OpenAI API 계정입니다.

7교시 실습과 비슷하게 작업하되, 이번에는 **HTTP 테스트**에 사용할 `httpx`와 `pytest`도 설치합니다. 이것들은 테스트 용도이며 서버에서 AI 모델을 학습시키기 위한 도구가 아닙니다.

```text
day1_ai_api/
├── .venv/                  # 로컬 가상환경, Git에 올리지 않음
├── app/
│   ├── __init__.py
│   ├── schemas.py           # 입력 및 AI 출력 형식
│   ├── ai_service.py        # Cloud AI 요청 및 결과 처리
│   └── main.py              # HTTP Endpoint 및 오류 응답
├── tests/
│   └── test_api.py          # 실제 Cloud 호출이 없는 검증
├── requirements.txt
└── .gitignore
```

`app/__init__.py`는 빈 파일로 만듭니다. Python이 `app.schemas`, `app.ai_service` 같은 경로로 파일을 불러오게 하기 위한 프로젝트 구성입니다.

## 3.2 가상환경 생성 및 패키지 설치

**Windows PowerShell** — 프로젝트 폴더에서:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pydantic openai httpx pytest
```

**macOS / Linux** — 프로젝트 폴더에서:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi uvicorn pydantic openai httpx pytest
```

설치 확인:

```bash
python -m pip show fastapi pydantic uvicorn openai httpx pytest
```

수업 자료를 실제 배포할 때에는 교육장에서 정상 검증한 각 패키지 버전을 기록해 `requirements.txt`에 고정합니다. **검증하지 않은 버전 번호를 임의로 적지 않습니다.** 강사용으로 다음 기본 의존성 목록을 기록해 둘 수 있습니다.

`requirements.txt`:

```text
fastapi
uvicorn
pydantic
openai
httpx
pytest
```

위 목록은 개별 버전을 고정한 파일이 아닙니다. **실제 수업 배포용 버전 고정 및 재현성 검증은 별도 작업**입니다.

`.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
```

## 3.3 API Key와 Model ID 설정

7교시에서 배운 것처럼 `OPENAI_API_KEY`를 환경 변수로 지정합니다. **실제 Key를 코드, 과제 제출물, 채팅 또는 화면 공유에 노출하지 않습니다.**

원본 8교시 예제는 `gpt-5.6`, 앞선 7교시 원본은 `gpt-5`를 사용했습니다. 이름만으로 현재 계정의 실제 사용 가능 여부를 확정할 수 없으므로, **이번 예제는 `OPENAI_MODEL`을 명시적으로 설정하도록 변경**합니다. 수업 진행 전 강사가 해당 계정에서 사용 가능한 모델을 확인해야 합니다.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="<실제 Key: 개인 환경에서만 입력>"
$env:OPENAI_MODEL="<교육장에서 확인한 모델 ID>"
```

macOS / Linux:

```bash
export OPENAI_API_KEY="<실제 Key: 개인 환경에서만 입력>"
export OPENAI_MODEL="<교육장에서 확인한 모델 ID>"
```

Key 값을 표시하지 않고 **설정 여부만** 확인합니다.

```bash
python -c "import os; print('Key 설정됨' if os.getenv('OPENAI_API_KEY') else 'Key 없음'); print('Model 설정됨' if os.getenv('OPENAI_MODEL') else 'Model 없음')"
```

이것은 환경 변수에 값이 있다는 확인이지, 인증 성공이나 모델 사용 권한의 증거는 아닙니다. 실제 확인은 API 연동 단계에서만 가능합니다.

---

# 4. 이번 실습의 책임 분리

앞 교시에서는 `ask_ai()` 함수를 통해 SDK 호출을 한곳으로 모았습니다. 이번에는 그 함수를 웹 서비스에 연결합니다.

| 파일 / 계층 | 하는 일 | 하지 말아야 할 일 |
|---|---|---|
| `schemas.py` — Pydantic | 입력 필드와 출력 필드, 자료형, 길이 조건 선언 | Provider 호출 |
| `ai_service.py` — AI Service | OpenAI SDK로 요청, 구조화 결과 처리 | HTTP 상태 코드 결정 |
| `main.py` — FastAPI | Route, 요청 검증 연결, 결과 반환, 오류의 HTTP 표현 | Prompt와 Provider 호출 로직을 중복 구현 |
| Cloud Provider | Model 실행 및 구조화 출력 생성 | 우리 서비스의 사용자 인증·업무 규칙 대신 처리 |

실습에서는 파일을 물리적으로 나눌 뿐 아니라, **한 계층이 실패했을 때 다른 계층이 어떻게 대응하는지**를 코드에서 확인합니다.

---

# 5. `app/schemas.py` — 입력과 출력 구조 작성

프로젝트에 다음 코드를 작성합니다.

```python
from pydantic import BaseModel, Field, field_validator


class ExplainRequest(BaseModel):
    term: str = Field(min_length=2, max_length=50)

    @field_validator("term")
    @classmethod
    def reject_blank_term(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("용어는 공백 제외 2자 이상이어야 합니다.")
        return cleaned


class AIExplanation(BaseModel):
    term: str
    definition: str
    easy_explanation: str
    practical_position: str
```

## 5.1 `ExplainRequest` — 우리 API가 받는 데이터

요청자는 `{"term": "Inference"}`처럼 JSON을 보내야 합니다. `term`은 문자열이어야 하고 2~50자라는 길이 조건을 만족해야 합니다.

원본 강의에는 `Field(min_length=1, max_length=100)` 예제와 학생 실습의 `2~50자` 확장 예제가 따로 있었습니다. 이번 수정본에서는 수업 마지막에 사용할 **2~50자 계약을 처음부터 일관되게** 적용합니다. 길이 조건을 바꾸는 학생 과제는 뒤에서 별도로 진행합니다.

**왜 `field_validator`를 추가할까요?** `"   "`는 문자열 길이만 보면 여러 글자지만 의미 있는 용어는 아닙니다. `strip()`으로 앞뒤 공백을 제거하고, 제거한 결과가 2자 미만이면 거부합니다. 이 검사는 **AI API 요청 전에 끝납니다.**

| 입력 | 예상 처리 | 이유 |
|---|---|---|
| `{"term":"Inference"}` | 수락 | 유효한 문자열 |
| `{"term":"  Transformer  "}` | 공백 제거 후 수락 | 실제 용어만 사용 |
| `{"term":""}` | `422` | 길이 조건 위반 |
| `{"term":"   "}` | `422` | 공백 제거 시 빈 값 |
| `{"term":"A"}` | `422` | 2자 미만 |
| `{"term":123}` | `422` | 문자열 자료형이 아님 |

## 5.2 `AIExplanation` — AI 결과의 구조

AI Provider에는 문자열 한 줄이 아니라, `definition`, `easy_explanation` 등 **미리 약속한 구조의 결과**를 요청합니다. `AIExplanation`은 그 결과가 만족해야 하는 필드 구성과 자료형을 표현합니다.

`ExplainRequest`가 **클라이언트 → Backend**, `AIExplanation`이 **AI Provider → Backend**에서 쓰인다는 사실을 구분하세요. 두 모델은 단순히 이름만 다른 중복 정의가 아닙니다.

---

# 6. `app/ai_service.py` — Structured Output 호출

이 파일은 7교시의 `ask_ai()`를 확장한 곳입니다. AI 호출 방식 자체를 처음부터 재설명하지 않고 **일반 텍스트 출력에서 Pydantic 객체 반환으로 바뀌는 지점**에 집중합니다.

```python
import os

from app.schemas import AIExplanation


class AIConfigurationError(RuntimeError):
    """교육용 AI 호출 설정이 누락된 경우."""


class AIProviderError(RuntimeError):
    """외부 AI 호출 또는 Provider 응답 처리에 실패한 경우."""


def explain_ai_term(term: str) -> AIExplanation:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL")
    if not api_key or not model_name:
        raise AIConfigurationError("AI API 실행 환경이 설정되지 않았습니다.")

    try:
        from openai import OpenAI
    except ImportError as error:
        raise AIConfigurationError("OpenAI SDK를 불러올 수 없습니다.") from error

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.parse(
            model=model_name,
            instructions=(
                "당신은 AI 입문 교육 조교입니다. "
                "한국어로 정확하고 이해하기 쉽게 설명하세요. "
                "주어진 용어를 설명하고 요청된 필드를 채우세요."
            ),
            input=f"다음 AI 용어를 설명하세요: {term}",
            text_format=AIExplanation,
        )
    except Exception as error:
        # 실제 서비스에서는 SDK 오류 유형별로 세분화합니다.
        raise AIProviderError("AI Provider 요청이 실패했습니다.") from error

    parsed = response.output_parsed
    if parsed is None:
        raise AIProviderError("구조화된 AI 결과를 받지 못했습니다.")

    # term은 모델이 다시 만들어낸 값보다 검증된 사용자 요청값을 사용합니다.
    return parsed.model_copy(update={"term": term})
```

## 6.1 이번 시간에 새로 배우는 세 줄

```python
response = client.responses.parse(..., text_format=AIExplanation)
parsed = response.output_parsed
return parsed.model_copy(update={"term": term})
```

- `text_format=AIExplanation`: Provider에 **어떤 구조의 결과를 요구할지** 전달합니다. 단순히 Prompt에 `"JSON으로 답해"`라고 쓰는 방식과 구분됩니다.
- `output_parsed`: SDK가 구조화된 내용을 Pydantic 객체로 제공하는 경로입니다. `None`이면 우리 서비스가 기대한 결과를 얻지 못한 것입니다.
- `model_copy(update={"term": term})`: 요청에서 검증한 용어를 응답의 `term` 필드에 사용해 **클라이언트가 요청한 항목과 응답 항목의 일관성**을 유지합니다. AI가 만들어낸 문자열을 무조건 신뢰하지 않는 예입니다.

**중요한 한계:** Pydantic이 JSON 필드와 자료형을 확인하더라도 설명의 사실 여부는 자동으로 보장하지 않습니다. 예를 들어 `definition`이 문자열인지 검사할 수 있지만, 그 문장이 올바른 정의인지는 별도의 내용 검증이 필요합니다.

## 6.2 왜 Client를 함수 안에서 생성할까?

원본에서는 모듈 최상단에서 `client = OpenAI()`를 생성합니다. 그러나 Key가 설정되지 않은 경우, **서버 시작 또는 모듈 import 시점에 오류가 날 수 있습니다.** 여기서는 실제 AI 요청이 발생할 때 Client를 만듭니다.

따라서 Key가 없어도 `/health` 같은 기본 Endpoint는 시작할 수 있습니다. 대신 AI 요청을 보내면 설정 부족을 알려줍니다. 이것은 ‘API Key 없이 AI 호출을 할 수 있다’는 뜻이 아닙니다.

이 방식은 **교육용으로 설정 오류와 Provider 호출 오류의 경계를 관찰하기 위한 선택**입니다. 실서비스에서는 Client 수명 주기와 연결 재사용, 요청 동시성도 별도로 설계합니다.

## 6.3 응답 거부·형식 불일치가 생기면?

Structured Output을 요청했다고 모든 입력에서 유효한 결과가 반드시 나오는 것은 아닙니다. 응답 생성이 실패하거나 거부되거나 구조화된 값을 받지 못할 수 있습니다. `None`을 그대로 정상 응답으로 보내지 않고 오류로 처리합니다. **오류를 만났다고 내용을 만들어 채워서 ‘성공’으로 둔갑시키지 않습니다.**

---

# 7. `app/main.py` — HTTP Endpoint와 상태 코드

```python
from fastapi import FastAPI, HTTPException

from app.ai_service import (
    AIConfigurationError,
    AIProviderError,
    explain_ai_term,
)
from app.schemas import AIExplanation, ExplainRequest


app = FastAPI(title="AI Term Explainer")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ai/explain", response_model=AIExplanation)
def explain(request: ExplainRequest) -> AIExplanation:
    try:
        return explain_ai_term(request.term)
    except AIConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail="AI 서비스 설정이 준비되지 않았습니다.",
        ) from error
    except AIProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="AI Provider 응답을 처리할 수 없습니다.",
        ) from error
```

## 7.1 오류를 발생한 위치에 맞게 표현하기

| 상황 | 담당 위치 | 결과 | 학생이 확인할 점 |
|---|---|---|---|
| `/health` 정상 | FastAPI | `200` | AI Key 없이도 서버 기본 상태 확인 가능 |
| 유효한 입력 + AI 정상 응답 | FastAPI + Provider | `200` | 약속한 네 개 필드 확인 |
| `term` 누락·타입 오류·길이 오류 | Pydantic Request Validation | `422` | Provider 호출 전에 거절 |
| Key 또는 Model 환경 변수 누락 | AI Service 설정 | `503` | 서버는 살아 있으나 AI 기능 이용 준비 안 됨 |
| 외부 AI 요청 실패·결과 없음 | AI Service | `502` | Backend가 외부 Provider 결과를 얻지 못함 |

`502`와 `503`은 **이번 교시의 단순화된 응답 정책**입니다. 모든 실패에 이 두 코드를 일률 적용하라는 뜻은 아닙니다. 실제 서비스에서는 Provider 오류 종류, Retry 가능성, 이용 제한 등의 조건에 따라 더 세밀한 구분이 필요합니다.

에러 본문에는 SDK 예외 원문, API Key, 내부 설정값을 그대로 보내지 않습니다. 오류 상세가 필요하면 서버에서 권한을 통제한 로깅 정책을 별도로 적용합니다.

## 7.2 왜 `def`를 사용할까?

이 예제는 **동기식 SDK 호출**을 사용하므로 원본과 같이 일반 `def` Route를 사용합니다. FastAPI는 동기 함수와 비동기 함수를 모두 지원합니다. `async def`로 바꾸기만 하면 요청이 빨라진다는 뜻은 아닙니다. 비동기 SDK Client를 사용하도록 별도로 설계할 때 구조를 변경합니다.

---

# 8. 서버 실행과 Swagger UI 사용

프로젝트 최상위 폴더(`day1_ai_api`)에서 실행합니다.

```bash
python -m uvicorn app.main:app --reload
```

정상적으로 시작되면 다음 주소를 사용합니다.

- 서버: `http://127.0.0.1:8000`
- Health Check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

먼저 `/health`를 요청해 다음 형태의 응답이 나오는지 확인합니다.

```json
{"status": "ok"}
```

그다음 `/docs`에서 `POST /ai/explain`을 열고 **Try it out → Request Body 입력 → Execute** 순서로 진행합니다.

```json
{"term":"Inference"}
```

정상 실행 시 화면에는 `definition`, `easy_explanation`, `practical_position`이 들어 있는 JSON이 나타납니다. 원문의 예시 JSON은 **형태를 설명하는 샘플**이지 실제 모델의 고정 출력이 아닙니다.

**실습 관찰:** 만약 `/health`는 성공하지만 `/ai/explain`은 `503`이라면, ‘FastAPI 서버가 아예 실행되지 않았다’고 판단하면 안 됩니다. API 서버 실행과 외부 AI 기능 사용 가능 여부는 서로 다른 조건입니다.

---

# 9. HTTP 요청에서 JSON 응답까지 따라가기

`POST /ai/explain` 요청이 어떻게 바뀌는지 추적합니다.

```text
① HTTP Request Body: {"term": "Inference"}
        ↓
② ExplainRequest: term의 문자열·길이·공백 검증
        ↓
③ FastAPI Route: explain(request)
        ↓
④ AI Service: explain_ai_term("Inference")
        ↓
⑤ OpenAI SDK: responses.parse(text_format=AIExplanation)
        ↓
⑥ Provider가 생성한 Structured Output
        ↓
⑦ AIExplanation: 네 가지 Field를 가진 Python 객체
        ↓
⑧ FastAPI response_model에 맞춘 직렬화
        ↓
⑨ HTTP Response Body: JSON
```

## 9.1 `Python 객체`와 `JSON`은 왜 다른가?

`AIExplanation`은 Python 프로그램 내부의 데이터 객체입니다. 브라우저가 그 객체를 Python 메모리에서 그대로 전달받는 것은 아닙니다. FastAPI는 응답 모델에 따라 데이터를 직렬화하여 **JSON 형식의 HTTP 응답 본문**을 만듭니다.

JSON이 주로 표현하는 유형은 객체, 배열, 문자열, 숫자, 참/거짓, `null`입니다. Python의 `dict`, `list`, `str`, `int`·`float`, `bool`, `None`과 개념적으로 연결됩니다.

아래 표는 앞서 작성한 코드와 실제 전송 형태를 연결합니다.

| 서버 내부 | 클라이언트에서 보이는 표현 |
|---|---|
| `AIExplanation(term="Inference", ...)` | `{"term":"Inference", ...}` |
| Python의 문자열 | JSON의 문자열 |
| Pydantic `response_model` 검증·직렬화 | HTTP `application/json` 응답 |

이것이 Structured Output을 단순 ‘보기 좋은 답변’이 아니라 **서로 다른 프로그램 사이의 계약**으로 다루는 이유입니다.

---

# 10. AI 응답 형식 검증과 실제 내용 검증을 구분하기

다음 두 상황을 비교합니다.

**사례 A — 구조가 틀림**

```json
{
  "term": "Inference",
  "definition": "설명",
  "easy_explanation": "쉬운 설명"
}
```

`practical_position` 필드가 없습니다. `AIExplanation`이 기대하는 필드 구조와 일치하지 않습니다.

**사례 B — 구조는 맞지만 내용이 틀릴 수 있음**

```json
{
  "term": "Inference",
  "definition": "학습된 모델을 완전히 삭제하는 작업입니다.",
  "easy_explanation": "모델을 지우는 단계입니다.",
  "practical_position": "모델 보관소를 비울 때 사용합니다."
}
```

모든 값이 문자열이므로 **형식만 보면 유효할 수 있지만**, 원본 강의의 Inference 설명과 맞지 않습니다. Pydantic은 이런 오류를 스스로 알아내지 못합니다.

따라서 실제 AI 서비스에서는 최소한 다음을 따로 평가합니다.

- **구조 검증:** 필수 필드, 자료형, 길이 제한, 허용 값 등
- **내용 검증:** 사실에 맞는가, 요청한 용어에 답했는가, 근거 없는 설명은 없는가

이번 교시는 구조 검증을 코드로 실습합니다. 내용 검증의 체계적인 평가 방법은 이후 이론 및 프로젝트에서 확장합니다. **문자열이 네 필드에 들어 있다는 사실만으로 내용이 올바르다고 채점하지 않습니다.**

---

# 11. 실제 Provider 없이 API 계약 테스트하기

개발 중에는 API Key나 네트워크 상태 때문에 결과가 자주 달라질 수 있습니다. 이때 모든 테스트를 실제 모델 호출로 진행하면 **요청 검증이 잘못된 것인지, Provider가 실패한 것인지** 구분하기 어렵습니다.

그래서 먼저 **AI Service 함수만 가짜 결과로 바꾼 테스트(Mock Test)**를 합니다. 이 테스트는 실제 OpenAI API를 호출하지 않습니다. 정상적인 `AIExplanation` 객체를 돌려주는 함수를 임시 연결하여 FastAPI가 HTTP 요청을 올바르게 처리하는지 검사합니다.

`tests/test_api.py`:

```python
from fastapi.testclient import TestClient

import app.main as main_module
from app.ai_service import AIConfigurationError, AIProviderError
from app.schemas import AIExplanation


client = TestClient(main_module.app)


def fake_explain(term: str) -> AIExplanation:
    return AIExplanation(
        term=term,
        definition="학습된 모델을 새 입력에 사용하는 단계",
        easy_explanation="새 문제를 풀게 하는 과정",
        practical_position="AI 서비스가 모델을 호출하는 지점",
    )


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_success(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "explain_ai_term", fake_explain)
    response = client.post("/ai/explain", json={"term": "Inference"})
    assert response.status_code == 200
    assert set(response.json()) == {
        "term", "definition", "easy_explanation", "practical_position"
    }
    assert response.json()["term"] == "Inference"


def test_invalid_input_does_not_call_ai(monkeypatch) -> None:
    def forbidden_call(term: str) -> AIExplanation:
        raise AssertionError("잘못된 입력은 AI를 호출하면 안 됩니다.")

    monkeypatch.setattr(main_module, "explain_ai_term", forbidden_call)
    for bad_term in ["", "   ", "A"]:
        response = client.post("/ai/explain", json={"term": bad_term})
        assert response.status_code == 422


def test_missing_configuration(monkeypatch) -> None:
    def missing_config(term: str) -> AIExplanation:
        raise AIConfigurationError("모의 설정 오류")

    monkeypatch.setattr(main_module, "explain_ai_term", missing_config)
    response = client.post("/ai/explain", json={"term": "Inference"})
    assert response.status_code == 503


def test_provider_failure(monkeypatch) -> None:
    def failing_call(term: str) -> AIExplanation:
        raise AIProviderError("모의 Provider 실패")

    monkeypatch.setattr(main_module, "explain_ai_term", failing_call)
    response = client.post("/ai/explain", json={"term": "Inference"})
    assert response.status_code == 502
```

테스트 실행:

```bash
python -m pytest -q
```

## 11.1 이 테스트가 입증하는 것과 입증하지 않는 것

| 입증할 수 있는 것 | 입증할 수 없는 것 |
|---|---|
| HTTP Route 연결 | 실제 OpenAI 인증 성공 |
| 정상 결과의 네 필드 구조 | 실제 `responses.parse()` 및 Model 호환성 |
| 입력이 잘못되면 `422` 반환 | 외부 API의 속도·비용·Rate Limit |
| Provider 실패를 `502`로 표시 | 모델이 생성한 설명의 사실 정확성 |

이 구분이 매우 중요합니다. **Mock Test 통과는 Backend 계약 검증 성공**이며, 외부 Model 연동 성공을 대신하지 않습니다.

---

# 12. 단계별 학생 활동

## 활동 1. AI 용어를 바꾸어 호출하기

Swagger UI에서 다음 용어를 하나씩 입력합니다.

```text
Machine Learning
Deep Learning
Transformer
LLM
Inference
Foundation Model
```

**확인 질문:** 설명 문장은 달라지는데 `term`, `definition`, `easy_explanation`, `practical_position` 네 필드는 유지되나요? 그 이유가 모델 출력의 ‘우연’인지, 프로그램의 Schema 계약인지 구분해 설명하세요.

## 활동 2. 요청 검증을 일부러 실패시키기

다음 세 요청을 비교합니다.

```json
{"term":""}
```

```json
{"term":"A"}
```

```json
{"term":"  "}
```

**확인 질문:** 이 요청들이 왜 AI Provider까지 도달할 필요가 없을까요? Swagger UI에서 HTTP 상태 코드가 무엇인지 기록하세요. `test_invalid_input_does_not_call_ai`도 실행해 호출 경계를 확인합니다.

## 활동 3. 응답 Schema 확장하기

사용자가 이해하기 쉬운 **용어 적용 사례**를 하나 더 받고 싶다고 가정합니다. `AIExplanation`에 다음 필드를 추가합니다.

```python
example: str
```

추가 후에는 **(1) Schema, (2) Provider Structured Output, (3) 자동 테스트에 쓰는 가짜 응답, (4) 클라이언트가 보는 JSON**의 변화를 확인합니다. 기존 테스트가 새 필드 때문에 실패하면, 이는 **데이터 계약을 변경했으면서 테스트 결과를 업데이트하지 않았다는 신호**입니다. Schema만 수정하고 테스트를 확인하지 않는 것으로 실습을 끝내지 않습니다.

## 활동 4. AI 기능의 실패 위치 찾기

다음 세 상황을 구분합니다.

| 조건 | 먼저 확인할 부분 | 예상 판단 |
|---|---|---|
| `/health` 자체가 연결되지 않음 | Uvicorn 프로세스와 접속 주소 | API 서버 시작·접속 문제 |
| `/health`는 `200`, `/ai/explain`은 `503` | Key와 Model 환경 변수 설정 | AI 기능 설정 누락 가능성 |
| `/health`는 `200`, `/ai/explain`은 `502` | Provider 응답·네트워크·권한·모델 지원 | 외부 호출 또는 결과 처리 실패 가능성 |

실제 API Key를 제거하거나 잘못된 Model ID를 입력하는 실습은 **강사가 안전한 환경을 마련했을 때만** 진행합니다. 오류를 만들기 위해 개인 Key를 공개하지 마세요.

---

# 13. 응용 과제 — Document Summary API

원본에는 `AI Term Explainer`를 **Document Summary API의 축소판**으로 확장하는 과제가 있습니다. Day 1의 기존 문서 분석 사례를 새로운 설명으로 다시 반복하는 대신, 지금 익힌 **Schema 변경과 검증의 적용 문제**로 사용합니다.

새 Endpoint를 다음처럼 설계해봅니다.

```text
POST /ai/summarize
```

요청:

```json
{"text":"긴 문서 내용..."}
```

응답:

```json
{
  "summary": "...",
  "keywords": ["...", "..."]
}
```

**구현 조건**

1. `SummarizeRequest`를 만들고, 빈 텍스트·공백만 있는 텍스트를 거부합니다.
2. `SummaryResult`를 만들어 `summary: str`, `keywords: list[str]`를 정의합니다.
3. AI Provider 호출은 FastAPI Route에 직접 작성하지 않고 AI Service에 분리합니다.
4. `responses.parse()`에 새 Schema를 사용합니다.
5. 정상 응답, 잘못된 입력, AI Provider 실패를 테스트합니다.
6. 실제 Key는 코드나 클라이언트에 저장하지 않습니다.

**과제 제출물:** 새 API의 요청/응답 JSON 예시, 수정한 코드, 자동 테스트 결과, 실제 AI 호출 여부를 구분한 짧은 실습 기록입니다.

이 응용 과제의 목적은 문서 요약의 이론을 다시 배우는 것이 아니라 **동일한 API 설계 방식을 다른 업무에 적용할 수 있는지 확인하는 것**입니다.

---

# 14. React와 연결하는 위치 이해하기

FastAPI API는 Swagger UI에서만 사용하도록 만든 기능이 아닙니다. 웹 화면에서 사용하려면 React가 **우리 Backend Endpoint**를 호출하면 됩니다.

```text
React (Browser)
    │ POST /ai/explain
    ▼
FastAPI (서버)
    │ Secret 보관·입력 검증
    ▼
AI Service → OpenAI SDK → Cloud AI
    │
    ▼
FastAPI JSON Response → React
```

React가 OpenAI API Key를 직접 보유하거나 브라우저에서 Provider Secret으로 호출하는 구성을 기본 방식으로 사용하지 않습니다.

아래 코드는 **개념 확인용**이며, React 프로젝트·서버 주소·CORS 등이 준비되어 있지 않으면 독립적으로 실행되는 완성 프로젝트는 아닙니다.

```javascript
const response = await fetch("/ai/explain", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ term: "Inference" }),
});

if (!response.ok) {
  throw new Error(`API 요청 실패: ${response.status}`);
}

const data = await response.json();
console.log(data.definition);
```

`fetch("/ai/explain")`처럼 상대 경로를 사용할 수 있으려면 같은 Origin으로 배포하거나 개발 환경에서 Proxy를 구성해야 할 수 있습니다. 이번 교시의 검증 대상은 **FastAPI Endpoint**이며 React 프로젝트의 실행은 아닙니다.

---

# 15. 실무에서 추가로 검토해야 하는 것

이번 실습은 교육용의 작은 API입니다. 실제 서비스에서는 단순히 Provider 호출이 된다는 이유로 배포 가능하다고 판단하지 않습니다.

| 검토 항목 | 왜 필요한가 | 이번 교시 범위 |
|---|---|---|
| 사용자 인증·권한 | 누가 비용이 발생하는 AI 호출을 할 수 있는가 | 구조만 소개 |
| API Key 보관 | Secret 노출로 무단 사용이 발생하지 않는가 | 환경 변수 사용 |
| 입력 길이·크기 | 매우 긴 요청이 비용·처리 시간을 증가시키지 않는가 | 용어 길이 검증 |
| Timeout / Retry | Provider가 응답하지 않을 때 어떻게 복구하는가 | 오류 경계 확인 |
| Rate Limit / 비용 | 요청량과 사용량을 통제할 수 있는가 | 별도 구현 필요 |
| 형식 및 사실 검증 | Schema만 맞는 잘못된 답변은 어떻게 다루는가 | 구분·토론 |
| Logging / 개인정보 | 오류를 진단하되 입력·Key를 과도하게 기록하지 않는가 | 별도 구현 필요 |
| Provider 교체 | Cloud/Local 변경 시 어디를 수정할 것인가 | AI Service 책임 구분 |

Provider를 교체한다면 HTTP Route와 Request/Response Schema를 유지하고, **AI Service의 구현만 교체할 수 있는 방향**으로 확장할 수 있습니다. 단, Cloud Provider와 Local Runtime의 Structured Output 지원 방식 및 품질은 서로 다를 수 있으므로 **코드 한 줄만 바꾸면 무조건 호환된다고 가정하지 않습니다.**

---

# 16. 실습 확인표 — 학생 제출 기준

다음 항목을 확인하고 성공하지 못한 항목은 오류와 원인을 적습니다.

- [ ] 가상환경을 만들고 필요한 패키지를 설치했다.
- [ ] `app/schemas.py`에 Request/Output Schema를 작성했다.
- [ ] `app/ai_service.py`에 AI Provider 호출을 분리했다.
- [ ] `app/main.py`에 `/health`, `/ai/explain`을 작성했다.
- [ ] Key와 Model ID를 환경 변수로 관리했다.
- [ ] `/health`와 `/docs`가 실행된다.
- [ ] 공백 및 짧은 입력의 `422`를 확인했다.
- [ ] 모의 AI 결과를 사용하는 자동 테스트를 실행했다.
- [ ] Provider 실패를 `502`로 표시하는 테스트를 확인했다.
- [ ] 정상 JSON의 네 Field를 확인했다.
- [ ] 실제 OpenAI API를 호출했다면 사용 모델·환경·결과를 기록했다.
- [ ] Schema 검증과 사실 검증의 차이를 설명할 수 있다.
- [ ] Cloud Provider와 Local Runtime 전환 시 변경할 위치를 설명할 수 있다.

**제출 예시:** `HTTP 계약 테스트: 통과 / 실제 Provider 호출: 미실행 / 미해결: API 계정 사용 권한 확인 필요`와 같이 **검증 가능한 결과와 미검증 상태를 나누어** 적습니다.

---

# 17. Day 1 마무리 및 Day 2 연결

Day 1의 앞부분에서 AI가 무엇인지, 어떻게 학습된 모델이 만들어지는지, 생성형 AI와 개발 도구가 어떤 관계인지 배웠습니다. 마지막 두 교시에서는 **7교시의 Python API 호출을 8교시의 웹 서비스로 확장**했습니다.

이번 시간에 완성한 가장 중요한 연결은 다음과 같습니다.

```text
Python에서 AI 호출에 성공했다 (7교시)
        ↓
HTTP 요청을 받는 Backend를 만든다 (8교시)
        ↓
입력을 Pydantic으로 검증한다
        ↓
AI Service가 Cloud Provider에 요청한다
        ↓
구조화된 AI 응답을 프로그램 데이터로 다룬다
        ↓
HTTP JSON 응답을 클라이언트에 전달한다
```

**Day 2에서는 같은 ‘모델 추론’ 기능을 Local Runtime으로 옮기는 방향**을 살펴봅니다. 따라서 `AI Model`, `Runtime`, `Provider`, `Application`을 구분했던 앞선 교시의 내용은 반복해서 외우는 이론이 아니라 **어떤 구현 부분이 달라지는지 판단하는 기준**이 됩니다.

> **이번 교시의 핵심:** AI 호출 자체보다, 호출 전후에 어떤 데이터 계약과 검증·오류 처리가 필요한지를 구현할 수 있어야 합니다.

---

# 참고자료 및 수업 전 확인 사항

이 강의는 `00. 교육과정(curriculum).zip`에 포함된 Day 1의 7·8교시 강의 원문 및 해당 과정의 교육 범위를 기준으로 개편했습니다. 외부 문서의 새 API 사양을 강의내용 수정의 근거로 가져오지 않았습니다.

원본에 안내된 참고 영역:

- OpenAI API 및 Structured Outputs 공식 문서
- OpenAI Model 안내 자료
- FastAPI 공식 문서
- Pydantic 공식 문서

**수업 전 검증할 항목:** 교육장에서 실제 설치한 OpenAI Python SDK가 `responses.parse(..., text_format=...)`를 지원하는지, 사용할 Model ID가 해당 계정에서 Structured Output을 지원하는지, 실제 Key로 인증 가능한지, 외부 API 호출의 비용과 사용 권한이 준비되었는지, 브라우저에서 API를 정상 테스트할 수 있는지 확인합니다.

이 자료의 JSON 응답과 Provider 정상 호출 결과는 별도 표시가 없는 한 **설명용 예상 결과**입니다. 인터넷·계정·모델까지 포함한 실제 호출 성공은 교육장 실습 결과로만 판정합니다.
