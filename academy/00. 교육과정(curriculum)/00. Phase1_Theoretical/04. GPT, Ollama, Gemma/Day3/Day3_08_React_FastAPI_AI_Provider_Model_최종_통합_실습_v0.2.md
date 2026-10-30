# Day 3 - 8교시. React → FastAPI → AI Provider → Model 최종 통합 실습 (강의용 v0.2)

## 개요 — 이미 완성한 Backend에 사용자 화면을 연결하고, 실제로 끝까지 검증한다

지금까지 각각의 계층을 따로 확인했습니다. Day 3 - 7교시에서는 Python Backend의 `AIProvider` 계약과 OpenAI/Ollama 구현체를 완성했습니다. **이번 시간에는 그 코드를 다시 만들지 않습니다.** 기존 `POST /ai/chat`을 그대로 사용하면서 React 화면에서 질문을 보내고, 응답과 장애 상태가 사용자의 화면에 어떻게 드러나는지 직접 구현합니다.

```text
사용자가 질문 입력
       ↓
React (입력·상태·화면)
       ↓ JSON / HTTP
FastAPI (기존 POST /ai/chat)
       ↓
AIService → AIProvider (Day3 7교시 완성본)
             ├─ OpenAIProvider → Cloud Model
             └─ OllamaProvider → Local Model
       ↓
같은 Response Contract로 React 화면에 결과 표시
```

**오늘 새로 배우는 것은 '모델 호출 방법'이 아니라, 서로 다른 실행 계층이 연결되었을 때 사용자가 관찰하는 성공·대기·실패·취소를 올바르게 처리하는 방법**입니다. 모델 내용의 좋고 나쁨을 평가하는 수업도, RAG·Agent·문서 처리 기능을 구현하는 수업도 아닙니다.

> **강사에게:** 이 자료는 Day3 7교시 v0.2의 Backend를 실습 출발점으로 삼습니다. 7교시 소스가 없다면 먼저 해당 교시의 완성본을 준비하십시오. 이 문서의 Backend 부분은 *변경 파일*만 제시하며, 이전 교시의 Provider·Factory·Service 구현 코드를 다시 복제하지 않습니다. `VITE_API_BASE_URL`과 실제 모델명 등 수업 환경이 결정되지 않은 값은 강사가 확인합니다.

---

# 1. 학습 목표와 최종 산출물

교시 종료 시 학생은 다음을 **화면·네트워크 기록·코드**로 입증해야 합니다.

1. Day3 7교시의 Backend를 재사용하고 **CORS 허용 Origin만** 필요한 범위로 설정한다.
2. Vite로 React 프로젝트를 준비하고 Browser가 호출할 Backend URL을 설정한다.
3. `aiApi.js`에서 HTTP 요청·응답 파싱을 담당하게 하며, `App.jsx`에서는 화면 상태에 집중한다.
4. `idle → loading → success/error/cancelled`의 상태 변화를 화면에서 확인한다.
5. `POST /ai/chat` Request `message`, Response `provider`·`model`·`answer`의 **동일한 계약**을 사용한다.
6. Browser Developer Tools에서 Request/Response 및 실패 위치를 근거로 오류를 분석한다.
7. Provider 선택을 변경해도 React 소스와 API 요청 구조는 수정하지 않음을 확인한다.
8. **Browser 요청 취소가 Model 실행 중단을 보장하지 않는다는 한계**를 설명한다.

**제출물:** 실행 가능한 `backend/`·`frontend/`, 설정 예시(`.env.example`), 정상 요청과 실패 요청의 Network 관찰 기록, Provider 교체 전후 비교표, 전체 연결 경로를 설명하는 간단한 구조도입니다. OpenAI API 이용이 불가능하면 Ollama + Backend Mock 경로로 Frontend 계약을 검증하고 Cloud Provider 실측은 `미검증`으로 표기합니다.

# 2. 이전 강의의 결과물과 이번 교시의 변경점

| 이미 완료한 학습 / 구현 | 이번 교시에서 사용할 방식 | 다시 하지 않을 것 |
|---|---|---|
| Day1: OpenAI SDK·FastAPI·Structured Output | 기존 지식을 오류·계약 확인에 적용 | 인증 방식·Pydantic 기본 문법 재강의 |
| Day2: Ollama CLI와 Local API | 실행 가능한 Local Backend 대상으로 사용 | `ollama pull`·`httpx.post` 실습 반복 |
| Day3 1~5교시: Model Family·Quantization·Hardware·Selection | 선정된 모델 이름과 실행 환경을 기록 | 후보 모델 평가·메모리 계산 반복 |
| Day3 6교시: Framework·Tool·Agent | 별도 Framework 없이 만든 아키텍처 사용 | RAG·Tool/Agent 흐름 구현 |
| Day3 7교시: `AIProvider`·`Factory`·`AIService` | Backend 디렉터리를 **그대로 복사해서 확장** | Provider·Factory·Service 코드 재작성 |
| **Day3 8교시: 최종 웹 연동** | React·Browser HTTP·CORS·상태·취소·장애 경계 | **이번 교시의 고유 결과** |

이 수업의 핵심 변화는 **'어떤 Provider에 요청할 것인가'에서 '사용자에게 어떻게 정확한 실행 상태와 결과를 보여줄 것인가'로 관심사가 이동한다는 것**입니다.

# 3. 완성할 프로젝트 구성 — 새 파일과 재사용 파일의 경계

Day3 7교시 프로젝트를 다음과 같이 가져옵니다. `backend/app/` 아래 파일은 **기존 소스 재사용**이 원칙입니다. 이번에 변경하는 Backend 파일은 `app/main.py` 하나입니다.

```text
ai_final_app/
├── backend/                        # Day3 7교시 소스 그대로 가져오기
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # 이번에 CORS 설정만 추가
│   │   ├── schemas.py              # 변경 없음
│   │   ├── config.py               # 변경 없음
│   │   ├── service.py              # 변경 없음
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── base.py             # 변경 없음
│   │       ├── errors.py           # 변경 없음
│   │       ├── factory.py          # 변경 없음
│   │       ├── openai_provider.py  # 변경 없음
│   │       └── ollama_provider.py  # 변경 없음
│   ├── tests/
│   │   └── test_provider.py        # 기존 테스트 유지
│   ├── requirements.txt            # 기존 검증 환경 사용
│   ├── .env.example                # Frontend Origin 항목만 추가
│   └── .env                        # Git에 포함하지 않음
└── frontend/                       # 이번 교시의 주요 구현 대상
    ├── index.html                  # Vite가 생성
    ├── package.json                # Vite가 생성
    ├── .env.example
    ├── .env
    └── src/
        ├── main.jsx
        ├── App.jsx                  # 새로 작성
        └── api/
            └── aiApi.js            # 새로 작성
```

**검수 질문:** 이 수업을 마친 뒤에도 Backend의 `schemas.py`, `service.py`, `providers/*.py`에 수정 사항이 없다면, 그 자체가 **기존 API 계약을 유지하면서 Frontend만 확장했다는 증거**입니다.

# 4. 실습 전 확인 — 한 번에 세 가지를 시작하지 않는다

수업 시작 전에 강사는 다음 준비 상태를 확인합니다.

| 검증 항목 | 확인할 증거 | 실패 시 대응 |
|---|---|---|
| Python Backend | Day3 7교시 `python -m pytest -q tests/test_provider.py` 결과 | 먼저 Backend 문제 해결 |
| Provider 설정 | `AI_PROVIDER`, 해당 Model 설정값, 필요한 인증/Local Runtime | 선택한 Provider 환경만 준비 |
| Backend 단독 응답 | `POST /ai/chat`의 JSON Response 확인 | Frontend 작업 전 API 정상화 |
| Frontend 실행 도구 | `node --version`, `npm --version` | Vite 설치·지원 버전 점검 |
| 두 Server의 실행 위치 | Backend URL 및 Vite가 출력한 Frontend URL | URL·Port 기록 |
| Cloud 실측 조건 | 실제 API Key·사용 권한·비용 허용 | 없으면 Mock/Local 중심으로 대체 |

**학생이 알아야 할 기준:** Backend 자체가 실패한 상황에서 React 코드를 먼저 고치는 것은 비효율적입니다. 이번 수업은 **Backend 단독 동작 → CORS → Frontend 연동 → 장애 실험** 순서로 진행합니다.

`.env`에는 실제 API Key가 들어갈 수 있습니다. 제출물·화면 캡처·Git Repository에 키가 노출되지 않도록 관리합니다. `VITE_`로 시작하는 Vite 환경 변수는 Browser에 노출될 수 있으므로 비밀키를 넣지 않습니다.

# 5. 변경하지 않을 API Contract — Frontend와 Backend의 약속

7교시에서 확정한 Client API를 그대로 사용합니다.

| 구분 | 값 |
|---|---|
| Method + Path | `POST /ai/chat` |
| Request Content-Type | `application/json` |
| Request Body | `{"message": "질문 문자열"}` |
| 성공 상태 | `200 OK` |
| 성공 Body | `{"provider": "...", "model": "...", "answer": "..."}` |
| 잘못된 입력 | Backend `422` |
| Provider 연결 실패 | Backend `503` |
| Provider Timeout | Backend `504` |
| Provider 응답 이상 | Backend `502` |

예상 **요청 형식**:

```json
{
  "message": "회의 일정 변경 시 확인할 항목을 두 가지로 적어줘."
}
```

예상 **응답 형식** (실제 모델 답변이 아닌 구조 예시):

```json
{
  "provider": "ollama",
  "model": "<강사가 검증한 모델명>",
  "answer": "<모델이 실제 생성한 텍스트>"
}
```

여기서 Browser의 URL은 FastAPI의 `http://localhost:8000`으로 향합니다. React는 Ollama의 `11434` Port도, OpenAI API Key도 알 필요가 없습니다. 중요한 것은 **서버가 약속한 JSON 필드만 받는 것**입니다.

# 6. CORS는 이번 교시의 Backend에서 새로 필요한 설정

앞선 교시에는 주로 CLI·Python Client에서 Backend를 호출했습니다. 이제 **Browser**가 `http://localhost:5173`에서 `http://localhost:8000`으로 요청합니다. Host는 같아도 Port가 다르므로 서로 다른 **Origin**입니다.

```text
React 개발 서버: http://localhost:5173
FastAPI Backend : http://localhost:8000
                         ↑ 서로 다른 Origin
```

Browser는 이런 교차 출처 요청에 대해 CORS 정책을 적용합니다. 이번 `POST /ai/chat`은 `Content-Type: application/json`을 사용하므로, Browser가 실제 POST 전에 **`OPTIONS` Preflight**를 보낼 수 있습니다.

```text
Browser ── OPTIONS /ai/chat ──▶ FastAPI (CORS 허용 여부 확인)
Browser ◀── CORS 허용 응답 ──── FastAPI
Browser ── POST /ai/chat ────▶ FastAPI (실제 질문)
```

**중요한 구분:** CORS는 **Browser의 교차 출처 응답 접근 제한**에 관한 설정입니다. Server API의 인증·권한 검사 기능을 대신하지 않습니다. CORS 오류는 AI 모델의 성능 문제가 아닙니다.

## 6-1. Day3 7교시 `app/main.py`에 적용할 수정

7교시 코드를 복사한 뒤, `app/main.py` 상단에 다음 Import를 **추가**합니다.

```python
import os
from fastapi.middleware.cors import CORSMiddleware
```

기존 `create_app()` 내부의 다음 줄:

```python
api = FastAPI(title="AI Provider Abstraction")
```

**바로 다음에** 아래 블록을 추가합니다. `@api.get(...)`, `@api.post(...)` 등 기존 Route와 오류 처리 코드는 **변경하지 않습니다.**

```python
    raw_origins = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173"
    )
    allowed_origins = [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    api.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
```

이 코드는 함수 내부에 들어가므로 들여쓰기를 그대로 유지합니다. 허용 Origin을 공백 없이 정확히 기록해야 합니다. 강사는 프런트엔드 개발 서버가 출력한 주소가 `5173`이 아니라면 `FRONTEND_ORIGINS` 값을 실제 URL로 수정합니다.

`backend/.env.example`에 **새로 추가할 한 줄**:

```dotenv
FRONTEND_ORIGINS=http://localhost:5173
```

`allow_credentials=False`는 이번 실습이 Cookie 인증을 사용하지 않기 때문입니다. 인증·세션을 추가하는 실습은 이 교시의 범위가 아니며, 추후 인증 정책에 따라 CORS를 다시 설계해야 합니다.

**코드가 제대로 변경됐는지 확인하는 질문:** `main.py` 안에 Provider 선택 분기나 Ollama URL, OpenAI Key가 새로 생겼는가? **그렇다면 이번 수업의 목적에서 벗어난 수정**입니다.

# 7. CORS 적용 후 Backend 먼저 실행

`backend/` 디렉터리에서 Day3 7교시에 사용한 가상환경을 활성화하고 `.env` 설정을 확인합니다. Local Model을 쓴다면 Day2에서 준비한 Ollama Runtime과 Model이 요청을 처리할 수 있어야 합니다.

```bash
cd ai_final_app/backend
python -m pytest -q tests/test_provider.py
python -m uvicorn app.main:app --reload --port 8000
```

위 명령은 **Backend 테스트 성공을 전제로 다음 줄을 별도로 실행**하는 절차입니다. 이미 8000 Port를 사용하는 프로그램이 있으면 Port를 조정하고 이후의 Frontend URL도 동일하게 변경합니다.

Browser에서 `http://localhost:8000/health`를 엽니다. 이 Endpoint는 서버가 살아 있고 선택한 Provider·Model 설정이 무엇인지 보여줄 뿐, **실제 Model의 Generation 성공을 보장하지 않습니다.** 실제 기능 확인에는 `POST /ai/chat` 응답이 필요합니다.

강사 관찰 포인트: 이 단계에서 FastAPI가 동작하지 않으면 아직 CORS 또는 React의 문제라고 단정해서는 안 됩니다.

# 8. React 프로젝트 생성 — 빠진 실행 파일 없이 시작하기

원본 자료에는 `App.jsx`와 `aiApi.js`가 있지만, 그것만 복사하면 `package.json`·`index.html`이 없어 Frontend가 실행되지 않을 수 있습니다. 이번에는 Vite로 **실행 가능한 프로젝트 골격부터** 만듭니다.

`ai_final_app/` 디렉터리에서:

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

**주의:** 위 명령은 온라인 설치 과정이 포함되며 최신 Vite·React 조합이 학생 PC의 Node 버전을 지원하는지 수업 전에 확인해야 합니다. 교실에서는 강사가 **사전에 설치·검증한 프로젝트와 의존성 버전**을 배포하는 방식을 권장합니다. 이 문서는 현재 외부 Package 버전의 실기 호환성을 검증한 자료가 아닙니다.

Vite 생성 시 `frontend` 폴더가 이미 존재한다면 내용을 덮어쓰기 전에 확인하십시오. 생성된 `src/App.jsx`는 아래 완성 예제로 교체하고, `src/api/aiApi.js`를 새로 추가합니다. `src/main.jsx`와 `index.html`, `package.json`은 생성된 기본 파일을 재사용합니다.

## 8-1. Frontend 환경 변수

`frontend/.env.example`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

`.env.example`을 `.env`로 복사합니다. 이 설정은 **Browser에서 접근 가능한 Backend 주소**여야 합니다. 다른 PC에 Backend가 있다면 Frontend PC 입장에서 `localhost`가 그 PC 자신을 뜻하므로 그대로 사용할 수 없습니다. 강사는 실습 배치에 따라 실제 주소와 접근 정책을 확인해야 합니다.

`.env` 값을 바꿨다면 Vite 개발 서버를 재시작해 적용 여부를 확인합니다.

# 9. 새 파일 ① — `src/api/aiApi.js`: HTTP 통신의 단일 창구

이 파일은 화면을 관리하지 않습니다. 입력을 JSON으로 보내고, 서버 응답을 읽으며, **HTTP Error와 Network Error를 구분해 UI에 전달**합니다. Day1의 Fetch·JSON 개념을 다시 강의하는 대신 실사용 결과를 확인합니다.

`frontend/src/api/aiApi.js`:

```javascript
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || ""
).replace(/\/$/, "");

export class AIRequestError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "AIRequestError";
    this.code = code;
  }
}

export async function sendChat(message, signal) {
  if (!API_BASE_URL) {
    throw new AIRequestError(
      "CONFIG", "Frontend의 VITE_API_BASE_URL 설정을 확인하세요."
    );
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal,
    });
  } catch (error) {
    // 사용자가 Cancel한 경우에는 React가 취소 상태를 처리합니다.
    if (error?.name === "AbortError") throw error;
    throw new AIRequestError(
      "NETWORK", "Backend에 연결할 수 없습니다. URL·Server·Network를 확인하세요."
    );
  }

  // 오류 Body가 JSON이 아닐 수도 있으므로 파싱 실패와 HTTP 오류를 구분합니다.
  let data;
  try {
    data = await response.json();
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    if (!response.ok) {
      throw new AIRequestError(
        "HTTP", `요청 실패: HTTP ${response.status}`
      );
    }
    throw new AIRequestError("FORMAT", "Backend 응답이 JSON 형식이 아닙니다.");
  }

  if (!response.ok) {
    const messageByStatus = {
      422: "입력 형식을 확인하세요.",
      502: "AI Provider의 응답을 처리할 수 없습니다.",
      503: "AI Provider에 연결할 수 없습니다.",
      504: "AI Provider 응답 시간이 초과되었습니다.",
    };
    throw new AIRequestError(
      "HTTP",
      messageByStatus[response.status] || `요청 실패: HTTP ${response.status}`
    );
  }

  if (
    !data ||
    typeof data.provider !== "string" ||
    typeof data.model !== "string" ||
    typeof data.answer !== "string"
  ) {
    throw new AIRequestError(
      "FORMAT", "Backend Response Contract가 일치하지 않습니다."
    );
  }

  return data;
}
```

## 9-1. 코드 읽기 — 이번 교시에서 새롭게 중요한 지점

| 코드 지점 | 이번 실습의 의미 | 확인할 관찰 결과 |
|---|---|---|
| `VITE_API_BASE_URL` | Browser가 호출할 서버 위치를 환경과 분리 | DevTools에서 실제 요청 URL 확인 |
| `fetch(..., {signal})` | Request를 AbortController와 연결 | 취소 시 Browser Request 중단 시도 |
| `response.ok` | HTTP Status를 성공·실패로 구분 | 4xx/5xx를 성공 답변으로 표시하지 않음 |
| `response.json()` | 우리 API 응답 본문을 읽음 | JSON이 아니면 `FORMAT` 오류 |
| Response 필드 검사 | Backend와 Frontend의 계약을 점검 | `answer`가 없으면 성공 화면을 표시하지 않음 |
| `AIRequestError.code` | 오류가 통신·설정·형식 중 어디에 가까운지 전달 | 화면의 진단 메시지에 활용 |

`fetch()`는 HTTP `500` 같은 상태가 나와도 네트워크 오류로 Promise를 자동 거부하지 않습니다. 따라서 `response.ok` 검사 없이 `await response.json()`만 호출하면 **실패를 정상 생성 결과로 해석하는 오류**가 생길 수 있습니다.

실제 Provider 내부 오류 상세나 Key·Traceback은 Frontend에 표시하지 않습니다. 사용자가 확인할 수 있는 상태 메시지와 개발자가 점검하는 서버 로그를 구분합니다.

# 10. 새 파일 ② — React의 상태는 사용자에게 보이는 사실을 표현한다

이번 UI는 한 번에 하나의 Request만 허용합니다. 화면에서 관리할 값은 다음과 같습니다.

| 값 | 의미 | 예 |
|---|---|---|
| `message` | 사용자가 편집 중인 질문 | `"공지 제목을 만들어줘"` |
| `status` | 진행 상태 | `idle`, `loading`, `success`, `error`, `cancelled` |
| `result` | 성공 후 표시할 JSON | `{ provider, model, answer }` |
| `errorMessage` | 실패·취소 안내 | `"Backend에 연결할 수 없습니다."` |
| `controllerRef` | 현재 Request 취소 컨트롤러 | `AbortController` |
| `requestSeqRef` | 이전 Request의 늦은 완료를 무시하기 위한 번호 | `1`, `2`, `3` |

상태 전이 표를 먼저 학생에게 보여줍니다.

| 지금 상태 | 사건 | 다음 상태 | 화면 결과 |
|---|---|---|---|
| `idle` | 유효한 질문 전송 | `loading` | 전송 비활성화·진행 안내 |
| `loading` | 성공 Response 수신 | `success` | Provider·Model·Answer 표시 |
| `loading` | Network 또는 HTTP 실패 | `error` | 오류 메시지 표시 |
| `loading` | 취소 Button 클릭 | `cancelled` | 취소 안내·이전 답변 무시 |
| `success/error/cancelled` | 새 질문 전송 | `loading` | 이전 결과 정리·다시 요청 |

**중요:** `cancelled`는 이 UI가 더 이상 해당 Request의 응답을 기다리거나 표시하지 않는다는 뜻입니다. **Backend·Ollama·Cloud Model의 실제 생성이 즉시 중단됐다는 보증은 아닙니다.**

# 11. 새 파일 ③ — `src/App.jsx`: 질문·결과·취소·오류를 한 화면에서 다루기

`frontend/src/App.jsx`:

```jsx
import { useRef, useState } from "react";
import { AIRequestError, sendChat } from "./api/aiApi.js";

export default function App() {
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const controllerRef = useRef(null);
  const requestSeqRef = useRef(0);

  async function handleSubmit(event) {
    event.preventDefault();

    // 같은 화면에서 동시 요청이 겹치지 않게 합니다.
    if (controllerRef.current !== null) return;

    const question = message.trim();
    if (!question || question.length > 2000) {
      setStatus("error");
      setErrorMessage("질문은 1~2000자로 입력하세요.");
      return;
    }

    const requestId = ++requestSeqRef.current;
    const controller = new AbortController();
    controllerRef.current = controller;
    setResult(null);
    setErrorMessage("");
    setStatus("loading");

    try {
      const data = await sendChat(question, controller.signal);
      // 취소된 이전 요청의 응답이 뒤늦게 도착해도 표시하지 않습니다.
      if (requestId !== requestSeqRef.current) return;
      setResult(data);
      setStatus("success");
    } catch (error) {
      if (requestId !== requestSeqRef.current) return;
      if (error?.name === "AbortError") {
        setStatus("cancelled");
        setErrorMessage("화면에서 요청을 취소했습니다.");
      } else {
        setStatus("error");
        setErrorMessage(
          error instanceof AIRequestError
            ? error.message
            : "예상하지 못한 오류가 발생했습니다."
        );
      }
    } finally {
      if (requestId === requestSeqRef.current) {
        controllerRef.current = null;
      }
    }
  }

  function handleCancel() {
    if (controllerRef.current === null) return;
    // 번호를 먼저 바꿔 이전 Request의 결과 적용을 차단합니다.
    ++requestSeqRef.current;
    controllerRef.current.abort();
    controllerRef.current = null;
    setResult(null);
    setStatus("cancelled");
    setErrorMessage("화면에서 요청을 취소했습니다.");
  }

  const busy = status === "loading";

  return (
    <main style={{ maxWidth: 720, margin: "2rem auto", padding: "1rem" }}>
      <h1>AI Provider Chat</h1>
      <p>FastAPI의 동일한 API로 Cloud 또는 Local Model에 질문합니다.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="question">질문</label>
        <textarea
          id="question"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="답변이 필요한 질문을 입력하세요."
          maxLength={2000}
          rows={5}
          disabled={busy}
          style={{ display: "block", width: "100%", margin: "0.5rem 0" }}
        />
        <button type="submit" disabled={busy || !message.trim()}>
          질문 전송
        </button>{" "}
        <button type="button" onClick={handleCancel} disabled={!busy}>
          요청 취소
        </button>
      </form>

      <section aria-live="polite" style={{ marginTop: "1.5rem" }}>
        {status === "idle" && <p>질문을 입력하면 결과가 여기에 표시됩니다.</p>}
        {busy && <p role="status">AI 응답을 기다리는 중입니다...</p>}
        {(status === "error" || status === "cancelled") && (
          <p role="alert">{errorMessage}</p>
        )}
        {status === "success" && result && (
          <div>
            <h2>AI Response</h2>
            <p>Provider: {result.provider}</p>
            <p>Model: {result.model}</p>
            <pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
              {result.answer}
            </pre>
          </div>
        )}
      </section>
    </main>
  );
}
```

## 11-1. 코드를 읽을 때 꼭 설명할 부분

**`status`는 Server가 보내는 필드가 아닙니다.** Browser에서 Request 진행 상황을 표현하는 React 상태입니다. 반면 `provider`, `model`, `answer`는 Backend가 실제로 반환한 JSON 필드입니다. 이 둘을 섞으면 Loading 중 과거 결과가 나타나는 등의 오류를 만들 수 있습니다.

**`AbortController`는 '모델 중지 버튼'이 아닙니다.** Browser에서 해당 `fetch`를 취소하도록 요청합니다. 일부 Server/Provider는 이미 시작한 Generation을 계속 처리할 수 있습니다.

**`requestSeqRef`는 취소 후의 늦은 응답을 무시하는 안전장치**입니다. 예를 들어 첫 번째 질문을 취소하고 두 번째 질문을 전송했는데 첫 번째 요청이 늦게 완료되어도, 번호가 맞지 않으면 React State를 덮어쓰지 않습니다. 이것은 Agent나 AI 내부 이론이 아니라 일반적인 비동기 UI의 **응답 순서 관리**입니다.

**이 UI는 질문 하나만 전송합니다.** 대화 이력, Context 보존, 사용자별 Session 관리, Streaming 응답은 구현하지 않습니다. 그런 기능은 별도 계약과 상태 설계가 필요합니다.

# 12. `main.jsx`는 Vite가 만든 기본 진입점을 사용한다

Vite React 템플릿의 `src/main.jsx`가 `App`을 렌더링하는지 확인합니다. 자동 생성한 기본 내용을 사용할 수 있습니다. 파일이 누락되었다면 다음 최소 예제를 사용합니다.

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

Vite의 `index.html`에 `<div id="root"></div>`가 있어야 이 진입점이 화면을 렌더링할 수 있습니다. Vite가 만든 기본 파일에서는 이미 준비되어 있습니다. 별도 CSS나 디자인 라이브러리는 필수가 아닙니다.

# 13. Backend와 Frontend를 두 개의 Terminal에서 실행한다

**Terminal A — Backend**:

```bash
cd ai_final_app/backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal B — Frontend**:

```bash
cd ai_final_app/frontend
npm run dev
```

Frontend 실행 주소는 Vite 출력에서 확인하고 Browser로 엽니다. 일반적인 기본값은 `http://localhost:5173`이지만, 실제 주소가 다르면 CORS 설정을 수정합니다.

학생이 첫 질문을 보내기 전에 확인할 조건:

- `GET http://localhost:8000/health`가 정상 응답하는가?
- Browser 개발자 도구에서 JavaScript Console 오류가 없는가?
- `VITE_API_BASE_URL`이 **Ollama 주소가 아닌 FastAPI 주소**인가?
- Backend의 CORS 허용 Origin과 실제 Frontend Origin이 일치하는가?

# 14. 첫 번째 End-to-End 실습 — 사용자의 질문이 왕복하는지 확인

이번 교시의 신규 예제는 이전 강의에서 자주 사용한 'AI 개념 설명'을 반복하지 않고, **행사 안내 문구**를 사용합니다.

React 입력창:

```text
동아리 발표회에 참여할 학생을 모집합니다.
참가 신청 마감 안내를 정중한 한국어 두 문장으로 작성해줘.
```

실제 화면과 Network 탭에서 다음 사항을 확인합니다.

| 단계 | 확인 위치 | 관찰할 내용 |
|---|---|---|
| 1 | React 입력창 | 전송한 문자열과 전송 Button의 상태 |
| 2 | Network `OPTIONS` (발생 시) | CORS Preflight Status와 응답 Header |
| 3 | Network `POST /ai/chat` | Request URL이 FastAPI인지, JSON `message`가 맞는지 |
| 4 | Backend 로그 | 요청이 `/ai/chat`에 도달했는지 |
| 5 | Network Response | `provider`, `model`, `answer` 필드가 모두 있는지 |
| 6 | React 화면 | `loading` 이후 `success`, 실제 Model 이름과 Answer 표시 |

**완료 조건:** 모델 문장이 강사의 예시와 한 글자까지 같아야 하는 것이 아닙니다. **Browser가 보낸 내용이 정해진 Backend 계약을 따라 Model까지 전달되고, 실제 응답의 필드가 화면에 표시되는지**가 이번 교시의 핵심입니다.

# 15. Developer Tools를 이용한 '눈에 보이는' 데이터 흐름 추적

학생은 Chrome/Edge 등 Browser 개발자 도구의 **Network** 탭에서 요청을 선택하고 아래 표를 채웁니다. 브라우저 종류에 따라 표시 항목명은 조금 다를 수 있습니다.

| 확인 항목 | 학생 기록 | 정상 판별 기준 |
|---|---|---|
| Request URL |  | FastAPI Backend의 `/ai/chat` |
| Request Method |  | `POST` |
| Status Code |  | 정상 시 `200` |
| Request Headers |  | JSON Content-Type |
| Request Payload |  | `message` 한 필드가 전송됨 |
| Response JSON |  | `provider`, `model`, `answer` |
| Response 시간 |  | 실측값 기록 (기준값 임의 지정 금지) |
| 화면 상태 |  | `loading`에서 `success`로 전이 |

**질문:** Network 탭에 `OPTIONS`만 보이고 `POST`가 없으면 어디를 조사할까? Browser의 CORS 정책과 FastAPI의 CORS 응답 설정을 먼저 확인합니다. `POST`가 `502`로 끝났다면 Browser에서 요청 자체는 Backend에 도달했으므로 Provider 방향을 확인합니다.

# 16. 화면 상태 실습 — `idle`, `loading`, `success`

서버가 빨리 응답하는 환경에서는 `loading` 상태가 순간적으로만 보일 수 있습니다. 이것은 반드시 실패가 아닙니다. 학생은 개발자 도구의 Network 기록과 React의 상태 변화를 함께 확인합니다.

실습 질문:

1. 전송 전에는 어떤 버튼이 비활성화되어 있는가?
2. `loading` 중 사용자가 연속 클릭해도 중복 Request가 발생하지 않는가?
3. 성공 후 화면에 Model 결과 외에 어떤 정보를 표시하는가?
4. 새로운 질문을 보내면 이전 Answer가 그대로 남아 혼동을 주는가?

이 질문은 React `useState` 전체 문법을 다시 배우기 위한 것이 아니라 **AI 요청의 대기 시간이 화면 상태를 필요하게 만드는 이유**를 코드와 연결하기 위한 것입니다.

# 17. 취소 실습 — UI 취소와 Backend의 실제 작업을 분리해서 생각하기

실행 시간이 충분한 모델을 사용하는 환경에서 질문을 전송하고 응답이 오기 전에 **요청 취소**를 클릭합니다. 모델이 즉시 응답하면 취소를 재현하기 어려울 수 있으므로, 그 경우에는 앞 교시의 Mock Provider나 수업용 지연 응답을 이용할 수 있습니다. 실제 Provider를 임의로 중지시키며 다른 학생의 작업에 영향을 주지 않습니다.

관찰:

```text
React에서 Cancel 클릭
        ↓
AbortController.abort() 호출
        ↓
Browser의 fetch 취소 시도
        ↓
React는 cancelled 상태 표시
        ↓
늦게 도착한 과거 Response는 화면에 반영하지 않음
```

**여기서 결론 내리면 안 되는 것:** "Model이 생성하던 Token도 즉시 중단됐다." Backend가 이미 Provider에 요청했다면 Browser 취소와 별개로 요청이 진행될 수 있습니다. 취소를 끝까지 전달하려면 Backend/Provider의 별도 Cancellation 설계가 필요합니다. **이번 교시에서는 이를 구현하지 않습니다.**

## 17-1. 학생 관찰 기록

| 사건 | 화면 | Network | Backend/Model에서 확인 가능한 사실 |
|---|---|---|---|
| 전송 | `loading` | POST 진행 | 요청 도달 여부를 Backend 로그로 확인 |
| Browser 취소 | `cancelled` | 요청 취소 또는 중단 표시 가능 | Model 중단은 별도 확인 없이는 판단 불가 |
| 새 질문 전송 | `loading` | 새 POST 발생 | 이전 응답과 새 응답이 섞이지 않아야 함 |

# 18. 오류를 어디에서 만났는가 — 화면과 원인을 1:1로 대응시키지 않는다

같은 '화면에 답변이 안 보임'이라도 실패 위치는 다릅니다. 아래 실습은 각각 **어떤 요청이 어디까지 도달했는지** 확인하는 데 초점을 둡니다.

| 상황 | Browser에서 관찰 | 우선 확인할 지점 |
|---|---|---|
| `VITE_API_BASE_URL` 비어 있음 | Frontend 설정 오류 | `.env`, Vite 재시작 |
| FastAPI 서버 중지 | `fetch` Network 오류 | Browser → FastAPI 경계 |
| CORS Origin 불일치 | Preflight/CORS Console 오류 | Backend CORS, 실제 Frontend Origin |
| 공백/잘못된 Body | `422` | 입력 검증이 Provider 호출 전에 작동했는지 |
| Ollama 서버 접근 실패 | `503` (7교시 v0.2 기준) | FastAPI → Local Provider 경계 |
| Provider Time-out | `504` (7교시 v0.2 기준) | Provider 대기/시간 초과 |
| Provider 응답 이상 | `502` (7교시 v0.2 기준) | Provider 응답과 공통 계약 변환 |
| JSON 필드 누락 | `FORMAT` 오류 | Frontend가 기대하는 Response Contract |

**주의:** Browser는 CORS 차단이나 Network 연결 실패를 비슷한 메시지로 표시할 수 있습니다. 화면 메시지만 보고 원인을 단정하지 말고 Console, Network, Backend 로그를 함께 확인합니다.

# 19. 의도적으로 실패시키는 실습 A — Backend가 꺼져 있는 경우

1. Backend가 정상 응답하는 상태에서 첫 요청을 성공시킵니다.
2. **FastAPI만** 종료합니다. Ollama를 끌 필요는 없습니다.
3. React에서 다른 질문을 전송합니다.
4. Browser Console/Network에 연결 실패 흔적이 있는지 확인합니다.
5. UI에서 `error`가 표시되는지 확인합니다.
6. Backend를 재실행한 뒤 동일 질문으로 복구를 검증합니다.

이 단계에서는 **AI Model에 요청이 전달되지 않았다는 것**이 핵심입니다. 단순히 'AI가 오류를 냈다'고 표현하면 실패 계층을 잘못 찾은 것입니다.

# 20. 의도적으로 실패시키는 실습 B — Local Provider에 연결할 수 없는 경우

1. FastAPI는 켜 둡니다.
2. **자신의 실습 환경에서만** Ollama Server 연결을 차단하거나 Runtime을 종료합니다.
3. React에서 질문을 전송합니다.
4. FastAPI가 요청을 수신했는지, 어떤 HTTP Status로 변환했는지 확인합니다.
5. UI의 안내 메시지와 실제 Network Status가 일치하는지 검증합니다.
6. Ollama를 다시 사용할 수 있는 상태로 복구합니다.

Day3 7교시 v0.2의 공통 오류 매핑에서는 연결 실패가 `503`입니다. 원본 8교시 자료의 일부 예시에는 `502`로 표현되어 있으나, **이번 수정본은 바로 앞 교시에서 완성한 코드의 실제 계약을 기준으로 `503`을 적용**합니다. 원본에 있던 오류 설명을 단순 복사하지 않고, **이어지는 실습 간 정합성**을 확보하기 위한 변경입니다.

# 21. 의도적으로 실패시키는 실습 C — 잘못된 입력과 API 계약

React 화면은 공백 입력을 미리 차단합니다. 하지만 Backend도 이를 검증해야 합니다. Browser 화면의 입력 검사만으로 Backend의 `422`를 검증했다고 주장해서는 안 됩니다.

Backend의 Swagger UI 또는 기존 테스트 Client에서 다음 요청을 직접 전송합니다.

```json
{
  "message": "   "
}
```

기대 결과: `422`이며, **Provider는 호출되지 않아야 합니다.** Day3 7교시에서 이미 만든 Pydantic Validation을 재사용합니다. 이번 교시의 새 관점은 **Frontend가 검사를 우회하는 Client로부터 Backend를 보호하지 못한다는 사실**입니다.

또 다른 테스트로, 서버에서 실수로 `answer` 대신 `response`라는 필드를 반환한다면 React의 `sendChat()`은 Response Contract가 맞지 않아 성공 화면을 표시하지 않습니다. 이 테스트는 **Mock Response**로 수행하고, 이미 완성한 Backend Schema를 고의로 깨뜨린 채 배포하지 않습니다.

# 22. Provider 교체 실습 — React 코드를 손대지 않고 Cloud/Local 전환

Day3 7교시에는 Python Client에서 Provider 교체를 검증했습니다. 이번에는 **Browser 화면을 열어 놓은 상태에서 같은 API 계약이 유지되는지** 관찰합니다.

| 순서 | 할 일 | 변경 대상 |
|---|---|---|
| 1 | Local Provider 실행 및 질문 전송 | `backend/.env`의 `AI_PROVIDER=ollama` |
| 2 | 첫 결과의 `provider`, `model` 기록 | 기록표만 |
| 3 | Backend 중지 후 Cloud 설정으로 변경 | `AI_PROVIDER=openai`, Key·Model (이용 가능 시) |
| 4 | Backend 재시작, **같은 React 화면**에서 같은 요청 | Frontend 코드는 변경하지 않음 |
| 5 | Provider·Model 표시와 Network Contract 확인 | 결과 비교표 |

Cloud API를 사용할 권한이나 비용이 없다면 **실제 OpenAI 호출은 하지 않고**, 7교시에서 준비한 Mock Provider로 같은 응답 계약을 확인합니다. 이 경우 **실제 Cloud Provider 전환 성공**이라고 적어서는 안 됩니다.

## 22-1. 학생 비교 결과표

| 항목 | Local 실행 | Cloud 실행 또는 Mock 실행 |
|---|---|---|
| 실제 사용한 Provider |  |  |
| Backend 설정 변경 여부 |  |  |
| React 소스 변경 여부 |  |  |
| 요청 URL |  |  |
| Request 필드 |  |  |
| Response 필드 |  |  |
| 실제 모델 추론 / Mock 구분 |  |  |
| 결과에 대한 판단 |  |  |

**핵심 성과:** **모델의 답변 내용은 달라져도 API Contract는 유지**할 수 있습니다. Provider를 바꾸는 과정에서 Request Body나 React 화면 코드를 수정했다면 그 이유를 찾아야 합니다.

# 23. 디버깅 순서 — 무작정 모든 것을 재설치하지 않는다

학생이 '답변이 안 나와요'라고 보고하면 다음 순서로 사실을 확인하게 합니다.

```text
[1] Frontend 페이지 자체가 열리는가?
          │ 아니오 → Vite / Browser 문제
          ▼ 예
[2] Network에 POST /ai/chat이 기록되는가?
          │ 아니오 → 전송 이벤트·URL·Console 확인
          ▼ 예
[3] Preflight가 허용되어 실제 POST가 전송되는가?
          │ 아니오 → CORS / Origin 확인
          ▼ 예
[4] POST의 HTTP Status는?
          │ 422 → Request Validation
          │ 502/503/504 → Provider 경계·Backend 로그
          │ Network 실패 → Backend 연결 확인
          ▼ 200
[5] Response JSON의 세 필드가 올바른가?
          │ 아니오 → Response Contract / 파싱
          ▼ 예
[6] React가 success 상태와 답변을 표시하는가?
          │ 아니오 → React State / Render 조건
          ▼ 예
End-to-End 요청·응답 완료
```

이 절차는 문제의 모든 원인을 자동으로 해결하지 않습니다. 다만 **어디까지 정상 동작하는지 증거를 바탕으로 범위를 좁히는 작업**입니다.

# 24. 자동 검증 A — Backend의 CORS와 기존 계약 테스트

이 교시에서 추가된 설정을 Model 호출 없이 확인할 수 있습니다. 아래는 **교육용 테스트**이며, 기존 7교시 `create_app(MockProvider)`가 동작하는 상황에서 실행합니다.

`backend/tests/test_frontend_contract.py`:

```python
import os

os.environ["AI_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "offline-test-model"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import create_app  # noqa: E402


class MockProvider:
    provider_name = "mock"
    model_name = "offline-model"

    def generate(self, message: str) -> str:
        return f"응답: {message}"


def test_frontend_post_contract():
    with TestClient(create_app(MockProvider())) as client:
        result = client.post(
            "/ai/chat",
            json={"message": "참가 안내 문구"},
            headers={"Origin": "http://localhost:5173"},
        )
    assert result.status_code == 200
    assert result.json() == {
        "provider": "mock",
        "model": "offline-model",
        "answer": "응답: 참가 안내 문구",
    }
    assert result.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_allows_classroom_origin():
    with TestClient(create_app(MockProvider())) as client:
        result = client.options(
            "/ai/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
    assert result.status_code == 200
    assert result.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_invalid_message_is_rejected_before_provider_call():
    class FailingIfCalled(MockProvider):
        def generate(self, message: str) -> str:
            raise AssertionError("Validation보다 Provider가 먼저 호출됐습니다")

    with TestClient(create_app(FailingIfCalled())) as client:
        result = client.post("/ai/chat", json={"message": "  "})
    assert result.status_code == 422
```

실행:

```bash
cd ai_final_app/backend
python -m pytest -q tests/test_provider.py tests/test_frontend_contract.py
```

**의미:** 이 테스트는 **Browser를 실제로 실행하지 않아도** Backend가 올바른 응답 형태와 CORS Header를 제공하는지 검증합니다. 실제 React 화면·Browser Preflight 성공을 증명하는 것은 아니므로 두 검증 결과를 구분해 기록합니다.

# 25. 자동 검증 B — Frontend API 함수만 Mock으로 확인하기

`aiApi.js`의 `fetch` 동작은 React 화면 없이도 단위 검증할 수 있습니다. 교육장에 Node 기반 테스트 환경이 이미 준비돼 있다면 다음 항목을 검사합니다. 새 Testing Framework 설정 자체를 이번 교시의 주제로 확대하지 않습니다.

| 모의 응답 또는 사건 | 기대 결과 |
|---|---|
| `200` + `{provider, model, answer}` | 정상 객체 반환 |
| `422` | `AIRequestError("HTTP", ...)` |
| `503` | 연결 실패 안내 |
| JSON 아닌 `200` | `FORMAT` 오류 |
| 필수 필드 없는 `200` | `FORMAT` 오류 |
| Network `fetch` 실패 | `NETWORK` 오류 |
| AbortError 발생 | 취소 흐름에 그대로 전달 |

최종 Browser 검증에서는 React의 **상태 전이**까지 추가 확인합니다. Mock 함수 테스트와 실제 Browser/UI 테스트를 혼동하지 않습니다.

# 26. 학생 종합 과제 — 증거를 제시하며 전체 경로 설명하기

학생은 정상 시나리오 하나와 실패 시나리오 하나를 골라, 시작부터 종료까지 **어느 계층이 무엇을 처리했는지** 설명합니다.

예시 정상 시나리오:

```text
학생이 안내 문구 생성 요청
  → React의 handleSubmit
  → aiApi.js의 fetch
  → Browser의 HTTP Request
  → FastAPI /ai/chat
  → AIService
  → AIProvider 구현체
  → 선택된 Model의 Response
  → FastAPI ChatResponse
  → aiApi.js JSON 파싱
  → React success 화면
```

예시 실패 시나리오:

```text
FastAPI는 정상 실행
  → Ollama Runtime에 연결 불가
  → Backend가 ProviderConnectionError를 503으로 변환
  → Browser가 HTTP 503 수신
  → aiApi.js가 AIRequestError 반환
  → React error 상태로 표시
```

관찰하지 않은 단계를 ‘성공’으로 단정하지 않습니다. 특히 Mock을 이용했다면 **Mock에서 검증된 계층과 실제 Provider 호출이 이루어진 계층을 구분**합니다.

# 27. 교시 완료 체크리스트 — '화면에 글자가 나온다'로 끝내지 않는다

- [ ] Day3 7교시 Backend 원본을 재사용했으며 Provider 파일을 불필요하게 수정하지 않았다.
- [ ] Backend가 시작되고 `/health`가 응답한다.
- [ ] CORS 허용 Origin과 Vite 실행 Origin이 일치한다.
- [ ] React 프로젝트에 `package.json`·`index.html`·`src/main.jsx`가 존재한다.
- [ ] `aiApi.js`가 `POST /ai/chat`에 `message` JSON을 전송한다.
- [ ] `loading`, `success`, `error`, `cancelled` 상태가 구분된다.
- [ ] Browser Network 탭에서 POST 및 응답 JSON을 확인했다.
- [ ] 정상 응답에서 `provider`·`model`·`answer`가 모두 표시된다.
- [ ] Backend 중지·Provider 연결 실패의 오류 위치를 구분했다.
- [ ] 요청 취소 후 늦은 응답이 화면을 덮어쓰지 않도록 처리했다.
- [ ] Provider를 변경해도 React 소스·Request Contract가 유지된다(실제 Provider 또는 Mock 여부 기록).
- [ ] 성공·실패·취소의 관찰 근거를 제출했다.

# 28. 자주 발생하는 오해 — 이번 교시에서 관찰한 증거로 답하기

| 오해 | 이번 수업에서 확인할 사실 |
|---|---|
| "Frontend가 AI Model을 호출한다" | Browser는 **우리 FastAPI**에 요청하고 Backend가 Provider를 호출한다. |
| "CORS 허용이면 누구나 안전하게 API를 사용해도 된다" | CORS는 인증과 다르다. |
| "Backend `/health` 200이면 AI 답변도 반드시 된다" | Health는 Provider Generation 성공을 검증하지 않는다. |
| "Browser 취소를 누르면 Local Model의 생성도 즉시 중단된다" | Browser 취소와 Provider 작업 취소는 별도이다. |
| "모델을 교체하면 반드시 React를 고쳐야 한다" | 계약이 유지되면 Frontend 코드 수정 없이 교체 가능하다. |
| "Mock 테스트가 성공했으니 OpenAI 실측도 성공한 것이다" | Mock은 인터페이스 검증이지 실제 API 연결 검증이 아니다. |
| "Response JSON이 200이면 화면에도 반드시 정상 표시된다" | 필수 필드 확인·상태 전이·Rendering까지 검증해야 한다. |

# 29. 강사 운영 가이드 — 순서와 관찰 포인트

| 단계 | 강사가 먼저 확인할 것 | 학습자가 남길 증거 |
|---|---|---|
| ① Backend 재사용 | Day3 7교시 테스트 통과·선택 Provider 준비 | 테스트 로그·환경 기록 |
| ② CORS 추가 | 실제 Frontend Origin·Preflight 허용 | OPTIONS/POST Network 기록 |
| ③ Frontend 생성 | Vite의 실제 파일/Version·실행 URL | 화면 실행 캡처 |
| ④ 통합 요청 | JSON Contract·Provider 응답 | Request/Response 기록 |
| ⑤ UI 상태 | Loading, Success, Error, Cancel | 상태별 캡처 및 설명 |
| ⑥ 장애 분석 | Backend vs Provider vs CORS vs React | 실패 계층과 복구 결과 |
| ⑦ 교체 검증 | API 이용 가능 여부 또는 Mock | React 소스·계약 불변 비교 |
| ⑧ 결과 발표 | 관찰값과 추정을 구별했는지 | 전체 요청 왕복 경로 설명 |

## 29-1. 교육장 환경별 실행 전략

**Local AI 실행 가능 환경:** Ollama를 기본 Provider로 선택하고 모델 생성까지 실측합니다. 실제 `provider`, `model`, `answer`를 기록합니다.

**Local Model 실행이 느리거나 부재한 환경:** Day3 7교시의 Mock Provider를 이용해 HTTP와 React 연결을 먼저 확인합니다. 이 경우 추론 품질·속도 실측을 완료했다고 표시하지 않습니다.

**Cloud API 이용 환경:** 강사가 승인한 계정·비용·모델을 사용해 교체 실습을 추가합니다. API Key는 학생 소스·Frontend·Git에 남기지 않습니다. 실제 비용 사용이 허용되지 않으면 Cloud 호출은 생략합니다.

# 30. 3일 과정의 최종 학습 성과 — 긴 복습 대신 '증명할 수 있는 것'으로 정리

Day1~Day3의 용어를 다시 순서대로 나열하지 않습니다. 수업 종료 시 학생이 **지금 실행한 Application을 기준으로** 다음 네 가지 질문에 답할 수 있으면 됩니다.

| 질문 | 학생이 증명할 내용 |
|---|---|
| "모델을 바꿨는데 Browser 요청은 왜 그대로인가?" | FastAPI의 Request/Response Contract와 Provider Abstraction |
| "취소 Button과 AI 작업 중단은 왜 다를 수 있나?" | Browser·Backend·Provider 각각의 실행 경계 |
| "HTTP 503을 봤다면 어느 코드를 먼저 확인하나?" | Backend의 Provider 오류 매핑과 해당 Runtime 연결 |
| "화면에 답변이 보인 것을 무엇으로 증명하나?" | Request, Status, Response JSON, React 상태·표시 결과 |

강사는 개념 암기보다 **직접 관찰한 증거·구체적인 파일 위치·책임을 구분한 설명**을 평가합니다.

# 31. 다음 학습과의 경계 — 여기서는 구현하지 않는다

이번 결과물은 다음 기능을 구현하는 기반이 될 수 있습니다. **다음 항목은 가능성만 연결하고, 코드·실습·평가를 앞당기지 않습니다.**

| 이후 학습 주제 | 이번 교시에서 연결되는 것 | 이번 교시에서 하지 않는 것 |
|---|---|---|
| Document AI / File Upload | 화면·Backend·AI Service의 역할 분리 | PDF Upload·Text Extraction 구현 |
| Structured Output 심화 | API Response Schema의 중요성 | 별도 요약 Schema / 정형 출력 Pipeline 구현 |
| Retrieval / RAG | 기존 Service 확장 지점 이해 | Embedding·Vector DB·Retriever 구현 |
| Tool / Agent | Provider 호출을 감싼 Application 구조 | Tool 실행 Loop·Agent Orchestration |
| 배포·운영 | Port·Origin·설정·실패 계층 기록 | 인증·인프라·분산 배포·모니터링 구축 |

> **최종 결론:** AI Application은 '모델 호출이 성공했다'에서 끝나지 않습니다. 사용자의 입력부터 Provider 실행 결과까지 **계약을 지키며 전달하고, 대기·실패·취소를 사용자에게 일관되게 보여주며, 문제를 책임 있는 계층에서 찾을 수 있어야** 하나의 실제 웹 서비스로 연결됩니다.

---

## 참고자료 — 원본 교육과정에 기재된 범위

- React 공식 문서
- Vite 공식 문서
- FastAPI 공식 문서
- Pydantic 공식 문서
- OpenAI API 및 Python SDK 공식 문서
- Ollama API 공식 문서
- Python 공식 문서
- Hugging Face 공식 문서

> 본 강의안은 유일한 교육과정 원문의 범위와 기존 교시의 학습 연결을 기준으로 개편했습니다. 본 작업에서 위 외부 자료의 최신 API/Version을 검증한 것은 아닙니다. 실제 교육장 배포 전 Node·Vite·React·Python·FastAPI·OpenAI SDK·Ollama·모델 버전과 OS별 실행 절차를 확인하십시오.

## 관련 Wiki Link

[[React]] · [[FastAPI]] · [[Pydantic]] · [[CORS]] · [[HTTP]] · [[REST API]] · [[AI Provider]] · [[Provider Abstraction]] · [[Ollama]] · [[OpenAI API]] · [[Model Serving]] · [[AI Service Architecture]]

## 저장 위치 제안 — 원본 경로 유지

```text
Academy/
└── 03. 실습/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day3_08교시_React_FastAPI_AI_Provider_Model_최종_통합_실습.md
```
