# 04. FastAPI — AI 서비스 Backend 만들기

## 개요

React가 사용자와 상호작용하는 Frontend라면 FastAPI는 **Frontend의 요청을 받아 검증하고, Python 업무 로직과 데이터 저장소·AI Provider를 연결한 뒤 결과를 다시 HTTP Response로 반환하는 Backend**를 만든다.

이 강의는 Endpoint 몇 개를 만드는 문법 수업이 아니다. 다음 흐름 전체를 이해하고 구현하는 것을 목표로 한다.

```text
React
  ↓ HTTP Request
FastAPI Router / Endpoint
  ↓
Pydantic Request Model
  ↓
Service
  ├─ 업무 규칙
  ├─ Repository
  └─ AI Provider Client
  ↓
Response Model
  ↓ HTTP Response
React
```

앞 과목 [[Python]]에서 배운 함수, Type Hint, Class, Decorator, Exception, JSON이 이 과정에서 실제 Backend 구성요소로 바뀐다.

## 학습 목표

학습자는 이 과정을 마친 뒤 다음을 할 수 있어야 한다.

- HTTP Request와 Response의 기본 구조를 설명할 수 있다.
- REST API, Endpoint, HTTP Method의 역할을 구분할 수 있다.
- `async`/`await`와 I/O 대기의 관계를 설명할 수 있다.
- ASGI와 Uvicorn, FastAPI의 역할을 구분할 수 있다.
- FastAPI 프로젝트를 만들고 서버를 실행할 수 있다.
- Path Parameter, Query Parameter, Request Body를 구분해 사용할 수 있다.
- Pydantic Request/Response Model로 데이터 계약을 만들 수 있다.
- Validation 오류가 어디에서 발생하고 어떻게 응답되는지 이해할 수 있다.
- APIRouter로 기능을 분리할 수 있다.
- Router, Service, Repository의 책임을 나눌 수 있다.
- Dependency Injection을 사용해 구현체를 교체하고 테스트할 수 있다.
- Settings와 환경변수로 Secret을 코드에서 분리할 수 있다.
- 표준 오류 응답과 Exception Handling을 설계할 수 있다.
- 외부 AI Provider 호출의 Timeout, Retry, Streaming을 Backend 구조 안에서 다룰 수 있다.

## 전체 학습 지도

```text
Python
  ↓
HTTP / REST
  ↓
async / await
  ↓
ASGI / Uvicorn
  ↓
FastAPI App
  ↓
Routing / Endpoint
  ↓
Path / Query / Body
  ↓
Pydantic Validation
  ↓
Response Model
  ↓
APIRouter
  ↓
Router - Service - Repository
  ↓
Dependency Injection
  ↓
Settings / Error / Test
  ↓
AI Provider Integration
```

## 수업 환경 기준

- Python: **3.12 계열**
- FastAPI: **0.141 계열을 기준으로 설명**
- Pydantic: v2 계열 문법
- ASGI Server: Uvicorn
- 개발 시 자동 문서: OpenAPI / Swagger UI

2026년 9월 확인 기준 FastAPI 공식 Release Notes의 최신 공개 버전은 0.141.1이다. 다만 강의에서 특정 patch에 종속되는 코드를 만들지 않고, 실제 프로젝트는 lock 파일에 기록된 버전을 재현 기준으로 삼는다.

> FastAPI 0.129.0부터 Python 3.9 지원이 제거되었다. 이 과정은 Python 3.12 계열을 사용하므로 해당 변화의 영향을 받지 않는다.

---
# Part 1. HTTP와 FastAPI 실행 구조

Python 프로그램을 웹 Backend로 만들기 전에 HTTP와 서버 실행 구조부터 연결한다.

## Module 11. 왜 FastAPI인가?


### Module 실습 예제

- [예제 1: minimal_fastapi.py](examples/module_11/minimal_fastapi.py) — 가장 작은 FastAPI 애플리케이션을 실행합니다.
- [예제 2: ai_boundary_fastapi.py](examples/module_11/ai_boundary_fastapi.py) — Client와 AI 처리 사이에 Backend 경계를 둡니다.



#### 프로젝트 연결 학습
- **문제 상황:** 문법을 외우기 전에 AI 요청을 받을 백엔드가 왜 필요한지 정의한다.
- **오늘 만드는 것:** 최소 AI 질문 API의 입력과 출력 경계를 그린다.
- **AI 플랫폼의 위치:** 사용자 질문 → FastAPI → AI Provider → 응답 흐름의 출발점이다.
- **실무에서 많이 하는 실수:** 프레임워크의 속도만 보고 기술을 선택하고 운영 조건을 빠뜨린다.
- **5분 실습:** AI 질문 API에 필요한 입력·처리·출력을 한 줄씩 적는다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 자신의 언어로 답할 수 있어야 합니다.

- FastAPI는 무엇인가?
    
- 왜 Flask가 아니라 FastAPI를 사용하는가?
    
- AI 서비스에서 FastAPI가 널리 사용되는 이유는 무엇인가?
    
- React와 FastAPI는 어떤 역할을 나누어 가지는가?
    
- 앞으로 FastAPI를 배우는 이유는 무엇인가?
    

---

### ① 문제 이해 (Why)
#### 우리는 지금 무엇을 만들려고 하는가?
지금까지 우리는 React를 공부했습니다.

React를 이용하면 멋진 화면을 만들 수 있습니다.

예를 들어

```
Chat 화면

파일 업로드

로그인 화면

문서 목록

AI 응답 출력
```

이런 UI는 모두 만들 수 있습니다.

그런데 한 가지 문제가 있습니다.

React는 **화면만 만드는 기술**입니다.

---

예를 들어 사용자가

```
"이 PDF를 요약해줘."
```

라고 입력했다고 가정해봅시다.

React는

- PDF를 선택할 수는 있습니다.
    
- 버튼을 누를 수는 있습니다.
    
- 결과를 화면에 출력할 수는 있습니다.
    

하지만

PDF를 분석할 수는 없습니다.

LLM을 호출할 수도 없습니다.

OCR을 수행할 수도 없습니다.

파일을 저장할 수도 없습니다.

---

즉,

React는

> **사용자와 대화하는 역할**

만 합니다.

---

그럼

실제로 일을 하는 사람은 누구일까요?

바로

**Backend(Server)** 입니다.

---

### AI 서비스를 회사에 비유해보자
회사에는 여러 부서가 있습니다.

```
고객

↓

안내데스크

↓

실무부서

↓

결과 전달
```

React는

안내데스크입니다.

고객을 응대합니다.

버튼도 눌러줍니다.

입력도 받습니다.

하지만

실제 업무는 하지 않습니다.

---

실무부서는

```
Backend
```

입니다.

Backend는

- 데이터 저장
    
- AI 호출
    
- OCR
    
- PDF 분석
    
- DB 저장
    
- 로그인 처리
    

등을 수행합니다.

---

즉

```
Frontend

↓

Backend

↓

AI

↓

Database
```

이 구조가 됩니다.

---

### 지금까지 우리가 만든 구조
```
사용자

↓

React

↓

???

↓

ChatGPT
```

여기에서

???

가 비어 있습니다.

---

우리는 이제

이 빈칸을 만들려고 합니다.

---

### Backend는 왜 필요한가?
만약 Backend 없이

React가 직접 ChatGPT를 호출하면 어떨까요?

겉보기에는 가능해 보입니다.

하지만 실제 서비스에서는 거의 사용하지 않습니다.

---

예를 들어

```
OpenAI API Key
```

를 생각해봅시다.

API Key는

회사 비밀번호와 같습니다.

---

React 안에 넣는 순간

누구나 볼 수 있습니다.

```
브라우저

↓

개발자도구

↓

JavaScript

↓

API Key 노출
```

서비스는 바로 공격당합니다.

---

그래서

AI 호출은 반드시

Backend에서 수행합니다.

---

구조는 이렇게 됩니다.

```
React

↓

FastAPI

↓

OpenAI

↓

응답

↓

React
```

---

### Backend는 AI 서비스의 두뇌이다
React는 얼굴입니다.

FastAPI는 두뇌입니다.

AI는 전문가입니다.

Database는 기억입니다.

```
          사용자

              │

              ▼

        React(Frontend)

              │

              ▼

      FastAPI(Backend)

      │      │      │

      ▼      ▼      ▼

 OpenAI    DB     OCR

      │

      ▼

   결과 생성
```

---

### 왜 FastAPI가 등장했는가?
여기서 질문이 하나 생깁니다.

Backend는

예전부터 존재했습니다.

그런데

왜 새로운 Framework가 등장했을까요?

---

과거에는

대표적으로

```
ASP.NET

Spring

Django

Flask
```

등을 많이 사용했습니다.

특히 Python에서는

오랫동안

```
Flask
```

가 가장 많이 사용되었습니다.

---

그러던 어느 날

AI 시대가 시작됩니다.

---

AI 서비스는

기존 웹 서비스와는 완전히 다른 특징을 갖습니다.

예를 들어

```
사용자 1명

↓

LLM 호출

↓

10~30초 대기
```

가 발생할 수 있습니다.

---

기존 웹서비스는

```
상품 조회

↓

DB 조회

↓

0.05초
```

정도로 끝나는 경우가 많았습니다.

---

하지만 AI는 다릅니다.

```
OCR

↓

Embedding

↓

Vector DB

↓

LLM

↓

Streaming

↓

Response
```

이 과정을 모두 거칩니다.

---

즉

Backend가

오랫동안

기다려야 하는 작업이 많아졌습니다.

---

기존 방식은 문제가 생깁니다.

직원 한 명이

손님 한 명만 계속 응대하고 있는 것과 같습니다.

```
직원

↓

손님1 처리

↓

끝날 때까지 대기

↓

다음 손님
```

효율이 매우 떨어집니다.

---

그래서 등장한 것이

[[#Module 13. 비동기 프로그래밍(Async Programming) - `async` / `await`|비동기처리(Asyncronomous)]] 입니다.

FastAPI는 AI 전용으로 만들어진 프레임워크는 아니지만, ASGI와 Python 타입 힌트를 기반으로 현대적인 API 서비스를 구축하도록 설계되었습니다.

외부 AI API처럼 대기 시간이 긴 I/O를 적절한 비동기 라이브러리로 호출하면, 한 요청이 응답을 기다리는 동안 다른 요청을 처리할 수 있습니다. 단, `async def`를 쓰는 것만으로 성능이 보장되지는 않으며 내부 코드가 이벤트 루프를 막지 않아야 합니다.


---

### 왜 FastAPI는 AI 서비스에서 널리 사용될까?
FastAPI가 인기를 얻은 이유는 단순히 "빠르다"가 아닙니다.

AI 서비스 개발자가 필요로 하는 거의 모든 조건을 만족했기 때문입니다.

대표적으로 다음과 같은 장점이 있습니다.

---

#### ① 매우 빠른 성능
FastAPI라는 이름 때문에

많은 사람들이

> "FastAPI = 실행 속도가 빠른 API"

정도로 이해합니다.

하지만 FastAPI의 "Fast"에는 두 가지 의미가 있습니다.

첫 번째는

실행 성능입니다.

FastAPI는 Python Framework 중에서도 매우 높은 처리 성능을 제공합니다.

그 이유는

```text
FastAPI

↓

Starlette

↓

ASGI

↓

uvicorn

↓

고성능 Event Loop
```

구조로 동작하기 때문입니다.

여기서 중요한 것은

FastAPI 혼자 빠른 것이 아니라

아래 라이브러리들의 장점을 모두 활용한다는 것입니다.

---

#### ② 개발 속도가 매우 빠르다
FastAPI의 "Fast"는

개발 속도도 의미합니다.

예를 들어

API 하나를 만든다고 생각해 봅시다.

Flask에서는

- URL 작성
    
- Parameter 검사
    
- JSON 변환
    
- Validation
    
- Documentation
    

등을 직접 작성해야 하는 경우가 많았습니다.

하지만 FastAPI에서는

Python의 타입 힌트(Type Hint)를 활용하면 대부분 자동으로 처리됩니다.

예를 들어

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

단 몇 줄만 작성해도

FastAPI는 자동으로

- URL 분석
    
- 정수 타입 검사
    
- JSON 변환
    
- API 문서 생성
    

까지 수행합니다.

즉,

개발자가 해야 할 일이 크게 줄어듭니다.

---

### ③ 자동 문서 생성(OpenAPI)
FastAPI를 처음 사용하는 사람들이 가장 놀라는 기능입니다.

API를 하나 만들면

별도의 작업 없이

문서가 자동 생성됩니다.

예를 들면

```text
GET /chat

POST /upload

DELETE /document/{id}
```

를 만들었다면

자동으로

```text
Swagger UI

↓

브라우저에서 테스트 가능

↓

API 설명 자동 생성
```

됩니다.

백엔드 개발자는 문서를 따로 작성하지 않아도 됩니다.

코드를 작성하는 것만으로도 API 문서가 함께 생성됩니다.

---

### ④ 타입 안정성(Type Safety)
Python은 원래

동적 타입(Dynamic Typing) 언어입니다.

예를 들어

```python
x = 10
x = "hello"
```

처럼 언제든지 타입이 변경될 수 있습니다.

이 때문에

규모가 커질수록 오류를 찾기 어려워지는 문제가 있었습니다.

FastAPI는

Python의 Type Hint를 적극 활용합니다.

```text
def get_user(user_id: int):
```

처럼 작성하면

FastAPI는

```text
user_id는 반드시 int

↓

문자열이 들어오면?

↓

자동 오류 반환
```

을 수행합니다.

즉,

실수할 가능성을 크게 줄여 줍니다.

---

### ⑤ Validation 자동 처리
예를 들어 회원가입 API를 만든다고 생각해 봅시다.

사용자는

```text
이름

나이

이메일
```

을 입력합니다.

그런데

```text
나이 = "스무살"

이메일 = 12345
```

처럼 잘못된 값이 들어오면 어떻게 해야 할까요?

기존 Framework에서는

직접 검사 코드를 작성해야 했습니다.

하지만 FastAPI에서는

Pydantic이라는 라이브러리를 이용하여

자동으로 검증합니다.

예를 들어

```python
class User(BaseModel):
    age: int
```

라고 작성하면

```text
age = "hello"
```

가 들어오는 순간

자동으로 오류를 반환합니다.

즉,

입력 데이터 검증을 개발자가 일일이 작성하지 않아도 됩니다.

---

### ⑥ AI 서비스에 최적화된 비동기 처리
이 부분이 가장 중요합니다.

AI 서비스에서는

하나의 요청이 매우 오래 걸립니다.

예를 들어

```text
PDF 업로드

↓

OCR

↓

텍스트 추출

↓

Embedding 생성

↓

Vector DB 저장

↓

LLM 호출

↓

응답 생성
```

이 모든 과정이 하나의 요청 안에서 일어날 수 있습니다.

이 작업은

수 초에서 수십 초까지 걸릴 수도 있습니다.

만약 서버가

이 요청 하나만 기다리고 있다면

다른 사용자는 아무것도 할 수 없습니다.

FastAPI는

이런 상황에서도

다른 요청을 계속 처리할 수 있도록 설계되었습니다.

이것이 바로 AI 서비스에서 FastAPI가 많이 선택되는 가장 큰 이유입니다.

---

### Flask와 FastAPI는 무엇이 다른가?
학생들이 가장 많이 하는 질문입니다.

> "Flask도 Python인데 FastAPI를 왜 배우나요?"

답은

**둘 다 훌륭한 Framework이지만 설계 목표가 다르기 때문**입니다.

|항목|Flask|FastAPI|
|---|---|---|
|출시|2010년|2018년|
|철학|가볍고 자유로운 웹 개발|현대적인 API 중심 개발|
|동기/비동기|기본적으로 동기 중심|비동기(Async) 지원이 핵심|
|자동 API 문서|직접 추가해야 함|기본 제공(OpenAPI/Swagger)|
|데이터 검증|직접 구현하거나 확장 라이브러리 사용|Pydantic 기반 자동 검증|
|타입 힌트 활용|선택 사항|핵심 기능|
|AI 서비스 적합성|가능하지만 추가 작업이 많음|매우 적합|

Flask가 "구형이라서" FastAPI가 등장한 것은 아닙니다.

Flask는 지금도 많은 서비스에서 사용되고 있습니다.

다만 AI 시대에는 **API 중심, 비동기 처리, 자동 검증, 자동 문서화**가 매우 중요해졌고, 이러한 요구에 맞춰 설계된 프레임워크가 FastAPI입니다.

---

### 지금까지 Phase 1에서 배운 기술과의 연결
우리는 지금까지 다음과 같은 흐름으로 학습해 왔습니다.

```text
Python
    ↓
React
    ↓
FastAPI 
    ↓
OpenAI API
    ↓
Ollama
    ↓
LangChain
    ↓
Document AI
```

각 기술의 역할은 명확합니다.

```text
Python
    ↓
백엔드 개발 언어

React
    ↓
사용자 인터페이스(UI)

FastAPI
    ↓
백엔드 서버

OpenAI API
    ↓
LLM 호출

Ollama
    ↓
로컬 AI 모델 실행

LangChain
    ↓
AI 워크플로우 구성

Document AI
    ↓
문서 처리 기능
```

여기서 **FastAPI는 모든 AI 기능을 연결하는 중심 허브** 역할을 합니다.

React는 사용자와 대화하고, OpenAI나 Ollama는 AI 추론을 수행하지만, 이 둘을 연결하고 비즈니스 로직을 담당하는 것이 바로 FastAPI입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **왜 FastAPI를 배우는가**에 집중했습니다.

핵심은 다음과 같습니다.

- React는 화면(UI)을 만들지만 실제 업무는 처리하지 못한다.
    
- AI 호출, 파일 처리, 데이터 저장 등은 백엔드가 담당한다.
    
- FastAPI는 AI 시대의 요구사항(비동기 처리, API 중심 설계, 자동 문서화, 데이터 검증)을 만족하도록 설계된 현대적인 백엔드 프레임워크이다.
    
- FastAPI는 앞으로 학습할 OpenAI API, Ollama, LangChain, Document AI를 연결하는 핵심 플랫폼이 된다.
    

---

## Module 12. HTTP와 REST API 다시 이해하기


### Module 실습 예제

- [예제 1: http_contracts.py](examples/module_12/http_contracts.py) — 기능별 HTTP Method·Path·Status Code 계약을 설계합니다.
- [예제 2: rest_routes.py](examples/module_12/rest_routes.py) — REST 관점의 문서 생성·조회 Route를 작성합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 클라이언트와 서버가 합의해야 할 HTTP 계약을 이해한다.
- **오늘 만드는 것:** 질문 생성·조회 API의 Method·URL·Status Code를 설계한다.
- **AI 플랫폼의 위치:** React와 FastAPI가 통신하는 공통 언어다.
- **실무에서 많이 하는 실수:** 동작 이름을 URL에 모두 넣거나 상태 코드를 항상 200으로 반환한다.
- **5분 실습:** 질문 생성과 결과 조회 Endpoint를 REST 관점에서 작성한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- HTTP는 무엇인가?
    
- Request와 Response는 무엇인가?
    
- REST API는 무엇인가?
    
- GET, POST, PUT, DELETE는 언제 사용하는가?
    
- FastAPI가 HTTP를 어떻게 사용하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서 우리는

AI 서비스의 구조를 배웠습니다.

```text
사용자

↓

React

↓

FastAPI

↓

OpenAI
```

그런데

여기서 중요한 질문이 하나 있습니다.

> React는 FastAPI에게 어떻게 말을 걸까요?

---

React도 프로그램입니다.

FastAPI도 프로그램입니다.

프로그램끼리는

사람처럼

한국어나 영어로 대화하지 않습니다.

공통된 약속이 필요합니다.

그 약속이

바로

**HTTP**입니다.

---

### 사람도 언어가 필요하다
한국 사람끼리는

한국어를 사용합니다.

미국 사람은

영어를 사용합니다.

프로그램도

마찬가지입니다.

React와 FastAPI도

공통 언어가 필요합니다.

```text
React

↓

HTTP

↓

FastAPI
```

HTTP는

컴퓨터끼리 대화하는 언어입니다.

---

### HTTP란 무엇인가?
HTTP는

HyperText Transfer Protocol의 약자입니다.

이름은 어렵지만

의미는 단순합니다.

> **웹에서 데이터를 주고받는 약속(Protocol)**

입니다.

---

예를 들어

브라우저에서

```text
https://www.google.com
```

을 입력합니다.

그러면

브라우저는

Google 서버에게

HTTP 요청(Request)을 보냅니다.

Google 서버는

HTTP 응답(Response)을 보냅니다.

```text
Browser

↓

HTTP Request

↓

Google

↓

HTTP Response

↓

Browser
```

---

### AI 서비스도 완전히 동일하다
우리도

똑같은 구조를 사용합니다.

```text
React

↓

HTTP Request

↓

FastAPI

↓

HTTP Response

↓

React
```

여기서

React는

Client입니다.

FastAPI는

Server입니다.

---

### Request란 무엇인가?
Request는

말 그대로

요청입니다.

예를 들어

```text
"이 PDF를 요약해주세요."
```

도

하나의 Request입니다.

---

React는

FastAPI에게

이렇게 이야기합니다.

```text
POST

/summary

파일 첨부
```

FastAPI는

이 요청을

받아서 처리합니다.

---

### Response란 무엇인가?
FastAPI가

작업을 끝내면

결과를 돌려줍니다.

```text
{
    "summary":
    "이 문서는..."
}
```

이것이

Response입니다.

---

전체 구조는

```text
React

↓

Request

↓

FastAPI

↓

Response

↓

React
```

입니다.

---

### HTTP는 편지와 비슷하다
HTTP를

택배로 생각하면

이해하기 쉽습니다.

```text
택배

↓

주소

↓

내용물

↓

배송
```

HTTP도

거의 같습니다.

```text
HTTP

↓

URL

↓

데이터

↓

전송
```

---

### Request는 무엇으로 구성될까?
HTTP Request는

크게 네 가지 요소를 가집니다.

```text
Method

URL

Header

Body
```

이 네 가지는

앞으로 계속 등장합니다.

하나씩 살펴보겠습니다.

---

### ① Method
Method는

무슨 일을 할 것인지

알려줍니다.

예를 들어

```text
GET
```

은

조회입니다.

```text
POST
```

는

새로운 데이터를 생성합니다.

```text
DELETE
```

는

삭제입니다.

Method는

동사라고 생각하면 쉽습니다.

---

### ② URL
URL은

어디로 갈 것인지

알려줍니다.

예를 들어

```text
/chat
```

```text
/upload
```

```text
/document
```

처럼

작업 위치를 의미합니다.

---

즉

```text
POST

/upload
```

은

"업로드를 수행해 주세요."

라는 의미입니다.

---

### ③ Header
Header는

부가 정보입니다.

예를 들어

```text
Authorization

Content-Type

Accept
```

등이 있습니다.

AI 서비스에서는

가장 많이 사용하는 것이

```text
Authorization
```

입니다.

로그인한 사용자의

토큰을

Header에 담습니다.

예를 들어

```text
Authorization

Bearer eyJhbG...
```

처럼 전송합니다.

---

또 하나 중요한 Header는

```text
Content-Type
```

입니다.

예를 들어

JSON이라면

```text
Content-Type

application/json
```

파일 업로드라면

```text
multipart/form-data
```

가 됩니다.

---

### ④ Body
Body는

실제 데이터입니다.

예를 들어

사용자가

```text
질문

파일

회원정보
```

등을

보내면

모두 Body에 들어갑니다.

예를 들어

```json
{
    "question":
    "FastAPI가 뭐예요?"
}
```

도

Body입니다.

---

### Request를 그림으로 보면
```text
POST /chat

──────────────────────

Header

Authorization

Content-Type

──────────────────────

Body

{

    "question":

    "안녕하세요"

}
```

FastAPI는

이 구조를

받아서

처리합니다.

---

### Response도 비슷하다
FastAPI는

결과를

JSON으로 돌려줍니다.

```text
Response

↓

Status Code

↓

Header

↓

Body
```

Body에는

실제 결과가 들어갑니다.

```json
{
    "answer":
    "안녕하세요."
}
```

---

### REST API란 무엇인가?
이제

REST API를 알아봅시다.

학생들이

REST를

어렵게 생각합니다.

사실은

매우 단순합니다.

REST는

> **HTTP를 일관성 있게 사용하는 설계 규칙**

입니다.

즉

HTTP를

잘 사용하는 방법입니다.

---

### REST가 없으면?
예를 들어

회원 정보를 조회한다고

생각해 봅시다.

개발자마다

API를

마음대로 만든다면

```text
/getUser

/showUser

/userInfo

/findUser

/member
```

모두

가능합니다.

그러면

협업이 매우 어려워집니다.

---

그래서

규칙을 만들었습니다.

예를 들어

사용자는

```text
/users
```

라고 합니다.

조회는

```text
GET
```

생성은

```text
POST
```

삭제는

```text
DELETE
```

처럼

Method로

구분합니다.

---

### REST API 예제
예를 들어

문서 관리 시스템입니다.

문서 조회

```text
GET

/documents
```

문서 생성

```text
POST

/documents
```

문서 수정

```text
PUT

/documents/10
```

문서 삭제

```text
DELETE

/documents/10
```

URL은

동일합니다.

Method만

달라집니다.

이것이

REST입니다.

---

### 왜 REST가 중요할까?
우리도

앞으로

AI 서비스를 만들 것입니다.

예를 들어

```text
/chat

/upload

/document

/ocr
```

같은

API를

만듭니다.

이 API들이

REST 규칙을 따르면

React 개발자도

Backend 개발자도

쉽게 이해할 수 있습니다.

협업이 훨씬 쉬워집니다.

---

### FastAPI는 REST API를 쉽게 만든다
FastAPI의 가장 큰 특징 중 하나는

REST API를 매우 자연스럽게 표현할 수 있다는 점입니다.

예를 들어

```text
@app.get("/documents")
```

이라고 작성하면

"문서 목록을 조회하는 API"

라는 의미가 바로 드러납니다.

또

```text
@app.post("/documents")
```

라고 작성하면

"새 문서를 생성하는 API"

라는 것을 코드만 봐도 쉽게 이해할 수 있습니다.

즉,

FastAPI는 코드 자체가 API 명세서처럼 읽히도록 설계되어 있습니다.

---

### 지금까지의 데이터 흐름
지금까지 배운 내용을 연결하면

다음과 같습니다.

```text
사용자

↓

React

↓

HTTP Request

(Method, URL, Header, Body)

↓

FastAPI

↓

AI 처리

↓

HTTP Response

(Status, Header, Body)

↓

React

↓

사용자
```

이 그림은 앞으로 FastAPI 전체 과정에서 계속 등장하는 핵심 구조입니다.

---

### 핵심 내용 정리
이번 Unit에서는 React와 FastAPI가 서로 통신하는 기본 원리를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **HTTP는 웹에서 데이터를 주고받기 위한 표준 통신 규약**이다.
    
- **Request**는 클라이언트가 서버에 보내는 요청이고, **Response**는 서버가 클라이언트에 돌려주는 결과이다.
    
- 하나의 HTTP Request는 **Method, URL, Header, Body**로 구성된다.
    
- **REST API**는 HTTP를 일관성 있게 설계하기 위한 규칙이며, 협업과 유지보수를 쉽게 만들어 준다.
    
- FastAPI는 이러한 REST API를 간결하고 직관적으로 구현하도록 설계된 프레임워크이다.
    

---

## Module 13. 비동기 프로그래밍(Async Programming) - `async` / `await`


### Module 실습 예제

- [예제 1: async_sequential.py](examples/module_13/async_sequential.py) — 두 I/O 작업을 순차적으로 기다립니다.
- [예제 2: async_concurrent.py](examples/module_13/async_concurrent.py) — asyncio.gather로 독립적인 I/O를 동시에 처리합니다.



### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 자신의 언어로 답할 수 있어야 합니다.

- 비동기 프로그래밍은 왜 필요한가?
    
- 동기(Synchronous)와 비동기(Asynchronous)의 차이는 무엇인가?
    
- `async`와 `await`는 어떻게 동작하는가?
    
- AI 서비스에서는 왜 비동기가 중요한가?
    
- 언제 비동기를 사용하고, 언제 사용하지 말아야 하는가?
    

---

### ① 문제 이해 (Why)
지금까지 작성한 코드는 대부분 다음과 같이 동작했습니다.

```text
작업 A

↓

완료

↓

작업 B

↓

완료

↓

작업 C
```

이것을 **동기(Synchronous)** 라고 합니다.

---

예를 들어

```python
read_file()

search_vector()

call_llm()

save_history()
```

프로그램은

```text
파일 읽기 완료

↓

Vector Search 완료

↓

LLM 완료

↓

저장 완료
```

순서대로 실행합니다.

---

문제는

**기다리는 시간이 많다**는 것입니다.

---

### AI 서비스에는 기다리는 작업이 많다.
예를 들어

```text
사용자 질문

↓

OpenAI API 호출

↓

2초 대기

↓

응답
```

Python은

2초 동안

CPU를 사용하는 것이 아닙니다.

그냥 기다립니다.

---

또 다른 예

```text
파일 다운로드

↓

3초 대기

↓

완료
```

역시

기다립니다.

---

또 다른 예

```text
Database 조회

↓

1초 대기

↓

완료
```

또 기다립니다.

---

즉,

AI 서비스는

```text
계산

보다

대기(I/O)
```

가 훨씬 많습니다.

---

### 순차 실행이라면?
예를 들어

세 개의 API를 호출합니다.

```text
API 1

2초
```

↓

```text
API 2

2초
```

↓

```text
API 3

2초
```

총

```text
6초
```

가 걸립니다.

---

하지만

세 개를 동시에 요청하면?

```text
API1 ────── 2초

API2 ────── 2초

API3 ────── 2초
```

전체는

약

```text
2초
```

면 끝납니다.

---

### 이것이 Async Programming이다.
> **기다리는 동안 다른 작업을 수행하는 프로그래밍 방식**

---

### AI 서비스에서는 왜 중요한가?
AI 서비스는

거의 모두

다음 작업을 합니다.

```text
HTTP 요청

↓

OpenAI API

↓

Ollama

↓

Vector DB

↓

Database

↓

파일 입출력
```

이들은

모두

I/O 작업입니다.

즉,

비동기의 효과가 매우 큽니다.

---

### ② 개념 이해 (Concept)
먼저

동기와

비동기를

비교해봅시다.

---

#### 동기(Synchronous)
```text
A

↓

완료

↓

B

↓

완료

↓

C
```

항상

앞의 작업이 끝나야

다음 작업을 합니다.

---

#### 비동기(Asynchronous)
```text
A 시작

↓

기다림

↓

B 실행

↓

기다림

↓

C 실행
```

기다리는 시간을

다른 작업에

사용합니다.

---

### 중요한 오해
많은 사람들이

비동기를

동시에 실행하는 것이라고 생각합니다.

엄밀히 말하면

조금 다릅니다.

---

비동기는

```text
기다리는 시간

↓

다른 작업 수행
```

입니다.

즉,

시간을

효율적으로 사용하는 것입니다.

---

### Thread와도 다르다.
Thread는

> **하나의 Process 안에서 여러 실행 흐름을 운영하는 방식**

입니다.

Thread가 여러 개라고 해서

CPU가 여러 개가 되는 것은 아닙니다.

Process는

> **서로 독립된 실행 공간에서 작업하는 방식**

이고,

Async는

> **작업이 기다리는 동안 같은 실행 흐름이 다른 작업을 처리하는 방식**

입니다.

---

Async

```text
한 사람이

여러 일을

번갈아 하는 것
```

입니다.

---

### 비유
은행 창구

동기

```text
손님 1

↓

끝날 때까지 기다림

↓

손님 2

↓

손님 3
```

---

비동기

```text
손님1

서류 작성

↓

기다리는 동안

↓

손님2 처리

↓

손님3 처리

↓

다시 손님1
```

대기 시간이

낭비되지 않습니다.

---

### ③ 구조 이해 (Architecture)
동기 구조

```text
Request

↓

File

↓

LLM

↓

Database

↓

Response
```

---

비동기 구조

```text
Request

↓

LLM 요청

↓

기다림

↓

다른 요청 처리

↓

LLM 응답

↓

Response
```

---

AI 서비스에서는

FastAPI도

이 구조를 사용합니다.

```text
User A

↓

OpenAI 호출

↓

기다림

↓

User B 처리

↓

User C 처리

↓

응답
```

---

### 내부 동작
Python에는

이벤트 루프(Event Loop)가 있습니다.

```text
Task A

↓

대기

↓

Task B

↓

대기

↓

Task C

↓

Task A 완료
```

이벤트 루프가

계속

작업을

전환합니다.

> **참고**
> 
> Event Loop의 내부 구현은 Python 심화 과정에서 다룹니다. 여기서는 "`await`로 대기하는 동안 다른 작업을 처리해 주는 관리자" 정도로 이해하면 충분합니다.

---

### ④ 실습 준비
프로젝트

```text
python-ai/

    async/

        async_example.py
```

추가 라이브러리

```python
import asyncio
```

Python 기본 모듈입니다.

---

### ⑤ 기본 사용법
#### async 함수
```python
async def hello():

    print("Hello")
```

일반 함수와

다르게

```text
async
```

를 붙입니다.

---

#### await
```python
await some_function()
```

의 의미는

```text
끝날 때까지

기다려라
```

입니다.

하지만

기다리는 동안

다른 작업을

수행할 수 있습니다.

---

#### 가장 간단한 예제
```python
import asyncio


async def hello():

    print("Hello")


asyncio.run(hello())
```

---

#### 기다리기
```python
import asyncio


async def work():

    print("시작")

    await asyncio.sleep(2)

    print("끝")


asyncio.run(work())
```

여기서

```python
await asyncio.sleep(2)
```

는

2초 동안

다른 작업을

실행할 기회를 제공합니다.

---

### 여러 작업 실행
```python
import asyncio


async def task1():

    await asyncio.sleep(2)

    print("Task1")


async def task2():

    await asyncio.sleep(2)

    print("Task2")
```

실행

```python
async def main():

    await asyncio.gather(

        task1(),

        task2()

    )


asyncio.run(main())
```

두 작업은

거의 동시에

진행됩니다.

---

### AI 서비스 예제
예를 들어

세 개의 API 호출

```python
await call_openai()

await search_vector()

await save_history()
```

이 아니라

```python
await asyncio.gather(

    search_vector(),

    save_history()

)
```

처럼

독립적인 작업은

함께 처리할 수 있습니다.

---

### FastAPI 예제
나중에 배우겠지만

FastAPI에서 외부 비동기 API를 호출하는 Endpoint는
다음처럼 작성할 수 있습니다.

```python
@app.post("/chat")

async def chat():

    ...
```

왜냐하면

API 서버는 여러 요청을 효율적으로 처리해야 하고,

외부 API처럼 `await`를 지원하는 작업을 호출할 때

비동기 함수를 활용할 수 있기 때문입니다.

하지만 모든 FastAPI 함수를

무조건 `async def`로 작성하는 것은 아닙니다.

---

### ⑥ 실무 활용
AI 프로젝트에서는

다음과 같은 I/O 작업이

비동기 처리의 후보가 됩니다.

```text
HTTP 요청

OpenAI API

Database

File I/O

Network

VectorDB
```

다만 I/O 작업이라고 해서

모든 코드가 자동으로 비동기가 되는 것은 아닙니다.

예를 들어 Python의 기본 `open()`, `read()`, `write()`는

동기 방식으로 동작합니다.

비동기 서버에서 큰 파일을 처리할 때는

Thread 실행, Streaming 또는 비동기 지원 도구를 고려해야 합니다.

---

반대로

다음은

비동기로

큰 효과가 없습니다.

```text
이미지 계산

행렬 계산

암호화

CPU 연산
```

이런 작업은

CPU가 바쁩니다.

---

### 언제 Async를 사용할까?
#### 좋은 예
```text
OpenAI API

↓

대기

↓

비동기
```

---

#### 좋지 않은 예
```text
10억 번 반복문
```

이런 계산은

비동기의

장점이 거의 없습니다.

---

### 실무 Best Practice
#### ① I/O 작업에 사용한다.
대표적으로

```text
HTTP

Database

File

API
```

입니다.

---

#### ② CPU 연산에는 남용하지 않는다.
AI 모델 학습처럼

계산량이 큰 작업은

순수 Python의 무거운 CPU 연산은

Process나 외부 작업 시스템을 고려합니다.

행렬 연산이나 모델 연산처럼 GPU에 적합한 작업은

GPU를 지원하는 라이브러리를 활용합니다.

Thread는 주로 Blocking I/O를 동시에 다룰 때 활용합니다.

---

#### ③ 동기와 비동기의 경계를 명확히 관리한다.
실제 서비스에서는

동기 코드와 비동기 코드가 함께 사용될 수 있습니다.

무계획하게 혼합하지 말고,

어떤 작업이 Event Loop를 막는지 확인해야 합니다.

---

#### ④ FastAPI에서는 호출하는 작업에 맞게 선택한다.
호출하려는 라이브러리가 `await`를 지원하면

`async def`를 사용합니다.

일반적인 동기 라이브러리를 사용한다면

`def`를 사용할 수 있습니다.

`async def` 안에서 오래 걸리는 동기 작업을 직접 실행하면

Event Loop를 막을 수 있으므로 주의해야 합니다.

FastAPI에서는 두 방식을 상황에 맞게 사용할 수 있으며,

자세한 기준은 FastAPI 과정에서 학습합니다.

---

### ⑦ 자주 발생하는 실수
#### 1. 모든 함수를 async로 만든다.
필요한 함수만

비동기로

만듭니다.

---

#### 2. await를 빼먹는다.
```python
call_api()
```

가 아니라

```python
await call_api()
```

입니다.

---

#### 3. CPU 작업에도 Async를 사용한다.
효과가 거의 없습니다.

---

#### 4. Async가 항상 빠르다고 생각한다.
아닙니다.

I/O 작업에서만

큰 효과가 있습니다.

---

### Sync vs Async
|Sync|Async|
|---|---|
|순차 실행|대기 중 다른 작업 수행|
|구현 단순|구현이 조금 복잡|
|I/O에서 느림|I/O에서 효율적|
|CPU 작업 적합|네트워크 작업 적합|

---

### AI 서비스에서 Async 구조
```text
User

↓

FastAPI

↓

OpenAI API

↓

대기

↓

다른 사용자 처리

↓

OpenAI 응답

↓

Response
```

이 구조 덕분에

수백 명의 사용자가 동시에 요청해도

효율적으로 처리할 수 있습니다.

---

### ⑧ 핵심 내용 정리
이번 Unit의 핵심은 다음과 같습니다.

- **비동기 프로그래밍은 기다리는 동안 다른 작업을 수행하여 자원을 효율적으로 사용하는 방식**이다.
    
- `async`는 비동기 함수를 정의하고, `await`는 비동기 작업의 완료를 기다리면서 다른 작업을 수행할 기회를 제공한다.
    
- AI 서비스는 OpenAI API, 데이터베이스, 파일 입출력 등 **I/O 작업이 많기 때문에 비동기의 효과가 매우 크다.**
    
- CPU 연산이 많은 작업에는 비동기가 아니라 다른 병렬 처리 기법을 사용하는 것이 적합하다.
    
- FastAPI는 `def`와 `async def`를 모두 지원하며, 호출하는 작업이 `await`를 지원하는지와 Blocking 여부에 따라 선택한다.
    

---

## Module 14. ASGI와 Uvicorn 동작 원리


### Module 실습 예제

- [예제 1: raw_asgi_app.py](examples/module_14/raw_asgi_app.py) — Framework 없이 ASGI 호출 규약을 확인합니다.
- [예제 2: fastapi_asgi_app.py](examples/module_14/fastapi_asgi_app.py) — Uvicorn이 불러올 FastAPI ASGI 객체를 만듭니다.



#### 프로젝트 연결 학습
- **문제 상황:** FastAPI 코드가 실제 네트워크 요청을 받는 과정을 연결한다.
- **오늘 만드는 것:** Uvicorn과 ASGI 애플리케이션의 역할을 구분한다.
- **AI 플랫폼의 위치:** AI 요청의 동시성과 연결 수명주기를 떠받치는 실행 계층이다.
- **실무에서 많이 하는 실수:** Uvicorn·FastAPI·ASGI를 같은 개념으로 설명한다.
- **5분 실습:** 서버 실행 명령의 모듈·객체·reload 의미를 설명한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Uvicorn은 무엇인가?
    
- ASGI는 무엇인가?
    
- FastAPI는 혼자 실행되는 프로그램인가?
    
- FastAPI 내부에서는 어떤 일이 일어나는가?
    
- Request는 어떻게 FastAPI까지 전달되는가?
    

---

### ① 문제 이해 (Why)
앞서 HTTP 단원에서는

React와 FastAPI가

HTTP를 이용하여 통신한다는 것을 배웠습니다.

그런데 아직 하나가 남아 있습니다.

우리는 항상

```bash
uvicorn main:app --reload
```

라는 명령을 실행합니다.

학생들은 보통 이렇게 생각합니다.

> "FastAPI를 실행하는 명령이구나."

사실은 조금 다릅니다.

---

FastAPI는

실행 프로그램이 아닙니다.

Framework입니다.

즉,

혼자서는 실행할 수 없습니다.

---

예를 들어

React도

```bash
npm run dev
```

를 실행합니다.

React가 실행되는 것이 아니라

Vite가 개발 서버를 실행하는 것입니다.

FastAPI도

똑같습니다.

---

### FastAPI는 자동차 엔진이다
자동차를 생각해봅시다.

자동차는

엔진만 있다고 움직이지 않습니다.

```text
엔진

+

바퀴

+

핸들

+

운전자
```

가 모두 있어야 합니다.

---

FastAPI도

혼자서는 동작하지 않습니다.

```text
FastAPI

+

ASGI

+

Uvicorn

+

Operating System
```

이 함께 동작해야 합니다.

---

### FastAPI는 누구와 함께 동작할까?
전체 구조를 먼저 봅시다.

```text
Browser

↓

HTTP Request

↓

Uvicorn

↓

ASGI

↓

FastAPI

↓

Python Code

↓

Response

↓

Browser
```

학생들은

보통

```text
Browser

↓

FastAPI
```

라고 생각합니다.

하지만

실제로는

그 사이에

여러 계층이 존재합니다.

---

### Uvicorn은 무엇인가?
Uvicorn은

ASGI Server입니다.

쉽게 말하면

> **HTTP 요청을 가장 먼저 받는 프로그램**

입니다.

사용자가

```text
http://localhost:8000
```

으로 접속하면

가장 먼저 만나는 프로그램이

바로

Uvicorn입니다.

---

즉,

```text
Browser

↓

Uvicorn
```

입니다.

아직

FastAPI는 등장하지 않습니다.

---

### Uvicorn의 역할
예를 들어

사용자가

```text
GET /chat
```

을 요청했습니다.

그러면

Uvicorn은

먼저

HTTP를 읽습니다.

```text
HTTP

↓

Method

↓

URL

↓

Header

↓

Body
```

를 분석합니다.

---

그리고

FastAPI에게

전달합니다.

```text
Browser

↓

Uvicorn

↓

FastAPI
```

---

즉,

Uvicorn은

택배 기사와 같습니다.

택배를

직접 만들지는 않습니다.

하지만

정확한 곳으로

배달합니다.

---

### ASGI는 무엇인가?
ASGI는

Asynchronous Server Gateway Interface입니다.

이름은 어렵지만

의미는 단순합니다.

> **Uvicorn과 FastAPI가 대화하는 약속**

입니다.

---

React와 FastAPI는

HTTP를 사용했습니다.

그렇다면

Uvicorn과 FastAPI는

무엇으로 대화할까요?

바로

ASGI입니다.

---

즉

```text
Browser

↓

HTTP

↓

Uvicorn

↓

ASGI

↓

FastAPI
```

입니다.

---

### HTTP와 ASGI는 다르다
학생들이

가장 많이 헷갈리는 부분입니다.

HTTP와

ASGI는

같은 것이 아닙니다.

HTTP는

```text
Browser

↓

Server
```

사이의 약속입니다.

---

ASGI는

```text
Server

↓

Python Application
```

사이의 약속입니다.

즉

역할이 다릅니다.

---

### 그림으로 이해하기
```text
사용자

↓

브라우저

↓

HTTP

↓

Uvicorn

↓

ASGI

↓

FastAPI

↓

Python 코드
```

이 구조를

머릿속에

반드시 기억해야 합니다.

---

### 요청(Request)은 어떻게 이동할까?
사용자가

브라우저에서

```text
GET /documents
```

를 요청합니다.

그러면

다음 순서가 발생합니다.

① 브라우저가 HTTP Request 생성

↓

② Uvicorn이 요청 수신

↓

③ ASGI 규칙에 맞게 FastAPI 호출

↓

④ FastAPI가 Python 함수 실행

↓

⑤ 결과 생성

↓

⑥ Uvicorn이 HTTP Response 생성

↓

⑦ 브라우저에게 반환

---

ASCII Diagram으로 보면

```text
Browser

     │

HTTP Request

     ▼

+----------------+

|    Uvicorn     |

+----------------+

     │

     │ ASGI

     ▼

+----------------+

|    FastAPI     |

+----------------+

     │

Python Function

     ▼

Business Logic

     │

     ▼

JSON

     │

     ▼

Uvicorn

     │

HTTP Response

     ▼

Browser
```

---

### 왜 Uvicorn이 필요한가?
학생들이

종종 묻습니다.

> FastAPI가 직접 HTTP를 처리하면 안 되나요?

가능은 합니다.

하지만

Framework의 역할과

Server의 역할은

분리하는 것이 좋습니다.

---

FastAPI는

비즈니스 로직에 집중합니다.

```text
로그인

문서 업로드

OCR

LLM 호출

DB 저장
```

---

반면

Uvicorn은

통신에 집중합니다.

```text
포트 열기

HTTP 처리

연결 유지

비동기 Event Loop

Response 전송
```

각자의 역할이 명확하기 때문에

유지보수가 쉬워집니다.

---

### Event Loop란 무엇일까?
ASGI가 빠른 이유는

Event Loop 때문입니다.

지금은

완벽히 이해하지 않아도 됩니다.

개념만 알아봅시다.

기존 방식은

```text
요청 A

↓

끝날 때까지 기다림

↓

요청 B
```

이었습니다.

---

Event Loop에서는

```text
요청 A

↓

기다리는 동안

↓

요청 B

↓

요청 C

↓

A 완료
```

가 가능합니다.

즉

기다리는 시간을

낭비하지 않습니다.

---

이 구조 덕분에

AI 서비스처럼

LLM 응답을 기다리는 동안에도

다른 요청을 처리할 수 있습니다.

---

### 앞으로 우리가 사용할 구조
FastAPI 과정에서는

항상

아래 구조를 사용합니다.

```text
React

↓

HTTP

↓

Uvicorn

↓

ASGI

↓

FastAPI

↓

Service Layer

↓

OpenAI

↓

FastAPI

↓

JSON

↓

React
```

이 구조는

OpenAI API,

Ollama,

LangChain,

Document AI를 배우더라도

절대 변하지 않습니다.

AI 기능만 추가될 뿐입니다.

---

### 학생들이 자주 하는 오해
##### 오해 1
> Uvicorn = FastAPI

아닙니다.

Uvicorn은 서버이고,

FastAPI는 프레임워크입니다.

---

##### 오해 2
> ASGI = Server

아닙니다.

ASGI는

**인터페이스(약속)**입니다.

실제 서버는

Uvicorn입니다.

---

##### 오해 3
> FastAPI가 HTTP를 직접 처리한다.

엄밀히 말하면 아닙니다.

HTTP 연결을 직접 관리하는 것은 Uvicorn이며, FastAPI는 **ASGI를 통해 전달받은 요청을 처리하는 애플리케이션 프레임워크**입니다.

---

### 지금까지의 전체 실행 구조
지금까지 배운 내용을 하나의 그림으로 정리하면 다음과 같습니다.

```text
                사용자
                   │
                   ▼
              Web Browser
                   │
             HTTP Request
                   │
                   ▼
            ┌──────────────┐
            │   Uvicorn    │
            │ (ASGI Server)│
            └──────────────┘
                   │
             ASGI Interface
                   │
                   ▼
            ┌──────────────┐
            │   FastAPI    │
            └──────────────┘
                   │
           Python Business Logic
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
       Database  OpenAI     Files
          │        │         │
          └────────┴─────────┘
                   │
                   ▼
               JSON Result
                   │
                   ▼
            HTTP Response
                   │
                   ▼
                Browser
```

이 그림은 앞으로 FastAPI뿐만 아니라 **OpenAI API, Ollama, LangChain, Document AI**까지 이어지는 AIKOS Phase 1 전체 백엔드의 기본 실행 구조입니다.

---

### 핵심 내용 정리
이번 Unit에서는 FastAPI가 실제로 실행되는 내부 구조를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **FastAPI는 실행 프로그램이 아니라 웹 애플리케이션 프레임워크**이다.
    
- **Uvicorn은 ASGI Server**이며 HTTP 요청을 가장 먼저 받아 FastAPI로 전달한다.
    
- **ASGI는 Uvicorn과 FastAPI가 통신하기 위한 표준 인터페이스**이다.
    
- 브라우저와 서버는 **HTTP**로 통신하고, 서버 내부에서는 **ASGI**를 통해 요청이 전달된다.
    
- 역할이 분리되어 있기 때문에 FastAPI는 비즈니스 로직에 집중하고, Uvicorn은 네트워크와 연결 관리에 집중할 수 있다.
    

---

## Module 15. FastAPI 개발환경 구축


### Module 실습 예제

- [예제 1: environment_check.py](examples/module_15/environment_check.py) — 현재 Python 실행 환경과 가상환경 여부를 확인합니다.
- [예제 2: dependency_versions.py](examples/module_15/dependency_versions.py) — 주요 Package의 설치 여부와 버전을 확인합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 학생마다 다른 환경 때문에 생기는 재현성 문제를 줄인다.
- **오늘 만드는 것:** Python 3.12 가상환경과 기준 패키지를 설치한다.
- **AI 플랫폼의 위치:** 모든 후속 실습의 동일한 출발점이다.
- **실무에서 많이 하는 실수:** requirements 파일만으로 OS와 Python까지 완전히 같아진다고 생각한다.
- **5분 실습:** 새 가상환경에서 FastAPI와 Uvicorn 버전을 확인한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- FastAPI 개발환경은 어떻게 구축하는가?
    
- 왜 Python 가상환경을 사용하는가?
    
- uvicorn은 어떻게 실행되는가?
    
- AI 서비스 프로젝트는 어떤 구조로 시작하는가?
    
- 앞으로 모든 실습은 어떤 프로젝트에서 진행되는가?
    

---

### ① 문제 이해 (Why)
드디어

코드를 작성할 시간입니다.

그런데 바로 코드를 작성하지는 않습니다.

실무에서는

가장 먼저 하는 일이 있습니다.

바로

> **개발환경 구축(Environment Setup)**

입니다.

---

많은 초보 개발자가

이 과정을 건너뜁니다.

```text
프로젝트 생성

↓

pip install

↓

main.py 작성

↓

끝
```

하지만

실무에서는

이렇게 하지 않습니다.

---

### 왜 개발환경이 중요할까?
예를 들어

회사에서 AI 프로젝트를 진행합니다.

팀원이 5명 있습니다.

```text
김개발

이개발

박개발

최개발

정개발
```

모두

같은 프로젝트를 개발합니다.

---

그런데

김개발은

```text
Python 3.13
```

을 사용합니다.

---

이개발은

```text
Python 3.11
```

을 사용합니다.

---

박개발은

```text
FastAPI 0.120
```

---

최개발은

```text
FastAPI 0.95
```

---

그러면

같은 코드인데

한 사람은 실행되고

다른 사람은 오류가 발생합니다.

---

실무에서는

이런 일을

절대 허용하지 않습니다.

---

### 개발환경도 프로젝트의 일부이다
학생들은

코드만 프로젝트라고 생각합니다.

하지만

실무에서는

환경도 프로젝트입니다.

```text
프로젝트

├── 코드

├── 라이브러리

├── Python 버전

├── 환경 변수

├── 실행 방법

└── 패키지 목록
```

즉,

환경까지 동일해야

같은 결과가 나옵니다.

---

### Python은 왜 가상환경을 사용할까?
Python에서

가장 중요한 개념 중 하나입니다.

바로

**Virtual Environment(가상환경)** 입니다.

---

예를 들어

컴퓨터에는

Python이 하나 설치되어 있습니다.

```text
Python

↓

FastAPI

↓

Requests

↓

NumPy

↓

Pandas
```

모든 프로젝트가

이것을 공유합니다.

---

처음에는 문제가 없어 보입니다.

---

### 프로젝트가 늘어나면?
예를 들어

프로젝트 A

```text
FastAPI 0.118
```

---

프로젝트 B

```text
FastAPI 0.120
```

---

프로젝트 C

```text
FastAPI 0.95
```

---

서로 다른 버전을 사용하면

어떻게 될까요?

한 프로젝트를 위해

업데이트하면

다른 프로젝트가

망가질 수도 있습니다.

---

이것을

Dependency Conflict(의존성 충돌)이라고 합니다.

---

### 해결 방법
Python은

프로젝트마다

독립된 환경을 만듭니다.

```text
Project A

Python

FastAPI

Pandas

Requests
```

---

```text
Project B

Python

FastAPI

OpenAI

LangChain
```

---

```text
Project C

Python

Flask

TensorFlow
```

각 프로젝트가

자기만의 Python 환경을 갖습니다.

이것이

Virtual Environment입니다.

---

### 회사 건물로 비유하기
하나의 건물에

회사들이 입주합니다.

```text
건물

↓

회사 A

↓

회사 B

↓

회사 C
```

회사마다

사무실이 따로 있습니다.

회사 A의 물건이

회사 B에 영향을 주지 않습니다.

---

가상환경도

완전히 같습니다.

```text
컴퓨터

↓

프로젝트 A 환경

↓

프로젝트 B 환경

↓

프로젝트 C 환경
```

---

### 앞으로 사용할 프로젝트
AIKOS에서는

하나의 프로젝트를

끝까지 확장합니다.

새 프로젝트를

계속 만들지 않습니다.

---

프로젝트 이름은

예를 들어

```text
ai-platform
```

으로 하겠습니다.

---

현재는

아래 정도의 구조만 만듭니다.

```text
ai-platform/

    backend/

    frontend/
```

React에서 만든

frontend는

이미 존재합니다.

이번에는

backend를

만듭니다.

---

### backend 구조
처음에는

아주 단순합니다.

```text
backend/

    main.py
```

앞으로

이 구조가

점점 커질 것입니다.

---

### Python 가상환경 생성
backend 폴더로 이동합니다.

```bash
cd backend
```

---

가상환경 생성

Windows

```bash
python -m venv venv
```

macOS / Linux

```bash
python3 -m venv venv
```

여기서

`venv`

는

가상환경 폴더 이름입니다.

---

### 왜 `python -m venv`를 사용할까?
많은 학생들이

명령만 외웁니다.

하지만

원리를 이해하는 것이 중요합니다.

```bash
python -m venv venv
```

를 나누어 보면

```text
python
```

↓

현재 Python 실행

---

```text
-m
```

↓

Python 모듈 실행

---

```text
venv
```

↓

venv 모듈 실행

---

```text
venv
```

↓

생성될 폴더 이름

---

즉

의미는

> Python에게 venv 모듈을 실행해서 `venv`라는 가상환경을 만들어 달라

입니다.

---

### 생성 결과
```text
backend/

    venv/

    main.py
```

`venv` 안에는

Python 실행 파일,

라이브러리,

패키지 관리 도구가

모두 들어 있습니다.

---

### 가상환경 활성화
Windows

```bash
venv\Scripts\activate
```

---

macOS / Linux

```bash
source venv/bin/activate
```

성공하면

터미널 앞에

```text
(venv)
```

가 표시됩니다.

```text
(venv)

backend>
```

이것은

현재 프로젝트의 Python을 사용한다는 의미입니다.

---

### FastAPI 설치
이제

가상환경 안에

FastAPI를 설치합니다.

```bash
pip install fastapi
```

그리고

웹 서버인

Uvicorn도 설치합니다.

```bash
pip install uvicorn
```

실무에서는

보통 한 번에 설치합니다.

```bash
pip install fastapi uvicorn
```

---

### 왜 Uvicorn도 설치할까?
지난 Unit에서

배웠습니다.

```text
FastAPI

↓

Application
```

```text
Uvicorn

↓

ASGI Server
```

FastAPI만 설치하면

실행할 서버가 없습니다.

그래서

반드시

Uvicorn도 함께 설치합니다.

---

### 설치 확인
다음 명령으로

설치 여부를 확인할 수 있습니다.

```bash
pip list
```

예를 들어

```text
fastapi

uvicorn

pydantic

starlette
```

등이 보이면

정상적으로 설치된 것입니다.

여기서 **pydantic**과 **starlette**는 FastAPI가 내부적으로 사용하는 핵심 라이브러리이며, FastAPI 설치 시 함께 설치됩니다.

---

### requirements.txt는 왜 필요할까?
실무에서는

설치한 패키지를

기억하지 않습니다.

대신

목록으로 저장합니다.

```bash
pip freeze > requirements.txt
```

미니프로젝트와 메인프로젝트의 공통 기준 환경은 다음과 같습니다.

```text
Python 3.12.x
FastAPI 0.141.1
Uvicorn 0.54.0
Pydantic 2.13.5
SQLAlchemy 2.0.54
httpx 0.28.1
OpenAI Python SDK 3.19.2
pytest 9.1.1
```

이 목록은 공통 Backend 기준입니다. AI/ML 학습용 패키지는 별도 가상환경 또는 별도 프로젝트 Lock File로 관리합니다. 실제 프로젝트에서는 `requirements.txt`, `uv.lock` 등 Lock File을 재현 기준으로 사용합니다.

처럼 저장됩니다.

나중에 다른 개발자는

```bash
pip install -r requirements.txt
```

한 줄로 검증된 Python 패키지 버전을 설치해 유사한 의존성 환경을 재현할 수 있습니다.

다만 Python 버전, 운영체제, CPU 아키텍처, 시스템 라이브러리까지 동일해지지는 않습니다. 더 높은 재현성이 필요하면 Python 버전, Lock File, Container 환경을 함께 관리합니다.

이것이 협업에서 매우 중요한 이유입니다.

---

### 지금까지 만든 개발환경
현재까지의 구조는 다음과 같습니다.

```text
ai-platform/

├── frontend/
│
└── backend/
    │
    ├── venv/
    ├── main.py
    └── requirements.txt
```

아직은 단순하지만,

이 구조가 앞으로 AI 플랫폼 백엔드의 기반이 됩니다.

---

### 실습 범위
##### Python 설치는 별도 Unit으로 만들 필요는 없습니다.
이미 **Python for AI**에서 Python 설치와 환경 구성을 학습했기 때문입니다.

이번 Unit에서는 설치 반복 대신 다음 협업 기준을 함께 확인합니다.

- 프로젝트 루트와 Backend 디렉터리의 역할
    
- `.gitignore`를 사용하는 이유
    
- `venv`를 Git에 올리면 안 되는 이유
    
- `requirements.txt`를 버전 관리하는 이유
    

이 내용은 실제 협업에서 매우 중요하며, 이후 Git/GitHub를 사용할 때도 자연스럽게 연결됩니다.

---

### 핵심 내용 정리
이번 Unit에서는 FastAPI 개발을 위한 실무 개발환경을 구축했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **프로젝트마다 독립적인 Python 가상환경(venv)을 사용**하여 의존성 충돌을 방지한다.
    
- **FastAPI는 애플리케이션**, **Uvicorn은 ASGI 서버**이므로 둘 다 설치해야 한다.
    
- `requirements.txt`는 프로젝트의 패키지 목록을 공유하기 위한 핵심 파일이다.
    
- 앞으로 AIKOS의 모든 FastAPI 실습은 **하나의 `backend` 프로젝트를 계속 확장**하는 방식으로 진행한다.
    

---

## Module 16. 첫 번째 FastAPI 프로젝트


### Module 실습 예제

- [예제 1: hello_app.py](examples/module_16/hello_app.py) — 첫 Endpoint와 Health Check를 구현합니다.
- [예제 2: chat_app.py](examples/module_16/chat_app.py) — 간단한 질문을 받아 응답하는 첫 AI 형태의 API를 만듭니다.



#### 프로젝트 연결 학습
- **문제 상황:** 설명만 듣지 않고 실제 요청이 왕복하는 첫 프로젝트를 만든다.
- **오늘 만드는 것:** health와 첫 API Endpoint를 실행한다.
- **AI 플랫폼의 위치:** AI 플랫폼의 가장 작은 실행 가능한 골격이다.
- **실무에서 많이 하는 실수:** 파일 이름·앱 객체·실행 명령의 관계를 모른 채 복사한다.
- **5분 실습:** Endpoint 하나를 추가하고 curl로 응답을 확인한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- FastAPI 프로젝트는 어떻게 시작하는가?
    
- `FastAPI()` 객체는 무엇인가?
    
- `main.py`는 왜 필요한가?
    
- Uvicorn은 무엇을 실행하는가?
    
- 첫 번째 API는 어떻게 만들어지는가?
    

---

### ① 문제 이해 (Why)
드디어

첫 번째 FastAPI 프로그램을 만들어 보겠습니다.

하지만 코드를 작성하기 전에

한 가지 질문을 해봅시다.

Python에서는

보통 이렇게 프로그램을 실행했습니다.

```python
print("Hello")
```

그리고

```bash
python main.py
```

를 실행했습니다.

그러면 프로그램이 실행되고 종료되었습니다.

---

그런데 FastAPI는 다릅니다.

우리는

```bash
uvicorn main:app --reload
```

를 실행합니다.

그리고 프로그램은 종료되지 않습니다.

왜 그럴까요?

---

### 일반 Python 프로그램과의 차이
우리가 지금까지 작성했던 Python 프로그램은

대부분 이런 형태였습니다.

```text
프로그램 시작

↓

코드 실행

↓

프로그램 종료
```

예를 들어

```python
print("Hello")
print("World")
```

실행하면

```text
Hello
World
```

를 출력하고 끝납니다.

---

하지만 서버(Server)는 다릅니다.

서버는

24시간 기다려야 합니다.

```text
사용자 없음

↓

기다림

↓

사용자 요청

↓

처리

↓

다시 기다림
```

즉,

서버 프로그램은

끝나면 안 됩니다.

---

### FastAPI 프로그램은 계속 살아있는 프로그램이다
웹 서버는

식당 직원과 비슷합니다.

```text
손님 없음

↓

대기

↓

손님 도착

↓

주문 처리

↓

다시 대기
```

직원이

손님이 없다고

퇴근하면 안 됩니다.

---

FastAPI도 같습니다.

```text
실행

↓

계속 대기

↓

요청 처리

↓

계속 대기

↓

요청 처리
```

이것이

웹 서버입니다.

---

### 프로젝트 구조
현재 프로젝트는

아래와 같습니다.

```text
backend/

    main.py

    requirements.txt

    venv/
```

오늘은

`main.py`

하나만 사용합니다.

---

### 첫 번째 코드
```python
from fastapi import FastAPI

app = FastAPI()
```

끝입니다.

학생들은

이 코드를 보고

당황합니다.

> "이게 전부인가요?"

네.

아직은

전부입니다.

---

### 코드 한 줄씩 이해하기
첫 번째 줄입니다.

```python
from fastapi import FastAPI
```

의미는

```text
FastAPI 라이브러리에서

FastAPI 클래스를 가져온다.
```

입니다.

Python에서 배운

import 문법과

완전히 같습니다.

---

두 번째 줄입니다.

```python
app = FastAPI()
```

이 한 줄이

FastAPI에서

가장 중요한 코드입니다.

---

### FastAPI()는 무엇일까?
학생들이

가장 많이 하는 오해입니다.

```python
FastAPI()
```

를

함수라고 생각합니다.

사실은

클래스입니다.

즉

객체(Object)를

생성하는 것입니다.

---

Python 시간에 배운

예를 떠올려 봅시다.

```python
class Dog:

    pass

dog = Dog()
```

였습니다.

FastAPI도

완전히 같습니다.

```python
app = FastAPI()
```

즉

FastAPI 객체를

생성하는 것입니다.

---

### app 객체는 무엇인가?
이 객체는

우리의 Backend 전체를

대표합니다.

조금 과장해서 말하면

```text
Backend = app
```

입니다.

앞으로

모든 API는

이 객체 안에

등록됩니다.

---

예를 들어

```text
@app.get(...)
```

도

사실은

```text
app 객체에

API를 등록하는 작업
```

입니다.

---

### 객체를 그림으로 보면
```text
app

│

├── GET API

├── POST API

├── Middleware

├── Exception

├── Router

└── 설정
```

앞으로

배울 모든 기능이

이 app 안으로

들어갑니다.

---

### 왜 이름이 app일까?
꼭

app일 필요는 없습니다.

예를 들어

```python
server = FastAPI()
```

도 가능합니다.

---

하지만

실무에서는

거의 대부분

```python
app = FastAPI()
```

를 사용합니다.

이유는

Uvicorn이

기본적으로

이 이름을 많이 사용하기 때문입니다.

또한 FastAPI 공식 문서와 대부분의 예제도 `app`이라는 이름을 사용하므로 협업과 가독성 측면에서 가장 일반적인 관례입니다.

---

### 첫 번째 API 만들기
이제

API 하나를

등록해 봅시다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}
```

이 코드가

우리의

첫 번째 Backend입니다.

---

### 코드 구조 이해
먼저

```text
@app.get("/")
```

가 있습니다.

학생들은

처음 보면

이상하게 보입니다.

이것은

Decorator입니다.

Decorator는

Python에서 이미 배운 개념입니다.

---

의미는

```text
"/"

URL에

GET 요청이 오면

아래 함수를 실행해라.
```

입니다.

---

즉

```text
@app.get("/")
```

는

"API 등록"

입니다.

---

### 함수는 언제 실행될까?
```python
def home():

    return ...
```

을 보면

함수입니다.

하지만

우리가 직접

호출하지 않았습니다.

---

그러면

누가 호출할까요?

정답은

FastAPI입니다.

---

구조는

이렇습니다.

```text
Browser

↓

GET /

↓

FastAPI

↓

home()

↓

return
```

즉

FastAPI가

자동으로

함수를 호출합니다.

---

### return은 무엇을 의미할까?
우리는

Python에서

```python
return 10
```

을 많이 사용했습니다.

FastAPI에서는

조금 다르게 동작합니다.

```python
return {

    "message":

    "Hello"
}
```

라고 작성하면

자동으로

JSON으로 변환됩니다.

즉

```json
{
    "message": "Hello"
}
```

를

브라우저에게

전송합니다.

---

### JSON으로 자동 변환되는 이유
학생들이

종종 묻습니다.

> "json.dumps() 안 해도 되나요?"

안 해도 됩니다.

FastAPI가

자동으로

변환합니다.

이 기능도

FastAPI의 큰 장점 중 하나입니다.

---

### Uvicorn 실행
이제

실행해봅시다.

```bash
uvicorn main:app --reload
```

---

이 명령을

하나씩 해석하면

```text
uvicorn
```

↓

ASGI Server 실행

---

```text
main
```

↓

main.py

---

```text
app
```

↓

app 객체

---

```text
--reload
```

↓

파일이 수정되면

자동 재시작

---

즉

전체 의미는

```text
main.py 안에 있는

app 객체를

Uvicorn으로 실행해라.
```

입니다.

---

### 왜 `main:app`일까?
이 부분은

실무에서도

많이 헷갈립니다.

학생들이

처음에는

파일 이름이라고

생각합니다.

사실은

```text
파일명

:

객체명
```

입니다.

예를 들어

```python
server.py

application = FastAPI()
```

라면

실행은

```bash
uvicorn server:application
```

이 됩니다.

즉

파일명과

객체 이름을

연결하는 문법입니다.

---

### 실행 후 발생하는 일
실행하면

다음 순서가 발생합니다.

```text
Uvicorn 시작

↓

main.py 읽기

↓

app 객체 생성

↓

HTTP Server 시작

↓

8000 포트 대기

↓

사용자 요청 기다림
```

이제

브라우저에서

```
http://localhost:8000
```

으로 접속하면

FastAPI가

요청을 처리합니다.

---

### 첫 번째 요청 처리 과정
사용자가

브라우저를 열면

실제로는

다음 과정이 일어납니다.

```text
Browser

↓

GET /

↓

Uvicorn

↓

FastAPI

↓

home()

↓

JSON 생성

↓

Response

↓

Browser
```

이것이

앞으로 수백 번 반복될

FastAPI의 기본 동작 원리입니다.

---

### 학생들이 자주 하는 실수
##### 실수 1
```python
app = FastAPI
```

괄호를 빼먹습니다.

반드시

```python
app = FastAPI()
```

이어야 합니다.

---

##### 실수 2
```text
@app.get("/")
```

를

`app = FastAPI()`

보다 먼저 작성합니다.

반드시

객체를 먼저 생성해야 합니다.

---

##### 실수 3
```text
uvicorn app:main
```

처럼

순서를 바꿉니다.

항상

```text
파일명:객체명
```

입니다.

---

##### 실수 4
`--reload` 없이 실행한 후

코드를 수정합니다.

변경사항이

적용되지 않습니다.

개발 중에는

항상

```bash
--reload
```

를 사용하는 습관을 들이는 것이 좋습니다.

---

### 지금까지 만든 Backend
아직은

아주 작은 서버입니다.

```text
Browser

↓

GET /

↓

FastAPI

↓

home()

↓

JSON

↓

Browser
```

하지만

이 구조 위에

OpenAI,

OCR,

RAG,

LangChain이

모두 올라가게 됩니다.

---

### 핵심 내용 정리
이번 Unit에서는 **첫 번째 FastAPI 애플리케이션**을 만들었습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- `FastAPI()`는 **FastAPI 애플리케이션 객체를 생성**한다.
    
- `app` 객체는 백엔드 전체의 중심이며, 모든 API는 이 객체에 등록된다.
    
- `@app.get("/")`는 특정 URL과 HTTP Method를 함수에 연결하는 **Decorator**이다.
    
- `return`한 Python 객체는 FastAPI가 **자동으로 JSON으로 변환**한다.
    
- `uvicorn main:app --reload`는 `main.py`의 `app` 객체를 개발 서버로 실행하는 명령이다.
    

---

## Module 17. Swagger(OpenAPI) 활용


### Module 실습 예제

- [예제 1: openapi_metadata.py](examples/module_17/openapi_metadata.py) — OpenAPI 문서에 제목·설명·Tag를 추가합니다.
- [예제 2: schema_examples.py](examples/module_17/schema_examples.py) — Request Model에 Swagger 입력 예시를 제공합니다.



#### 프로젝트 연결 학습
- **문제 상황:** API 계약을 브라우저에서 탐색하고 직접 검증한다.
- **오늘 만드는 것:** OpenAPI 문서에서 요청과 응답을 실행한다.
- **AI 플랫폼의 위치:** 프론트엔드·백엔드 협업의 계약 확인 지점이다.
- **실무에서 많이 하는 실수:** Swagger UI를 운영용 보안이나 테스트 전체의 대체물로 본다.
- **5분 실습:** 잘못된 입력을 보내 자동 생성된 검증 응답을 확인한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Swagger란 무엇인가?
    
- OpenAPI란 무엇인가?
    
- FastAPI는 왜 API 문서를 자동으로 만드는가?
    
- API를 어떻게 테스트하는가?
    
- Frontend 없이 Backend를 먼저 개발하는 이유는 무엇인가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

첫 번째 API를 만들었습니다.

```python
@app.get("/")
def home():
    return {"message": "Hello FastAPI"}
```

하지만

여기서 새로운 문제가 생깁니다.

> 정말 이 API가 제대로 동작하는지 어떻게 확인할까요?

---

React가 아직 없습니다.

그러면 테스트를 못할까요?

아닙니다.

FastAPI는

아주 강력한 기능을 제공합니다.

바로

**Swagger UI**

입니다.

---

### 예전에는 API 테스트가 매우 어려웠다
과거에는

Backend 개발자가 API를 만들면

Frontend 개발자가

직접 연결해야 했습니다.

```text
Backend 개발

↓

React 개발

↓

버튼 생성

↓

클릭

↓

API 테스트
```

즉

API 하나를 테스트하기 위해

Frontend까지 필요했습니다.

---

더 불편한 방법도 있었습니다.

```text
curl

Postman

직접 HTTP 작성
```

처음 학습하는 사람에게는

상당히 어려운 작업이었습니다.

---

### FastAPI는 왜 인기가 많아졌을까?
FastAPI가 등장하면서

생각이 바뀌었습니다.

> **API를 만들면 자동으로 테스트 화면도 만들자.**

이것이

Swagger입니다.

---

### Swagger란?
Swagger는

API를

브라우저에서

직접 실행할 수 있는 도구입니다.

예를 들어

```text
@app.get("/hello")
```

를 만들면

브라우저에서

```
http://localhost:8000/docs
```

에 접속하는 것만으로

자동으로

```text
GET /hello
```

버튼이 생깁니다.

---

### OpenAPI는 무엇일까?
학생들이

Swagger와

OpenAPI를

자주 헷갈립니다.

사실

역할이 다릅니다.

```text
OpenAPI

↓

API를 설명하는 표준 문서
```

---

```text
Swagger UI

↓

OpenAPI 문서를

예쁘게 보여주는 화면
```

즉

OpenAPI는

문서 형식이고

Swagger는

그 문서를 보는 프로그램입니다.

---

### 쉽게 비유하면
OpenAPI는

설계도입니다.

Swagger는

설계도를 보여주는

뷰어입니다.

```text
설계도

↓

OpenAPI

↓

Swagger UI

↓

브라우저
```

---

### FastAPI는 왜 자동으로 문서를 만들까?
예를 들어

우리가

API를 만들었습니다.

```text
@app.get("/documents")
```

그러면

FastAPI는

자동으로

다음을 생성합니다.

```text
GET

/documents

설명

응답 형식
```

우리가

따로 문서를 작성하지 않았습니다.

그런데도

문서가 생깁니다.

---

### 왜 가능한가?
FastAPI는

Python Type Hint를

적극 활용합니다.

예를 들어

```text
@app.get("/users/{user_id}")
def get_user(user_id: int):
```

라고 작성하면

FastAPI는

자동으로

```text
Parameter

↓

int

↓

필수 여부

↓

문서 생성
```

을 수행합니다.

즉

코드가

곧 문서입니다.

---

### Swagger 접속
서버를 실행합니다.

```bash
uvicorn main:app --reload
```

그리고

브라우저에서

```
http://localhost:8000/docs
```

를 입력합니다.

그러면

Swagger 화면이 나타납니다.

---

### Swagger에는 무엇이 보일까?
예를 들어

우리가 만든 API가

```text
@app.get("/")
```

라면

Swagger에는

```text
GET /

↓

Try it out
```

버튼이 나타납니다.

---

### Try it out
FastAPI에서

가장 많이 사용하는 버튼입니다.

누르면

API를

직접 실행할 수 있습니다.

```text
GET /

↓

Execute
```

버튼을 누르면

실제로

FastAPI에게

HTTP Request를 보냅니다.

---

### 결과 확인
우리의 코드가

```python
return {

    "message":

    "Hello FastAPI"

}
```

였다면

Swagger는

```json
{
    "message": "Hello FastAPI"
}
```

를 보여줍니다.

즉

React 없이도

Backend를

검증할 수 있습니다.

---

### Swagger가 보내는 것도 HTTP이다
많은 학생들이

Swagger를

특별한 기능이라고 생각합니다.

사실은

아닙니다.

Swagger도

HTTP를 사용합니다.

```text
Swagger

↓

HTTP Request

↓

FastAPI

↓

HTTP Response

↓

Swagger
```

React 대신

Swagger가

Request를 보내는 것입니다.

---

### 그래서 개발이 빨라진다
실무에서는

보통

순서가 이렇습니다.

```text
FastAPI 개발

↓

Swagger 테스트

↓

React 연결
```

먼저

Backend가

정상 동작하는지

확인합니다.

그다음

React를

붙입니다.

---

### API 문서는 왜 중요할까?
예를 들어

Backend 개발자가

회사에 있습니다.

Frontend 개발자는

다른 팀입니다.

Backend가

다음 API를 만들었습니다.

```text
POST

/chat
```

Frontend는

어떻게 사용할까요?

Swagger를 보면 됩니다.

```text
URL

Method

Parameter

Request

Response
```

모두

자동으로

설명되어 있습니다.

---

### 실무에서는 Swagger를 많이 사용할까?
네.

매우 많이 사용합니다.

실제로는

React보다

Swagger를

더 많이 보는 Backend 개발자도 있습니다.

이유는

API 테스트가

가장 빠르기 때문입니다.

---

### docs와 redoc
FastAPI는

문서를

두 가지 형태로 제공합니다.

첫 번째

```
/docs
```

Swagger UI

---

두 번째

```
/redoc
```

ReDoc

둘 다

같은 OpenAPI 문서를

사용합니다.

화면만

다릅니다.

---

### API를 하나 더 만들어 보자
예를 들어

```python
@app.get("/hello")
def hello():

    return {

        "message": "Hello"

    }
```

를 작성합니다.

---

Swagger를

새로고침하면

자동으로

```text
GET /

GET /hello
```

두 개의 API가

생깁니다.

이것이

자동 문서 생성입니다.

---

### 학생들이 자주 하는 실수
#### 실수 1
```
/docs
```

에 접속했는데

404가 발생합니다.

대부분

Uvicorn이

실행되지 않았거나

잘못된 포트에

접속한 경우입니다.

---

#### 실수 2
코드를 수정했는데

Swagger가

변하지 않습니다.

보통

```bash
--reload
```

없이

실행했기 때문입니다.

---

#### 실수 3
API는 만들었는데

Swagger에

안 보입니다.

대부분

Decorator를

빼먹었습니다.

예를 들어

```text
def hello():
```

만 작성하면

FastAPI는

API인지

모릅니다.

반드시

```text
@app.get(...)
```

가 필요합니다.

---

### 지금까지 만든 Backend
이제

우리의 Backend는

직접 테스트할 수 있습니다.

```text
Browser

↓

Swagger

↓

HTTP

↓

FastAPI

↓

Python

↓

JSON

↓

Swagger
```

React 없이도

Backend 개발이

가능해졌습니다.

---

### 왜 이것이 AI 서비스에서 중요할까?
앞으로 우리는

OpenAI API를 연결합니다.

React 없이도

먼저

```text
POST /chat

↓

LLM 호출

↓

응답 확인
```

을

Swagger에서

모두 테스트합니다.

OCR도

파일 업로드도

Embedding도

전부

Swagger에서

먼저 검증합니다.

이것이

실무 개발 방식입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Swagger(OpenAPI)**를 이용하여 FastAPI API를 테스트하는 방법을 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **OpenAPI**는 API를 설명하는 표준 문서 형식이다.
    
- **Swagger UI**는 OpenAPI 문서를 기반으로 API를 테스트할 수 있는 웹 인터페이스이다.
    
- FastAPI는 코드와 타입 힌트를 분석하여 **API 문서를 자동 생성**한다.
    
- `/docs`에서는 Swagger UI, `/redoc`에서는 ReDoc 형태의 문서를 확인할 수 있다.
    
- 실무에서는 **FastAPI 개발 → Swagger 검증 → React 연동** 순서로 작업하는 것이 일반적이다.
    

---

### Part 1 완료
여기까지가 **Part 1. FastAPI 이해 (Unit 1~8)** 입니다.

학생은 이제 다음 내용을 설명할 수 있어야 합니다.

- FastAPI가 왜 등장했는가?
    
- CGI → WSGI → ASGI의 발전 과정
    
- AI 서비스에서 FastAPI의 역할
    
- HTTP와 REST API의 관계
    
- Uvicorn과 ASGI의 동작 원리
    
- FastAPI 프로젝트 생성과 실행
    
- Swagger를 이용한 API 테스트
    

이제부터는 **Part 2. API 개발**로 들어갑니다.

다음 Unit부터는 실제로 GET, POST, Path Parameter, Query Parameter, Request Body, Pydantic 등을 사용하여 **AI 서비스에서 사용할 API를 하나씩 구현**하게 됩니다. 여기부터가 본격적인 FastAPI 개발의 시작입니다.

---

### Part 1 Architecture Review
#### 5분 복습
```text
사용자
→ HTTP 요청
→ Uvicorn(ASGI Server)
→ FastAPI 애플리케이션
→ Path Operation
→ HTTP 응답
```

- **따라 하기:** 첫 프로젝트를 실행하고 Swagger UI에서 요청한다.
- **부분 완성:** 비어 있는 `/health` Handler와 응답 모델을 완성한다.
- **독립 구현:** AI 질문을 받는 최소 Endpoint의 계약을 직접 설계한다.

#### 학생 질문
1. FastAPI와 Uvicorn은 각각 무슨 일을 하는가?
2. ASGI를 사용해도 비동기 이점을 얻지 못하는 경우는 언제인가?
3. Swagger UI와 자동화 테스트의 역할은 어떻게 다른가?

#### 확인 퀴즈
1. 외부 AI API를 기다리는 작업은 CPU 작업과 I/O 작업 중 어디에 가까운가?
2. `requirements.txt`만 같으면 운영체제와 Python 버전까지 동일해지는가?
3. GET 응답 내용은 항상 동일해야 멱등한가?

<details>
<summary>정답</summary>

1. I/O 작업에 가깝다.
2. 아니다. Python·OS·시스템 라이브러리 조건도 별도로 관리해야 한다.
3. 아니다. 멱등성은 서버에 미치는 의도된 효과를 기준으로 판단한다.

</details>

### Day 1-3. Request와 Response Pipeline

첫 FastAPI 애플리케이션과 Swagger를 실행했습니다. 이제 Route를 등록하고 Path·Query·Body 입력을 받은 뒤, Pydantic으로 검증하고 Response Model로 출력 계약을 정의합니다.

# Part 2. Request와 Response Pipeline

이 Part에서는 하나의 HTTP 요청이 FastAPI 내부에서 어떤 Python 값과 객체로 변환되고 다시 Response가 되는지 추적한다.

## Module 18. Routing과 Endpoint


### Module 실습 예제

- [예제 1: route_order.py](examples/module_18/route_order.py) — 고정 Path를 동적 Path보다 먼저 선언합니다.
- [예제 2: separate_features.py](examples/module_18/separate_features.py) — Chat과 Document Route를 URL 기준으로 분리합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 기능이 늘어날 때 URL과 Handler가 뒤섞이지 않게 한다.
- **오늘 만드는 것:** 질문·문서 기능의 Route를 구분한다.
- **AI 플랫폼의 위치:** 요청이 적절한 Router로 들어가는 첫 분기점이다.
- **실무에서 많이 하는 실수:** Route 선언 순서와 동적 Path 충돌을 무시한다.
- **5분 실습:** 고정 Path와 동적 Path가 충돌하는 예를 수정한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 자신의 언어로 답할 수 있어야 합니다.

- Routing이란 무엇인가?
    
- Endpoint란 무엇인가?
    
- URL은 어떻게 함수와 연결되는가?
    
- FastAPI는 요청을 어떻게 찾는가?
    
- 왜 Router가 필요한가?
    

---

### ① 문제 이해 (Why)
지난 Unit까지 우리는

FastAPI를 실행했고

첫 번째 API도 만들었습니다.

```python
@app.get("/")
def home():
    return {
        "message": "Hello FastAPI"
    }
```

그런데 여기서

한 가지 의문이 생깁니다.

---

브라우저에서

```
GET /
```

를 요청하면

왜

```python
home()
```

함수가 실행될까요?

우리는

직접

```python
home()
```

를 호출하지 않았습니다.

그런데도

실행됩니다.

누가 호출하는 걸까요?

---

정답은

FastAPI입니다.

---

### FastAPI는 길 안내 프로그램이다
FastAPI를

네비게이션으로 생각해 봅시다.

예를 들어

택배가 왔습니다.

주소는

```text
서울

강남구

테헤란로
```

입니다.

네비게이션은

주소를 보고

목적지를 찾아갑니다.

---

FastAPI도 같습니다.

사용자가

```
GET /chat
```

를 요청하면

FastAPI는

```text
@app.get("/chat")
```

를 찾습니다.

즉

URL을 보고

실행할 함수를 찾습니다.

---

이 과정을

**Routing**

이라고 합니다.

---

### Routing이란?
Routing은

말 그대로

길(Route)을 찾는 것입니다.

웹에서는

조금 다르게 사용합니다.

> **URL을 어떤 함수와 연결할 것인지 결정하는 과정**

입니다.

---

예를 들어

```text
@app.get("/")
def home():
```

은

```
"/"

↓

home()
```

를 연결합니다.

---

```text
@app.get("/chat")
def chat():
```

은

```
"/chat"

↓

chat()
```

를 연결합니다.

---

즉

FastAPI 안에는

이런 표가 있습니다.

```text
URL

↓

실행 함수
```

---

조금 더 자세히 보면

```text
/

↓

home()

----------------

/chat

↓

chat()

----------------

/upload

↓

upload()
```

이런 연결 정보가

저장됩니다.

---

### Endpoint란 무엇인가?
학생들이

가장 많이 헷갈리는 용어입니다.

Routing과

Endpoint는

같은 것이 아닙니다.

---

Routing은

**길을 찾는 과정**입니다.

Endpoint는

**도착 지점**입니다.

---

예를 들어

```
GET /chat
```

은

하나의 Endpoint입니다.

```
POST /upload
```

도

하나의 Endpoint입니다.

---

즉

Endpoint는

사용자가 접근할 수 있는

API 하나를 의미합니다.

---

쉽게 말하면

```
GET /documents
```

↓

문서 목록 API

---

```
POST /documents
```

↓

문서 생성 API

---

둘 다

Endpoint입니다.

---

### Endpoint는 URL만 의미하지 않는다
여기서

많은 초보 개발자가

실수합니다.

```
/documents
```

만

Endpoint라고 생각합니다.

사실은

아닙니다.

---

HTTP Method도

같이 포함됩니다.

예를 들어

```
GET /documents
```

와

```
POST /documents
```

는

URL은 같습니다.

하지만

완전히 다른 Endpoint입니다.

---

즉

Endpoint는

```
HTTP Method

+

URL
```

의 조합입니다.

---

### FastAPI는 Routing Table을 만든다
우리가

코드를 작성하면

FastAPI는

내부적으로

Routing Table을 만듭니다.

예를 들어

```python
@app.get("/")
def home():
    ...

@app.get("/chat")
def chat():
    ...

@app.post("/upload")
def upload():
    ...
```

FastAPI 내부에서는

대략

다음과 같은 정보를

가지게 됩니다.

```text
GET /

↓

home()

----------------

GET /chat

↓

chat()

----------------

POST /upload

↓

upload()
```

이것을

Routing Table이라고 합니다.

---

### 요청은 어떻게 함수를 찾을까?
예를 들어

브라우저에서

```
GET /chat
```

이 들어옵니다.

그러면

FastAPI는

Routing Table을

검색합니다.

```text
GET /chat

↓

검색

↓

chat()

↓

실행
```

이것이

Routing입니다.

---

### 존재하지 않는 URL이면?
예를 들어

우리의 코드에는

```text
@app.get("/chat")
```

만 있습니다.

그런데

브라우저가

```
GET /hello
```

를 요청합니다.

Routing Table에는

없습니다.

그러면

FastAPI는

자동으로

```
404 Not Found
```

를 반환합니다.

즉

개발자가

404를

직접 만들 필요가 없습니다.

---

### Routing을 그림으로 이해하기
```text
Browser

↓

GET /chat

↓

Routing Table

↓

chat()

↓

JSON

↓

Browser
```

아주 단순합니다.

---

### 왜 Decorator를 사용할까?
학생들이

많이 묻습니다.

```text
@app.get("/chat")
```

이게

왜 필요한가요?

---

Decorator의 역할은

API를

등록하는 것입니다.

예를 들어

```text
@app.get("/chat")
def chat():
```

를 실행하면

FastAPI는

```
GET /chat

↓

chat()
```

를

Routing Table에

등록합니다.

---

즉

Decorator가 없다면

FastAPI는

이 함수가

API인지

알 수 없습니다.

---

### 하나의 함수가 여러 Endpoint를 가질 수도 있을까?
가능합니다.

예를 들어

```python
@app.get("/")
@app.get("/home")
def home():
    return {"message": "Home"}
```

그러면

두 개의 URL이

같은 함수를 호출합니다.

```
GET /

↓

home()

----------------

GET /home

↓

home()
```

실무에서도

가끔 사용하는 방법입니다.

---

### 하나의 URL에 여러 Method를 사용할 수도 있을까?
당연히 가능합니다.

예를 들어

```
/documents
```

는

조회도 해야 하고

생성도 해야 합니다.

그래서

```text
@app.get("/documents")
```

과

```text
@app.post("/documents")
```

를

동시에 사용할 수 있습니다.

FastAPI는

Method까지

함께 확인합니다.

---

### AI 서비스에서는 Routing이 더 많아진다
앞으로 만들

AI 플랫폼에서는

API가

매우 많아집니다.

예를 들어

```text
/chat

/chat/stream

/upload

/documents

/documents/{id}

/ocr

/embedding

/vector

/rag

/agent
```

등

수십 개의 Endpoint가

생깁니다.

---

그래서

Routing이

굉장히 중요합니다.

---

### 지금은 app에 모두 등록하고 있다
현재는

```python
app = FastAPI()
```

에

모든 API를

등록하고 있습니다.

```text
@app.get("/")
@app.get("/chat")
@app.post("/upload")
```

하지만

API가

100개가 되면

어떻게 될까요?

---

`main.py`가

수천 줄이 됩니다.

관리하기가

매우 어렵습니다.

---

그래서

다음 Unit부터 배우는

APIRouter가

등장합니다.

---

### 학생들이 자주 하는 실수
##### 실수 1
같은 Method와 같은 URL을

두 번 작성합니다.

```python
@app.get("/chat")
def chat1():
    ...

@app.get("/chat")
def chat2():
    ...
```

이렇게 작성하면

충돌이 발생합니다.

---

##### 실수 2
URL 앞의 `/`를

빼먹습니다.

```text
@app.get("chat")
```

보다는

```text
@app.get("/chat")
```

를 사용해야 합니다.

---

##### 실수 3
URL 이름을

동사로 만듭니다.

예를 들어

```
/getUser

/createUser

/deleteUser
```

처럼 작성합니다.

REST에서는

이렇게 작성하지 않습니다.

보통

```
/users
```

를 만들고

Method로

행동을 구분합니다.

---

### 지금까지의 구조
현재 우리의 Backend는

다음과 같이 동작합니다.

```text
Browser

↓

GET /chat

↓

Uvicorn

↓

FastAPI

↓

Routing Table

↓

chat()

↓

JSON

↓

Browser
```

앞으로 API가 수십 개가 되더라도

핵심 흐름은 변하지 않습니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Routing과 Endpoint**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Routing**은 URL과 HTTP Method를 분석하여 실행할 함수를 찾는 과정이다.
    
- **Endpoint**는 `HTTP Method + URL`의 조합으로 정의되는 하나의 API이다.
    
- `@app.get()`, `@app.post()` 같은 Decorator는 Endpoint를 Routing Table에 등록하는 역할을 한다.
    
- FastAPI는 요청이 들어오면 Routing Table을 검색하여 해당 함수를 자동으로 실행한다.
    
- API가 많아질수록 `main.py` 하나로 관리하기 어려워지므로 이후 **APIRouter**를 사용하여 구조를 분리하게 된다.
    

---

## Module 19. GET 요청


### Module 실습 예제

- [예제 1: get_documents.py](examples/module_19/get_documents.py) — GET으로 문서 목록을 조회합니다.
- [예제 2: get_model_status.py](examples/module_19/get_model_status.py) — GET으로 AI Provider 상태를 표현합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 조회 API가 서버 상태를 바꾸지 않도록 계약을 세운다.
- **오늘 만드는 것:** 질문 또는 작업 상태 조회 Endpoint를 만든다.
- **AI 플랫폼의 위치:** AI 작업 결과와 상태를 읽는 진입점이다.
- **실무에서 많이 하는 실수:** GET 요청에서 DB를 갱신하거나 캐시 가능성을 무조건 보장한다.
- **5분 실습:** 작업 조회 API의 성공·없음 응답을 설계한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- GET은 무엇인가?
    
- GET은 언제 사용하는가?
    
- 왜 조회에는 GET을 사용하는가?
    
- FastAPI에서 GET API는 어떻게 만드는가?
    
- AI 서비스에서는 GET을 어디에 사용하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

Routing을 배웠습니다.

이제

실제 API를 하나씩 만들어 보겠습니다.

첫 번째는

가장 많이 사용하는

GET입니다.

---

학생들에게 질문을 하나 해보겠습니다.

문서 관리 서비스가 있습니다.

사용자가

문서 목록을 보고 싶습니다.

여러분이라면

어떤 API를 만들겠습니까?

많은 초보 개발자는

이렇게 작성합니다.

```text
POST /documents
```

혹은

```text
POST /list
```

하지만

실무에서는

이렇게 하지 않습니다.

---

### 조회와 변경은 다르다
예를 들어

은행 창구가 있습니다.

통장 잔액을 조회합니다.

```text
잔액 조회
```

은행의 돈은

변했습니까?

아닙니다.

---

이번에는

입금을 합니다.

```text
10만원 입금
```

은행 데이터가

변했습니다.

---

조회와

변경은

완전히 다른 행동입니다.

그래서

HTTP도

둘을 구분합니다.

---

### GET은 조회이다
GET은

데이터를 가져오는 요청입니다.

가장 중요한 특징은

> **데이터를 변경하지 않는다.**

입니다.

예를 들어

```text
GET /documents
```

는

문서를 읽기만 합니다.

삭제하지 않습니다.

수정하지 않습니다.

생성하지 않습니다.

---

### 실무에서 GET을 사용하는 경우
AI 서비스에서는

GET을

굉장히 많이 사용합니다.

예를 들어

```text
GET /documents
```

↓

문서 목록 조회

---

```text
GET /documents/10
```

↓

10번 문서 조회

---

```text
GET /models
```

↓

사용 가능한 AI 모델 조회

---

```text
GET /health
```

↓

서버 상태 확인

---

```text
GET /version
```

↓

현재 서버 버전 확인

---

모두

조회입니다.

---

### GET은 왜 중요한가?
학생들은

GET를

"조회"

정도로만 기억합니다.

하지만

REST에서는

더 중요한 의미가 있습니다.

바로

**Safe Method**

입니다.

---

### Safe Method란?
Safe는

안전하다는 뜻입니다.

즉

몇 번을 호출해도

데이터가

변하지 않습니다.

예를 들어

```text
GET /documents
```

를

100번 호출해도

문서는

100개 늘어나지 않습니다.

삭제되지도 않습니다.

---

즉

조회만 합니다.

---

### Idempotent(멱등성)
실무에서는

Safe와 함께

멱등성(Idempotency)이라는 개념도 많이 등장합니다.

조금 어려운 용어이지만

의미는 간단합니다.

> **같은 요청을 여러 번 보내도 서버에 미치는 의도된 효과는 한 번 보낸 것과 같아야 한다.**

예를 들어

```text
GET /documents
```

를

1번 호출하든 10번 호출하든 조회 요청 자체가 서버 데이터를 추가로 생성하거나 변경해서는 안 됩니다.

다른 사용자가 문서를 추가했다면 각 GET 응답의 목록은 달라질 수 있습니다. 멱등성은 **응답 내용이 항상 같다**는 뜻이 아니라 **반복 요청의 의도된 효과가 같다**는 뜻입니다.

---

GET 응답은 HTTP 캐시의 대상이 될 수 있지만, 실제 저장과 재사용 여부는 `Cache-Control`, 인증, 응답 헤더, 프록시와 CDN 정책에 따라 달라집니다. GET이라고 항상 캐시되거나 빠른 것은 아닙니다.

---

### 첫 번째 GET API 만들기
이번에는

조금 더 실무처럼 만들어 봅시다.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "AIKOS Backend Server"
    }


@app.get("/health")
def health_check():
    return {
        "status": "OK"
    }
```

---

### 코드 분석
첫 번째 API입니다.

```text
@app.get("/")
```

Backend의

메인 페이지입니다.

---

두 번째 API입니다.

```text
@app.get("/health")
```

이 API는

실무에서

정말 많이 사용합니다.

---

### Health Check란?
학생들이

처음 듣는 용어입니다.

Health Check는

서버가

살아있는지 확인하는 API입니다.

예를 들어

React가

Backend를 호출하기 전에

```text
GET /health
```

를 호출합니다.

응답이

```json
{
    "status": "OK"
}
```

라면

Backend가

정상이라는 뜻입니다.

---

AWS

Docker

Kubernetes

모두

이 Health Check API를

사용합니다.

즉,

AI 서비스에서도

반드시 필요한 API입니다.

---

### Browser에서 실행해보기
브라우저에서

```
http://localhost:8000/health
```

를 입력합니다.

그러면

브라우저는

```http
GET /health
```

를 보냅니다.

---

FastAPI는

Routing Table을 검색합니다.

```text
GET /health

↓

health_check()
```

를 찾습니다.

---

함수를 실행합니다.

```python
return {
    "status": "OK"
}
```

---

FastAPI는

자동으로 JSON으로 변환합니다.

```json
{
    "status": "OK"
}
```

---

Browser에게

Response를 보냅니다.

---

### Swagger에서도 확인하기
`/docs`에 접속하면

```
GET /

GET /health
```

두 개의 Endpoint가

생깁니다.

Execute를 누르면

실제로

Request와 Response를

확인할 수 있습니다.

---

### AI 서비스에서는 GET을 어디에 사용할까?
우리가 앞으로 만들 플랫폼에서는

GET API가

굉장히 많습니다.

예를 들어

```text
GET /documents

↓

문서 목록
```

---

```text
GET /chat/history

↓

채팅 목록
```

---

```text
GET /models

↓

사용 가능한 LLM
```

---

```text
GET /prompts

↓

프롬프트 목록
```

---

```text
GET /settings

↓

환경설정 조회
```

---

즉

**조회하는 모든 기능은 GET부터 시작**한다고 생각하면 됩니다.

---

### AIKOS 실무 Best Practice
여기서부터는 실무에서 많이 사용하는 규칙을 함께 익혀야 합니다.

#### 1. URL에는 동사를 쓰지 않는다.
좋지 않은 예

```text
/getDocuments
```

좋은 예

```text
/documents
```

조회인지 생성인지는

Method가 결정합니다.

---

#### 2. Health Check API는 항상 만든다.
거의 모든 Backend에는

```text
GET /health
```

가 존재합니다.

나중에

Docker,

Nginx,

Kubernetes에서도

계속 사용합니다.

---

#### 3. GET에서는 데이터를 변경하지 않는다.
절대

```text
GET /delete-user
```

같은 API는

만들지 않습니다.

이 규칙은

REST의 가장 중요한 원칙 중 하나입니다.

---

### 이번 Unit에서 미리 알아둘 내용
다음 Unit에서는

이 API를

조금 더 발전시킵니다.

예를 들어

```text
GET /documents/10
```

에서

`10`은

어떻게 가져올까요?

바로

**Path Parameter**입니다.

즉

다음 Unit은

GET의 확장이라고

생각하면 됩니다.

---

### 핵심 내용 정리
이번 Unit에서는 GET 요청의 의미와 활용을 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **GET은 데이터를 조회하는 HTTP Method**이다.
    
- GET은 **Safe Method**이며 데이터를 변경하지 않는다.
    
- 같은 GET 요청을 여러 번 보내도 의미가 변하지 않는 **멱등성(Idempotency)** 특성을 가진다.
    
- FastAPI에서는 `@app.get()`을 사용하여 조회 API를 정의한다.
    
- AI 서비스에서는 문서 조회, 채팅 기록 조회, 모델 목록 조회, Health Check 등 대부분의 조회 기능에 GET을 사용한다.
    

---

### AIKOS FastAPI (업그레이드)
각 Unit은 아래 순서로 진행합니다.

```
Why
↓

REST 설계 철학

↓

Concept

↓

Architecture

↓

Implementation

↓

실행 과정

↓

실무 Best Practice

↓

AI Service 적용

↓

자주 하는 실수

↓

Summary
```

이렇게 하면

FastAPI 문법을 배우는 것이 아니라

Backend를 설계하는 능력이 생깁니다.

---

## Module 20. Path Parameter


### Module 실습 예제

- [예제 1: path_document.py](examples/module_20/path_document.py) — Path Parameter로 단일 리소스를 식별합니다.
- [예제 2: path_validation.py](examples/module_20/path_validation.py) — Path에 숫자 범위 제약을 적용합니다.



#### 프로젝트 연결 학습
- **문제 상황:** URL 안의 식별자를 안전하게 받아 특정 자원을 찾는다.
- **오늘 만드는 것:** document_id 또는 job_id Path Parameter를 검증한다.
- **AI 플랫폼의 위치:** 문서·AI 작업 하나를 지정하는 주소 역할을 한다.
- **실무에서 많이 하는 실수:** 타입 검증만 믿고 존재 여부와 권한 검사를 생략한다.
- **5분 실습:** 존재하지 않는 ID와 잘못된 형식의 ID를 각각 처리한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Path Parameter는 무엇인가?
    
- 왜 Path Parameter가 필요한가?
    
- Query Parameter와 어떤 차이가 있는가?
    
- REST에서는 언제 Path Parameter를 사용하는가?
    
- AI 서비스에서는 어디에 사용하는가?
    

---

### ① 문제 이해 (Why)
문서 관리 시스템이 있습니다.

문서가

100개 있습니다.

사용자가

15번 문서를 열고 싶습니다.

여러분이라면

API를 어떻게 만들겠습니까?

초보 개발자는

보통

```
GET /document15
```

처럼 만듭니다.

또는

```
GET /getDocument15
```

처럼 작성합니다.

하지만

이 방식은

실무에서는 사용하지 않습니다.

---

왜일까요?

---

문서가

100개가 아니라

100만 개라면?

```
/document1

/document2

/document3

...

/document1000000
```

를

모두 만들어야 합니다.

불가능합니다.

---

그러면

URL 안에서

숫자만 바꿀 수 있으면 되지 않을까요?

바로

그것이

Path Parameter입니다.

---

### REST 설계 철학
REST에는

아주 중요한 원칙이 있습니다.

> **URL은 Resource를 표현한다.**

행동(Action)은

Method가 표현합니다.

---

예를 들어

```
/documents
```

는

문서들의 집합(Collection)입니다.

---

```
/documents/10
```

은

10번 문서 하나입니다.

---

즉

```
/documents
```

↓

Collection

---

```
/documents/{id}
```

↓

Single Resource

---

REST에서는

이 구조를

매우 중요하게 생각합니다.

---

### Concept
Path Parameter는

URL의 일부를

변수처럼 사용하는 것입니다.

예를 들어

```
/documents/{id}
```

에서

```
{id}
```

가

Path Parameter입니다.

---

실제로 요청하면

```
GET /documents/15
```

↓

```
id = 15
```

가 됩니다.

---

### FastAPI 구현
FastAPI에서는

아주 간단합니다.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/documents/{document_id}")
def get_document(document_id: int):
    return {
        "document_id": document_id
    }
```

---

학생들이

여기서 가장 놀라는 부분은

바로

```
document_id: int
```

입니다.

---

URL인데

왜

함수의 매개변수(Parameter)가

자동으로 채워질까요?

---

### 내부 동작 원리
사용자가

```
GET /documents/25
```

를 요청합니다.

FastAPI는

먼저

Routing Table을 검색합니다.

```
GET

/documents/{document_id}
```

를 찾습니다.

---

그리고

URL을

분석합니다.

```
/documents/25
```

↓

```
document_id

↓

25
```

를

추출합니다.

---

그리고

함수를 호출합니다.

```
get_document(25)
```

즉

우리가 호출하는 것이 아니라

FastAPI가

자동으로

함수를 호출합니다.

---

### 내부 동작 과정
```text
Browser

↓

GET /documents/25

↓

Uvicorn

↓

FastAPI

↓

Routing

↓

Path Parsing

↓

document_id = 25

↓

get_document(25)

↓

JSON

↓

Browser
```

---

### Type Hint의 역할
우리는

이렇게 작성했습니다.

```python
document_id: int
```

그러면

FastAPI는

자동으로

문자열을

정수로 변환합니다.

---

예를 들어

```
GET /documents/100
```

↓

```
document_id

↓

100 (int)
```

---

반대로

```
GET /documents/hello
```

를

호출하면?

FastAPI는

자동으로

오류를 반환합니다.

```json
{
    "detail": [
        ...
    ]
}
```

우리는

검사 코드를

작성하지 않았습니다.

FastAPI가

자동으로

Validation을 수행합니다.

---

### 왜 이것이 중요한가?
Flask에서는

보통

```python
id = int(request.args["id"])
```

같은 코드를

직접 작성하는 경우가 많았습니다.

FastAPI는

Type Hint 하나로

자동 처리합니다.

이것이

FastAPI 생산성이 높은 이유 중 하나입니다.

---

### AI 서비스에서는 언제 사용할까?
앞으로 만들

생성형 AI 플랫폼을

생각해봅시다.

예를 들어

문서를 조회합니다.

```
GET /documents/15
```

↓

15번 문서 조회

---

채팅 하나를 조회합니다.

```
GET /chats/8
```

↓

8번 대화 조회

---

OCR 결과를 조회합니다.

```
GET /ocr/21
```

↓

21번 OCR 결과

---

프롬프트를 조회합니다.

```
GET /prompts/5
```

↓

5번 Prompt

---

즉

**하나의 객체(Resource)를 조회할 때는 대부분 Path Parameter를 사용합니다.**

---

### Query Parameter와의 차이
학생들이

가장 많이 헷갈리는 부분입니다.

예를 들어

```
GET /documents/15
```

와

```
GET /documents?id=15
```

둘 다

가능해 보입니다.

하지만

REST에서는

의미가 다릅니다.

---

```
/documents/15
```

↓

15번 문서

---

```
/documents?page=2
```

↓

문서 목록

2페이지

---

즉

Path는

**대상(Resource)**

Query는

**조건(Condition)**

입니다.

이 차이는

매우 중요합니다.

다음 Unit에서

더 자세히 다룹니다.

---

### 실무 Best Practice
#### 좋은 설계
```
GET /documents/15
```

---

나쁜 설계

```
GET /getDocument?id=15
```

---

좋은 설계

```
GET /users/20
```

---

나쁜 설계

```
GET /findUser?id=20
```

---

REST에서는

URL이

리소스를 표현해야 합니다.

행동은

Method가 표현합니다.

---

### 학생들이 자주 하는 실수
##### ① URL 변수 이름과 함수 매개변수 이름이 다르다.
```text
@app.get("/documents/{id}")
def get_document(document_id: int):
```

이렇게 작성하면

FastAPI는

값을 전달할 수 없습니다.

반드시

같아야 합니다.

```text
@app.get("/documents/{document_id}")
def get_document(document_id: int):
```

---

##### ② 문자열로 받는다.
```python
document_id: str
```

로 작성해 놓고

나중에

직접 int()를 사용합니다.

FastAPI에서는

처음부터

올바른 타입을

작성하는 것이 좋습니다.

---

##### ③ Query와 Path를 혼동한다.
```
/documents?id=10
```

보다

```
/documents/10
```

이

REST 설계에 맞습니다.

---

### AIKOS 실무 설계 원칙
여기서부터는 하나의 원칙을 기억하면 됩니다.

```
Collection

↓

/documents
```

---

```
Single Resource

↓

/documents/{id}
```

---

```
Collection Filtering

↓

/documents?page=1

/documents?author=kim

/documents?status=completed
```

이 원칙은

FastAPI뿐 아니라

Spring,

ASP.NET,

Node.js,

Go,

Django,

Flask

모든 REST API에서 동일하게 사용됩니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Path Parameter**를 단순한 문법이 아니라 **REST 설계 원칙**과 함께 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Path Parameter는 URL의 일부를 변수처럼 사용하는 기능**이다.
    
- 하나의 리소스를 식별할 때는 `/{id}` 형태의 **Path Parameter를 사용하는 것이 REST 원칙**이다.
    
- FastAPI는 URL 값을 자동으로 함수 매개변수에 전달하고, Type Hint를 이용해 자동 변환과 Validation까지 수행한다.
    
- Path는 **리소스(Resource)** 를 나타내고, Query는 **조건(Condition)** 을 나타낸다.
    
- AI 서비스에서는 문서, 채팅, OCR 결과, 프롬프트 등 **개별 객체를 조회할 때 Path Parameter를 사용**한다.
    

---

이제 다음 **Unit 12**에서는 학생들이 가장 많이 혼동하는 **Query Parameter**를 배우면서,

- Path vs Query
    
- Resource vs Filter
    
- REST 설계 원칙
    

을 한 번에 연결하여 설명하겠습니다. 이 부분을 이해하면 API 설계 수준이 한 단계 올라가게 됩니다.

---

## Module 21. Query Parameter


### Module 실습 예제

- [예제 1: query_filter.py](examples/module_21/query_filter.py) — Query Parameter로 상태와 개수를 필터링합니다.
- [예제 2: pagination.py](examples/module_21/pagination.py) — offset과 limit으로 간단한 Pagination을 구현합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 검색·필터·페이지네이션 조건을 URL에 표현한다.
- **오늘 만드는 것:** 작업 목록의 status·limit·offset Query Parameter를 만든다.
- **AI 플랫폼의 위치:** AI 작업 목록과 운영 조회 기능에 사용한다.
- **실무에서 많이 하는 실수:** 필수값·기본값·범위를 모호하게 둔다.
- **5분 실습:** limit 범위를 제한하고 잘못된 값을 테스트한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Query Parameter란 무엇인가?
    
- Path Parameter와 무엇이 다른가?
    
- 언제 Query를 사용하는가?
    
- 검색과 조회는 어떻게 설계하는가?
    
- AI 서비스에서는 어디에 사용하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

문서 하나를 조회했습니다.

```text
GET /documents/15
```

여기서

15번 문서를 가져왔습니다.

이번에는

조금 다른 상황입니다.

사용자가

문서를 검색합니다.

예를 들어

```
작성자가 Kim인 문서만 보여주세요.
```

이 API는

어떻게 만들까요?

학생들은

보통 두 가지를 생각합니다.

```text
/documents/kim
```

또는

```text
/documents?author=kim
```

둘 중 어느 것이 맞을까요?

---

### 먼저 Resource를 생각하자
REST에서는

항상

먼저

Resource를 생각합니다.

이번에도

Resource는

문서입니다.

```text
documents
```

입니다.

---

그런데

이번에는

문서 하나가 아니라

조건이 있습니다.

```
작성자 = Kim
```

---

즉

우리는

문서를 지정하는 것이 아니라

문서를

검색하는 것입니다.

---

여기서

Query Parameter가 등장합니다.

---

### REST 설계 철학
Path는

Resource를

가리킵니다.

Query는

Resource를

필터링합니다.

이것이

REST에서

가장 중요한 원칙입니다.

---

예를 들어

```text
/documents/15
```

↓

15번 문서

---

```text
/documents?page=2
```

↓

문서 목록

2페이지

---

```text
/documents?author=kim
```

↓

Kim의 문서 목록

---

```text
/documents?category=AI
```

↓

AI 문서 목록

---

즉

Query는

조건입니다.

---

### Path와 Query를 그림으로 보면
```text
               documents

                  │

      ┌───────────┴────────────┐

      ▼                        ▼

/documents/15          /documents?page=2

      │                        │

특정 문서              문서 목록 조건
```

---

학생들이

여기서

많이 헷갈립니다.

---

### Path는 "누구"
Query는 "어떻게"

사람으로 비유하면

굉장히 쉽습니다.

---

Path는

누구를

찾을 것인가입니다.

```text
/users/20
```

↓

20번 사용자

---

Query는

어떤 조건인가입니다.

```text
/users?age=30
```

↓

30세 사용자

---

즉

```text
Path

↓

대상

(Resource)

----------------------

Query

↓

조건

(Filter)
```

---

### FastAPI 구현
FastAPI에서는

Query Parameter는

아주 자연스럽게 처리됩니다.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/documents")
def get_documents(page: int = 1):
    return {
        "page": page
    }
```

학생들은

놀랍니다.

```
Decorator에는

page가 없는데요?
```

맞습니다.

---

FastAPI는

함수의

매개변수를

자동으로 분석합니다.

---

### 실행 과정
사용자가

```text
GET /documents?page=3
```

를 요청합니다.

FastAPI는

URL을

분석합니다.

```text
page

↓

3
```

그리고

함수를

호출합니다.

```python
get_documents(3)
```

즉

Path Parameter와

거의 같습니다.

---

### Query가 없으면?
이번에는

```text
GET /documents
```

를 호출합니다.

Query가 없습니다.

그러면

```python
page = 1
```

이 됩니다.

왜냐하면

```python
page: int = 1
```

이라고

기본값(Default Value)을

주었기 때문입니다.

---

### Query Parameter는 여러 개 사용할 수 있다
예를 들어

문서 검색입니다.

```python
@app.get("/documents")
def get_documents(
    page: int = 1,
    size: int = 20,
    author: str = "",
):
    ...
```

그러면

다음과 같이 사용할 수 있습니다.

```text
/documents

?page=2

&size=50

&author=kim
```

FastAPI는

자동으로

모든 값을

매개변수에 넣어줍니다.

---

### AI 서비스에서는 어디에 사용할까?
생성형 AI 플랫폼에서는

Query Parameter가

엄청나게 많이 사용됩니다.

예를 들어

문서 목록

```text
GET /documents

?page=1

&size=20
```

---

검색

```text
GET /documents

?keyword=AI
```

---

작성자 검색

```text
GET /documents

?author=kim
```

---

상태 검색

```text
GET /documents

?status=completed
```

---

날짜 검색

```text
GET /documents

?from=2026-01-01

&to=2026-01-31
```

---

모두

Query입니다.

---

### Path와 Query를 함께 사용할 수도 있다
예를 들어

문서 하나를

조회합니다.

그런데

출력 형식을

선택합니다.

```text
GET

/documents/15

?format=markdown
```

여기서

```text
15
```

는

Path입니다.

---

```text
format
```

은

Query입니다.

---

즉

둘은

같이 사용할 수도 있습니다.

---

### 내부 동작
```text
GET

/documents/15

?format=markdown

↓

Path

↓

15

↓

document_id

--------------------

Query

↓

markdown

↓

format
```

FastAPI는

둘을

자동으로

구분합니다.

---

### Path와 Query 비교
|항목|Path Parameter|Query Parameter|
|---|---|---|
|의미|리소스 식별|조건(Filter)|
|REST 역할|대상(Resource)|검색/정렬/페이지|
|필수 여부|대부분 필수|대부분 선택|
|예시|`/documents/15`|`?page=2`|
|AI 서비스 예|문서 조회|문서 검색|

이 표는 앞으로 REST API를 설계할 때 계속 기준이 됩니다.

---

### 실무 Best Practice
#### 페이지네이션은 Query를 사용한다
좋은 예

```text
/documents?page=3
```

나쁜 예

```text
/documents/page/3
```

---

#### 검색도 Query를 사용한다
좋은 예

```text
/documents?keyword=AI
```

---

나쁜 예

```text
/searchAI
```

---

#### 정렬도 Query를 사용한다
```text
/documents

?sort=name

&order=asc
```

실무에서는

거의 모두

이렇게 작성합니다.

---

### 학생들이 가장 많이 하는 실수
##### 실수 ①
검색인데

Path를 사용한다.

```text
/kim
```

보다는

```text
?author=kim
```

이 맞습니다.

---

##### 실수 ②
페이지 번호를

Path로 만든다.

```text
/documents/page/3
```

보다

```text
/documents?page=3
```

가 REST에 맞습니다.

---

##### 실수 ③
Query를

필수 데이터로 사용한다.

예를 들어

회원 ID는

```text
/users?id=20
```

보다

```text
/users/20
```

이 적절합니다.

---

### AIKOS 실무 설계 원칙
API를 설계할 때

항상

다음 순서로 생각합니다.

```
① 내가 접근하려는 것은

하나의 Resource인가?

↓

YES

↓

Path Parameter

------------------------

NO

↓

목록인가?

↓

YES

↓

Query Parameter
```

이 사고방식만 익혀도

REST API 설계 수준이

상당히 높아집니다.

---

### AI 서비스 설계 예제
문서 플랫폼을 예로 들어보겠습니다.

```
GET /documents
```

↓

문서 목록

---

```
GET /documents/15
```

↓

15번 문서

---

```
GET /documents?page=2
```

↓

2페이지

---

```
GET /documents?author=kim
```

↓

Kim의 문서

---

```
GET /documents/15?format=markdown
```

↓

15번 문서를

Markdown으로 출력

이처럼 **Path는 "무엇을", Query는 "어떻게"**를 표현한다고 기억하면 설계가 훨씬 쉬워집니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Query Parameter를 REST 설계 관점**에서 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Path Parameter는 리소스를 식별**할 때 사용한다.
    
- **Query Parameter는 리소스를 검색, 필터링, 정렬, 페이지네이션**할 때 사용한다.
    
- FastAPI는 함수의 매개변수를 분석하여 Query Parameter를 자동으로 매핑한다.
    
- Path와 Query는 함께 사용할 수 있으며, 각각의 역할을 명확히 구분하는 것이 좋은 REST API 설계의 핵심이다.
    
- AI 서비스에서는 문서 검색, 채팅 목록 조회, 모델 목록 조회, 페이지네이션 등 대부분의 목록 조회 기능에 Query Parameter를 사용한다.
    

---

#### 학습 흐름 정리
여기까지 오면서 FastAPI 강의의 방향이 기존 튜토리얼과는 달라졌습니다.

기존 강의는 **"문법"**을 설명하지만, AIKOS에서는 **"설계 사고"**를 먼저 가르칩니다.

이 방식을 계속 유지하면 학생들은 FastAPI 문법을 외우는 것이 아니라, **Spring, ASP.NET, NestJS, Go 등 어떤 백엔드 프레임워크를 만나도 통하는 REST API 설계 능력**을 갖추게 됩니다.

다음 **Unit 13 (POST 요청)**부터는 이 설계 원칙을 바탕으로 **데이터 생성(Create)** 을 다루며, GET과 POST의 차이, Request Body가 필요한 이유까지 자연스럽게 이어가겠습니다.

---

여기서부터는 FastAPI 강의의 난이도를 **실무 Backend 설계 수준**으로 올리겠습니다.

GET과 Query를 이해했다면 이제 학생들이 가장 많이 실수하는 부분이 등장합니다.

바로

> **"언제 GET을 쓰고 언제 POST를 쓰는가?"**

입니다.

놀랍게도 실무에서도 REST API를 잘 모르는 개발자는

```text
POST /getDocuments
```

같은 API를 많이 만듭니다.

그래서 이번 Unit에서는 **문법보다 HTTP 설계 철학**부터 설명하겠습니다.

---

## Module 22. POST 요청


### Module 실습 예제

- [예제 1: post_job.py](examples/module_22/post_job.py) — POST로 새로운 AI 작업을 접수합니다.
- [예제 2: post_status_codes.py](examples/module_22/post_status_codes.py) — 201과 202 응답의 용도를 비교합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 새 자원을 만드는 요청과 응답 계약을 정의한다.
- **오늘 만드는 것:** AI 질문 또는 문서 생성 POST Endpoint를 만든다.
- **AI 플랫폼의 위치:** 사용자 입력이 플랫폼 내부 작업으로 바뀌는 시작점이다.
- **실무에서 많이 하는 실수:** 생성 성공에 무조건 200을 쓰거나 중복 요청을 고려하지 않는다.
- **5분 실습:** 201 또는 202 중 어떤 상태 코드가 맞는지 선택해 설명한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- POST는 무엇인가?
    
- GET과 무엇이 다른가?
    
- 왜 POST가 필요한가?
    
- 언제 POST를 사용해야 하는가?
    
- AI 서비스에서는 어디에 사용하는가?
    

---

### ① 문제 이해 (Why)
지금까지는

조회만 했습니다.

```text
GET /documents

GET /users

GET /health
```

모두

읽기(Read)입니다.

---

이번에는

새로운 문서를 등록합니다.

사용자가

```text
새 문서 업로드
```

버튼을 눌렀습니다.

그러면

GET으로 만들까요?

---

많은 초보 개발자가

처음에는

이렇게 생각합니다.

```text
GET /upload
```

하지만

이것은

REST에서는 잘못된 설계입니다.

---

왜일까요?

---

### 조회와 생성은 완전히 다른 행동이다
은행을 생각해 봅시다.

잔액 조회

```text
조회
```

돈은

변하지 않습니다.

---

이번에는

입금을 합니다.

```text
+100,000원
```

은행 DB가

변했습니다.

---

즉

조회는

읽기입니다.

입금은

생성 또는 변경입니다.

---

HTTP도

이 둘을

구분합니다.

---

### POST는 "새로운 데이터를 만든다"
POST는

가장 중요한 특징이 있습니다.

> **Server의 상태를 변경한다.**

---

예를 들어

```text
POST /documents
```

↓

새 문서 생성

---

```text
POST /users
```

↓

회원 가입

---

```text
POST /chat
```

↓

새 채팅 생성

---

모두

Server 데이터가

변합니다.

---

### GET과 POST 비교
GET은

```text
읽기
```

POST는

```text
쓰기
```

입니다.

---

조금 더 정확하게 보면

|GET|POST|
|---|---|
|조회|생성|
|Server 변경 없음|Server 변경|
|Safe|Not Safe|
|Cache 가능|일반적으로 Cache 안 함|

이 차이는

매우 중요합니다.

---

### 왜 POST가 필요한가?
학생들에게

질문을 하나 해봅시다.

문서를 생성하려면

이 정보가 필요합니다.

```text
제목

작성자

내용

카테고리
```

이 데이터를

어디에 넣을까요?

URL일까요?

---

예를 들어

```text
/documents/MyTitle/Kim/AI/...
```

가능은 합니다.

하지만

매우 이상합니다.

---

데이터가

많아질수록

URL은

길어집니다.

---

그래서

HTTP는

Body라는 공간을

제공합니다.

---

### POST는 Body를 사용한다
GET은

주로

```text
Path

Query
```

를 사용합니다.

---

POST는

```text
Body
```

를 사용합니다.

예를 들어

```json
{
    "title":"AIKOS",

    "author":"Kim",

    "content":"..."
}
```

이 데이터를

Body에 담습니다.

---

### 그림으로 이해하기
```text
POST /documents

──────────────

Header

──────────────

Body

{

"title":"AIKOS",

"author":"Kim"

}
```

이 Body가

Server로 전달됩니다.

---

### FastAPI 구현
지금은

Body를

아직 배우지 않았습니다.

그래도

형태만

미리 보겠습니다.

```python
@app.post("/documents")
def create_document():
    return {
        "message": "Document Created"
    }
```

GET과

거의 같습니다.

---

다른 것은

하나입니다.

```text
@app.post(...)
```

입니다.

---

### 내부 동작
```text
Browser

↓

POST /documents

↓

Uvicorn

↓

FastAPI

↓

Routing

↓

create_document()

↓

JSON

↓

Browser
```

GET과

동일합니다.

Method만

다릅니다.

---

### 왜 Method가 중요할까?
학생들이

많이 하는 질문입니다.

URL이

같은데

왜 GET과 POST를

나누나요?

---

예를 들어

```text
/documents
```

를 생각해봅시다.

조회도

필요합니다.

생성도

필요합니다.

---

REST는

Method로

구분합니다.

```text
GET /documents

↓

문서 목록
```

---

```text
POST /documents

↓

문서 생성
```

같은 URL이지만

행동이 다릅니다.

---

### AI 서비스에서는 POST를 어디에 사용할까?
생성형 AI 플랫폼에서는

POST가

엄청 많이 등장합니다.

예를 들어

새 채팅

```text
POST /chat
```

---

파일 업로드

```text
POST /upload
```

---

OCR 시작

```text
POST /ocr
```

---

Embedding 생성

```text
POST /embedding
```

---

Prompt 저장

```text
POST /prompts
```

---

사용자 생성

```text
POST /users
```

---

모두

Server의 상태가

변합니다.

---

### "Chat도 조회 아닌가요?"
학생들이

여기서

많이 질문합니다.

ChatGPT는

조회가 아닌가요?

사실은

아닙니다.

---

질문을 하면

Server에서는

새로운 작업이

발생합니다.

```text
질문 저장

↓

LLM 호출

↓

응답 생성

↓

대화 저장
```

Server 상태가

변합니다.

그래서

보통

```text
POST /chat
```

를 사용합니다.

---

### AIKOS 설계 관점
앞으로 만들

AI 플랫폼에서는

이렇게 설계합니다.

```text
GET /documents
```

↓

조회

---

```text
POST /documents
```

↓

생성

---

```text
GET /chat/history
```

↓

채팅 목록

---

```text
POST /chat
```

↓

새 질문

---

```text
GET /models
```

↓

모델 목록

---

```text
POST /upload
```

↓

파일 업로드

---

이 구조는

OpenAI,

Claude,

Gemini,

Azure OpenAI,

LangChain

모두

비슷합니다.

---

### 학생들이 가장 많이 하는 실수
##### 실수 ①
생성인데

GET을 사용한다.

```text
GET /createUser
```

좋지 않습니다.

---

##### 실수 ②
URL에

동사를 넣는다.

```text
/createDocument
```

보다는

```text
POST /documents
```

가

REST입니다.

---

##### 실수 ③
GET으로

DB를 변경한다.

예를 들어

```text
GET /deleteUser/3
```

이런 API는

절대 만들지 않습니다.

---

### 실무 Best Practice
항상

다음 질문을 먼저 합니다.

```text
Server 데이터가

변하는가?
```

↓

YES

↓

POST

---

NO

↓

GET

이 사고방식만 익혀도

HTTP Method 선택의 대부분은 해결됩니다.

※ 참고로 이후에 배울 **PUT, PATCH, DELETE**는 모두 서버의 상태를 변경하는 Method입니다. 지금은 **"조회(GET)와 생성(POST)를 명확히 구분한다"**는 원칙만 확실히 익히면 됩니다.

---

### AI 서비스 설계 예제
AIKOS에서 만들 생성형 AI 플랫폼의 일부를 설계해 보면 다음과 같습니다.

|기능|Method|URL|이유|
|---|---|---|---|
|문서 목록 조회|GET|`/documents`|데이터를 읽기만 함|
|문서 등록|POST|`/documents`|새 문서 생성|
|채팅 목록 조회|GET|`/chat/history`|기록 조회|
|새 질문 보내기|POST|`/chat`|새 대화 생성 및 AI 호출|
|서버 상태 확인|GET|`/health`|상태 조회|
|파일 업로드|POST|`/upload`|새 파일 저장|

이 표를 기준으로 생각하면 대부분의 API Method를 올바르게 선택할 수 있습니다.

---

### AIKOS 실무 Tip
여기서 한 가지 실무적인 내용을 미리 알려드리겠습니다.

많은 AI 서비스는 **"AI에게 질문을 하는 것"**도 POST로 설계합니다.

그 이유는 단순히 응답을 받는 것이 아니라,

```text
질문 저장
↓

대화 생성

↓

토큰 사용량 기록

↓

AI 호출

↓

응답 저장

↓

로그 기록
```

처럼 서버 내부에서 여러 작업이 발생하기 때문입니다.

즉, **"겉으로는 조회처럼 보이지만 서버 상태가 변한다"**는 점을 이해하는 것이 중요합니다.

---

### 핵심 내용 정리
이번 Unit에서는 **POST 요청을 REST 설계 철학과 함께** 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **GET은 조회(Read)**, **POST는 생성(Create)** 이다.
    
- POST는 **서버의 상태를 변경하는 요청**이다.
    
- POST에서는 일반적으로 **Request Body**를 이용해 데이터를 전달한다.
    
- 같은 URL이라도 HTTP Method에 따라 완전히 다른 Endpoint가 될 수 있다.
    
- AI 서비스에서는 파일 업로드, 채팅 생성, OCR 시작, LLM 호출 요청 등 대부분의 작업 시작은 POST로 설계한다.
    

---

## Module 23. Request Body


### Module 실습 예제

- [예제 1: request_body.py](examples/module_23/request_body.py) — Pydantic Model로 JSON Request Body를 받습니다.
- [예제 2: nested_body.py](examples/module_23/nested_body.py) — 중첩 Request Model로 복합 JSON을 표현합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 복합 JSON 입력을 Python 객체로 안전하게 받는다.
- **오늘 만드는 것:** AI 질문 Request Body 모델을 정의한다.
- **AI 플랫폼의 위치:** 프론트엔드 입력과 Service 호출 사이의 검증 경계다.
- **실무에서 많이 하는 실수:** dict를 그대로 넘겨 필드 의미와 타입을 잃는다.
- **5분 실습:** 선택 필드와 필수 필드를 구분한 요청 모델을 만든다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Request Body는 무엇인가?
    
- 왜 Body가 필요한가?
    
- Body와 Query는 무엇이 다른가?
    
- JSON은 왜 사용하는가?
    
- FastAPI는 Body를 어떻게 읽는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

POST를 배웠습니다.

그런데

여기서 질문이 하나 생깁니다.

새로운 문서를 생성하려면

다음 정보가 필요합니다.

```text
제목

작성자

내용

카테고리

작성일
```

이 데이터를

어디에 담아야 할까요?

---

URL일까요?

```
POST

/documents/AIKOS/Kim/FastAPI/...
```

가능은 합니다.

하지만

문서 내용이

100페이지라면?

URL은

말도 안 되게 길어집니다.

---

그래서

HTTP는

Body라는 공간을 제공합니다.

---

### HTTP는 편지봉투와 같다
HTTP Request를

우리는

하나의 편지라고 생각하면 됩니다.

```
주소

↓

봉투

↓

내용
```

HTTP도

거의 같습니다.

```
URL

↓

Header

↓

Body
```

여기서

Body는

편지 내용입니다.

---

### 지금까지 사용했던 GET
우리는

GET만 사용할 때는

Body가 필요 없었습니다.

예를 들어

```
GET /documents/15
```

이미

필요한 정보가

모두 있습니다.

---

또는

```
GET

/documents?page=2
```

도

Body가 필요 없습니다.

---

하지만

생성(Create)은 다릅니다.

---

### 생성에는 데이터가 필요하다
문서를 만든다고 해봅시다.

```
제목

내용

작성자

태그

파일
```

이런 정보를

보내야 합니다.

그래서

POST는

Body를 사용합니다.

---

### Body 안에는 무엇이 들어갈까?
오늘날

웹 서비스의

표준은

JSON입니다.

예를 들어

```
POST /documents
```

Body에는

```json
{
    "title":"AIKOS",

    "author":"Kim",

    "content":"FastAPI"

}
```

가 들어갑니다.

---

학생들은

여기서

질문합니다.

왜 XML이 아니라

JSON인가요?

---

### JSON이 표준이 된 이유
예전에는

XML을 많이 사용했습니다.

```xml
<document>

<title>AIKOS</title>

</document>
```

너무 길었습니다.

---

JSON은

훨씬 단순합니다.

```json
{
    "title":"AIKOS"
}
```

사람도 읽기 쉽고

프로그램도 처리하기 쉽습니다.

---

그래서

현재 대부분의

REST API는

JSON을 사용합니다.

---

### Browser에서 실제로 일어나는 일
사용자가

문서를 작성합니다.

```
제목 입력

↓

내용 입력

↓

저장 버튼
```

React는

JavaScript 객체를 만듭니다.

```javascript
{
    title: "AIKOS",
    author: "Kim"
}
```

---

그리고

HTTP Body 안에

JSON으로 넣습니다.

```
POST

/documents

↓

Body

↓

JSON
```

---

### Backend에서는 어떻게 될까?
FastAPI는

Body를 받습니다.

```
HTTP Request

↓

Body

↓

JSON
```

그리고

JSON을

읽습니다.

여기까지는

모든 Framework가

비슷합니다.

---

여기서

FastAPI의 강점이

등장합니다.

---

### FastAPI는 JSON을 객체로 바꾼다
학생들이

처음에는

이렇게 생각합니다.

```
JSON

↓

dict

↓

직접 꺼낸다.
```

Flask에서는

보통

이런 코드를 작성했습니다.

```python
data = request.json

title = data["title"]
```

---

FastAPI는

조금 다릅니다.

```
JSON

↓

Python Object

↓

함수
```

이 흐름으로

동작합니다.

---

지금은

아직

Pydantic을

배우지 않았기 때문에

구조만

먼저 이해합시다.

```
Browser

↓

JSON

↓

Body

↓

FastAPI

↓

Python Object

↓

Function
```

다음 Unit에서

이 Python Object를

만드는 것이

Pydantic입니다.

---

### Request Processing Pipeline (AIKOS 핵심 개념)
여기서부터

AIKOS에서는

새로운 그림 하나를

계속 사용할 것입니다.

```
React

↓

JavaScript Object

↓

JSON

↓

HTTP Body

↓

FastAPI

↓

Pydantic

↓

Validation

↓

Python Object

↓

Business Logic
```

이 그림은

FastAPI의 핵심입니다.

앞으로

Request Body,

Pydantic,

Validation은

이 그림 안에서

계속 설명합니다.

---

### Query와 Body의 차이
학생들이

가장 많이 헷갈립니다.

예를 들어

```
GET

/documents?page=3
```

여기서는

조건만 있습니다.

---

반면

```
POST

/documents
```

에서는

문서 전체를

보냅니다.

---

즉

```
Query

↓

검색 조건
```

---

```
Body

↓

실제 데이터
```

입니다.

---

### AI 서비스에서는 어떻게 사용할까?
예를 들어

ChatGPT입니다.

질문을 보냅니다.

```
POST /chat
```

Body는

```json
{
    "question":"FastAPI가 뭐예요?"
}
```

---

OCR입니다.

```
POST /ocr
```

Body는

```json
{
    "language":"ko",

    "engine":"easyocr"
}
```

---

Embedding입니다.

```
POST /embedding
```

Body는

```json
{
    "text":"..."
}
```

---

LLM 호출도

모두

Body를 사용합니다.

---

### 실무 Best Practice
#### Body에는 Resource를 넣는다
좋은 예

```json
{
    "title":"AIKOS",

    "author":"Kim"
}
```

---

나쁜 예

```
POST

/createDocument

?title=AIKOS

&author=Kim
```

생성(Create)에 필요한 데이터는

Body를 사용하는 것이 REST와 HTTP의 의도에 맞습니다.

---

#### JSON은 구조를 표현하는 용도
JSON은

단순 문자열이 아닙니다.

```
Document

↓

JSON

↓

Document Object
```

입니다.

즉

객체(Object)를

전송하는 방법입니다.

---

### 학생들이 가장 많이 하는 실수
##### ① Body 대신 Query를 사용한다.
```
POST

/documents

?title=AIKOS
```

가능은 하지만

좋은 설계가 아닙니다.

---

##### ② URL에 데이터를 넣는다.
```
POST

/documents/AIKOS/Kim
```

REST에서는

지양합니다.

---

##### ③ JSON을 문자열이라고 생각한다.
JSON은

문자열이 아니라

**객체를 표현하는 표준 형식**입니다.

---

### AIKOS 핵심 그림
이번 Unit에서

반드시 기억해야 하는 그림입니다.

```
사용자

↓

React Form

↓

JavaScript Object

↓

JSON

↓

HTTP Body

↓

FastAPI

↓

(다음 Unit)

Pydantic

↓

Python Object

↓

Business Logic
```

이 그림은

OpenAI API,

LangChain,

Document AI까지

계속 등장합니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Request Body를 단순한 문법이 아니라 HTTP와 객체(Object) 전달 관점**에서 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Request Body는 서버에 전달할 실제 데이터를 담는 공간**이다.
    
- GET은 주로 **Path와 Query**를 사용하고, POST는 **Body**를 사용한다.
    
- 현대 REST API에서는 **JSON이 표준 데이터 형식**이다.
    
- React는 JavaScript 객체를 JSON으로 변환하여 Body에 담아 전송한다.
    
- FastAPI는 이 JSON을 다음 단계에서 **Pydantic을 이용해 Python 객체로 변환**한다.
    

---

## Module 24. Pydantic과 객체 매핑(Object Mapping)


### Module 실습 예제

- [예제 1: pydantic_mapping.py](examples/module_24/pydantic_mapping.py) — Dictionary가 Pydantic 객체로 변환되는 과정을 확인합니다.
- [예제 2: pydantic_serialization.py](examples/module_24/pydantic_serialization.py) — Pydantic 객체를 Dictionary와 JSON으로 직렬화합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 외부 JSON과 내부 Python 객체 사이의 변환 원리를 이해한다.
- **오늘 만드는 것:** Pydantic 모델로 요청·응답 객체를 매핑한다.
- **AI 플랫폼의 위치:** Router 바깥으로 검증된 데이터만 전달하는 관문이다.
- **실무에서 많이 하는 실수:** ORM 모델과 API Schema를 같은 용도로 사용한다.
- **5분 실습:** 같은 데이터의 Request·Domain·Response 표현을 구분한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Pydantic은 왜 필요한가?
    
- JSON은 어떻게 Python 객체가 되는가?
    
- 객체 매핑(Object Mapping)이란 무엇인가?
    
- FastAPI는 왜 Pydantic을 사용하는가?
    
- AI 서비스에서는 어떤 데이터를 Pydantic으로 표현하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서

우리는

Browser가

JSON을 보낸다는 것을 배웠습니다.

```json
{
    "title":"AIKOS",
    "author":"Kim"
}
```

그런데

여기서 질문이 하나 생깁니다.

Python은

JSON을 사용할까요?

아닙니다.

Python은

객체(Object)를 사용합니다.

---

그렇다면

JSON을

Python 객체로

누가 바꾸는 걸까요?

---

많은 학생들이

이렇게 생각합니다.

```python
data = request.json

title = data["title"]
```

직접 꺼내면 되지 않나요?

---

가능합니다.

하지만

실무에서는

절대 이렇게 하지 않습니다.

---

### 객체(Object)와 Dictionary는 다르다
학생들이

가장 많이 하는 오해입니다.

```python
{
    "title":"AIKOS"
}
```

이것은

Dictionary입니다.

---

하지만

실무에서는

우리가 원하는 것은

Document입니다.

```text
Document

↓

title

author

content
```

즉

하나의

객체입니다.

---

### 객체를 사용하는 이유
예를 들어

문서를 표현한다고 해봅시다.

Dictionary 방식

```python
document["title"]
```

---

객체 방식

```python
document.title
```

둘 다 가능합니다.

---

하지만

객체는

의미가 있습니다.

```text
Document
```

라는

도메인 모델이

생깁니다.

---

### 객체 매핑(Object Mapping)
여기서

객체 매핑이라는

개념이 등장합니다.

JSON

↓

Python Object

이 변환 과정을

Object Mapping이라고 합니다.

---

그림으로 보면

```text
HTTP Body

↓

JSON

↓

Object Mapping

↓

Python Object
```

---

FastAPI에서는

이 작업을

Pydantic이

담당합니다.

---

### Pydantic이란?
Pydantic은

단순한 라이브러리가 아닙니다.

AIKOS에서는

이렇게 정의하겠습니다.

> **외부 데이터를 Python 객체로 변환하고 검증하는 데이터 모델링 라이브러리**

여기서

중요한 단어는

두 개입니다.

```text
Object Mapping

Validation
```

---

### 첫 번째 Pydantic 모델
```python
from pydantic import BaseModel


class Document(BaseModel):

    title: str

    author: str

    content: str
```

학생들은

여기서

이것이

클래스인지

모델인지

헷갈립니다.

---

사실

둘 다 맞습니다.

Python에서는

클래스입니다.

FastAPI에서는

데이터 모델입니다.

---

### BaseModel은 무엇일까?
Python 시간에

우리는

이렇게 만들었습니다.

```python
class Dog:

    pass
```

Pydantic도

같습니다.

```text
class Document(BaseModel):
```

차이점은

BaseModel이

JSON 처리,

Validation,

직렬화 기능을

추가해 준다는 것입니다.

---

### Request Processing Pipeline
지난 Unit에서

잠깐 보았던 그림을

완성해 봅시다.

```text
React

↓

JavaScript Object

↓

JSON

↓

HTTP Body

↓

FastAPI

↓

Pydantic

↓

Python Object

↓

Business Logic
```

여기서

오늘 배운 부분은

바로

```text
JSON

↓

Python Object
```

입니다.

---

### 실제 동작 과정
Browser가

보냅니다.

```json
{
    "title":"AIKOS",

    "author":"Kim"
}
```

---

FastAPI는

Pydantic을

호출합니다.

---

Pydantic은

Document 객체를

생성합니다.

```python
Document(

    title="AIKOS",

    author="Kim"

)
```

---

그리고

FastAPI는

이 객체를

함수에게

전달합니다.

---

### 코드로 보면
```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Document(BaseModel):
    title: str
    author: str
    content: str


@app.post("/documents")
def create_document(document: Document):
    return document
```

학생들이

여기서

가장 놀라는 부분은

```python
document: Document
```

입니다.

---

왜

JSON인데

Document 객체가

들어올까요?

---

정답은

FastAPI가

자동으로

Pydantic을

호출하기 때문입니다.

---

### 내부 구조
```text
Browser

↓

JSON

↓

Body

↓

FastAPI

↓

Pydantic

↓

Document 객체

↓

create_document()
```

이것이

FastAPI 내부에서

실제로

일어나는 일입니다.

---

### AI 서비스에서는?
예를 들어

ChatGPT입니다.

Body

```json
{
    "question":"FastAPI가 뭐예요?"
}
```

---

Pydantic

```python
class ChatRequest(BaseModel):

    question: str
```

---

OCR

```json
{
    "language":"ko"
}
```

↓

```python
class OCRRequest(BaseModel):

    language: str
```

---

Embedding

```json
{
    "text":"..."
}
```

↓

```python
class EmbeddingRequest(BaseModel):

    text: str
```

즉,

AI 서비스의 모든 요청은

Pydantic Model이 됩니다.

---

### DTO라는 용어
실무에서는

이런 객체를

DTO라고도 부릅니다.

Data Transfer Object

입니다.

AIKOS에서는

현재는

간단히

이 정도만 기억하면 됩니다.

```text
DTO

↓

데이터를 전달하는 객체
```

나중에

SQLAlchemy,

Service Layer,

Repository Pattern에서

다시 등장합니다.

---

### 실무 Best Practice
#### Dictionary보다 객체를 사용한다.
좋은 예

```python
document.title
```

---

좋지 않은 예

```python
document["title"]
```

객체는 자동완성, 타입 검사, 유지보수 측면에서 훨씬 유리합니다.

---

#### Request마다 별도의 모델을 만든다.
```text
ChatRequest

OCRRequest

EmbeddingRequest

LoginRequest
```

하나의 거대한 모델을 공유하지 않습니다.

요청의 목적에 맞는 모델을 만드는 것이 좋습니다.

---

### 학생들이 자주 하는 실수
##### ① Dictionary와 Pydantic Model을 같은 것으로 생각한다.
둘은 다릅니다.

Dictionary는 단순한 자료구조이고,

Pydantic Model은 **의미와 타입을 가진 객체**입니다.

---

##### ② 하나의 Model을 여러 API에서 재사용한다.
처음에는 편해 보이지만

나중에 수정이 매우 어려워집니다.

---

##### ③ Pydantic을 Validation 라이브러리로만 생각한다.
Validation도 하지만

더 중요한 역할은

**객체 생성(Object Mapping)** 입니다.

---

### AIKOS 핵심 그림
이번 Unit부터

앞으로 계속 사용할

Backend 데이터 흐름입니다.

```text
React

↓

JavaScript Object

↓

JSON

↓

HTTP Body

↓

Pydantic

↓

DTO

↓

Business Logic

↓

AI Provider
```

이 그림은

FastAPI뿐 아니라

Spring Boot,

ASP.NET,

NestJS,

Django REST Framework에서도

거의 동일한 구조입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Pydantic을 객체 매핑(Object Mapping)의 관점**에서 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Pydantic은 JSON을 Python 객체로 변환하는 데이터 모델링 라이브러리**이다.
    
- FastAPI는 Request Body를 Pydantic Model로 자동 매핑한다.
    
- Pydantic Model은 단순한 Dictionary가 아니라 **의미와 타입을 가진 객체(DTO)** 이다.
    
- AI 서비스에서는 ChatRequest, OCRRequest, EmbeddingRequest 등 요청마다 별도의 모델을 정의하는 것이 일반적이다.
    
- 객체 매핑은 이후 Validation, Response Model, ORM, SQLAlchemy까지 이어지는 핵심 개념이다.
    

---

#### Unit 16 연결
Validation을 독립된 기능으로만 이해하면 Pydantic의 객체 매핑 과정과 분리해서 생각하기 쉽습니다. 이번 과정에서는 다음 흐름으로 연결합니다.

```text
Python Type Hint
+
Pydantic
+
HTTP Request
↓
객체 매핑과 Validation
```

Unit 15~17은 Request와 Response를 하나의 파이프라인으로 설명합니다.

```text
15. Pydantic과 객체 매핑(Object Mapping)
16. 데이터 검증(Validation)과 타입 시스템
17. Response Model과 Response DTO
```

```text
Client
↓
Request DTO
↓
Validation
↓
Business Logic
↓
Response DTO
↓
Client
```

이 구조는 Spring Boot의 DTO, ASP.NET의 Model Binding, NestJS의 DTO와 같은 요청·응답 경계 개념으로 확장해 이해할 수 있습니다.

---

## Module 25. 데이터 검증(Validation)과 타입 시스템


### Module 실습 예제

- [예제 1: field_constraints.py](examples/module_25/field_constraints.py) — Field 제약으로 질문 길이와 숫자 범위를 검증합니다.
- [예제 2: model_validator.py](examples/module_25/model_validator.py) — 여러 Field 사이의 비즈니스 입력 규칙을 검증합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 잘못된 입력을 비즈니스 로직 전에 차단한다.
- **오늘 만드는 것:** 질문 길이·범위·형식 Validation을 추가한다.
- **AI 플랫폼의 위치:** AI 비용이 발생하기 전의 첫 방어선이다.
- **실무에서 많이 하는 실수:** Validation을 보안 전체로 오해하거나 과도한 제약을 숨긴다.
- **5분 실습:** 빈 질문과 지나치게 긴 질문에 대한 테스트를 작성한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Validation은 왜 필요한가?
    
- Type Hint는 Validation과 어떤 관계가 있는가?
    
- FastAPI는 Validation을 언제 수행하는가?
    
- Validation은 누가 수행하는가?
    
- AI 서비스에서는 무엇을 검증해야 하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

JSON이

Pydantic Model로

변환되는 과정을 배웠습니다.

그런데

한 가지 문제가 있습니다.

사용자가

항상

올바른 데이터를

보낼까요?

그렇지 않습니다.

---

예를 들어

회원 나이를 입력합니다.

정상 데이터

```json
{
    "age":20
}
```

---

잘못된 데이터

```json
{
    "age":"스무살"
}
```

둘 다

올 수 있습니다.

---

FastAPI는

어떻게 해야 할까요?

---

학생들이

보통 생각하는 방법은

이렇습니다.

```python
if type(age) != int:

    ...
```

혹은

```python
try:

    age = int(age)

except:

    ...
```

직접 검사하는 것입니다.

---

실무에서는

거의 이렇게 하지 않습니다.

---

### Validation은 "방어벽"이다
Backend는

외부와 연결되어 있습니다.

누구나

잘못된 데이터를

보낼 수 있습니다.

```
Browser

↓

Mobile

↓

React

↓

Postman

↓

Swagger

↓

외부 API
```

즉,

Backend는

항상

잘못된 데이터를

받을 수 있습니다.

---

그래서

입구에서

막아야 합니다.

```
잘못된 데이터

↓

Validation

↓

통과

↓

Business Logic
```

Validation은

Backend의

첫 번째 방어벽입니다.

---

### AI 서비스에서는 더 중요하다
AI 서비스는

LLM을 호출합니다.

예를 들어

질문이

```
null
```

이라면?

LLM은

호출할 이유가 없습니다.

---

Embedding Text가

```
""
```

빈 문자열이라면?

Embedding도

생성하면 안 됩니다.

---

OCR Language가

```
123
```

이라면?

OCR는

실행하면 안 됩니다.

---

즉

Validation은

LLM 비용도

절약합니다.

---

### Validation은 언제 수행될까?
많은 학생들이

Business Logic 안에서

Validation이

수행된다고 생각합니다.

실제로는

그보다 훨씬 먼저입니다.

```
Browser

↓

JSON

↓

FastAPI

↓

Pydantic

↓

Validation

↓

Python Object

↓

Business Logic
```

Business Logic은

Validation을

통과한 데이터만

받습니다.

---

### Type Hint가 중요한 이유
우리는

이렇게 작성했습니다.

```python
age: int
```

학생들은

Type Hint를

자동완성 정도로

생각합니다.

FastAPI에서는

다릅니다.

```
age:int
```

↓

Validation Rule

이 됩니다.

---

예를 들어

```python
class User(BaseModel):

    age:int
```

---

Browser

```json
{
    "age":"hello"
}
```

---

FastAPI는

자동으로

400번대 오류(실제로는 **422 Unprocessable Entity**)를

반환합니다.

우리는

검사 코드를

작성하지 않았습니다.

---

### FastAPI는 누가 Validation을 할까?
많은 학생들이

FastAPI가

한다고 생각합니다.

조금 더 정확하게 말하면

```
FastAPI

↓

Pydantic

↓

Validation
```

입니다.

FastAPI가

Pydantic에게

검사를 맡깁니다.

---

### Validation Pipeline
이번 Unit에서

가장 중요한 그림입니다.

```
HTTP Request

↓

JSON

↓

Object Mapping

↓

Validation

↓

Python Object

↓

Business Logic
```

Validation은

중간 과정입니다.

---

### 타입 검증(Type Validation)
```python
class User(BaseModel):

    age:int
```

정상

```json
{
    "age":30
}
```

↓

통과

---

비정상

```json
{
    "age":"abc"
}
```

↓

422 Error

---

### 필수값 검증
```python
class User(BaseModel):

    name:str
```

Browser

```json
{
}
```

name이 없습니다.

↓

Validation 실패

↓

422

---

### AI 서비스에서는 무엇을 검증할까?
Chat API

```python
question:str
```

---

Embedding API

```python
text:str
```

---

OCR API

```python
language:str
```

---

Upload API

```python
filename:str
```

---

Document API

```python
title:str
```

---

즉

AI 서비스의

모든 입력은

Validation 대상입니다.

---

### Validation을 통과하면?
Business Logic은

안심하고

사용합니다.

```python
document.title
```

를

바로 사용할 수 있습니다.

매번

```
None인가?

String인가?

```

를

검사하지 않습니다.

---

### 실무 Best Practice
#### Validation은 최대한 앞에서 한다.
```
Controller

↓

Validation

↓

Service
```

Service에서

Validation하지 않습니다.

---

#### Type Hint를 적극 활용한다.
좋은 예

```python
age:int
```

---

좋지 않은 예

```python
age:any
```

---

#### Business Logic은 Validation을 믿는다.
Service는

검사보다

업무 로직에

집중해야 합니다.

---

### 학생들이 가장 많이 하는 실수
##### ① Service에서 다시 Validation한다.
중복입니다.

---

##### ② 모든 타입을 str로 만든다.
Type Hint의 장점이 사라집니다.

---

##### ③ Validation과 Exception을 같은 것으로 생각한다.
Validation은

입력 검증입니다.

Exception은

실행 중 발생하는 오류 처리입니다.

둘은

다른 개념입니다.

---

### AIKOS 핵심 그림
```
Client

↓

JSON

↓

Request DTO

↓

Object Mapping

↓

Validation

↓

Business Logic

↓

Response DTO

↓

Client
```

이 그림이

FastAPI뿐 아니라

Spring Boot,

NestJS,

ASP.NET,

Go Fiber,

Django REST Framework에서도

거의 동일합니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Validation을 객체 매핑 파이프라인의 일부**로 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- Validation은 **Backend의 첫 번째 방어벽**이다.
    
- FastAPI는 **Pydantic을 이용해 타입 검증과 필수값 검증을 자동 수행**한다.
    
- Validation은 **Business Logic보다 먼저 실행**된다.
    
- Type Hint는 단순한 문법이 아니라 **Validation 규칙**으로도 사용된다.
    
- AI 서비스에서는 LLM 호출, OCR, Embedding, 파일 업로드 등 모든 입력을 먼저 검증해야 한다.
    

---

### AIKOS FastAPI (최종 교육 철학)
앞으로 모든 Unit은 아래 순서를 유지합니다.

```text
Why

↓

REST Design

↓

Concept

↓

Internal Architecture

↓

Implementation

↓

Execution Flow

↓

AI Backend Architecture

↓

Best Practice

↓

Common Mistakes

↓

Summary

↓

Project Connection
```

그리고 각 Unit은 반드시

현재 만들고 있는 AI Platform 프로젝트와 연결됩니다.

---

## Module 26. Response Model과 Response DTO


### Module 실습 예제

- [예제 1: response_model.py](examples/module_26/response_model.py) — Response Model로 출력 계약을 고정합니다.
- [예제 2: private_field_filter.py](examples/module_26/private_field_filter.py) — response_model이 내부 Field 노출을 차단하는지 확인합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 내부 데이터 전체를 노출하지 않고 응답 계약을 고정한다.
- **오늘 만드는 것:** AI 결과 Response Model을 정의한다.
- **AI 플랫폼의 위치:** Service 결과를 클라이언트 계약으로 변환하는 마지막 경계다.
- **실무에서 많이 하는 실수:** DB 객체를 그대로 반환해 민감 필드가 노출된다.
- **5분 실습:** 내부 필드를 하나 추가해도 응답에 노출되지 않는지 확인한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Response Model은 무엇인가?
    
- Response DTO는 왜 필요한가?
    
- Request DTO와 Response DTO는 무엇이 다른가?
    
- 왜 그대로 return하면 안 되는가?
    
- AI 서비스에서는 어떤 응답 구조를 사용하는가?
    

---

### ① 문제 이해 (Why)
지금까지 우리는

Browser가

Backend로 데이터를 보내는 과정만 공부했습니다.

```text
React

↓

JSON

↓

Request DTO

↓

Validation

↓

Business Logic
```

여기까지는

입력(Input)입니다.

---

그런데

Backend는

결과를

다시 돌려줘야 합니다.

질문은

여기서 시작됩니다.

Backend 내부 객체를

그대로

브라우저에게

보내도 될까요?

많은 초보 개발자는

그렇게 합니다.

```python
return document
```

혹은

```python
return db_document
```

---

처음에는

잘 동작하는 것처럼 보입니다.

하지만

실무에서는

거의 사용하지 않습니다.

---

### 왜 그대로 반환하면 안 될까?
회원 정보를 조회한다고 해봅시다.

Database에는

다음과 같은 정보가 있습니다.

```text
id

name

email

password

created_at

updated_at
```

사용자에게

모두 보여줘도 될까요?

당연히

안 됩니다.

---

예를 들어

```json
{
    "id":1,

    "name":"Kim",

    "password":"123456"
}
```

이렇게 응답한다면

보안 사고가 발생합니다.

---

즉,

Database 객체와

API 응답은

같아서는 안 됩니다.

---

### AIKOS 핵심 원칙
여기서부터

AIKOS는

하나의 원칙을 사용합니다.

```text
Database Model

≠

API Response
```

이 원칙은

FastAPI뿐 아니라

Spring Boot,

ASP.NET,

NestJS,

Go,

Django에서도

동일합니다.

---

### Request와 Response는 대칭 구조이다
지금까지

우리는

입력을 받았습니다.

```text
Request

↓

DTO

↓

Validation
```

이제

출력도

같은 방식으로 합니다.

```text
Business Logic

↓

Response DTO

↓

JSON

↓

React
```

---

즉

Backend는

입력과 출력 모두

객체(Object)를 사용합니다.

---

### 전체 Request/Response Pipeline
이제

FastAPI 전체 흐름이

완성됩니다.

```text
React

↓

Request JSON

↓

Request DTO

↓

Validation

↓

Business Logic

↓

Response DTO

↓

JSON

↓

React
```

이 그림은

앞으로 AIKOS 전체에서

계속 사용됩니다.

---

### Response DTO란?
Response DTO는

Client에게

전달하기 위한

객체입니다.

예를 들어

```python
class DocumentResponse(BaseModel):

    id: int

    title: str

    author: str
```

입니다.

---

학생들이

여기서

많이 하는 질문이 있습니다.

> Request DTO와 뭐가 다른가요?

좋은 질문입니다.

---

### Request DTO
입력을 위한 객체입니다.

```python
class DocumentCreateRequest(BaseModel):

    title:str

    author:str

    content:str
```

---

### Response DTO
출력을 위한 객체입니다.

```python
class DocumentResponse(BaseModel):

    id:int

    title:str

    author:str
```

---

보시면

content가

없습니다.

왜일까요?

Client에게

보여줄 필요가

없기 때문입니다.

---

### FastAPI 구현
FastAPI에서는

응답 모델을

직접 지정할 수 있습니다.

```python
@app.get(
    "/documents/{id}",
    response_model=DocumentResponse
)
def get_document():

    ...
```

학생들은

여기서

처음으로

```text
response_model=
```

을 보게 됩니다.

---

이 옵션은

매우 중요합니다.

---

### response_model의 역할
FastAPI는

Business Logic이

반환한 데이터를

Response DTO로

변환합니다.

```text
Business Object

↓

Response DTO

↓

JSON
```

즉,

응답도

자동 매핑됩니다.

---

### 내부 실행 과정
```text
Business Logic

↓

Document

↓

Response DTO

↓

JSON

↓

Browser
```

Request와

완전히

대칭입니다.

---

### AI 서비스에서는?
예를 들어

ChatGPT 응답입니다.

Browser는

필요한 정보만

받으면 됩니다.

```python
class ChatResponse(BaseModel):

    answer:str

    model:str

    tokens:int
```

---

OCR

```python
class OCRResponse(BaseModel):

    text:str

    language:str
```

---

Embedding

```python
class EmbeddingResponse(BaseModel):

    dimension:int

    model:str
```

---

즉

AI 서비스에서는

API마다

Response DTO가

존재합니다.

---

### Response DTO의 장점
##### ① 보안
불필요한 데이터가

노출되지 않습니다.

---

##### ② 일관성
모든 API가

같은 형태를

유지합니다.

---

##### ③ 문서화
Swagger도

자동으로

응답 형식을

생성합니다.

---

##### ④ 유지보수
Database가

변해도

API는

유지됩니다.

---

### AI Backend Architecture
지금까지 배운 내용을

AI Backend 구조로

다시 보면

```text
Client

↓

Request DTO

↓

Validation

↓

Service

↓

AI Provider

↓

Response DTO

↓

Client
```

여기서

중요한 점이 있습니다.

Business Logic은

Database 객체를

알고 있습니다.

하지만

Client는

Response DTO만

알고 있습니다.

---

### 학생들이 가장 많이 하는 실수
##### 실수 ①
Database 객체를

그대로 반환한다.

---

##### 실수 ②
Request DTO를

Response DTO로

재사용한다.

입력과 출력은

목적이 다르므로

분리하는 것이 좋습니다.

---

##### 실수 ③
Response DTO 없이

Dictionary만

반환한다.

작은 프로젝트에서는 가능하지만

실무에서는

유지보수가 매우 어려워집니다.

---

### AIKOS 실무 Best Practice
실무에서는

DTO를

역할별로

분리합니다.

```text
schemas/

    request/

        chat.py

        document.py

        upload.py

    response/

        chat.py

        document.py

        upload.py
```

지금은

아직 하나의 파일에

작성해도 됩니다.

하지만

프로젝트가 커질수록

이 구조로

발전하게 됩니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Response Model과 Response DTO**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Request DTO는 입력**, **Response DTO는 출력**을 위한 객체이다.
    
- Database Model과 API Response는 분리하는 것이 실무 원칙이다.
    
- FastAPI의 `response_model`은 응답 데이터를 자동으로 Response DTO에 맞게 변환한다.
    
- Response DTO를 사용하면 보안, 유지보수, Swagger 문서화 측면에서 큰 장점이 있다.
    
- AI 서비스에서는 Chat, OCR, Embedding 등 모든 API가 목적에 맞는 Response DTO를 갖는 것이 일반적이다.
    

---

### Project Connection
이번 Unit에서 **Request Pipeline이 완성**되었습니다.

```text
React Form
      │
      ▼
Request JSON
      │
      ▼
Request DTO
      │
      ▼
Validation
      │
      ▼
Service Layer (Day 2 Architecture)
      │
      ▼
AI Provider
      │
      ▼
Response DTO
      │
      ▼
JSON Response
      │
      ▼
React UI
```

---

### Part 2 Architecture Review
#### 5분 복습
```text
React 입력
→ Route 선택
→ Path / Query / Body 추출
→ Pydantic 검증
→ Path Operation
→ Response Model
→ JSON 응답
```

- **따라 하기:** 질문 생성과 작업 조회 Endpoint를 실행한다.
- **부분 완성:** 누락된 Parameter 제약과 Response Model을 채운다.
- **독립 구현:** 생성·단건 조회·목록 조회 API 계약을 스스로 작성한다.

#### 학생 질문
1. Path Parameter와 Query Parameter의 선택 기준은 무엇인가?
2. Request Model과 Response Model을 분리하는 이유는 무엇인가?
3. 검증을 통과한 입력도 Service에서 다시 확인해야 하는 규칙은 무엇인가?

#### 확인 퀴즈
1. 장시간 작업 접수 응답에 201과 202 중 무엇이 더 자연스러운가?
2. 내부 객체를 Response Model 없이 그대로 반환할 때 생길 수 있는 문제는 무엇인가?
3. 잘못된 타입의 Path Parameter는 어느 계층에서 먼저 차단되는가?

<details>
<summary>정답</summary>

1. 아직 처리가 끝나지 않았다면 일반적으로 202가 더 자연스럽다.
2. 내부·민감 필드 노출과 API 계약 결합이 생길 수 있다.
3. FastAPI와 Pydantic의 요청 검증 단계에서 먼저 차단된다.

</details>

### Day 2 — AI Backend 구조와 Provider 연동

### Day 2-1. Pydantic 이후의 객체 설계

Pydantic Model은 API 경계에서 요청과 응답을 검증합니다. 이어서 순수 Python 내부 데이터에는 Data Class를 사용할 수 있음을 확인하고, Service가 AI Client를 전달받는 Composition 구조를 준비합니다.

|구분|Pydantic Model|Data Class|
|---|---|---|
|주요 위치|HTTP 요청·응답 경계|Service 내부 데이터|
|핵심 역할|변환·검증·API Schema|데이터 중심 객체의 반복 코드 축소|
|FastAPI 연결|Request·Response Model|내부 Command·Result Model|

# Part 3. Backend Architecture와 책임 분리

Endpoint가 늘어나면 모든 코드를 하나의 함수에 넣을 수 없다. 이 Part부터는 "동작하는 코드"에서 "변경하고 테스트할 수 있는 구조"로 넘어간다.

## Module 29. Service Layer와 Business Logic


### Module 실습 예제

- [예제 1: thin_router.py](examples/module_29/thin_router.py) — Router는 HTTP를 처리하고 Service가 규칙을 담당합니다.
- [예제 2: service_unit_demo.py](examples/module_29/service_unit_demo.py) — HTTP 없이 Service의 Business Logic을 검증합니다.



#### 프로젝트 연결 학습
- **문제 상황:** Router에서 비즈니스 규칙을 분리해 테스트 가능하게 만든다.
- **오늘 만드는 것:** AIJobService의 핵심 메서드를 설계한다.
- **AI 플랫폼의 위치:** Router와 Repository·AI Client 사이의 의사결정 계층이다.
- **실무에서 많이 하는 실수:** Service를 단순 전달 함수로 만들거나 HTTP 객체에 결합한다.
- **5분 실습:** Router의 조건문 하나를 Service로 옮긴다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Business Logic이란 무엇인가?
    
- 왜 Router에 코드를 작성하면 안 되는가?
    
- Service Layer는 무엇인가?
    
- AI Backend에서는 Service가 어떤 역할을 하는가?
    
- 앞으로 Router와 Service는 어떻게 분리되는가?
    

---

### ① 문제 이해 (Why)
우리는 지금까지

API를 이렇게 만들었습니다.

```python
@app.post("/chat")
def chat():

    return {
        "message":"Hello"
    }
```

아직은 문제가 없습니다.

---

그런데

조금만 기능이 늘어나면

어떻게 될까요?

예를 들어

AI Chat입니다.

```text
@app.post("/chat")
def chat():

    ...

    사용자 확인

    ...

    Prompt 생성

    ...

    OpenAI 호출

    ...

    Token 계산

    ...

    DB 저장

    ...

    Log 저장

    ...

    Response 생성

    ...

    return ...
```

학생들은

처음에는

이렇게 작성합니다.

---

문제는

이 코드가

계속 길어진다는 것입니다.

---

### Router는 점점 거대해진다
처음

```text
@app.post("/chat")
```

↓

20줄

---

조금 후

↓

80줄

---

조금 더

↓

200줄

---

프로젝트 후반

↓

700줄

---

학생들은

이 시점에서

질문합니다.

> "이걸 어떻게 분리하죠?"

바로

Service Layer가

등장하는 순간입니다.

---

### AI Backend는 역할을 나눈다
실무에서는

한 사람이

모든 일을 하지 않습니다.

예를 들어

식당입니다.

```text
손님

↓

주문

↓

주방

↓

요리

↓

서빙
```

주문받는 사람이

요리까지 하지 않습니다.

---

Backend도 같습니다.

---

### Router의 역할
Router는

입구입니다.

```text
HTTP Request

↓

Router
```

여기서 하는 일은

많지 않습니다.

```text
Request 받기

↓

Validation

↓

Service 호출

↓

Response 반환
```

끝입니다.

---

### Service의 역할
실제 업무는

Service가 합니다.

```text
Service

↓

Business Logic
```

예를 들어

Chat Service입니다.

```text
Prompt 생성

↓

LLM 호출

↓

Token 계산

↓

대화 저장

↓

응답 생성
```

이것이

Business Logic입니다.

---

### Business Logic이란?
학생들이

Business Logic이라는 말을

처음 듣습니다.

쉽게 말하면

> **서비스가 실제로 해야 하는 일**

입니다.

예를 들어

은행입니다.

```text
입금

출금

송금
```

이것이

Business Logic입니다.

---

AI 서비스에서는

```text
OCR

Embedding

LLM

Vector Search

RAG

Prompt 생성
```

이것이

Business Logic입니다.

---

### Router는 업무를 하지 않는다
여기서

아주 중요한 원칙이 있습니다.

```text
Router

↓

업무 안 함
```

Router는

그냥

전달합니다.

---

그림으로 보면

```text
Client

↓

Router

↓

Service

↓

Response
```

입니다.

---

### 왜 이렇게 분리할까?
예를 들어

Chat 기능이 있습니다.

Router 안에

모든 코드를 작성했습니다.

그러면

OCR에서도

같은 코드가 필요합니다.

Embedding에서도

같은 코드가 필요합니다.

복사합니다.

복사합니다.

또 복사합니다.

---

유지보수가

불가능해집니다.

---

Service로 분리하면

```text
Chat Router

↓

Chat Service

------------

OCR Router

↓

OCR Service

------------

Embedding Router

↓

Embedding Service
```

역할이

명확해집니다.

---

### 첫 번째 Service 만들기
프로젝트 구조를

조금 바꿔봅시다.

```text
app/

    routers/

    services/

        chat_service.py

    schemas/

    main.py
```

---

`chat_service.py`

```python
class ChatService:

    def chat(self):

        return {
            "answer":"Hello AI"
        }
```

---

Router

```python
@app.post("/chat")
def chat():

    service = ChatService()

    return service.chat()
```

학생들은

놀랍니다.

Router가

엄청 짧아졌습니다.

---

### 실행 과정
```text
Browser

↓

Router

↓

ChatService

↓

OpenAI

↓

Response DTO

↓

Browser
```

이것이

실제 AI Backend입니다.

---

### 앞으로 Service는 점점 커진다
현재는

```python
chat()
```

하나뿐입니다.

나중에는

```text
ChatService

↓

create_prompt()

↓

call_llm()

↓

save_history()

↓

calculate_tokens()

↓

build_response()
```

처럼

여러 메서드로

분리됩니다.

---

### AI Backend Architecture
여기서부터

AIKOS의

Backend 구조가

등장합니다.

```text
React

↓

Router

↓

Service

↓

Repository

↓

Database

↓

OpenAI
```

학생들은

이 그림을

앞으로 계속 보게 됩니다.

---

### 왜 Repository는 아직 안 나오나요?
좋은 질문입니다.

아직

Database를

배우지 않았습니다.

그래서

현재는

```text
Router

↓

Service
```

까지만

사용합니다.

Database를 배우는 Part에서

Repository가

추가됩니다.

이렇게 하면

학습 흐름이

매우 자연스럽습니다.

---

### AI 서비스 예제
Chat

```text
Chat Router

↓

Chat Service

↓

OpenAI
```

---

OCR

```text
OCR Router

↓

OCR Service

↓

OCR Engine
```

---

Embedding

```text
Embedding Router

↓

Embedding Service

↓

Embedding Model
```

---

Document

```text
Document Router

↓

Document Service

↓

Database
```

---

모든 기능이

같은 구조를

사용합니다.

---

### 실무 Best Practice
#### Router는 얇게(Thin Controller)
Router에서는

비즈니스 로직을

작성하지 않습니다.

좋은 Router는

보통

10~20줄 안쪽입니다.

---

#### Service는 하나의 책임만 가진다.
예를 들어

`ChatService`는

채팅만 담당합니다.

OCR까지

담당하지 않습니다.

---

#### Business Logic은 Service에 모은다.
Prompt 생성,

LLM 호출,

토큰 계산,

로그 저장,

DB 저장은

모두

Service의 역할입니다.

---

### 학생들이 가장 많이 하는 실수
##### 실수 ①
Router에서

OpenAI를 직접 호출한다.

---

##### 실수 ②
Router에서

DB를 직접 조회한다.

---

##### 실수 ③
Router에서

Validation 이후

모든 업무를 처리한다.

Router는

업무를 수행하는 곳이 아닙니다.

---

### AIKOS 핵심 그림
이번 Unit부터

AI Backend는

다음 구조를 사용합니다.

```text
Request

↓

Router

↓

Service

↓

(다음 Part)

Repository

↓

Database

↓

OpenAI

↓

Response DTO

↓

Client
```

이 구조는

Spring Boot의

Controller → Service → Repository와도 동일하며,

ASP.NET,

NestJS,

Laravel,

Django에서도

거의 같은 계층 구조를 사용합니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Service Layer와 Business Logic**을 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Router는 HTTP 요청을 받아 Service로 전달하는 역할**을 한다.
    
- **Business Logic은 Service Layer에 작성**하는 것이 실무 원칙이다.
    
- Router를 얇게 유지하면 코드의 재사용성과 유지보수성이 크게 향상된다.
    
- AI 서비스에서는 LLM 호출, Prompt 생성, OCR 처리, Embedding 생성, 토큰 계산 등이 모두 Service의 책임이다.
    
- 데이터 저장이 필요한 서비스에서는 Service 아래에 Repository Layer를 추가할 수 있다.
    

---

## Module 30. APIRouter와 기능별 모듈 분리


### Module 실습 예제

- [예제 1: router_prefix.py](examples/module_30/router_prefix.py) — APIRouter Prefix와 Tag로 기능 Route를 묶습니다.
- [예제 2: multi_router_app.py](examples/module_30/multi_router_app.py) — 여러 APIRouter를 하나의 애플리케이션에 조립합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 기능별 Endpoint를 분리하면서 하나의 앱으로 조립한다.
- **오늘 만드는 것:** documents·jobs APIRouter를 구성한다.
- **AI 플랫폼의 위치:** 요청을 기능별 모듈로 배치하는 입구다.
- **실무에서 많이 하는 실수:** prefix·tags·dependency를 여러 파일에 중복 선언한다.
- **5분 실습:** 새 Router를 만들고 main 앱에 한 번만 등록한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- APIRouter는 왜 필요한가?
    
- Router를 분리하지 않으면 어떤 문제가 생기는가?
    
- AI Backend에서는 Router를 어떻게 구성하는가?
    
- Service와 Router는 어떻게 연결되는가?
    
- 기능별 모듈화는 왜 중요한가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서는

Business Logic을

Service로 옮겼습니다.

Router는

아주 짧아졌습니다.

예를 들어

```python
@app.post("/chat")
def chat(request: ChatRequest):

    service = ChatService()

    return service.chat(request)
```

그런데

새로운 문제가 생깁니다.

---

서비스가 늘어나기 시작합니다.

```text
Chat

OCR

Embedding

Prompt

Document

Upload

Users

Auth

Vector

RAG

Agent
```

API도

같이 늘어납니다.

---

그러면

main.py는

어떻게 될까요?

---

### main.py가 거대해진다
처음에는

```text
@app.get("/")
```

하나였습니다.

---

하지만

AI Platform에서는

```text
@app.post("/chat")

@app.post("/upload")

@app.post("/ocr")

@app.post("/embedding")

@app.get("/documents")

@app.post("/documents")

@app.put("/documents/{id}")

@app.delete("/documents/{id}")

...

...
```

계속 늘어납니다.

---

결국

main.py는

1000줄이 됩니다.

학생들은

여기서

또 질문합니다.

> "파일을 나누고 싶은데요?"

바로

APIRouter가 등장하는 이유입니다.

---

### Service를 분리한 이유와 같다
잘 생각해보면

Service를 배운 이유와

똑같습니다.

처음에는

Router 안에

Business Logic이

모여 있었습니다.

↓

Service로 분리했습니다.

---

이번에는

main.py 안에

모든 Router가

모여 있습니다.

↓

Router를 분리합니다.

---

즉

같은 문제를

한 단계 더 해결하는 것입니다.

---

### Router는 기능별로 나눈다
AI Backend에서는

기능별로

Router를 나눕니다.

예를 들어

```text
Chat

OCR

Document

Embedding

User

Auth
```

각각

독립적인 Router를

가집니다.

---

### APIRouter란?
FastAPI는

Router도

객체(Object)입니다.

```python
from fastapi import APIRouter

router = APIRouter()
```

이 Router는

하나의 작은 FastAPI라고

생각하면 됩니다.

---

조금 과장해서 말하면

```text
FastAPI

↓

Router

↓

Mini FastAPI
```

입니다.

---

각 Router는

자기 Endpoint만

관리합니다.

---

### 첫 번째 Router
예를 들어

Chat 기능입니다.

```python
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
def chat():

    ...
```

학생들은

여기서

처음으로

```text
@router.post()
```

를 보게 됩니다.

---

왜

app이 아니라

router일까요?

---

이 Router는

아직

FastAPI에

등록되지 않았기 때문입니다.

---

### main.py의 역할
main.py는

모든 Router를

모읍니다.

```python
from routers.chat import router

app.include_router(router)
```

여기서

학생들은

중요한 개념을

배웁니다.

---

main.py는

API를

작성하는 곳이 아니라

조립하는 곳입니다.

---

이것이

AIKOS에서

가장 중요한

관점입니다.

---

### 조립(Composition)
현재 구조는

이렇습니다.

```text
main.py

↓

Chat Router

↓

Chat Service
```

---

조금 후에는

```text
main.py

↓

Chat Router

↓

Chat Service

-----------------

OCR Router

↓

OCR Service

-----------------

Embedding Router

↓

Embedding Service
```

---

main.py는

전체 시스템을

조립하는 역할만

합니다.

---

### AI Backend Architecture
이제

우리의 구조는

이렇게 됩니다.

```text
Client

↓

FastAPI

↓

Chat Router

↓

Chat Service

↓

OpenAI

----------------

OCR Router

↓

OCR Service

↓

OCR Engine

----------------

Document Router

↓

Document Service

↓

Repository
```

학생들은

처음으로

기능별 Backend를

보게 됩니다.

---

### include_router()
FastAPI는

Router를

등록합니다.

```python
app.include_router(chat_router)
```

이 의미는

```text
Chat Router를

Backend에

연결한다.
```

입니다.

---

여러 개라면

```python
app.include_router(chat_router)

app.include_router(ocr_router)

app.include_router(document_router)
```

처럼

계속 연결합니다.

---

### Prefix
실무에서는

거의 항상

Prefix를 사용합니다.

예를 들어

```python
router = APIRouter(
    prefix="/chat"
)
```

그러면

```text
@router.post("/")
```

가

실제로는

```text
POST

/chat
```

이 됩니다.

---

OCR

```python
prefix="/ocr"
```

↓

```text
POST /ocr
```

---

Document

```python
prefix="/documents"
```

↓

```text
GET /documents

POST /documents
```

---

학생들이

이 Prefix를

굉장히 좋아합니다.

왜냐하면

URL 관리가

매우 쉬워지기 때문입니다.

---

### Tags
Swagger를

보면

API가

엄청 많아집니다.

그래서

Tag를 사용합니다.

```python
router = APIRouter(

    prefix="/chat",

    tags=["Chat"]

)
```

그러면

Swagger에서

```text
Chat

▼

POST /chat

GET /chat/history
```

처럼

그룹으로

보입니다.

---

AI 서비스에서는

Tag를

반드시 사용하는 것이 좋습니다.

---

### AI Platform 구조
AIKOS에서는

다음 구조를

사용합니다.

```text
routers/

    chat.py

    document.py

    embedding.py

    ocr.py

    upload.py

    auth.py
```

Service도

같습니다.

```text
services/

    chat_service.py

    document_service.py

    embedding_service.py

    ocr_service.py

    upload_service.py
```

이 구조는

뒤에서 배울

Project Structure와

연결됩니다.

---

### 실행 흐름
학생들이

반드시 이해해야 하는

흐름입니다.

```text
Browser

↓

FastAPI

↓

Chat Router

↓

Chat Service

↓

OpenAI

↓

Response DTO

↓

Browser
```

---

### 실무 Best Practice
#### Router는 Endpoint만 관리한다.
Router에는

Business Logic을

넣지 않습니다.

---

#### Router는 기능별로 나눈다.
좋은 예

```text
chat.py

ocr.py

document.py
```

나쁜 예

```text
api.py
```

하나의 파일에

모든 API를

넣지 않습니다.

---

#### Prefix를 적극 사용한다.
```text
/chat

/ocr

/documents

/users
```

이렇게 Resource 단위로

구성합니다.

---

#### Tags를 사용하여 Swagger를 정리한다.
API가 50개만 넘어가도

Tag가 없으면

Swagger를

사용하기 어렵습니다.

---

### 학생들이 가장 많이 하는 실수
##### ① Router마다 FastAPI()를 새로 만든다.
```python
app = FastAPI()
```

를

Router 파일에

작성하면 안 됩니다.

Router는

```python
router = APIRouter()
```

를 사용합니다.

---

##### ② main.py에서 API를 계속 만든다.
main.py는

조립(Composition)만

담당합니다.

---

##### ③ Prefix 없이 URL을 반복 작성한다.
```text
@router.post("/chat")

@router.get("/chat/history")
```

보다

```python
prefix="/chat"
```

를 사용하는 것이

더 좋습니다.

---

### AIKOS 핵심 그림
```text
                FastAPI

                    │

    ┌───────────────┼───────────────┐

    ▼               ▼               ▼

Chat Router     OCR Router     Document Router

    │               │               │

    ▼               ▼               ▼

Chat Service   OCR Service   Document Service

    │               │               │

    ▼               ▼               ▼

 OpenAI        OCR Engine      Repository
```

이 그림이

AIKOS Backend의

기본 아키텍처입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **APIRouter와 기능별 모듈 분리**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **APIRouter는 기능별 Endpoint를 관리하는 독립적인 Router 객체**이다.
    
- `main.py`는 API를 작성하는 곳이 아니라 **각 Router를 조립(Composition)하는 곳**이다.
    
- Router는 기능(Chat, OCR, Document 등) 단위로 분리하는 것이 실무 표준이다.
    
- `prefix`와 `tags`를 활용하면 URL 관리와 Swagger 문서 구성이 훨씬 쉬워진다.
    
- Router는 Endpoint만 담당하고, Business Logic은 Service Layer에 두는 것이 AI Backend의 기본 설계 원칙이다.
    

---

## Module 31. AI Backend Project Structure와 Layered Architecture


### Module 실습 예제

- [예제 1: layered_single_file.py](examples/module_31/layered_single_file.py) — Router·Service·Client의 의존 방향을 한 파일에서 확인합니다.
- [예제 2: dependency_direction.py](examples/module_31/dependency_direction.py) — 상위 계층이 구체 Provider 대신 Protocol에 의존하게 만듭니다.



#### 프로젝트 연결 학습
- **문제 상황:** 파일 수가 늘어도 의존 방향을 읽을 수 있게 한다.
- **오늘 만드는 것:** Router → Service → Repository/Client 구조를 만든다.
- **AI 플랫폼의 위치:** AI 플랫폼 전체 소스 구조의 기준이다.
- **실무에서 많이 하는 실수:** 폴더 이름만 Layered Architecture로 만들고 역방향 import를 허용한다.
- **5분 실습:** 각 계층이 import할 수 있는 대상을 표로 적는다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Layered Architecture란 무엇인가?
    
- 왜 Backend를 Layer로 나누는가?
    
- 각 Layer는 어떤 역할을 하는가?
    
- 의존성은 어떤 방향으로 흘러야 하는가?
    
- AI Backend는 어떤 프로젝트 구조를 사용하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit까지

우리는

Router와

Service를

분리했습니다.

학생들은

곧바로

질문합니다.

> Router와 Service는 어디에 두나요?

그래서

처음에는

이렇게 만듭니다.

```
backend/

    main.py

    chat.py

    ocr.py

    service.py

    utils.py

    helper.py

    test.py

    ...
```

---

처음에는

괜찮아 보입니다.

---

하지만

프로젝트가

커집니다.

```
Chat

OCR

Embedding

RAG

Prompt

User

Document

Upload

Agent

History

Admin
```

파일이

계속 증가합니다.

---

결국

```
backend/

    chat.py

    chat2.py

    chat_utils.py

    chat_service.py

    ocr.py

    ocr2.py

    ...

    80개 파일
```

학생들은

원하는 파일을

찾지 못합니다.

---

그래서

Layer가

등장합니다.

---

### Layer란?
Layer는

역할(Role)별로

구분하는 것입니다.

쉽게 말하면

회사를 생각하면 됩니다.

```
대표

↓

영업

↓

개발

↓

회계
```

모든 사람이

모든 일을

하지 않습니다.

---

Backend도

같습니다.

```
Router

↓

Service

↓

Repository

↓

Database
```

각각

하는 일이

다릅니다.

---

### AIKOS 핵심 원칙
Layer는

**기능이 아니라 책임(Responsibility)** 으로 나눕니다.

예를 들어

잘못된 구조는

```
Chat

↓

OCR

↓

User

↓

Database
```

기능과 기술이

섞여 있습니다.

---

좋은 구조는

```
HTTP

↓

Business

↓

Data

↓

Infrastructure
```

입니다.

---

### Layer의 역할
먼저

전체 구조를

보겠습니다.

```
React

↓

FastAPI

↓

Router

↓

Service

↓

Repository

↓

Database
```

---

각 Layer를

설명해보겠습니다.

---

### Router Layer
Router는

HTTP만

압니다.

```
GET

POST

PUT

DELETE
```

만

관심 있습니다.

---

Router는

절대로

DB를

알면 안 됩니다.

---

Router는

Service만

호출합니다.

```
Request

↓

Router

↓

Service
```

---

### Service Layer
Service는

Business Logic입니다.

예를 들어

Chat입니다.

```
Prompt 생성

↓

LLM 호출

↓

History 저장

↓

Response 생성
```

Service는

HTTP를

몰라도 됩니다.

---

즉

```
POST

GET

Header

Body
```

를

알 필요가 없습니다.

---

Service는

업무만

알면 됩니다.

---

### Repository Layer
아직

배우지 않았지만

미리 구조를

보겠습니다.

Repository는

Database만

압니다.

```
SELECT

INSERT

UPDATE

DELETE
```

를

담당합니다.

---

Service는

SQL을

몰라도 됩니다.

---

### Database
가장 아래입니다.

```
MySQL

PostgreSQL

SQLite
```

입니다.

---

### 의존성 방향
AIKOS에서

가장 중요한

그림입니다.

```
Router

↓

Service

↓

Repository

↓

Database
```

반대로

올라가면

안 됩니다.

---

예를 들어

Repository가

Router를

호출하면

안 됩니다.

---

Service가

Router를

호출해도

안 됩니다.

---

의존성은

항상

한 방향입니다.

---

### 왜 한 방향일까?
학생들이

많이 궁금해합니다.

예를 들어

Router가

Service를

호출합니다.

```
Router

↓

Service
```

---

그런데

Service도

Router를

호출하면?

```
Router

↓

Service

↑

──────
```

순환(Circular Dependency)이

발생합니다.

---

프로젝트는

점점

복잡해집니다.

---

그래서

Layer는

항상

아래 방향으로만

흐릅니다.

---

### AI Backend Architecture
AI 서비스를

예로 들어보겠습니다.

```
React

↓

POST /chat

↓

Chat Router

↓

Chat Service

↓

Prompt Builder

↓

OpenAI

↓

Repository

↓

Database

↓

Response DTO

↓

React
```

학생들은

처음으로

AI 서비스의

전체 구조를

보게 됩니다.

---

### AIKOS 표준 프로젝트 구조
여기서부터는

AIKOS 표준 구조를

사용합니다.

```
backend/

│

├── app/

│   ├── routers/

│   ├── services/

│   ├── repositories/

│   ├── schemas/

│   ├── models/

│   ├── core/

│   ├── db/

│   ├── utils/

│   └── main.py

│

├── tests/

│

├── uploads/

│

├── requirements.txt

│

└── .env
```

---

학생들이

처음에는

폴더가

많다고

느낍니다.

---

하지만

프로젝트가

커질수록

오히려

찾기 쉽습니다.

---

### 폴더 역할
#### routers/
```
HTTP API
```

만

관리합니다.

---

#### services/
```
Business Logic
```

를

작성합니다.

---

#### repositories/
```
Database 접근
```

을

담당합니다.

---

#### schemas/
```
DTO

Request

Response
```

를

관리합니다.

---

#### models/
```
ORM Model

Database Model
```

입니다.

(SQLAlchemy에서 자세히 다룹니다.)

---

#### core/
```
환경설정

Security

Middleware

Dependency
```

같이

프로젝트 전체에서

사용하는 기능을

관리합니다.

---

#### db/
```
Database 연결

Session 생성
```

입니다.

---

#### utils/
```
공통 함수
```

입니다.

---

### 실행 흐름
학생들이

반드시

외워야 하는

구조입니다.

```
React

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Response DTO

↓

React
```

이 구조는

AIKOS 전체에서

계속 사용됩니다.

---

### 실무 Best Practice
#### Layer를 건너뛰지 않는다.
좋은 구조

```
Router

↓

Service

↓

Repository
```

---

좋지 않은 구조

```
Router

↓

Database
```

---

#### Repository는 SQL만 담당한다.
Business Logic을

넣지 않습니다.

---

#### Service는 HTTP를 모른다.
Service는

FastAPI 없이도

동작할 수 있어야 합니다.

---

#### Router는 가장 얇게 유지한다.
Router에는

Business Logic을

넣지 않습니다.

---

### 학생들이 가장 많이 하는 실수
##### ① Router에서 Database를 조회한다.
잘못된 구조입니다.

---

##### ② Service에서 SQL을 작성한다.
Repository의

역할입니다.

---

##### ③ Utility에 모든 코드를 넣는다.
`utils.py`가

만능 파일이 되면

유지보수가

어려워집니다.

---

##### ④ Layer를 건너뛴다.
```
Router

↓

Database
```

는

AIKOS에서는

사용하지 않습니다.

---

### AIKOS 핵심 그림
```
                React

                  │

                  ▼

              FastAPI

                  │

                  ▼

              Router Layer

                  │

                  ▼

             Service Layer

                  │

                  ▼

          Repository Layer

                  │

                  ▼

             Database / AI

                  │

                  ▼

             Response DTO

                  │

                  ▼

                React
```

이 그림이

AIKOS Backend의

표준 아키텍처입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **AI Backend Project Structure와 Layered Architecture**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Layer는 기능이 아니라 책임(Responsibility)을 기준으로 분리**한다.
    
- **Router → Service → Repository → Database** 방향으로만 의존성이 흐르는 것이 기본 원칙이다.
    
- Router는 HTTP를, Service는 Business Logic을, Repository는 데이터 접근을 담당한다.
    
- AIKOS 표준 프로젝트 구조는 역할별 폴더를 기준으로 설계하여 유지보수성과 확장성을 높인다.
    
- 이 구조는 FastAPI뿐 아니라 Spring Boot, ASP.NET, NestJS 등 대부분의 실무 백엔드 프레임워크에서 공통적으로 사용된다.
    

---

## Module 32. Dependency Injection(DI)와 객체 생명주기


### Module 실습 예제

- [예제 1: depends_service.py](examples/module_32/depends_service.py) — Depends로 Service 생성과 주입을 FastAPI에 맡깁니다.
- [예제 2: override_dependency.py](examples/module_32/override_dependency.py) — Dependency Override로 실제 구현을 Fake로 교체합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 객체 생성과 수명주기를 Handler 밖에서 관리한다.
- **오늘 만드는 것:** DB Session·Service·AI Client Dependency를 구성한다.
- **AI 플랫폼의 위치:** 요청마다 필요한 협력 객체를 연결하는 조립 지점이다.
- **실무에서 많이 하는 실수:** Depends를 Service Locator처럼 남용하거나 수명주기를 무시한다.
- **5분 실습:** FakeAIClient를 주입해 Provider 호출 없이 테스트한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Dependency란 무엇인가?
    
- 객체(Object)는 누가 생성하는가?
    
- Dependency Injection은 왜 등장했는가?
    
- FastAPI의 Depends()는 무엇을 하는가?
    
- AI Backend에서는 왜 DI를 사용하는가?
    

---

### ① 문제 이해 (Why)
지난 Unit에서

우리는

Service를 만들었습니다.

```python
class ChatService:

    def chat(self):
        ...
```

Router에서는

이렇게 사용했습니다.

```python
service = ChatService()

service.chat()
```

처음에는

아무 문제가 없습니다.

---

그런데

서비스가 늘어납니다.

```text
ChatService

OCRService

EmbeddingService

PromptService

DocumentService
```

그리고

각 Service마다

또 다른 객체가 필요합니다.

예를 들어

```python
class ChatService:

    def __init__(self):

        self.prompt = PromptBuilder()

        self.client = OpenAIClient()

        self.repository = ChatRepository()
```

학생들은

처음에는

이렇게 작성합니다.

---

문제는

객체를

객체가

계속 만들기 시작합니다.

---

### 객체가 객체를 만드는 문제
조금만 커져도

이렇게 됩니다.

```text
Router

↓

ChatService

↓

PromptBuilder

↓

OpenAIClient

↓

Tokenizer

↓

Repository

↓

Database
```

모든 객체가

직접

새 객체를

생성합니다.

---

그러면

무슨 문제가 생길까요?

---

### 강한 결합(Strong Coupling)
ChatService는

항상

```python
OpenAIClient()
```

만

사용할 수 있습니다.

---

만약

나중에

Claude를

사용하고 싶다면?

```python
ClaudeClient()
```

로

모든 코드를

수정해야 합니다.

---

즉

객체들이

너무 강하게

묶여 있습니다.

이것을

**Strong Coupling**

이라고 합니다.

---

### 현실로 비유해 보자
회사에서

직원을

채용합니다.

개발자가

직접

노트북을 만들까요?

```text
개발자

↓

노트북 제작

↓

업무 시작
```

아닙니다.

---

회사가

노트북을

준비합니다.

```text
회사

↓

노트북 지급

↓

개발자
```

즉

필요한 것을

밖에서

넣어줍니다.

---

이것이

Dependency Injection입니다.

---

### Dependency란?
Dependency는

의존성입니다.

쉽게 말하면

```text
A가

B가 있어야

동작한다.
```

입니다.

예를 들어

```text
class ChatService:

    def __init__(

        self,

        repository

    ):
```

ChatService는

Repository에

의존합니다.

---

즉

```text
ChatService

↓

Repository
```

의존 관계가

생깁니다.

---

### Injection이란?
Injection은

주입입니다.

즉

밖에서

넣어주는 것입니다.

---

기존 방식

```python
repository = Repository()

service = ChatService(repository)
```

객체를

직접 만듭니다.

---

DI 방식

```text
Framework

↓

Repository 생성

↓

ChatService 생성

↓

Router 전달
```

Framework가

대신 만들어 줍니다.

---

### 객체 생명주기(Lifecycle)
여기서

학생들이

처음 듣는

개념이 나옵니다.

Lifecycle입니다.

질문입니다.

```python
ChatService()
```

는

언제

생성될까요?

---

매 요청마다?

---

프로그램 시작할 때?

---

하나만?

---

이것을

Lifecycle이라고 합니다.

---

### FastAPI는 객체를 관리한다
FastAPI는

필요한 순간에

객체를

생성합니다.

우리가

```python
Depends(...)
```

를

사용하면

FastAPI가

객체를

관리하기 시작합니다.

---

### Depends()
FastAPI에서는

이렇게 작성합니다.

```text
from fastapi import Depends


@app.post("/chat")
def chat(

    service:

    ChatService = Depends()

):
```

학생들은

여기서

질문합니다.

---

왜

```python
ChatService()
```

를

안 쓰나요?

---

정답은

FastAPI가

대신

객체를

생성하기 때문입니다.

---

### 내부 동작
학생들이

반드시

이해해야 하는

그림입니다.

```text
Browser

↓

Router

↓

FastAPI

↓

Depends()

↓

ChatService 생성

↓

Router

↓

chat()
```

우리는

생성하지 않았습니다.

Framework가

생성했습니다.

---

### AI Backend에서는?
예를 들어

ChatService입니다.

```text
ChatService

↓

OpenAI Client

↓

Prompt Builder

↓

Repository
```

모두

Dependency입니다.

---

FastAPI는

이 객체들을

관리할 수 있습니다.

---

### 왜 중요한가?
나중에

OpenAI 대신

Ollama를

사용합니다.

기존

```text
ChatService

↓

OpenAI
```

↓

변경

```text
ChatService

↓

Ollama
```

Service는

거의

변경되지 않습니다.

---

즉

확장성이

좋아집니다.

---

### AIKOS AI Backend 구조
```text
Client

↓

Router

↓

Depends()

↓

ChatService

↓

Repository

↓

Database

↓

OpenAI
```

학생들은

여기서

Framework가

객체를

관리한다는 것을

처음 이해합니다.

---

### 실무 Best Practice
#### 객체를 직접 생성하지 않는다.
좋지 않은 예

```python
service = ChatService()
```

---

가능하면

Framework가

생성하도록

한다.

---

#### Service는 구현이 아니라 인터페이스에 의존한다.
(지금은 개념만 소개)

```text
ChatService

↓

LLMClient

↓

OpenAI

Claude

Ollama
```

이 구조는

나중에

LLM 교체를

쉽게 합니다.

---

#### 객체 생명주기를 고려한다.
매 요청마다

생성해야 하는 객체와

프로그램 시작 시

한 번만 생성하는 객체를

구분해야 합니다.

예를 들어

```text
OpenAI Client

↓

재사용 가능

----------------

Request DTO

↓

요청마다 생성
```

이 차이는

나중에 성능에도

큰 영향을 줍니다.

---

### 학생들이 가장 많이 하는 실수
##### ① Router에서 계속 객체를 생성한다.
```python
ChatService()

OpenAI()

Repository()
```

를

매 요청마다

직접 생성합니다.

---

##### ② Service 안에서 또 객체를 생성한다.
```python
OpenAIClient()
```

를

Service 안에서

직접 생성합니다.

---

##### ③ DI를 단순 문법으로 외운다.
DI는

문법이 아니라

**객체 관리 전략**입니다.

---

### AIKOS 핵심 그림
```text
              FastAPI

                  │

                  ▼

          Dependency Injection

                  │

      ┌───────────┴───────────┐

      ▼                       ▼

 ChatService           DocumentService

      │                       │

      ▼                       ▼

 Repository             Repository

      │                       │

      ▼                       ▼

 Database               Database
```

Framework가

객체를

생성하고

연결합니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Dependency Injection과 객체 생명주기**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Dependency**는 하나의 객체가 다른 객체를 필요로 하는 관계이다.
    
- **Dependency Injection(DI)** 은 필요한 객체를 외부에서 생성하여 주입하는 방식이다.
    
- FastAPI의 `Depends()`는 객체 생성을 Framework에 맡기는 메커니즘이다.
    
- DI를 사용하면 객체 간 결합도가 낮아지고 테스트와 유지보수가 쉬워진다.
    
- AI 서비스에서는 LLM Client, Repository, 설정 객체 등 공통 컴포넌트를 효율적으로 관리하기 위해 DI를 적극 활용한다.
    

---

### Project Connection
이제 AIKOS Backend의 핵심 구조가 거의 완성되었습니다.

```text
React
      │
      ▼
FastAPI
      │
      ▼
Router
      │
      ▼
Depends (DI)
      │
      ▼
Service
      │
      ▼
Repository
      │
      ▼
Database / AI Engine
      │
      ▼
Response DTO
      │
      ▼
React
```

---

## Module 33. Configuration(Settings)과 환경설정 관리


### Module 실습 예제

- [예제 1: settings_env.py](examples/module_33/settings_env.py) — Pydantic Settings로 환경변수를 타입 안전하게 읽습니다.
- [예제 2: cached_settings.py](examples/module_33/cached_settings.py) — Settings 객체를 캐시해 재사용합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 코드 변경 없이 환경별 설정을 바꾼다.
- **오늘 만드는 것:** Settings 모델에서 DB URL과 AI 설정을 읽는다.
- **AI 플랫폼의 위치:** 애플리케이션 조립과 외부 인프라 선택에 사용한다.
- **실무에서 많이 하는 실수:** 비밀값을 저장소에 커밋하거나 import 때마다 Settings를 새로 만든다.
- **5분 실습:** 필수 환경변수가 없을 때 조기에 실패하게 만든다.

> **학습 층위 — 기초**  
> 이 Unit은 Settings를 코드와 분리하고 Dependency로 전달하는 기본을 다룬다. 이어지는 AI Provider 설정에서 Provider별 구성으로 확장하고, 후속 운영 과정에서는 Secret·Fail Fast 정책으로 심화한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Configuration은 왜 필요한가?
    
- 왜 API Key를 코드에 작성하면 안 되는가?
    
- .env는 무엇인가?
    
- FastAPI에서는 설정을 어떻게 관리하는가?
    
- AI 서비스에서는 어떤 설정들을 관리하는가?
    

---

### ① 문제 이해 (Why)
AI Chat 서비스를 만들어 봅시다.

OpenAI를 연결합니다.

학생들은 대부분 이렇게 작성합니다.

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxxxxxxxxxx"
)
```

잘 동작합니다.

문제가 없어 보입니다.

---

며칠 후

GitHub에 Push합니다.

```text
git push origin main
```

API Key도

같이 올라갑니다.

---

누군가

그 Key를 사용합니다.

```text
OpenAI

↓

LLM 호출

↓

과금
```

개발자가

돈을 내는 상황도

발생할 수 있습니다.

---

그래서

실무에서는

절대로

API Key를

코드에 작성하지 않습니다.

---

### Configuration이란?
Configuration은

프로그램이 실행되기 전에

필요한 설정입니다.

예를 들어

```text
OpenAI API Key

Database URL

Upload Path

Secret Key

Debug 여부
```

이런 것들은

프로그램의

동작 방식을

결정합니다.

---

### Configuration과 Business Logic은 다르다
학생들이

많이 혼동합니다.

예를 들어

```python
ChatService.chat()
```

이것은

Business Logic입니다.

---

반면

```text
OPENAI_API_KEY
```

는

환경설정입니다.

---

즉

```text
Business Logic

↓

무엇을 할 것인가?

--------------------

Configuration

↓

어떻게 실행할 것인가?
```

입니다.

---

### 환경(Environment)이란?
실무에서는

프로그램이

한 곳에서만

실행되지 않습니다.

예를 들어

```text
개발 PC

↓

테스트 서버

↓

운영 서버
```

모두

설정이 다릅니다.

---

개발 환경에서는

```text
Debug = True
```

---

운영 환경에서는

```text
Debug = False
```

입니다.

---

Database도

다릅니다.

---

개발

```text
SQLite
```

---

운영

```text
PostgreSQL
```

---

그래서

설정을

분리해야 합니다.

---

### .env 파일
가장 많이 사용하는

방법입니다.

예를 들어

```text
OPENAI_API_KEY=sk-xxxxxxxx

DATABASE_URL=postgres://...

DEBUG=True

UPLOAD_PATH=uploads/
```

코드에는

이 값이

없습니다.

---

### 코드에서는?
```python
from os import getenv

api_key = getenv("OPENAI_API_KEY")
```

또는

FastAPI에서는

조금 더 좋은 방법을

사용합니다.

---

### Pydantic Settings
AIKOS에서는

FastAPI 표준 방식을

사용합니다.

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    openai_api_key: str

    database_url: str

    debug: bool = False


settings = Settings()
```

학생들은

여기서

질문합니다.

---

왜

또

Pydantic인가요?

---

### AIKOS 연결
여기서

Phase1의

모든 내용이

연결됩니다.

우리는

이미

Pydantic을

배웠습니다.

Pydantic은

외부 데이터를

Python 객체로

변환합니다.

---

이번에는

JSON이 아니라

환경변수입니다.

```text
Environment Variables

↓

Pydantic Settings

↓

Python Object
```

즉

원리는

똑같습니다.

---

### Settings 객체
이제

프로젝트 어디에서든

사용합니다.

```python
settings.openai_api_key

settings.database_url

settings.debug
```

학생들은

처음으로

Configuration도

객체라는 것을

이해합니다.

---

### AI Backend에서는?
예를 들어

OpenAI입니다.

```python
client = OpenAI(

    api_key=settings.openai_api_key

)
```

---

Database

```python
settings.database_url
```

---

Upload

```python
settings.upload_path
```

---

OCR

```python
settings.ocr_model
```

---

Embedding

```python
settings.embedding_model
```

---

모든 설정이

Settings 객체에

모입니다.

---

### Configuration도 Dependency이다
여기서

지난 Unit과

연결됩니다.

Settings도

객체입니다.

즉

Dependency입니다.

```text
Router

↓

Service

↓

Settings
```

DI를

사용하면

Settings도

주입할 수 있습니다.

---

### 실행 과정
```text
프로그램 시작

↓

.env 읽기

↓

Settings 생성

↓

FastAPI 시작

↓

Service에서 사용
```

중요한 점은

매 요청마다

읽지 않습니다.

프로그램 시작 시

한 번만

읽습니다.

---

### AIKOS 표준 구조
```text
app/

    core/

        settings.py

        security.py

        logging.py
```

Settings는

core에

둡니다.

왜냐하면

프로젝트 전체가

사용하기 때문입니다.

---

### Dev / Test / Prod
실무에서는

환경이

여러 개입니다.

```text
Development

↓

Testing

↓

Production
```

각 환경은

다른

Configuration을

가집니다.

예를 들어

```text
.env.dev

.env.test

.env.prod
```

처럼

관리하기도 합니다.

---

### AI 서비스 예제
AI 플랫폼에서는

설정이

엄청 많습니다.

```text
OpenAI Model

Temperature

Max Tokens

Embedding Model

OCR Engine

Upload Path

Vector DB URL

Redis URL

JWT Secret

Database URL
```

이 모든 것을

Settings가

관리합니다.

---

### 실무 Best Practice
#### API Key는 절대 코드에 작성하지 않는다.
좋은 예

```python
settings.openai_api_key
```

---

좋지 않은 예

```python
"sk-xxxxxxxx"
```

---

#### Settings는 하나로 관리한다.
프로젝트마다

여러 개의

환경설정 클래스를

만들지 않습니다.

하나의 Settings를

중심으로

관리하는 것이 좋습니다.

(프로젝트가 매우 커지면 기능별 설정 클래스로 나눌 수 있지만, AIKOS에서는 하나의 Settings 객체부터 시작합니다.)

---

#### .env는 Git에 올리지 않는다.
반드시

`.gitignore`에

추가합니다.

```text
.env
```

---

#### Configuration은 Business Logic에서 분리한다.
Service 안에

환경변수를

직접 읽지 않습니다.

---

### 학생들이 가장 많이 하는 실수
##### ① API Key를 GitHub에 올린다.
가장 위험한 실수입니다.

---

##### ② Service에서 os.getenv()를 계속 호출한다.
Settings 객체를

사용하는 것이

더 좋습니다.

---

##### ③ 개발 환경과 운영 환경을 같은 설정으로 사용한다.
실무에서는

환경별

설정을 분리합니다.

---

##### ④ 설정을 여러 파일에서 중복 관리한다.
Settings 객체를

프로젝트의

단일 진실 공급원(Single Source of Truth)으로 유지하는 것이 좋습니다.

---

### AIKOS 핵심 그림
```text
          .env

            │

            ▼

    Pydantic Settings

            │

            ▼

     Configuration Object

            │

            ▼

 Dependency Injection

            │

            ▼

 Service Layer

            │

            ▼

 OpenAI / Database
```

Configuration도

AI Backend의

하나의 객체입니다.

---

### 핵심 내용 정리
이번 Unit에서는 **Configuration(Settings)과 환경설정 관리**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Configuration은 프로그램 실행 방식을 결정하는 설정 정보**이다.
    
- API Key, Database URL, Debug 여부 등은 코드가 아니라 환경설정으로 관리한다.
    
- FastAPI에서는 **Pydantic Settings**를 이용하여 환경변수를 객체로 관리하는 것이 일반적이다.
    
- Settings 객체는 DI와 함께 사용되어 프로젝트 전반에서 일관된 설정을 제공한다.
    
- AI 서비스에서는 OpenAI, OCR, Embedding, Database, JWT 등 거의 모든 외부 시스템이 Settings를 통해 구성된다.
    

---

## Module 34. Exception Handling과 표준 오류 응답


### Module 실습 예제

- [예제 1: domain_exception.py](examples/module_34/domain_exception.py) — Domain Exception을 HTTP 오류 응답으로 변환합니다.
- [예제 2: standard_error.py](examples/module_34/standard_error.py) — 표준 Error Response Model을 사용합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 오류를 일관된 API 계약으로 변환한다.
- **오늘 만드는 것:** 도메인 예외와 표준 Error Response를 연결한다.
- **AI 플랫폼의 위치:** Service 실패가 클라이언트 응답으로 바뀌는 경계다.
- **실무에서 많이 하는 실수:** 모든 예외를 500으로 숨기거나 내부 메시지를 그대로 노출한다.
- **5분 실습:** NotFound와 ProviderTimeout을 서로 다른 응답으로 매핑한다.


### 이번 학습 목표
이번 Unit이 끝나면 다음 질문에 자신의 언어로 답할 수 있어야 합니다.

- Exception과 Error Response는 무엇이 다른가?
    
- 왜 Router마다 `try-except`를 작성하면 안 되는가?
    
- FastAPI의 `HTTPException`은 언제 사용하는가?
    
- 사용자 정의 예외는 왜 필요한가?
    
- 전역 Exception Handler는 어떤 역할을 하는가?
    
- Validation 오류와 Business 오류는 무엇이 다른가?
    
- AI 서비스의 오류 응답은 어떤 구조로 설계해야 하는가?
    
- Middleware와 Exception Handler는 어떻게 역할을 나누는가?
    

---

### ① 문제 이해 (Why)
지금까지 우리는 요청이 정상적으로 처리되는 흐름을 중심으로 학습했습니다.

```text
Request

↓

Middleware

↓

Router

↓

Service

↓

Repository / AI Engine

↓

Response
```

하지만 실제 서비스에서는 모든 요청이 성공하지 않습니다.

예를 들어 문서를 조회합니다.

```text
GET /documents/100
```

그런데 100번 문서가 존재하지 않습니다.

Chat API를 호출합니다.

```text
POST /chat
```

그런데 OpenAI API 호출에 실패합니다.

파일을 업로드합니다.

```text
POST /documents
```

그런데 지원하지 않는 파일 형식입니다.

이런 상황에서 서버는 무엇을 반환해야 할까요?

---

### 학습자가 만드는 오류 처리
처음에는 각 Router에 다음과 같이 작성합니다.

```python
@router.get("/documents/{document_id}")
async def get_document(document_id: int):
    try:
        document = document_service.get_document(
            document_id
        )

        return document

    except Exception:
        return {
            "message": "오류가 발생했습니다."
        }
```

겉보기에는 오류를 처리한 것처럼 보입니다.

하지만 문제가 많습니다.

---

### 문제 1. 성공과 실패의 HTTP Status Code가 같다
위 코드는 오류가 발생해도 일반적으로 성공 응답처럼 처리될 수 있습니다.

```text
HTTP 200 OK

{
    "message": "오류가 발생했습니다."
}
```

Client는 HTTP Status Code를 보고 요청 성공 여부를 판단합니다.

그런데 상태는 `200 OK`이고 Body만 오류 메시지라면 React는 이것을 성공으로 해석할 수 있습니다.

---

### 문제 2. 모든 오류가 같은 메시지가 된다
실제 원인은 다를 수 있습니다.

```text
문서 없음

권한 없음

DB 연결 실패

외부 API Timeout

잘못된 파일 형식
```

그런데 모두 다음 응답이 됩니다.

```json
{
    "message": "오류가 발생했습니다."
}
```

Client는 어떤 문제인지 알 수 없습니다.

운영자도 원인을 추적하기 어렵습니다.

---

### 문제 3. Router마다 같은 코드가 반복된다
```text
Chat Router

↓

try-except

Document Router

↓

try-except

OCR Router

↓

try-except

Upload Router

↓

try-except
```

API가 많아질수록 중복도 증가합니다.

오류 응답 형식을 변경하려면 모든 Router를 수정해야 합니다.

---

### 우리가 원하는 구조
각 Layer는 자신의 책임만 수행해야 합니다.

```text
Router

↓

Request 전달

Service

↓

Business Logic 수행

Exception Handler

↓

오류를 HTTP Response로 변환
```

즉, Router마다 오류 응답을 직접 만드는 것이 아니라 **발생한 예외를 중앙에서 일관된 Response로 변환**해야 합니다.

---

### ② 개념 이해 (Concept)
#### Exception이란?
Exception은 프로그램 실행 중 정상 흐름을 계속할 수 없는 상황을 표현하는 Python 객체입니다.

예를 들어 다음과 같습니다.

```python
raise ValueError("잘못된 값입니다.")
```

`raise`가 실행되면 현재 코드의 정상 흐름이 중단되고, 예외를 처리할 수 있는 곳으로 이동합니다.

---

### Exception과 Error Response는 다르다
이 차이가 매우 중요합니다.

#### Exception
서버 내부에서 발생합니다.

```text
DocumentNotFoundError

InvalidFileTypeError

LLMTimeoutError
```

---

#### Error Response
Client에게 전달되는 HTTP 응답입니다.

```json
{
    "code": "DOCUMENT_NOT_FOUND",
    "message": "문서를 찾을 수 없습니다."
}
```

즉, 다음 변환 과정이 필요합니다.

```text
Python Exception

↓

Exception Handler

↓

HTTP Status Code + JSON Response
```

---

### AIKOS 핵심 정의
> **Exception Handling은 서버 내부의 실패 상황을 Client가 이해할 수 있는 표준 HTTP 응답으로 변환하는 과정이다.**

---

### 오류 처리 파이프라인
정상 흐름은 다음과 같습니다.

```text
Request

↓

Router

↓

Service

↓

Response DTO

↓

Client
```

오류 흐름은 다음과 같습니다.

```text
Request

↓

Router

↓

Service

↓

Exception 발생

↓

Exception Handler

↓

Error Response DTO

↓

Client
```

두 흐름을 합치면 다음과 같습니다.

```text
                    ┌── 성공 ──→ Response DTO
Request → Service ──┤
                    └── 실패 ──→ Exception
                                      │
                                      ▼
                              Exception Handler
                                      │
                                      ▼
                               Error Response DTO
```

---

### ③ 오류의 종류
Backend 오류를 모두 같은 종류로 보면 안 됩니다.

AIKOS에서는 크게 네 종류로 구분합니다.

```text
1. Request Validation Error

2. Business Exception

3. External System Exception

4. Unexpected Server Error
```

하나씩 살펴보겠습니다.

---

### 1. Request Validation Error
Client가 형식에 맞지 않는 데이터를 보냈습니다.

예를 들어 모델이 다음과 같습니다.

```python
class ChatRequest(BaseModel):
    question: str
```

그런데 Client가 다음 요청을 보냅니다.

```json
{
    "question": 123
}
```

또는 필수 Field를 보내지 않습니다.

```json
{}
```

FastAPI는 Request Body, Path, Query 등의 검증에 실패하면 Validation 오류 응답을 자동으로 생성합니다. FastAPI는 이 과정에서 `RequestValidationError`를 사용하며, 기본적으로 `422 Unprocessable Entity` 응답을 반환합니다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/ "Handling Errors"))

```text
Client Input

↓

Pydantic Validation

↓

실패

↓

422 Response
```

Business Logic은 실행되지 않습니다.

---

### 2. Business Exception
입력 형식은 올바르지만, 서비스 규칙상 작업을 수행할 수 없습니다.

예를 들어 다음과 같습니다.

```text
문서 ID는 정수이다.

↓

Validation 통과

↓

하지만 해당 문서가 존재하지 않는다.
```

또 다른 예입니다.

```text
파일 확장자는 문자열이다.

↓

Validation 통과

↓

하지만 지원하지 않는 파일 형식이다.
```

이런 오류는 Service가 판단합니다.

```text
Service

↓

Business Rule 확인

↓

위반

↓

Business Exception 발생
```

---

### 3. External System Exception
우리 서비스가 의존하는 외부 시스템에서 문제가 발생합니다.

AI Backend에서는 매우 자주 발생합니다.

```text
OpenAI Timeout

Ollama 연결 실패

Vector DB 오류

OCR Engine 실패

외부 Storage 오류

Database 연결 실패
```

외부 오류를 그대로 Client에게 노출해서는 안 됩니다.

예를 들어 다음과 같은 내부 메시지가 노출되면 안 됩니다.

```text
Connection refused:
postgresql://admin:password@10.0.0.12:5432
```

내부 구조와 보안 정보가 노출될 수 있기 때문입니다.

---

### 4. Unexpected Server Error
개발자가 예상하지 못한 오류입니다.

예를 들어 다음과 같습니다.

```python
result = None

print(result["answer"])
```

또는 코드의 논리적 버그가 발생한 경우입니다.

이런 오류는 일반적으로 다음 상태로 처리합니다.

```text
500 Internal Server Error
```

Client에게는 안전한 메시지만 보여주고, 실제 상세 오류는 서버 로그에 기록해야 합니다.

---

### ④ HTTP Status Code 설계
오류 처리에서 Message만큼 중요한 것이 Status Code입니다.

대표적인 상태를 정리하면 다음과 같습니다.

|Status Code|의미|AI Backend 예시|
|--:|---|---|
|400|잘못된 요청|지원하지 않는 파일 옵션|
|401|인증 필요 또는 인증 실패|유효하지 않은 Token|
|403|권한 없음|다른 사용자의 문서 접근|
|404|Resource 없음|문서를 찾을 수 없음|
|409|현재 상태와 충돌|중복 문서 등록|
|422|입력 데이터 검증 실패|필수 Field 누락|
|429|요청 한도 초과|AI 호출 Rate Limit|
|500|예상하지 못한 서버 오류|코드 버그|
|502|외부 서비스의 잘못된 응답|AI Provider 응답 오류|
|503|서비스 사용 불가|AI Engine 일시 중단|
|504|외부 서비스 응답 Timeout|LLM 응답 시간 초과|

상태 코드 선택은 단순한 숫자 선택이 아닙니다.

Client가 오류를 어떻게 처리할지 결정하는 API 계약입니다.

---

### ⑤ FastAPI의 `HTTPException`
FastAPI에서는 Client에게 HTTP 오류를 전달할 때 `HTTPException`을 사용할 수 있습니다.

`HTTPException`은 API 오류에 필요한 Status Code, Detail, Header 정보를 포함하는 Python Exception이며, 반환하는 것이 아니라 `raise`해야 합니다. 공식 Reference에서는 잘못된 인증, 잘못된 데이터 같은 Client 관련 오류에 사용하고, 코드 내부의 서버 오류를 표현하는 용도로는 사용하지 않는다고 설명합니다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/ "Handling Errors"))

```python
from fastapi import HTTPException


@router.get("/documents/{document_id}")
async def get_document(document_id: int):
    document = document_service.get_document(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="문서를 찾을 수 없습니다.",
        )

    return document
```

---

### 왜 `return`이 아니라 `raise`일까?
좋지 않은 예입니다.

```python
return HTTPException(
    status_code=404,
    detail="문서를 찾을 수 없습니다.",
)
```

`HTTPException`은 Response 객체가 아닙니다.

Exception이므로 다음처럼 발생시켜야 합니다.

```python
raise HTTPException(
    status_code=404,
    detail="문서를 찾을 수 없습니다.",
)
```

`raise`가 실행되는 순간 현재 함수는 중단됩니다.

```text
Service 실행

↓

문서 없음

↓

raise HTTPException

↓

현재 흐름 중단

↓

FastAPI Exception Handler

↓

404 Response
```

---

### 기본 응답
FastAPI는 기본적으로 다음과 같은 JSON 응답을 생성합니다.

```json
{
    "detail": "문서를 찾을 수 없습니다."
}
```

HTTP Status는 다음과 같습니다.

```text
404 Not Found
```

---

### `detail`에는 객체도 사용할 수 있다
문자열만 넣어야 하는 것은 아닙니다.

```python
raise HTTPException(
    status_code=404,
    detail={
        "code": "DOCUMENT_NOT_FOUND",
        "message": "문서를 찾을 수 없습니다.",
    },
)
```

응답은 다음과 같습니다.

```json
{
    "detail": {
        "code": "DOCUMENT_NOT_FOUND",
        "message": "문서를 찾을 수 없습니다."
    }
}
```

다만 프로젝트 전체의 오류 구조를 통일하려면 이후에 배우는 전역 Exception Handler가 더 적합합니다.

---

### `HTTPException`은 어디에서 사용할까?
작은 프로젝트에서는 Router나 Dependency에서 직접 사용할 수 있습니다.

예를 들어 인증 Dependency입니다.

```python
async def get_current_user(
    authorization: str | None = None,
):
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="인증이 필요합니다.",
        )
```

하지만 Service Layer를 가진 프로젝트에서는 주의해야 합니다.

Service가 FastAPI의 `HTTPException`에 직접 의존하면 Service가 HTTP Framework를 알아야 하기 때문입니다.

```text
Service

↓

FastAPI HTTPException
```

이렇게 되면 Service를 FastAPI 밖에서 재사용하기 어려워집니다.

---

### AIKOS 권장 방식
#### 작은 프로젝트
```text
Router / Dependency

↓

HTTPException
```

---

#### Layered Architecture
```text
Service

↓

Custom Business Exception

↓

Global Exception Handler

↓

HTTP Response
```

AIKOS에서는 두 번째 방식을 표준으로 사용합니다.

---

### ⑥ 사용자 정의 예외(Custom Exception)
문서가 없을 때 사용할 예외를 만들어 보겠습니다.

```python
class DocumentNotFoundError(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id

        super().__init__(
            f"Document not found: {document_id}"
        )
```

이 예외는 FastAPI를 모릅니다.

```text
Status Code 모름

JSON 모름

HTTP 모름
```

단지 다음 의미만 표현합니다.

> 요청한 문서가 존재하지 않는다.

---

### Service에서 사용하기
```python
class DocumentService:
    def __init__(self, repository):
        self.repository = repository

    async def get_document(
        self,
        document_id: int,
    ):
        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise DocumentNotFoundError(
                document_id=document_id
            )

        return document
```

Service는 HTTP Status Code를 결정하지 않습니다.

```text
Service의 관심사

↓

문서 존재 여부
```

---

### Service가 알지 않아야 하는 것
```text
404

JSONResponse

FastAPI

HTTP Header
```

이들은 Web Layer의 관심사입니다.

이렇게 분리하면 Service는 FastAPI 없이도 테스트할 수 있습니다.

---

### ⑦ 전역 Exception Handler
이제 `DocumentNotFoundError`를 HTTP Response로 변환해야 합니다.

FastAPI에서는 `@app.exception_handler()`를 이용하여 특정 예외에 대한 Handler를 등록할 수 있습니다. FastAPI와 기반 프레임워크인 Starlette는 사용자 정의 Exception Handler를 설치해 처리된 예외를 원하는 Response로 변환할 수 있습니다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/ "Handling Errors"))

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(
    request: Request,
    exc: DocumentNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "code": "DOCUMENT_NOT_FOUND",
            "message": (
                "요청한 문서를 찾을 수 없습니다."
            ),
            "document_id": exc.document_id,
        },
    )
```

---

### 실행 과정
```text
GET /documents/100

↓

Document Router

↓

Document Service

↓

Repository

↓

문서 없음

↓

DocumentNotFoundError 발생

↓

Global Exception Handler

↓

404 JSON Response
```

---

### 응답 예시
```json
{
    "code": "DOCUMENT_NOT_FOUND",
    "message": "요청한 문서를 찾을 수 없습니다.",
    "document_id": 100
}
```

이제 모든 문서 조회 API에서 같은 오류 형식을 사용할 수 있습니다.

---

### ⑧ 표준 Error Response DTO
프로젝트가 커지면 오류 응답 구조를 통일해야 합니다.

AIKOS에서는 다음과 같은 기본 구조를 사용하겠습니다.

```python
from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    status: int
    request_id: str | None = None
    details: Any | None = None
```

---

### 각 Field의 역할
#### `code`
프로그램이 이해할 수 있는 오류 코드입니다.

```text
DOCUMENT_NOT_FOUND

INVALID_FILE_TYPE

LLM_TIMEOUT

UNAUTHORIZED
```

React는 이 값을 기준으로 화면 동작을 결정할 수 있습니다.

---

#### `message`
사용자나 개발자가 읽을 수 있는 메시지입니다.

```text
요청한 문서를 찾을 수 없습니다.
```

---

#### `status`
HTTP Status Code입니다.

```text
404
```

---

#### `request_id`
Middleware에서 Request ID를 사용하는 경우 전달되는 요청 식별자입니다.

```text
X-Request-ID
```

운영 로그와 Client 오류를 연결하는 데 사용합니다.

---

#### `details`
추가 정보입니다.

```json
{
    "document_id": 100
}
```

Validation 오류라면 어떤 Field가 잘못되었는지 포함할 수 있습니다.

---

### 표준 오류 응답 예시
```json
{
    "code": "DOCUMENT_NOT_FOUND",
    "message": "요청한 문서를 찾을 수 없습니다.",
    "status": 404,
    "request_id": "a07eecf1-4384-4932-81aa-c4806d0a6f55",
    "details": {
        "document_id": 100
    }
}
```

---

### 왜 `code`가 필요할까?
메시지만 사용하면 Frontend가 문자열에 의존하게 됩니다.

좋지 않은 예입니다.

```javascript
if (
  error.message ===
  "요청한 문서를 찾을 수 없습니다."
) {
  // 화면 처리
}
```

문구가 조금만 바뀌면 동작하지 않습니다.

좋은 방식은 안정적인 Error Code를 사용하는 것입니다.

```javascript
if (error.code === "DOCUMENT_NOT_FOUND") {
  // 문서 없음 화면 표시
}
```

따라서 다음과 같이 역할을 나눕니다.

```text
code

↓

프로그램 판단용

message

↓

사람이 읽는 용도
```

---

### ⑨ 공통 Business Exception 설계
사용자 정의 예외가 많아지면 공통 부모 예외를 만들 수 있습니다.

```python
from typing import Any


class BusinessError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: Any | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

        super().__init__(message)
```

---

### 문서 없음 예외
```python
class DocumentNotFoundError(BusinessError):
    def __init__(self, document_id: int):
        super().__init__(
            code="DOCUMENT_NOT_FOUND",
            message="요청한 문서를 찾을 수 없습니다.",
            status_code=404,
            details={
                "document_id": document_id,
            },
        )
```

---

### 지원하지 않는 파일 형식 예외
```python
class UnsupportedFileTypeError(BusinessError):
    def __init__(self, extension: str):
        super().__init__(
            code="UNSUPPORTED_FILE_TYPE",
            message="지원하지 않는 파일 형식입니다.",
            status_code=400,
            details={
                "extension": extension,
            },
        )
```

---

### LLM Timeout 예외
```python
class LLMTimeoutError(BusinessError):
    def __init__(self, provider: str):
        super().__init__(
            code="LLM_TIMEOUT",
            message=(
                "AI 모델의 응답 시간이 초과되었습니다."
            ),
            status_code=504,
            details={
                "provider": provider,
            },
        )
```

---

### 공통 Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse


async def business_error_handler(
    request: Request,
    exc: BusinessError,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "status": exc.status_code,
            "request_id": request_id,
            "details": exc.details,
        },
    )
```

등록합니다.

```python
app.add_exception_handler(
    BusinessError,
    business_error_handler,
)
```

이제 `BusinessError`를 상속한 모든 예외가 같은 구조로 응답됩니다.

---

### 전체 흐름
```text
Service

↓

DocumentNotFoundError

또는

UnsupportedFileTypeError

또는

LLMTimeoutError

↓

BusinessError Handler

↓

표준 Error Response
```

---

### ⑩ Validation 오류 형식 통일
FastAPI가 기본 제공하는 Validation 응답은 자세하지만, 프로젝트의 Error Response 구조와 다를 수 있습니다.

따라서 `RequestValidationError` Handler를 재정의할 수 있습니다.

```python
from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import JSONResponse


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": (
                "요청 데이터가 올바르지 않습니다."
            ),
            "status": 422,
            "request_id": request_id,
            "details": exc.errors(),
        },
    )
```

등록합니다.

```python
app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)
```

---

### Validation 응답 예시
```json
{
    "code": "VALIDATION_ERROR",
    "message": "요청 데이터가 올바르지 않습니다.",
    "status": 422,
    "request_id": "92e18d5c-f05d-40d1-aebd-c694fcb62b20",
    "details": [
        {
            "type": "missing",
            "loc": [
                "body",
                "question"
            ],
            "msg": "Field required",
            "input": {}
        }
    ]
}
```

Client는 모든 오류를 비슷한 구조로 처리할 수 있습니다.

---

### ⑪ 예상하지 못한 오류 처리
모든 오류를 사전에 정의할 수는 없습니다.

따라서 마지막 방어선이 필요합니다.

```python
import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger("aikos.error")


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    logger.exception(
        "Unexpected server error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": (
                "서버 내부 오류가 발생했습니다."
            ),
            "status": 500,
            "request_id": request_id,
            "details": None,
        },
    )
```

등록합니다.

```python
app.add_exception_handler(
    Exception,
    unexpected_error_handler,
)
```

---

### Client에게 상세 오류를 노출하면 안 된다
좋지 않은 응답입니다.

```json
{
    "message": "KeyError at service/chat.py line 153"
}
```

또는 다음 정보가 포함될 수 있습니다.

```text
서버 파일 경로

Database 주소

Library 버전

내부 SQL

API Key 일부

Stack Trace
```

이런 정보는 공격자에게 유용할 수 있습니다.

Client에게는 안전한 메시지를 보내고, 상세 정보는 로그에 기록합니다.

```text
Client

↓

안전한 오류 메시지

Server Log

↓

상세 Stack Trace
```

---

### ⑫ Exception Handler와 Middleware의 차이
지난 Unit과 연결해 보겠습니다.

#### Middleware
모든 요청과 응답의 공통 흐름을 처리합니다.

```text
Logging

Request ID

CORS

처리 시간
```

---

#### Exception Handler
특정 Exception을 HTTP Response로 변환합니다.

```text
DocumentNotFoundError

↓

404 Response
```

---

### 역할 비교
|항목|Middleware|Exception Handler|
|---|---|---|
|목적|공통 요청·응답 처리|예외를 응답으로 변환|
|정상 요청|처리함|관여하지 않음|
|오류 요청|통과·기록 가능|실제 오류 Response 생성|
|대표 사례|Logging, Request ID|404, 422, 500|
|Business Logic|포함하지 않음|포함하지 않음|

Starlette의 애플리케이션에는 처리되지 않은 서버 오류를 다루는 `ServerErrorMiddleware`와, Routing 및 Endpoint에서 발생한 처리 가능한 예외를 다루는 `ExceptionMiddleware`가 기본적으로 포함됩니다. 이는 오류 처리와 일반 Middleware가 내부적으로도 서로 다른 책임을 가진다는 점을 보여줍니다. ([Starlette](https://www.starlette.io/applications/ "Applications"))

---

### 오류를 Middleware에서 모두 처리하면 안 되는 이유
예를 들어 다음과 같이 작성했다고 가정해 봅시다.

```python
@app.middleware("http")
async def catch_all_errors(
    request: Request,
    call_next,
):
    try:
        return await call_next(request)

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "error"
            },
        )
```

이 방식은 모든 Exception을 같은 오류로 만들어 버릴 수 있습니다.

```text
404 Business Error

↓

500

422 Validation Error

↓

500

권한 오류

↓

500
```

오류의 의미를 잃어버립니다.

따라서 다음처럼 역할을 나눕니다.

```text
Middleware

↓

공통 추적과 Logging

Exception Handler

↓

예외별 HTTP 응답 생성
```

---

### ⑬ AI 서비스 오류 설계
AI Backend에서는 외부 AI Provider 오류가 중요합니다.

예를 들어 OpenAI 호출에서 Timeout이 발생했습니다.

이를 그대로 `500`으로 처리할 수도 있지만, 더 구체적인 내부 예외로 변환하는 것이 좋습니다.

```python
class ChatService:
    async def chat(self, request):
        try:
            result = await self.llm_client.generate(
                request.question
            )

        except TimeoutError as exc:
            raise LLMTimeoutError(
                provider="openai"
            ) from exc

        return result
```

---

### `raise ... from exc`
```python
raise LLMTimeoutError(
    provider="openai"
) from exc
```

이 문법은 원래 발생한 Exception과 새 Exception의 관계를 유지합니다.

Client는 표준화된 `LLM_TIMEOUT` 오류를 받고, Server Log에서는 실제 원인인 `TimeoutError`까지 추적할 수 있습니다.

---

### AI 오류 분류 예시
```text
LLM_AUTHENTICATION_FAILED

↓

AI Provider 인증 실패

LLM_RATE_LIMITED

↓

호출 한도 초과

LLM_TIMEOUT

↓

응답 시간 초과

LLM_RESPONSE_INVALID

↓

응답 형식 오류

VECTOR_SEARCH_FAILED

↓

Vector DB 검색 실패

OCR_PROCESSING_FAILED

↓

OCR Engine 실행 실패
```

각 오류에 맞는 Status Code와 재시도 정책을 설계해야 합니다.

---

### 재시도 가능한 오류와 불가능한 오류
AI 서비스에서는 오류가 재시도 가능한지도 중요합니다.

#### 재시도 가능할 수 있는 오류
```text
Timeout

일시적인 503

Rate Limit

네트워크 단절
```

---

#### 재시도해도 해결되지 않는 오류
```text
잘못된 API Key

지원하지 않는 파일 형식

존재하지 않는 문서

권한 없음
```

Error Response에 `retryable` 정보를 포함하는 설계도 가능합니다.

```json
{
    "code": "LLM_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다.",
    "status": 504,
    "retryable": true
}
```

다만 모든 프로젝트에 필수인 Field는 아닙니다. 운영 요구사항이 있을 때 추가합니다.

---

### ⑭ AIKOS 표준 프로젝트 구조
Exception 관련 코드를 구조화해 보겠습니다.

```text
backend/

└── app/
    ├── core/
    │   ├── settings.py
    │   └── logging.py
    │
    ├── exceptions/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── document.py
    │   ├── file.py
    │   └── ai.py
    │
    ├── handlers/
    │   ├── __init__.py
    │   └── exception_handlers.py
    │
    ├── middleware/
    │   └── request_context.py
    │
    ├── schemas/
    │   └── error.py
    │
    ├── routers/
    ├── services/
    └── main.py
```

---

### `exceptions/base.py`
```python
from typing import Any


class BusinessError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: Any | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

        super().__init__(message)
```

---

### `schemas/error.py`
```python
from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    status: int
    request_id: str | None = None
    details: Any | None = None
```

---

### `handlers/exception_handlers.py`
```python
import logging

from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import JSONResponse

from app.exceptions.base import BusinessError


logger = logging.getLogger("aikos.error")


async def business_error_handler(
    request: Request,
    exc: BusinessError,
) -> JSONResponse:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "status": exc.status_code,
            "request_id": request_id,
            "details": exc.details,
        },
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": (
                "요청 데이터가 올바르지 않습니다."
            ),
            "status": 422,
            "request_id": request_id,
            "details": exc.errors(),
        },
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    logger.exception(
        "Unexpected server error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": (
                "서버 내부 오류가 발생했습니다."
            ),
            "status": 500,
            "request_id": request_id,
            "details": None,
        },
    )
```

---

### `main.py`
```python
from fastapi import FastAPI
from fastapi.exceptions import (
    RequestValidationError,
)

from app.exceptions.base import BusinessError
from app.handlers.exception_handlers import (
    business_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AIKOS AI Backend",
        version="1.0.0",
    )

    app.add_exception_handler(
        BusinessError,
        business_error_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )

    app.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )

    return app


app = create_app()
```

이제 `main.py`는 여전히 애플리케이션을 조립하는 역할을 담당합니다.

---

### ⑮ Router 응답 문서화
Swagger에 오류 응답도 표시할 수 있습니다.

```python
@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": (
                "문서를 찾을 수 없습니다."
            ),
        },
        422: {
            "model": ErrorResponse,
            "description": (
                "요청 데이터 검증 실패"
            ),
        },
    },
)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(
        get_document_service
    ),
):
    return await service.get_document(
        document_id
    )
```

이렇게 하면 Swagger를 보는 Frontend 개발자도 성공 응답과 오류 응답 구조를 함께 확인할 수 있습니다.

---

### ⑯ 실무 Best Practice
#### 1. 오류 코드와 메시지를 분리한다
```text
code

↓

프로그램 처리용

message

↓

사람이 읽는 용도
```

---

#### 2. Service에서는 Business Exception을 발생시킨다
```python
raise DocumentNotFoundError(document_id)
```

Service가 `JSONResponse`를 반환하지 않습니다.

---

#### 3. Handler에서 HTTP Response로 변환한다
```text
Business Exception

↓

Exception Handler

↓

HTTP Response
```

---

#### 4. 예상하지 못한 오류는 반드시 로그로 기록한다
`500` 오류를 Client에게만 반환하고 로그를 남기지 않으면 원인을 찾을 수 없습니다.

---

#### 5. 민감한 내부 정보를 Client에게 노출하지 않는다
```text
Stack Trace

SQL

API Key

Database URL

서버 파일 경로
```

를 Response에 포함하지 않습니다.

---

#### 6. Request ID를 오류 응답에 포함한다
```text
Client 오류

↓

Request ID

↓

Server Log 추적
```

Middleware를 추가하는 경우 연결할 수 있는 핵심 설계입니다.

---

#### 7. Exception을 너무 광범위하게 잡지 않는다
좋지 않은 예입니다.

```text
except Exception:
    pass
```

오류를 숨기면 서비스가 잘못된 상태로 계속 실행될 수 있습니다.

---

#### 8. `HTTPException`과 Business Exception을 구분한다
```text
Web Layer의 단순 HTTP 오류

↓

HTTPException

Domain / Service의 업무 오류

↓

Custom Business Exception
```

---

### ⑰ 자주 발생하는 실수
#### 실수 1. 모든 오류를 500으로 반환한다
Client 오류와 Server 오류를 구분할 수 없습니다.

---

#### 실수 2. 모든 오류를 200으로 반환한다
```json
{
    "success": false
}
```

만 사용하면 HTTP의 의미를 제대로 활용하지 못합니다.

---

#### 실수 3. Router마다 `try-except`를 작성한다
중복 코드가 증가하고 오류 응답 형식이 달라집니다.

---

#### 실수 4. `except Exception`으로 원인을 숨긴다
실제 문제를 찾기 어려워집니다.

---

#### 실수 5. Service에서 `JSONResponse`를 반환한다
Service가 HTTP Layer에 결합됩니다.

---

#### 실수 6. Python Exception 메시지를 그대로 노출한다
내부 정보가 Client에게 노출될 수 있습니다.

---

#### 실수 7. Business 오류와 시스템 오류를 구분하지 않는다
```text
문서 없음

≠

DB 연결 실패
```

둘은 완전히 다른 문제입니다.

---

### ⑱ 전체 Error Processing Pipeline
이번 Unit에서 반드시 기억해야 하는 그림입니다.

```text
Client
  │
  ▼
Middleware
  │
  ├── Request ID 생성
  └── 요청 기록
  │
  ▼
Validation
  │
  ├── 실패
  │     │
  │     ▼
  │ RequestValidationError
  │
  ▼
Router
  │
  ▼
Service
  │
  ├── Business Rule 실패
  │     │
  │     ▼
  │ BusinessError
  │
  ├── 외부 시스템 실패
  │     │
  │     ▼
  │ External Service Error
  │
  └── 예상하지 못한 오류
        │
        ▼
      Exception
        │
        ▼
Global Exception Handler
        │
        ├── Status Code 결정
        ├── Error Code 결정
        ├── 안전한 Message 생성
        ├── Request ID 연결
        └── 상세 오류 Logging
        │
        ▼
Standard Error Response
        │
        ▼
Client
```

---

### 핵심 내용 정리
이번 Unit에서는 **Exception Handling과 표준 오류 응답 설계**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- Exception은 서버 내부의 실패 상황이고, Error Response는 이를 Client에게 전달하는 HTTP 응답이다.
    
- `HTTPException`은 단순한 HTTP 오류를 표현할 때 사용할 수 있으며 `return`이 아니라 `raise`한다.
    
- Layered Architecture에서는 Service가 FastAPI의 `HTTPException`에 직접 의존하기보다 사용자 정의 Business Exception을 발생시키는 것이 좋다.
    
- 전역 Exception Handler는 Exception을 Status Code와 표준 JSON Response로 변환한다.
    
- Validation 오류, Business 오류, 외부 시스템 오류, 예상하지 못한 서버 오류를 구분해야 한다.
    
- Error Response는 `code`, `message`, `status`, `request_id`, `details`처럼 일관된 구조를 사용하는 것이 좋다.
    
- 예상하지 못한 오류의 상세 정보는 Server Log에 기록하고 Client에게는 안전한 메시지만 반환한다.
    
- Middleware에서 Request ID를 추가한 경우 오류 응답과 로그에 연결하면 운영 중 문제를 추적하기 쉬워진다.
    

---

### Part 3 완료
여기까지 **Part 3. AI Backend Architecture**가 완료되었습니다.

학생은 이제 다음 구조를 설명할 수 있어야 합니다.

```text
Client

↓

Middleware

↓

Router

↓

Dependency Injection

↓

Request DTO / Validation

↓

Service

↓

Business Exception

↓

Exception Handler

↓

Response DTO / Error DTO

↓

Client
```

Part 3에서 완성된 핵심 요소는 다음과 같습니다.

```text
Service Layer

APIRouter

Layered Architecture

Dependency Injection

Configuration

Exception Handling
```

이제 AI Backend의 **Web Layer와 Business Layer의 기본 구조**가 완성되었습니다.

이번 과정에서는 Data Layer를 생략하고, 이 구조 아래에 AI Client를 직접 연결합니다.

---


### Part 3 Architecture Review
#### 5분 복습
```text
Request
→ Router
→ Dependency 조립
→ Service
→ AI Client
→ Exception Handler
→ Response
```

- **따라 하기:** Router에서 Service를 주입받아 호출한다.
- **부분 완성:** 섞여 있는 비즈니스 규칙을 올바른 계층으로 이동한다.
- **독립 구현:** 문서 기능의 Router·Service·Dependency 구조를 설계한다.

#### 학생 질문
1. Router를 얇게 유지하면 무엇이 쉬워지는가?
2. Dependency Injection이 테스트 대역 교체에 어떤 도움을 주는가?

#### 확인 퀴즈
1. Service가 `HTTPException`에 직접 의존하면 어떤 결합이 생기는가?
2. Settings 객체를 요청마다 새로 만들 필요가 있는가?

<details>
<summary>정답</summary>

1. 비즈니스 계층이 HTTP 전달 계층에 결합된다.
2. 보통 없다. 캐시하거나 애플리케이션 수명주기에 맞춰 재사용한다.

</details>

### Day 2-3. AI Provider Integration

Web Layer와 Service Layer의 경계가 준비되었습니다. SQLAlchemy Data Layer를 거치지 않고, Service 아래에 AI Client를 연결하여 Provider 설정·OpenAI 호출·Prompt·비동기 요청·오류 정책·Streaming까지 완성합니다.

```text
Client
→ Router
→ Request DTO
→ Service
→ AI Client
→ AI Provider
→ Response DTO
```

# Part 4. AI Backend Integration

여기서는 Backend 구조에 외부 AI Provider를 연결한다. Provider 자체의 세부 학습은 뒤의 [[GPT]], [[Ollama]], [[Gemma]], [[AI Integration]] 과정에서 다시 다룰 수 있으며, 이 Part에서는 **FastAPI Backend 안에서 어디에 배치하고 어떻게 실패를 통제하는지**에 초점을 둔다.

## Module 35. AI Backend Integration의 이해


### Module 실습 예제

- [예제 1: provider_boundary.py](examples/module_35/provider_boundary.py) — 외부 Provider 응답을 내부 모델로 변환합니다.
- [예제 2: internal_result.py](examples/module_35/internal_result.py) — Provider가 달라도 동일한 내부 결과 계약을 유지합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 외부 AI Provider를 내부 아키텍처에 연결할 위치를 정한다.
- **오늘 만드는 것:** Provider Client와 Service 경계를 설계한다.
- **AI 플랫폼의 위치:** Router → Service → AI Client → Provider 흐름을 완성한다.
- **실무에서 많이 하는 실수:** SDK 호출을 Router에 직접 넣어 교체와 테스트를 어렵게 만든다.
- **5분 실습:** 외부 응답을 내부 결과 모델로 변환하는 위치를 정한다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI Backend란 무엇인가?
    
- React에서 AI API를 직접 호출하면 왜 안 되는가?
    
- FastAPI는 AI 서비스에서 어떤 역할을 담당하는가?
    
- 일반적인 CRUD 백엔드와 AI 백엔드는 무엇이 다른가?
    
- AI 모델 호출 코드는 프로젝트의 어느 계층에 위치해야 하는가?
    
- 사용자의 요청은 어떤 과정을 거쳐 LLM에 전달되는가?
    
- AI 모델의 응답을 그대로 반환하면 왜 문제가 되는가?
    
- AI Provider와 우리의 비즈니스 로직은 왜 분리해야 하는가?
    

---

### 2. 문제 이해 — Why
#### 2.1 지금까지 만든 FastAPI는 무엇을 했는가?
앞선 Part에서 우리는 FastAPI를 이용해 다음 기능을 구현했다.

```text
클라이언트 요청 수신
        ↓
요청 데이터 검증
        ↓
비즈니스 로직 실행
        ↓
Repository를 통한 데이터 접근
        ↓
응답 모델 반환
```

예를 들어 문서 정보를 조회하는 API는 다음과 같은 흐름을 가졌다.

```text
GET /documents/1
        ↓
DocumentRouter
        ↓
DocumentService
        ↓
DocumentRepository
        ↓
Database
```

이 구조에서 백엔드가 사용하는 외부 자원은 주로 데이터베이스였다.

그러나 AI 서비스에서는 새로운 외부 자원이 등장한다.

```text
LLM
Embedding Model
OCR Model
Speech Model
Image Generation Model
```

즉, FastAPI가 데이터베이스뿐 아니라 **AI 모델과도 통신해야 한다.**

---

#### 2.2 React에서 OpenAI API를 직접 호출하면 되지 않을까?
처음 AI 서비스를 만드는 개발자는 흔히 다음 구조를 생각한다.

```text
React
  ↓
OpenAI API
```

React 코드에서 직접 AI API를 호출하면 구조가 단순해 보인다.

```javascript
const response = await fetch("https://api.openai.com/v1/responses", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${OPENAI_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "모델 이름",
    input: userMessage,
  }),
});
```

그러나 이 구조에는 심각한 문제가 있다.

---

#### 2.3 문제 1 — API Key가 사용자에게 노출된다
React 코드는 브라우저에서 실행된다.

따라서 React에 포함된 API Key는 다음 방법으로 확인할 수 있다.

- 브라우저 개발자 도구
    
- JavaScript 번들 분석
    
- Network 요청 확인
    
- 환경변수가 포함된 빌드 결과 확인
    

프론트엔드 환경변수에 API Key를 넣더라도 안전해지는 것은 아니다.

```env
VITE_OPENAI_API_KEY=secret-key
```

`VITE_`로 시작하는 환경변수는 React 애플리케이션의 빌드 결과에 포함되어 브라우저에서 사용할 수 있게 된다.

즉, 이것은 비밀정보 저장소가 아니다.

```text
프론트엔드 환경변수
≠
서버 비밀정보
```

##### 올바른 구조
```text
React
  ↓
FastAPI
  ↓
OpenAI API
```

API Key는 FastAPI 서버에만 저장한다.

```env
OPENAI_API_KEY=...
```

브라우저는 API Key를 알지 못한다.

---

#### 2.4 문제 2 — 사용량과 비용을 통제할 수 없다
AI API 호출은 일반적인 데이터 조회와 다르다.

대부분의 상용 AI API는 다음 요소에 따라 비용이 발생한다.

- 입력 토큰
    
- 출력 토큰
    
- 사용 모델
    
- 이미지 크기
    
- 음성 길이
    
- 호출 횟수
    
- 도구 사용량
    

React에서 외부 AI API를 직접 호출하면 사용자가 호출 조건을 임의로 변경할 수 있다.

예를 들어 개발자가 최대 출력 길이를 제한했다고 가정하자.

```javascript
{
  max_output_tokens: 500
}
```

사용자는 브라우저 요청을 직접 수정할 수 있다.

```javascript
{
  max_output_tokens: 10000
}
```

또는 반복 호출 스크립트를 만들 수도 있다.

```text
1명의 악의적인 사용자
        ↓
수천 번의 AI API 요청
        ↓
예상하지 못한 비용 발생
```

FastAPI를 중간에 배치하면 다음 정책을 적용할 수 있다.

- 사용자 인증
    
- 호출 횟수 제한
    
- 모델 제한
    
- 입력 길이 제한
    
- 출력 길이 제한
    
- 사용량 기록
    
- 월별 사용 한도
    
- 관리자 승인
    
- 금지된 요청 차단
    

---

#### 2.5 문제 3 — 비즈니스 규칙을 보호할 수 없다
AI 서비스는 단순히 사용자의 문장을 그대로 모델에 전달하지 않는다.

실제 서비스에서는 다음과 같은 처리가 필요하다.

```text
사용자 입력
   ↓
입력 검증
   ↓
사용자 권한 확인
   ↓
문서 데이터 조회
   ↓
프롬프트 조합
   ↓
AI 모델 호출
   ↓
출력 검증
   ↓
결과 저장
   ↓
응답 반환
```

예를 들어 사용자가 다음 요청을 보냈다고 하자.

```json
{
  "document_id": 10,
  "summary_type": "executive"
}
```

FastAPI는 단순히 이 JSON을 LLM에 전달하는 것이 아니다.

다음 작업을 수행해야 한다.

1. 사용자가 로그인했는지 확인한다.
    
2. 사용자가 10번 문서를 열람할 권한이 있는지 확인한다.
    
3. 데이터베이스에서 문서를 조회한다.
    
4. 문서의 텍스트를 가져온다.
    
5. 문서가 너무 길면 여러 조각으로 분할한다.
    
6. 요약 목적에 맞는 프롬프트를 만든다.
    
7. AI 모델을 호출한다.
    
8. AI 응답이 형식에 맞는지 검사한다.
    
9. 결과를 데이터베이스에 저장한다.
    
10. 클라이언트 응답 모델로 변환한다.
    

이 모든 과정이 **AI Backend Logic**이다.

---

#### 2.6 문제 4 — AI Provider가 바뀌면 프론트엔드까지 수정해야 한다
처음에는 OpenAI를 사용하다가 다음과 같은 이유로 다른 모델을 사용하게 될 수 있다.

- 비용 절감
    
- 개인정보 보호
    
- 사내망 운영
    
- 응답 속도 개선
    
- 특정 언어 성능
    
- 장애 대응
    
- 고객별 모델 선택
    

예를 들면 다음과 같다.

```text
OpenAI
Anthropic
Google Gemini
Azure OpenAI
AWS Bedrock
Ollama
사내 모델 서버
```

React에서 OpenAI API를 직접 호출하도록 구현하면 Provider가 바뀔 때 프론트엔드 코드도 바뀌어야 한다.

```text
React
  ↓
OpenAI 전용 요청 구조
```

FastAPI를 중간에 두면 React는 우리 서비스의 API만 호출한다.

```text
POST /api/v1/summaries
```

내부 Provider가 바뀌더라도 React의 API 계약은 유지할 수 있다.

```text
                ┌→ OpenAI
React → FastAPI ├→ Ollama
                └→ 사내 LLM
```

이것이 **추상화 경계**를 만드는 이유다.

---

### 3. 개념 이해 — Concept
#### 3.1 AI Backend란 무엇인가?
AI Backend는 다음 두 영역을 연결하는 서버 애플리케이션이다.

```text
사용자 애플리케이션
        ↕
AI 모델 및 AI 인프라
```

조금 더 정확하게 정의하면 다음과 같다.

> AI Backend는 사용자의 요청을 검증하고, 필요한 데이터를 준비하며, AI 모델을 호출하고, 모델의 출력을 서비스에서 사용할 수 있는 형태로 가공하는 백엔드 시스템이다.

AI Backend는 단순한 AI API 대리 호출기가 아니다.

```text
AI Backend
≠
OpenAI API Proxy
```

올바른 AI Backend에는 다음 책임이 있다.

|책임|설명|
|---|---|
|요청 검증|잘못되거나 지나치게 긴 입력 차단|
|인증·인가|사용자의 신원과 권한 확인|
|컨텍스트 구성|DB, 파일, 검색 결과를 프롬프트에 결합|
|모델 선택|작업에 적합한 모델 결정|
|AI 호출|외부 또는 로컬 모델 호출|
|출력 검증|모델 응답의 형식과 안전성 검사|
|예외 처리|Timeout, Rate Limit, Provider 장애 처리|
|비용 관리|토큰과 호출 사용량 기록|
|결과 저장|생성 결과와 상태 저장|
|관찰 가능성|로그, 추적 ID, 처리 시간 기록|

---

#### 3.2 일반 Backend와 AI Backend의 차이
일반적인 백엔드는 비교적 결정적인 규칙을 실행한다.

```python
total_price = price * quantity
```

입력이 같으면 결과도 같다.

```text
1000 × 3 = 3000
```

그러나 LLM 호출은 확률적 특성을 가진다.

```text
동일한 요청
   ↓
표현이나 구성 방식이 다른 응답
```

또한 외부 모델 상태와 설정에 따라 다음이 달라질 수 있다.

- 응답 내용
    
- 응답 시간
    
- 토큰 사용량
    
- 비용
    
- 실패 가능성
    
- 출력 형식
    
- 안전 정책 결과
    

따라서 AI Backend는 일반 Backend보다 더 많은 방어 계층이 필요하다.

|일반 Backend|AI Backend|
|---|---|
|명확한 계산 규칙|확률적 모델 출력|
|짧은 처리 시간|수 초에서 수십 초가 걸릴 수 있음|
|정형화된 응답|형식이 달라질 수 있음|
|내부 로직 중심|외부 AI Provider 의존|
|호출 비용이 낮음|호출별 비용 발생 가능|
|입력 영향 범위가 제한적|Prompt Injection 등 새로운 위협 존재|

---

#### 3.3 FastAPI가 담당하는 역할
FastAPI는 AI 모델 자체가 아니다.

FastAPI는 AI 모델을 학습하지도 않고 직접 추론하지도 않는다.

FastAPI의 역할은 AI 모델을 **서비스로 사용할 수 있도록 감싸는 것**이다.

비유하면 다음과 같다.

```text
LLM             = 전문 요리사
FastAPI         = 식당 운영 시스템
React           = 주문 화면
Database        = 재료·주문 기록 창고
사용자          = 고객
```

요리사가 뛰어나더라도 식당 운영 시스템이 없다면 다음 문제가 발생한다.

- 주문 형식이 제각각이다.
    
- 누가 주문했는지 알 수 없다.
    
- 재료 사용량을 기록할 수 없다.
    
- 알레르기 정보를 확인할 수 없다.
    
- 주문이 실패해도 고객에게 설명할 수 없다.
    
- 비용을 계산할 수 없다.
    

FastAPI는 AI 모델 주변의 서비스 운영을 담당한다.

---

### 4. 후속 AI 과정과의 연결
이 단원은 아래 AI 개념을 이미 숙달했다고 가정하지 않는다. 각 개념의 세부 원리는 후속 AI·Document AI 과정에서 다루고, 여기서는 FastAPI 내부의 연결 위치만 이해한다.

- Transformer
    
- LLM
    
- Prompt Engineering
    
- Embedding
    
- Vector DB
    
- RAG
    
- Agent
    
- Fine-tuning
    
- OCR
    
- Multimodal
    
- AI Service Architecture
    

이번 Part에서는 이 기술들의 내부 알고리즘보다, 외부 AI Provider와 데이터 처리 모듈을 실제 Web API에 연결하는 방법에 집중한다.

```text
후속 AI 과정
AI 기술의 원리와 구현
        ↓
현재 FastAPI 과정
AI 기술을 서비스 경계에 연결
```

예를 들어 후속 과정에서 다룰 RAG의 개념적 흐름은 다음과 같다.

```text
질문
 ↓
Embedding
 ↓
Vector DB 검색
 ↓
관련 문서
 ↓
LLM
 ↓
답변
```

FastAPI 관점에서는 다음과 같이 구현된다.

```text
POST /api/v1/answers
        ↓
AnswerRouter
        ↓
AnswerService
        ├─→ EmbeddingService
        ├─→ VectorRepository
        └─→ LLMService
        ↓
AnswerResponse
```

개념적 AI 파이프라인은 FastAPI 안에서 코드 계층과 API 계약으로 표현된다.

---

### 5. 구조 이해 — Architecture
#### 5.1 가장 단순한 AI Backend 구조
```text
┌───────────────┐
│     React     │
│ 사용자 입력 UI │
└───────┬───────┘
        │ HTTP
        ▼
┌───────────────┐
│    FastAPI    │
│ 요청 검증     │
│ 프롬프트 구성  │
│ AI 호출       │
│ 응답 변환     │
└───────┬───────┘
        │ HTTPS
        ▼
┌───────────────┐
│  AI Provider  │
│ OpenAI/Ollama │
└───────────────┘
```

이 구조는 학습용으로는 충분하지만 실무 구조로는 책임이 한곳에 몰릴 수 있다.

---

#### 5.2 잘못된 구조 — Router가 모든 일을 수행
```python
@app.post("/summaries")
async def create_summary(request: SummaryRequest):
    # 데이터 조회
    document = database.get(request.document_id)

    # 프롬프트 생성
    prompt = f"다음 문서를 요약하세요: {document.content}"

    # AI 호출
    response = await openai_client.responses.create(
        model="configured-model",
        input=prompt,
    )

    # 결과 저장
    database.save_summary(
        document_id=request.document_id,
        content=response.output_text,
    )

    # 응답 반환
    return {
        "summary": response.output_text,
    }
```

코드가 짧을 때는 문제가 없어 보인다.

하지만 Router가 다음 책임을 모두 갖고 있다.

```text
HTTP 요청 처리
데이터베이스 조회
프롬프트 생성
AI Provider 호출
결과 저장
응답 변환
```

이 구조는 다음 문제를 만든다.

- Router 테스트가 어려워진다.
    
- OpenAI를 Ollama로 교체하기 어렵다.
    
- 프롬프트를 재사용하기 어렵다.
    
- 데이터 처리 코드가 중복된다.
    
- 예외 처리 정책이 여러 Router에 흩어진다.
    
- AI 호출 없이 비즈니스 로직만 테스트하기 어렵다.
    

---

#### 5.3 권장 구조 — 계층 분리
```text
┌─────────────────────────────────────┐
│ Presentation Layer                  │
│ Router / Request / Response         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Application Layer                   │
│ SummaryService                      │
│ 작업 순서와 비즈니스 규칙 관리       │
└─────────┬─────────────────┬─────────┘
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ Data Layer       │  │ AI Integration   │
│ Repository       │  │ LLMService       │
│ Document 조회    │  │ Prompt 구성/호출 │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Database         │  │ OpenAI / Ollama  │
└──────────────────┘  └──────────────────┘
```

핵심은 역할을 다음과 같이 분리하는 것이다.

##### Router
```text
HTTP를 이해한다.
```

- 요청 수신
    
- 요청 모델 검증
    
- 인증 정보 전달
    
- Service 호출
    
- 응답 모델 반환
    

##### Application Service
```text
업무 흐름을 이해한다.
```

- 문서 조회
    
- 권한 확인
    
- AI 처리 요청
    
- 결과 저장
    
- 트랜잭션 흐름 관리
    

##### AI Service
```text
AI 작업을 이해한다.
```

- 프롬프트 생성
    
- 모델 선택
    
- AI Provider 호출
    
- 응답 추출
    
- 모델 오류 변환
    

##### Repository
```text
데이터 저장소를 이해한다.
```

- 문서 조회
    
- 분석 결과 저장
    
- 사용량 기록
    

---

#### 5.4 전체 데이터 흐름
사용자가 문서 요약 버튼을 클릭했다고 가정하자.

```text
1. React
   POST /api/v1/documents/10/summaries
                │
                ▼
2. SummaryRouter
   요청 모델 검증
                │
                ▼
3. SummaryService
   문서 조회 및 작업 흐름 제어
                │
                ├───────────────┐
                ▼               ▼
4. DocumentRepository     5. LLMService
   문서 데이터 조회          프롬프트 생성
                                │
                                ▼
                         6. AI Provider
                            요약 생성
                                │
                                ▼
5. SummaryService
   결과 검증 및 저장
                │
                ▼
6. SummaryRouter
   SummaryResponse 반환
                │
                ▼
7. React
   요약 결과 화면 출력
```

여기서 중요한 점은 React가 다음 사항을 알 필요가 없다는 것이다.

- 어떤 AI Provider를 사용했는가?
    
- 어떤 프롬프트를 사용했는가?
    
- API Key는 무엇인가?
    
- 모델 입력 형식은 무엇인가?
    
- 문서를 몇 번 분할했는가?
    
- Retry를 몇 번 수행했는가?
    

React는 우리 백엔드와의 API 계약만 알면 된다.

---

### 6. AI Backend의 경계
#### 6.1 우리 API와 Provider API는 다르다
우리 서비스가 제공하는 API는 다음과 같을 수 있다.

```http
POST /api/v1/summaries
```

요청:

```json
{
  "document_id": 10,
  "summary_type": "executive"
}
```

응답:

```json
{
  "document_id": 10,
  "summary": "이 문서는 생성형 AI 도입 전략을 설명한다.",
  "status": "completed"
}
```

하지만 내부에서 사용하는 AI Provider의 요청은 이와 전혀 다를 수 있다.

개념적으로는 다음과 같은 정보가 필요하다.

```json
{
  "model": "configured-model",
  "instructions": "당신은 전문 문서 요약가입니다.",
  "input": "문서 본문...",
  "max_output_tokens": 1000
}
```

FastAPI는 두 계약 사이를 변환한다.

```text
서비스 API 계약
       ↓ 변환
AI Provider 계약
       ↓ 변환
서비스 응답 계약
```

이를 **Anti-Corruption Layer**, 즉 외부 시스템의 구조가 우리 도메인 안으로 직접 침투하지 못하게 하는 경계로 이해할 수 있다.

---

#### 6.2 Provider 응답을 그대로 반환하면 안 되는 이유
다음과 같이 Provider 응답 전체를 그대로 반환하는 것은 피해야 한다.

```python
return response
```

외부 AI SDK의 응답에는 다음 정보가 포함될 수 있다.

- Provider 전용 객체 구조
    
- 모델 이름
    
- 내부 식별자
    
- 토큰 사용량
    
- 생성 상태
    
- 도구 호출 정보
    
- 추론 관련 메타데이터
    
- SDK 버전에 따라 달라질 수 있는 필드
    

이를 그대로 프론트엔드에 반환하면 React가 Provider의 구조에 종속된다.

```text
React
  ↓ 의존
OpenAI SDK 응답 구조
```

Provider를 교체하면 React까지 변경해야 한다.

대신 백엔드에서 필요한 데이터만 추출해 우리 응답 모델로 반환한다.

```python
return SummaryResponse(
    document_id=document.id,
    summary=generated_text,
    status="completed",
)
```

```text
AI Provider Response
        ↓
Backend 변환
        ↓
SummaryResponse
```

---

### 7. 실습 준비
#### 7.1 실습 목표
이번 Unit에서는 실제 AI API를 호출하기 전에 AI 연동 계층의 뼈대를 만든다.

구현할 기능은 다음과 같다.

```text
POST /api/v1/ai/summaries
```

사용자가 텍스트를 보내면 아직 실제 LLM을 호출하지 않고, 가짜 AI Service가 요약 결과를 반환하도록 구성한다.

실제 Provider를 먼저 연결하지 않는 이유는 다음과 같다.

- API 계약을 먼저 확정할 수 있다.
    
- 계층 구조를 먼저 이해할 수 있다.
    
- API Key 없이 실행할 수 있다.
    
- AI 호출 비용 없이 테스트할 수 있다.
    
- 외부 API 장애와 무관하게 개발할 수 있다.
    
- 이후 실제 AI Client로 교체하기 쉽다.
    

이 방식을 흔히 **Fake 구현** 또는 **Test Double**을 활용한 개발이라고 한다.

---

#### 7.2 개발환경
권장 환경:

```text
Python 3.12
FastAPI
Uvicorn
Pydantic 2
pytest
httpx
```

설치:

```bash
pip install fastapi "uvicorn[standard]" pytest httpx
```

이번 Unit에서는 아직 OpenAI 라이브러리를 설치하지 않는다.

---

#### 7.3 권장 프로젝트 구조
```text
app/
├── main.py
│
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── ai.py
│
├── schemas/
│   ├── __init__.py
│   └── summary.py
│
├── services/
│   ├── __init__.py
│   └── ai_service.py
│
└── core/
    └── __init__.py
```

각 디렉터리의 역할은 다음과 같다.

```text
api/
HTTP 요청과 응답 처리

schemas/
API 데이터 계약 정의

services/
AI 작업과 비즈니스 로직 처리

core/
설정, 보안, 공통 인프라 구성
```

Repository 구조를 추가로 사용하는 경우 다음과 같이 함께 사용할 수 있다.

```text
app/
├── api/
├── schemas/
├── services/
├── repositories/
├── models/
├── db/
└── core/
```

---

### 8. 기본 구현
#### 8.1 요청과 응답 모델 작성
파일:

```text
app/schemas/summary.py
```

```python
from pydantic import BaseModel, Field


class SummaryCreateRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
        description="요약할 원문",
    )


class SummaryResponse(BaseModel):
    summary: str
    input_length: int
    status: str
```

---

#### 8.2 코드 설명
##### `SummaryCreateRequest`
```text
class SummaryCreateRequest(BaseModel):
```

클라이언트가 보내는 요청 데이터의 계약이다.

```json
{
  "text": "요약할 문서 내용"
}
```

---

##### 최소 길이 검증
```python
min_length=10
```

너무 짧은 입력은 문서 요약 요청으로 의미가 없을 수 있다.

FastAPI와 Pydantic이 Service 실행 전에 요청을 검증한다.

---

##### 최대 길이 검증
```python
max_length=20_000
```

AI API에 전달되는 입력은 무제한으로 허용하면 안 된다.

입력 크기가 커지면 다음 문제가 발생할 수 있다.

- 토큰 비용 증가
    
- 처리 시간 증가
    
- 모델 컨텍스트 한도 초과
    
- 서버 메모리 사용량 증가
    
- 악의적인 대용량 요청
    

현재의 20,000자는 학습용 정책이다. 실무에서는 모델의 토큰 제한, 비용 정책, 문서 분할 전략에 따라 결정해야 한다.

---

##### `SummaryResponse`
```text
class SummaryResponse(BaseModel):
```

우리 백엔드가 React에 반환할 데이터 계약이다.

```json
{
  "summary": "생성된 요약",
  "input_length": 1200,
  "status": "completed"
}
```

Provider가 어떤 응답 구조를 사용하더라도 우리 응답 계약은 유지한다.

---

### 9. AI Service 작성
파일:

```text
app/services/ai_service.py
```

```python
class AIService:
    async def summarize(self, text: str) -> str:
        normalized_text = " ".join(text.split())

        preview_length = 120
        preview = normalized_text[:preview_length]

        if len(normalized_text) > preview_length:
            preview += "..."

        return f"[연습용 요약] {preview}"
```

---

#### 9.1 왜 Service를 별도 파일로 만드는가?
Router 안에서 요약 코드를 작성할 수도 있다.

```python
@router.post("/summaries")
async def create_summary(request: SummaryCreateRequest):
    summary = request.text[:120]
    return {"summary": summary}
```

하지만 나중에 실제 AI Provider가 연결되면 다음 코드가 추가된다.

- API Key 설정
    
- 모델 선택
    
- 프롬프트 구성
    
- 비동기 요청
    
- Timeout 처리
    
- Rate Limit 처리
    
- 응답 추출
    
- 로깅
    
- 사용량 기록
    

Router가 빠르게 복잡해진다.

따라서 처음부터 AI 관련 로직을 Service에 둔다.

---

#### 9.2 `async def`를 사용하는 이유
```text
async def summarize(self, text: str) -> str:
```

현재 Fake 구현은 네트워크 요청을 하지 않지만, 이후 실제 AI API 호출은 네트워크 I/O가 된다.

```text
FastAPI
  ↓ 요청 전송
AI Provider
  ↓ 응답 대기
FastAPI
```

AI 응답을 기다리는 동안 CPU가 계산을 계속하는 것이 아니라 대부분 네트워크 응답을 기다린다.

따라서 비동기 클라이언트와 연결할 예정인 Service 인터페이스를 처음부터 `async`로 설계한다.

FastAPI 공식 문서에서는 `await`로 호출하는 서드파티 라이브러리를 사용할 경우 경로 처리 함수도 `async def`로 선언하도록 설명한다. OpenAI 공식 Python SDK 역시 동기 클라이언트와 비동기 클라이언트를 모두 제공하며, 비동기 클라이언트는 `await` 방식으로 호출할 수 있다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

---

#### 9.3 텍스트 정규화
```python
normalized_text = " ".join(text.split())
```

다음 입력을 생각해 보자.

```text
FastAPI는


Python 기반의   웹 프레임워크입니다.
```

`split()`은 연속된 공백과 줄바꿈을 기준으로 문자열을 나눈다.

```python
[
    "FastAPI는",
    "Python",
    "기반의",
    "웹",
    "프레임워크입니다.",
]
```

다시 하나의 공백으로 결합한다.

```text
FastAPI는 Python 기반의 웹 프레임워크입니다.
```

실제 AI 서비스에서도 모델에 전달하기 전에 필요 없는 공백이나 제어문자를 정리하는 전처리를 수행할 수 있다.

단, 모든 줄바꿈을 무조건 제거하는 것이 항상 좋은 것은 아니다. 문단 구조, 표, 코드 블록이 중요한 문서는 원래 구조를 보존해야 한다.

---

### 10. Router 작성
파일:

```text
app/api/v1/ai.py
```

```python
from fastapi import APIRouter, Depends, status

from app.schemas.summary import SummaryCreateRequest, SummaryResponse
from app.services.ai_service import AIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def get_ai_service() -> AIService:
    return AIService()


@router.post(
    "/summaries",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def create_summary(
    request: SummaryCreateRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> SummaryResponse:
    summary = await ai_service.summarize(request.text)

    return SummaryResponse(
        summary=summary,
        input_length=len(request.text),
        status="completed",
    )
```

---

### 11. Router 코드 분석
#### 11.1 Router Prefix
```python
router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)
```

이 Router의 모든 API에는 `/ai`가 붙는다.

```text
/summaries
        ↓
/ai/summaries
```

`main.py`에서 `/api/v1` prefix를 추가하면 최종 경로는 다음과 같다.

```text
/api/v1/ai/summaries
```

---

#### 11.2 의존성 제공 함수
```python
def get_ai_service() -> AIService:
    return AIService()
```

AIService 객체를 생성해 반환한다.

Router에서 직접 다음과 같이 생성할 수도 있다.

```python
ai_service = AIService()
```

하지만 `Depends()`를 사용하면 구현을 교체하기 쉬워진다.

```python
ai_service: AIService = Depends(get_ai_service)
```

FastAPI의 의존성 주입 시스템은 외부 컴포넌트를 경로 처리 함수에 연결하고, 공통 로직이나 객체 생성을 분리하는 데 사용할 수 있다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/ "Dependencies"))

---

#### 11.3 Service 호출
```python
summary = await ai_service.summarize(request.text)
```

AIService의 `summarize()`가 `async def`로 선언되어 있으므로 `await`를 사용한다.

잘못된 호출:

```python
summary = ai_service.summarize(request.text)
```

이 경우 실제 요약 문자열이 아니라 Coroutine 객체를 얻게 된다.

개념적으로는 다음과 같다.

```text
ai_service.summarize(...)
        ↓
아직 실행 완료되지 않은 비동기 작업
        ↓ await
최종 결과 문자열
```

---

#### 11.4 응답 모델 생성
```python
return SummaryResponse(
    summary=summary,
    input_length=len(request.text),
    status="completed",
)
```

AIService가 반환한 문자열을 우리 API의 응답 계약으로 변환한다.

Router는 Provider 전용 응답 객체를 반환하지 않는다.

---

### 12. 애플리케이션에 Router 등록
파일:

```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.ai import router as ai_router


app = FastAPI(
    title="AIKOS AI Backend",
    version="1.0.0",
)


app.include_router(
    ai_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }
```

최종 엔드포인트:

```text
POST /api/v1/ai/summaries
```

---

### 13. 서버 실행
프로젝트 루트에서 실행한다.

```bash
uvicorn app.main:app --reload
```

브라우저에서 다음 주소로 이동한다.

```text
http://127.0.0.1:8000/docs
```

Swagger UI에서 다음 API를 확인한다.

```text
POST /api/v1/ai/summaries
```

---

### 14. API 테스트
#### 14.1 정상 요청
```json
{
  "text": "FastAPI는 Python 타입 힌트를 기반으로 API를 개발할 수 있도록 지원하는 웹 프레임워크입니다. 요청 검증과 API 문서화를 자동으로 제공하여 백엔드 개발 생산성을 높여 줍니다."
}
```

예상 응답:

```json
{
  "summary": "[연습용 요약] FastAPI는 Python 타입 힌트를 기반으로 API를 개발할 수 있도록 지원하는 웹 프레임워크입니다. 요청 검증과 API 문서화를 자동으로 제공하여 백엔드 개발 생산성을 높여 줍니다.",
  "input_length": 107,
  "status": "completed"
}
```

---

#### 14.2 curl 테스트
```bash
curl -X POST \
  "http://127.0.0.1:8000/api/v1/ai/summaries" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI는 사용자 애플리케이션과 AI 모델 사이에서 요청 검증, 보안, 프롬프트 구성, 모델 호출, 응답 변환을 담당할 수 있습니다."
  }'
```

---

#### 14.3 너무 짧은 요청
```json
{
  "text": "짧음"
}
```

`min_length=10` 조건을 만족하지 않으므로 FastAPI가 `422 Unprocessable Entity` 응답을 반환한다.

Service는 호출되지 않는다.

```text
요청
 ↓
Pydantic 검증 실패
 ↓
422 응답
```

이것은 매우 중요하다.

잘못된 입력을 AI Provider까지 보내면 불필요한 비용이 발생할 수 있다.

```text
검증 실패 요청
   X
AI API 호출 없음
```

---

### 15. 의존성 주입이 필요한 이유
#### 15.1 실제 Service와 Fake Service 교체
테스트에서는 실제 AI API를 호출하고 싶지 않다.

다음과 같은 Fake Service를 사용할 수 있다.

```python
class FakeAIService:
    async def summarize(self, text: str) -> str:
        return "테스트 요약 결과"
```

FastAPI의 dependency override를 사용하면 테스트 중에 구현을 교체할 수 있다.

```python
app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
```

이후 Router 코드는 수정할 필요가 없다.

```text
운영 환경
Router → OpenAIService

테스트 환경
Router → FakeAIService
```

---

#### 15.2 Provider 교체
나중에는 다음 구현을 만들 수 있다.

```text
OpenAIService
OllamaService
GeminiService
```

Router는 특정 Provider를 몰라야 한다.

```python
summary = await ai_service.summarize(request.text)
```

Router 입장에서는 `summarize()`가 어떻게 구현되어 있는지만 중요하지, OpenAI인지 Ollama인지는 중요하지 않다.

---

### 16. 더 나은 추상화 — Protocol
Python의 `Protocol`을 사용하면 AI Service가 지켜야 할 계약을 정의할 수 있다.

파일:

```text
app/services/ai_service.py
```

```python
from typing import Protocol


class AIServiceProtocol(Protocol):
    async def summarize(self, text: str) -> str:
        ...


class FakeAIService:
    async def summarize(self, text: str) -> str:
        normalized_text = " ".join(text.split())
        preview = normalized_text[:120]

        if len(normalized_text) > 120:
            preview += "..."

        return f"[연습용 요약] {preview}"
```

Router:

```python
from fastapi import APIRouter, Depends

from app.schemas.summary import SummaryCreateRequest, SummaryResponse
from app.services.ai_service import AIServiceProtocol, FakeAIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def get_ai_service() -> AIServiceProtocol:
    return FakeAIService()


@router.post(
    "/summaries",
    response_model=SummaryResponse,
)
async def create_summary(
    request: SummaryCreateRequest,
    ai_service: AIServiceProtocol = Depends(get_ai_service),
) -> SummaryResponse:
    summary = await ai_service.summarize(request.text)

    return SummaryResponse(
        summary=summary,
        input_length=len(request.text),
        status="completed",
    )
```

---

#### 16.1 Protocol의 의미
`AIServiceProtocol`은 다음 규칙을 선언한다.

```text
AI Service라면
summarize(text: str) 비동기 메서드를 제공해야 한다.
그리고 문자열을 반환해야 한다.
```

구현체는 달라질 수 있다.

```python
class OpenAIService:
    async def summarize(self, text: str) -> str:
        ...


class OllamaService:
    async def summarize(self, text: str) -> str:
        ...


class FakeAIService:
    async def summarize(self, text: str) -> str:
        ...
```

세 구현 모두 같은 계약을 따른다.

```text
AIServiceProtocol
     ▲
     ├── FakeAIService
     ├── OpenAIService
     └── OllamaService
```

---

### 17. 실무 프로젝트에서의 구조
AI 기능이 많아지면 하나의 `AIService`가 모든 기능을 담당하지 않도록 주의해야 한다.

잘못된 예:

```text
class AIService:
    async def summarize(...):
        ...

    async def translate(...):
        ...

    async def extract_keywords(...):
        ...

    async def classify(...):
        ...

    async def answer_question(...):
        ...

    async def generate_image(...):
        ...

    async def transcribe_audio(...):
        ...
```

이 클래스는 시간이 지나면서 지나치게 커진다.

기능별 Service를 분리할 수 있다.

```text
services/
├── summary_service.py
├── keyword_service.py
├── classification_service.py
├── question_answer_service.py
└── translation_service.py
```

Provider 통신은 별도 Client로 분리한다.

```text
clients/
├── openai_client.py
└── ollama_client.py
```

전체 구조:

```text
app/
├── api/
│   └── v1/
│       ├── summaries.py
│       ├── keywords.py
│       └── answers.py
│
├── schemas/
│   ├── summary.py
│   ├── keyword.py
│   └── answer.py
│
├── services/
│   ├── summary_service.py
│   ├── keyword_service.py
│   └── answer_service.py
│
├── clients/
│   ├── base.py
│   ├── openai_client.py
│   └── ollama_client.py
│
├── repositories/
│   ├── document_repository.py
│   └── analysis_repository.py
│
├── core/
│   ├── config.py
│   ├── exceptions.py
│   └── logging.py
│
└── main.py
```

---

### 18. Service와 Client의 차이
학습자가 자주 혼동하는 부분이다.

#### AI Client
AI Provider와 기술적으로 통신한다.

```text
HTTP 요청
API Key
모델 파라미터
SDK 호출
Timeout
Provider 응답 해석
```

예:

```python
class OpenAIClient:
    async def generate(self, prompt: str) -> str:
        ...
```

#### Application Service
우리 서비스의 업무 흐름을 담당한다.

```text
문서 조회
권한 확인
프롬프트용 데이터 준비
AI Client 호출
결과 저장
응답 생성
```

예:

```python
class SummaryService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        ai_client: AIClientProtocol,
    ):
        self.document_repository = document_repository
        self.ai_client = ai_client

    async def summarize_document(
        self,
        document_id: int,
        user_id: int,
    ) -> str:
        document = self.document_repository.get_by_id(document_id)

        if document.owner_id != user_id:
            raise PermissionError("문서 접근 권한이 없습니다.")

        summary = await self.ai_client.generate(document.content)

        return summary
```

차이를 한 문장으로 정리하면 다음과 같다.

```text
Client는 외부 AI 시스템을 이해하고,
Service는 우리 업무를 이해한다.
```

---

### 19. 자주 발생하는 실수
#### 실수 1 — React에 AI API Key 저장
```env
VITE_OPENAI_API_KEY=...
```

##### 문제
브라우저에서 노출될 수 있다.

##### 해결
AI Provider Key는 FastAPI 서버 환경변수에만 저장한다.

---

#### 실수 2 — Router에서 AI SDK 직접 호출
```text
@router.post("/summaries")
async def summarize(...):
    response = await openai_client.responses.create(...)
```

##### 문제
HTTP 계층과 Provider 통신 계층이 결합된다.

##### 해결
```text
Router → Service → AI Client
```

구조를 사용한다.

---

#### 실수 3 — Provider 응답 전체 반환
```python
return provider_response
```

##### 문제
프론트엔드가 특정 Provider와 SDK 구조에 종속된다.

##### 해결
우리 서비스의 Pydantic 응답 모델로 변환한다.

---

#### 실수 4 — 사용자 입력을 검증하지 않음
```python
class Request(BaseModel):
    text: str
```

##### 문제
지나치게 긴 요청이 AI Provider로 전달될 수 있다.

##### 해결
```python
text: str = Field(min_length=10, max_length=20_000)
```

단, 문자 수와 토큰 수는 같지 않으므로 실제 서비스에서는 토큰 기준 검증도 고려한다.

---

#### 실수 5 — 비동기 메서드를 `await`하지 않음
```python
result = ai_service.summarize(text)
```

##### 문제
최종 결과가 아니라 Coroutine 객체를 받는다.

##### 해결
```python
result = await ai_service.summarize(text)
```

---

#### 실수 6 — 모든 AI 기능을 하나의 클래스에 넣음
```text
AIService
 ├─ 요약
 ├─ 번역
 ├─ 분류
 ├─ 질의응답
 ├─ 이미지 생성
 └─ 음성 처리
```

##### 문제
클래스가 지나치게 커지고 변경 영향 범위가 넓어진다.

##### 해결
업무 기능별 Service와 Provider별 Client를 구분한다.

---

#### 실수 7 — Fake 구현 없이 처음부터 실제 API에 의존
##### 문제
- API Key가 없으면 개발할 수 없다.
    
- 테스트할 때마다 비용이 발생한다.
    
- 외부 서비스 장애 시 개발이 중단된다.
    
- 테스트 결과가 매번 달라질 수 있다.
    

##### 해결
먼저 인터페이스와 Fake 구현으로 API 계약을 완성한 후 실제 Provider를 연결한다.

---

### 20. Best Practice
#### 20.1 외부 AI Provider를 인프라로 취급한다
OpenAI나 Ollama는 우리 서비스의 중심이 아니라 교체 가능한 외부 의존성으로 본다.

```text
우리 서비스
   ↓
AI Client Interface
   ↓
외부 Provider
```

---

#### 20.2 API 계약을 Provider 계약과 분리한다
프론트엔드 요청:

```json
{
  "document_id": 10,
  "summary_type": "executive"
}
```

Provider 요청:

```json
{
  "model": "...",
  "instructions": "...",
  "input": "..."
}
```

둘을 동일하게 만들지 않는다.

---

#### 20.3 입력과 출력을 모두 검증한다
AI 서비스에서는 입력 검증만으로 충분하지 않다.

```text
사용자 입력 검증
        ↓
AI 호출
        ↓
AI 출력 검증
```

LLM은 요청한 형식을 항상 완벽하게 지킨다고 보장할 수 없다.

따라서 이후 Unit에서는 구조화된 출력과 Pydantic 검증을 연결한다.

---

#### 20.4 AI 호출은 비용이 있는 외부 I/O라고 생각한다
데이터베이스 조회보다 더 신중하게 관리해야 한다.

- 불필요한 중복 호출 방지
    
- 입력 크기 제한
    
- Timeout 적용
    
- Retry 횟수 제한
    
- 사용량 로깅
    
- 결과 캐싱 검토
    
- 사용자별 호출 제한
    

---

#### 20.5 Router는 얇게 유지한다
좋은 Router:

```python
@router.post("/summaries")
async def create_summary(
    request: SummaryCreateRequest,
    service: SummaryService = Depends(get_summary_service),
) -> SummaryResponse:
    return await service.create_summary(request)
```

Router는 HTTP 계약만 담당한다.

---

### 21. 실습
#### 실습 목표
- AI Backend의 계층 구조를 이해한다.
    
- 요청·응답 모델을 정의한다.
    
- Fake AI Service를 구현한다.
    
- 의존성 주입으로 Router와 Service를 연결한다.
    
- 실제 AI API 없이 요약 엔드포인트를 완성한다.
    

---

#### 실습 절차
##### 1단계 — 디렉터리 생성
```bash
mkdir -p app/api/v1
mkdir -p app/schemas
mkdir -p app/services
```

각 디렉터리에 `__init__.py` 파일을 만든다.

---

##### 2단계 — 요청·응답 모델 작성
```text
app/schemas/summary.py
```

```python
from pydantic import BaseModel, Field


class SummaryCreateRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
    )


class SummaryResponse(BaseModel):
    summary: str
    input_length: int
    status: str
```

---

##### 3단계 — AI Service 계약과 Fake 구현 작성
```text
app/services/ai_service.py
```

```python
from typing import Protocol


class AIServiceProtocol(Protocol):
    async def summarize(self, text: str) -> str:
        ...


class FakeAIService:
    async def summarize(self, text: str) -> str:
        normalized_text = " ".join(text.split())
        preview = normalized_text[:120]

        if len(normalized_text) > 120:
            preview += "..."

        return f"[연습용 요약] {preview}"
```

---

##### 4단계 — Router 작성
```text
app/api/v1/ai.py
```

```python
from fastapi import APIRouter, Depends, status

from app.schemas.summary import SummaryCreateRequest, SummaryResponse
from app.services.ai_service import AIServiceProtocol, FakeAIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def get_ai_service() -> AIServiceProtocol:
    return FakeAIService()


@router.post(
    "/summaries",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def create_summary(
    request: SummaryCreateRequest,
    ai_service: AIServiceProtocol = Depends(get_ai_service),
) -> SummaryResponse:
    summary = await ai_service.summarize(request.text)

    return SummaryResponse(
        summary=summary,
        input_length=len(request.text),
        status="completed",
    )
```

---

##### 5단계 — Router 등록
```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.ai import router as ai_router


app = FastAPI(
    title="AIKOS AI Backend",
    version="1.0.0",
)

app.include_router(
    ai_router,
    prefix="/api/v1",
)
```

---

##### 6단계 — 서버 실행
```bash
uvicorn app.main:app --reload
```

---

##### 7단계 — Swagger UI 테스트
```text
http://127.0.0.1:8000/docs
```

다음 API를 실행한다.

```text
POST /api/v1/ai/summaries
```

---

### 22. 예상 결과
요청:

```json
{
  "text": "FastAPI는 AI 모델을 직접 구현하는 도구가 아니라 사용자 요청과 AI 모델 사이의 서비스 계층을 구축하는 웹 프레임워크입니다."
}
```

응답:

```json
{
  "summary": "[연습용 요약] FastAPI는 AI 모델을 직접 구현하는 도구가 아니라 사용자 요청과 AI 모델 사이의 서비스 계층을 구축하는 웹 프레임워크입니다.",
  "input_length": 67,
  "status": "completed"
}
```

---

### 23. 실습 확인
다음 항목을 확인한다.

-  `/api/v1/ai/summaries`가 Swagger UI에 표시되는가?
    
-  정상적인 텍스트를 보내면 HTTP 200이 반환되는가?
    
-  10자 미만의 텍스트를 보내면 HTTP 422가 반환되는가?
    
-  20,000자를 초과하면 요청 검증에 실패하는가?
    
-  Router에 요약 로직이 직접 작성되어 있지 않은가?
    
-  AI Service가 `async def`로 선언되어 있는가?
    
-  Service 호출에 `await`가 사용되었는가?
    
-  Provider 전용 응답이 아닌 `SummaryResponse`가 반환되는가?
    

---

### 24. 응용 과제
#### 과제 1 — 요약 길이 선택
요청 모델에 다음 필드를 추가한다.

```python
summary_length: Literal["short", "medium", "long"]
```

각 값에 따라 Fake Service의 미리보기 길이를 변경한다.

```text
short  → 50자
medium → 120자
long   → 250자
```

---

#### 과제 2 — 요약 문체 선택
다음 필드를 추가한다.

```python
tone: Literal["neutral", "professional", "friendly"]
```

응답 앞부분에 문체를 표시한다.

```text
[전문적인 요약]
[친근한 요약]
```

---

#### 과제 3 — 빈 문자열 정규화 검증
다음 입력은 길이가 10자 이상이지만 실제 내용은 공백뿐일 수 있다.

```json
{
  "text": "             "
}
```

Pydantic의 `field_validator`를 사용해 공백 제거 후 비어 있는 입력을 차단한다.

예:

```python
from pydantic import BaseModel, Field, field_validator


class SummaryCreateRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("요약할 텍스트가 필요합니다.")

        return normalized
```

---

#### 과제 4 — 테스트용 Service 교체
다음 Service를 작성한다.

```python
class TestAIService:
    async def summarize(self, text: str) -> str:
        return "고정된 테스트 결과"
```

FastAPI dependency override를 사용하여 테스트 환경에서만 교체한다.

---

### 25. 이해도 확인
#### 질문 1
React에서 AI Provider API를 직접 호출하면 안 되는 가장 중요한 이유는 무엇인가?

##### 모범 답안
React 코드는 브라우저에서 실행되기 때문에 API Key를 안전하게 숨길 수 없다. 또한 사용량, 입력 크기, 모델, 비용, 인증과 같은 정책을 서버에서 통제하기 어렵다. 따라서 React는 FastAPI를 호출하고 FastAPI가 AI Provider와 통신해야 한다.

---

#### 질문 2
AI Backend는 단순한 API Proxy와 무엇이 다른가?

##### 모범 답안
AI Backend는 요청을 그대로 전달하는 데 그치지 않는다. 사용자 인증, 권한 확인, 데이터 조회, 입력 검증, 프롬프트 구성, 모델 선택, 출력 검증, 결과 저장, 비용 관리, 오류 처리까지 담당한다.

---

#### 질문 3
Router에서 OpenAI SDK를 직접 호출하면 어떤 문제가 생기는가?

##### 모범 답안
HTTP 처리와 외부 AI Provider 통신이 결합된다. 그 결과 테스트와 Provider 교체가 어려워지고, 프롬프트·오류 처리·로깅 같은 코드가 여러 Router에 중복될 수 있다.

---

#### 질문 4
AI Client와 Application Service의 차이는 무엇인가?

##### 모범 답안
AI Client는 API Key, SDK, 모델 파라미터, Timeout처럼 외부 AI Provider와 통신하는 방법을 담당한다. Application Service는 문서 조회, 권한 확인, AI 호출, 결과 저장과 같은 우리 서비스의 업무 흐름을 담당한다.

---

#### 질문 5
Fake AI Service를 먼저 만드는 이유는 무엇인가?

##### 모범 답안
실제 API Key와 외부 서비스 없이 API 계약과 계층 구조를 개발할 수 있기 때문이다. 테스트 비용을 줄이고 외부 API 장애나 확률적인 응답에 영향을 받지 않으며, 이후 실제 구현으로 쉽게 교체할 수 있다.

---

### 26. 핵심 내용 정리
#### 핵심 1
AI Backend는 사용자와 AI 모델 사이의 중간 서버다.

```text
React → FastAPI → AI Provider
```

---

#### 핵심 2
FastAPI는 단순히 AI 요청을 전달하지 않는다.

```text
검증
인증
권한
데이터 준비
프롬프트 구성
모델 호출
출력 검증
저장
비용 관리
예외 처리
```

를 담당한다.

---

#### 핵심 3
React가 외부 AI API를 직접 호출하게 만들면 안 된다.

```text
API Key 노출
비용 통제 불가
비즈니스 로직 노출
Provider 종속
```

문제가 발생한다.

---

#### 핵심 4
AI Provider는 교체 가능한 외부 의존성으로 다룬다.

```text
Router
  ↓
Application Service
  ↓
AI Client Interface
  ↓
OpenAI / Ollama / 기타 Provider
```

---

#### 핵심 5
우리 API 계약과 Provider API 계약을 분리한다.

```text
Provider Response
        ↓ 변환
우리 Response Model
```

React에는 Provider 응답을 그대로 반환하지 않는다.

---

#### 핵심 6
실제 AI API를 연결하기 전에 Fake 구현으로 구조와 API 계약을 먼저 완성할 수 있다.

```text
FakeAIService
      ↓ 교체
OpenAIService
```

---

### 27. 한 문장으로 설명하기
> FastAPI 기반 AI Backend는 사용자의 요청을 안전하게 검증하고 필요한 데이터를 준비한 뒤 AI Provider를 호출하며, 모델의 응답을 우리 서비스의 안정적인 API 계약으로 변환하는 중간 서비스 계층이다.

---

### FastAPI Part 5. AI Backend Integration

## Module 36. AI Provider와 환경 설정


### Module 실습 예제

- [예제 1: provider_factory.py](examples/module_36/provider_factory.py) — 설정값에 따라 Fake·OpenAI Provider 구현을 선택합니다.
- [예제 2: secret_settings.py](examples/module_36/secret_settings.py) — SecretStr로 API Key가 출력되는 것을 방지합니다.



#### 프로젝트 연결 학습
- **문제 상황:** Provider 종류와 키를 환경별로 바꿀 수 있게 한다.
- **오늘 만드는 것:** AI Settings와 Client Factory 정책을 구성한다.
- **AI 플랫폼의 위치:** 실행 환경에 맞는 AI Client를 조립한다.
- **실무에서 많이 하는 실수:** 환경변수 이름을 코드 곳곳에서 직접 읽거나 키를 로그로 남긴다.
- **5분 실습:** Fake와 실제 Provider를 설정만으로 전환하는 구조를 그린다.

> **학습 층위 — AI 연결**  
> Unit 22의 Settings 기초를 반복하는 단원이 아니라, Provider 선택·API Key·Model·조건부 검증을 AI 서비스 구성에 적용하는 단원이다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI Provider란 무엇인가?
    
- AI Model과 AI Provider는 무엇이 다른가?
    
- API Key는 왜 소스 코드에 작성하면 안 되는가?
    
- 환경변수와 `.env` 파일은 어떤 차이가 있는가?
    
- 개발·테스트·운영 환경의 설정을 왜 분리해야 하는가?
    
- Pydantic Settings는 어떤 문제를 해결하는가?
    
- FastAPI에서 설정 객체를 왜 한 번만 생성해야 하는가?
    
- `SecretStr`을 사용하면 무엇이 안전해지는가?
    
- 애플리케이션 시작 시 설정을 검증해야 하는 이유는 무엇인가?
    
- 특정 AI Provider에 종속되지 않는 설정 구조는 어떻게 만드는가?
    

---

### 2. 문제 이해 — Why
#### 2.1 AI 모델을 사용하려면 무엇이 필요한가?
이 단원은 LLM의 내부 원리를 선행 지식으로 요구하지 않는다. 여기서는 LLM을 입력을 받아 결과를 반환하는 외부 AI Provider로 다룬다.

```text
사용자 입력
   ↓
Tokenizer
   ↓
Transformer
   ↓
다음 Token 예측
   ↓
생성 결과
```

그러나 실제 서비스에서 LLM을 사용하려면 단순히 모델의 원리를 아는 것만으로는 부족하다.

백엔드에는 다음 정보가 필요하다.

```text
어떤 Provider를 사용할 것인가?
어떤 Model을 사용할 것인가?
API Key는 무엇인가?
API 주소는 어디인가?
응답을 얼마나 기다릴 것인가?
최대 출력 크기는 얼마인가?
개발환경과 운영환경의 설정은 같은가?
```

예를 들면 다음과 같다.

```python
provider = "openai"
model = "설정된 모델"
api_key = "비밀 API Key"
timeout_seconds = 30
max_output_tokens = 1000
```

이 값들은 모두 AI 서비스의 **설정값(Configuration)** 이다.

---

#### 2.2 설정값을 코드에 직접 작성하면 안 될까?
처음에는 다음과 같이 작성하기 쉽다.

```python
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key="실제-API-Key",
)
```

또는 모델 이름도 코드에 직접 작성할 수 있다.

```python
response = await client.responses.create(
    model="특정-모델-이름",
    input="안녕하세요.",
)
```

이 방법은 코드가 짧아 보이지만 심각한 문제를 만든다.

---

#### 2.3 문제 1 — 비밀정보가 저장소에 남는다
API Key를 코드에 작성하고 Git에 커밋하면 다음 위치에 남을 수 있다.

- 현재 소스 코드
    
- Git Commit History
    
- GitHub 또는 GitLab 저장소
    
- 코드 리뷰 화면
    
- CI 빌드 로그
    
- 배포 아카이브
    
- 개발자의 로컬 복사본
    
- 백업 시스템
    

현재 코드에서 API Key를 삭제하더라도 과거 Commit에 남아 있을 수 있다.

```text
현재 파일에서 Key 삭제
        ≠
Git 기록에서 완전 삭제
```

API Key가 노출되면 다른 사람이 그 Key를 사용해 AI API를 호출할 수 있다.

그 결과 다음 문제가 발생할 수 있다.

```text
무단 사용
비용 증가
사용량 제한 초과
서비스 중단
데이터 보안 문제
```

따라서 비밀정보를 소스 코드와 분리해야 한다.

OpenAI 공식 Python 라이브러리도 API Key를 코드에 직접 저장하기보다는 `OPENAI_API_KEY` 환경변수나 `.env` 기반으로 관리하는 방식을 안내한다.

---

#### 2.4 문제 2 — 환경마다 설정이 다르다
하나의 애플리케이션은 여러 환경에서 실행된다.

```text
Local Development
Test
Staging
Production
```

각 환경은 서로 다른 설정을 사용할 수 있다.

|설정|개발환경|테스트환경|운영환경|
|---|---|---|---|
|AI Provider|Fake 또는 Local|Fake|OpenAI|
|Model|저비용 모델|테스트 모델|운영 모델|
|API Key|개인 개발 Key|테스트용 Key|운영 Secret|
|Timeout|60초|5초|30초|
|Logging|DEBUG|WARNING|INFO|
|Database|Local DB|Test DB|Production DB|

코드에 값을 직접 작성하면 환경을 바꿀 때마다 코드를 수정해야 한다.

```text
개발 배포
  ↓ 코드 수정
테스트 배포
  ↓ 코드 수정
운영 배포
```

이는 설정과 코드가 섞인 구조다.

올바른 구조는 동일한 코드를 유지하고 외부 설정만 변경하는 것이다.

```text
동일한 Application Code
          ↑
 ┌────────┼────────┐
 │        │        │
개발 설정 테스트 설정 운영 설정
```

---

#### 2.5 문제 3 — 모델 변경이 코드 변경이 된다
AI 서비스는 모델을 변경할 가능성이 높다.

변경 이유는 다음과 같다.

- 비용 최적화
    
- 품질 개선
    
- 응답 속도 개선
    
- 모델 지원 종료
    
- 고객별 모델 구분
    
- Provider 장애 대응
    
- 특정 기능 지원 여부
    
- 개발용 모델과 운영용 모델 분리
    

모델 이름이 여러 파일에 직접 작성되어 있다면 변경이 어려워진다.

```python
### summary_service.pymodel="model-a"

### translation_service.pymodel="model-a"

### keyword_service.pymodel="model-a"

### answer_service.pymodel="model-a"
```

모델을 변경하려면 모든 파일을 찾아 수정해야 한다.

```text
model-a
   ↓
model-b
```

하나라도 수정하지 않으면 기능마다 다른 모델을 호출할 수 있다.

따라서 모델 이름도 중앙 설정에서 관리해야 한다.

---

#### 2.6 문제 4 — 잘못된 설정을 너무 늦게 발견한다
다음과 같은 상황을 생각해 보자.

```text
서버 시작 성공
   ↓
사용자가 AI 기능 요청
   ↓
그때 API Key 누락 발견
   ↓
요청 실패
```

애플리케이션에 반드시 필요한 설정이라면 서버가 시작될 때 검증하는 것이 좋다.

```text
서버 시작
   ↓
설정 검증
   ├─ 정상 → 서비스 시작
   └─ 오류 → 즉시 시작 실패
```

잘못된 설정으로 애플리케이션이 실행되는 것보다 시작 단계에서 명확하게 실패하는 편이 안전하다.

이를 다음 원칙으로 표현할 수 있다.

> **Fail Fast: 잘못된 상태라면 가능한 한 빠르게 실패한다.**

---

### 3. 개념 이해 — Concept
#### 3.1 AI Provider란 무엇인가?
AI Provider는 AI 모델을 사용할 수 있도록 API나 실행 환경을 제공하는 주체 또는 시스템이다.

예를 들면 다음과 같다.

```text
OpenAI
Azure OpenAI
Google
Anthropic
AWS Bedrock
Ollama
사내 Model Server
```

AI Provider는 일반적으로 다음 기능을 제공한다.

- 모델 접근
    
- 인증
    
- 요청 API
    
- 응답 형식
    
- 사용량 측정
    
- Rate Limit
    
- 과금
    
- 모델 버전 관리
    
- 보안 정책
    
- 장애 관리
    

---

#### 3.2 AI Model과 AI Provider의 차이
두 개념을 구분해야 한다.

##### AI Model
입력을 받아 추론 결과를 생성하는 학습된 모델이다.

```text
입력
 ↓
Model
 ↓
출력
```

##### AI Provider
그 모델을 실제 서비스에서 호출할 수 있도록 API와 운영 환경을 제공한다.

```text
사용자 애플리케이션
        ↓ API
AI Provider
        ↓
AI Model
```

비유하면 다음과 같다.

```text
AI Model    = 자동차
AI Provider = 자동차를 빌리고 관리할 수 있는 렌터카 회사
API Key     = 계약자 확인용 출입 카드
API         = 차량을 요청하는 절차
```

자동차와 렌터카 회사가 같은 개념이 아니듯, Model과 Provider도 같은 개념이 아니다.

---

#### 3.3 API Key란 무엇인가?
API Key는 외부 API가 호출자를 식별하고 인증하기 위해 사용하는 비밀 문자열이다.

```text
FastAPI Server
      │
      │ API Key
      ▼
AI Provider
```

Provider는 API Key를 통해 다음을 판단할 수 있다.

- 누가 요청했는가?
    
- 요청 권한이 있는가?
    
- 어느 프로젝트의 사용량인가?
    
- Rate Limit을 어떻게 적용할 것인가?
    
- 비용을 어느 계정에 청구할 것인가?
    

API Key는 사용자 비밀번호와 완전히 같은 개념은 아니지만, **외부에 노출해서는 안 되는 인증정보**라는 점은 같다.

---

#### 3.4 환경변수란 무엇인가?
환경변수는 운영체제나 실행 환경이 프로세스에 전달하는 이름과 값의 쌍이다.

예:

```text
OPENAI_API_KEY=...
AI_PROVIDER=openai
AI_MODEL=...
AI_TIMEOUT_SECONDS=30
```

Python에서는 다음과 같이 읽을 수 있다.

```python
import os


api_key = os.getenv("OPENAI_API_KEY")
```

애플리케이션 코드는 Key의 실제 값을 저장하지 않는다.

```text
Source Code
    ↓ 변수 이름만 사용
OPENAI_API_KEY
    ↓ 실행 환경이 실제 값 제공
Secret Value
```

---

#### 3.5 `.env` 파일이란 무엇인가?
`.env`는 환경변수 형식의 값을 파일로 관리하는 개발 편의 수단이다.

```env
APP_ENV=development
AI_PROVIDER=openai
OPENAI_API_KEY=실제-키
OPENAI_MODEL=설정된-모델
AI_TIMEOUT_SECONDS=30
```

`.env` 파일은 주로 로컬 개발환경에서 사용한다.

중요한 점은 다음과 같다.

```text
.env 파일
≠
소스 코드에 포함해도 되는 일반 설정 파일
```

`.env`에는 비밀정보가 포함될 수 있으므로 Git에 Commit하지 않아야 한다.

```gitignore
.env
.env.*
!.env.example
```

여기서 예외로 남긴 파일은 다음과 같다.

```text
.env.example
```

이 파일에는 실제 비밀값이 아닌 필요한 설정 항목의 예시만 작성한다.

```env
APP_ENV=development
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=
AI_TIMEOUT_SECONDS=30
```

---

#### 3.6 환경변수와 `.env`의 관계
환경변수와 `.env`는 완전히 같은 개념이 아니다.

```text
.env 파일
   ↓ 애플리케이션이 읽음
환경변수 형태의 설정값
```

운영환경에서는 `.env` 파일 대신 다음 시스템이 값을 주입할 수 있다.

- Docker Environment
    
- Docker Compose Secrets
    
- Kubernetes Secret
    
- GitHub Actions Secret
    
- AWS Secrets Manager
    
- Azure Key Vault
    
- Google Secret Manager
    
- CI/CD 환경변수
    
- 운영체제 환경변수
    

따라서 `.env`는 여러 설정 주입 방법 중 하나다.

---

### 4. 왜 `os.getenv()`만 사용하지 않는가?
간단한 프로젝트에서는 다음과 같이 설정을 읽을 수 있다.

```python
import os


provider = os.getenv("AI_PROVIDER")
api_key = os.getenv("OPENAI_API_KEY")
timeout = os.getenv("AI_TIMEOUT_SECONDS")
```

하지만 문제가 있다.

---

#### 4.1 모든 값이 문자열이다
환경변수는 기본적으로 문자열로 읽힌다.

```python
timeout = os.getenv("AI_TIMEOUT_SECONDS")
```

`.env`에 다음과 같이 작성해도

```env
AI_TIMEOUT_SECONDS=30
```

Python에서 읽으면 문자열이다.

```python
print(type(timeout))
```

결과:

```text
<class 'str'>
```

따라서 직접 변환해야 한다.

```python
timeout = int(os.getenv("AI_TIMEOUT_SECONDS", "30"))
```

Boolean도 직접 변환해야 한다.

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

설정이 늘어날수록 변환 코드도 많아진다.

---

#### 4.2 필수값 검증이 어렵다
```python
api_key = os.getenv("OPENAI_API_KEY")
```

환경변수가 없으면 `None`을 반환한다.

이 상태로 애플리케이션이 계속 실행될 수 있다.

```text
API Key 없음
   ↓
서버는 일단 시작
   ↓
나중에 AI 호출 때 실패
```

직접 검사하려면 다음 코드가 필요하다.

```python
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 필요합니다.")
```

설정마다 이런 검증을 작성하면 코드가 분산된다.

---

#### 4.3 잘못된 값의 범위를 검증하기 어렵다
```env
AI_TIMEOUT_SECONDS=-100
```

정수 변환에는 성공하지만 올바른 설정은 아니다.

```python
timeout = int("-100")
```

다음과 같은 추가 검증이 필요하다.

```python
if timeout <= 0:
    raise ValueError("Timeout은 0보다 커야 합니다.")
```

---

#### 4.4 설정 이름이 코드 전체에 퍼진다
```python
### openai_client.pyos.getenv("OPENAI_API_KEY")

### summary_service.pyos.getenv("OPENAI_MODEL")

### answer_service.pyos.getenv("OPENAI_MODEL")

### main.pyos.getenv("APP_ENV")
```

환경변수 이름이 여러 파일에 흩어진다.

오타도 컴파일 단계에서 확인되지 않는다.

```python
os.getenv("OPEN_AI_API_KEY")
```

올바른 이름:

```text
OPENAI_API_KEY
```

이런 문제를 해결하기 위해 설정 객체를 만든다.

---

### 5. Pydantic Settings
#### 5.1 Pydantic Settings란 무엇인가?
Pydantic Settings는 환경변수와 설정 파일에서 값을 읽어 타입이 있는 Python 설정 객체로 변환한다.

```text
.env / Environment Variables
            ↓
     Pydantic Settings
            ↓
       Settings Object
```

예를 들어 다음 문자열 설정을

```env
AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
AI_ENABLED=true
```

다음과 같은 타입으로 변환한다.

```python
timeout_seconds: float
max_output_tokens: int
enabled: bool
```

FastAPI 공식 문서도 애플리케이션 설정에 Pydantic Settings를 사용할 수 있으며, `.env` 지원과 테스트 시 의존성 교체, `@lru_cache`를 통한 설정 객체 재사용 방법을 설명한다.

---

#### 5.2 설치
```bash
pip install pydantic-settings
```

현재 프로젝트에 필요한 패키지를 함께 설치하면 다음과 같다.

```bash
pip install fastapi "uvicorn[standard]" pydantic-settings
```

이후 실제 OpenAI 연동 Unit에서 OpenAI SDK를 추가한다.

```bash
pip install openai
```

---

### 6. 구조 이해 — Architecture
#### 6.1 설정 계층의 위치
설정은 `core` 계층에 둔다.

```text
app/
├── api/
├── schemas/
├── services/
├── clients/
├── repositories/
│
├── core/
│   ├── config.py
│   └── dependencies.py
│
└── main.py
```

`core/config.py`는 애플리케이션 전반에서 사용하는 설정을 정의한다.

```text
Environment Variables
        ↓
core/config.py
        ↓
Settings Object
        ↓
Client / Service / Application
```

---

#### 6.2 잘못된 구조
각 파일에서 직접 환경변수를 읽는 구조다.

```text
summary_service.py ──→ os.getenv()
openai_client.py ────→ os.getenv()
main.py ─────────────→ os.getenv()
router.py ───────────→ os.getenv()
```

문제:

- 설정 이름이 분산된다.
    
- 타입 검증이 없다.
    
- 기본값 정책이 분산된다.
    
- 테스트가 어렵다.
    
- 어떤 설정이 필요한지 한눈에 알기 어렵다.
    

---

#### 6.3 권장 구조
```text
Environment / .env
        ↓
Settings
        ↓
Dependency Provider
        ↓
AI Client
        ↓
AI Service
```

설정 접근 경로가 하나로 모인다.

```text
              ┌→ main.py
              ├→ OpenAIClient
Settings ─────┼→ AIService
              └→ Logging Config
```

---

### 7. 실습 준비
#### 7.1 이번 Unit에서 구현할 기능
이번 Unit에서는 실제 AI 요청을 보내지 않는다.

대신 다음 기능을 구현한다.

- 애플리케이션 설정 모델
    
- `.env` 파일 로딩
    
- 설정값 타입 검증
    
- API Key 비밀값 처리
    
- `@lru_cache`를 이용한 설정 재사용
    
- 설정 확인용 안전한 API
    
- 테스트 환경에서 설정 교체
    
- Provider별 설정 검증
    

---

#### 7.2 프로젝트 구조
```text
app/
├── api/
│   └── v1/
│       ├── ai.py
│       └── system.py
│
├── schemas/
│   └── summary.py
│
├── services/
│   └── ai_service.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── dependencies.py
│
└── main.py

.env
.env.example
.gitignore
```

---

### 8. 기본 설정 모델 작성
파일:

```text
app/core/config.py
```

```python
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AIKOS AI Backend"
    app_version: str = "1.0.0"
    app_env: Literal["development", "test", "staging", "production"] = (
        "development"
    )
    debug: bool = False

    ai_provider: Literal["fake", "openai", "ollama"] = "fake"

    openai_api_key: SecretStr | None = None
    openai_model: str | None = None

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str | None = None

    ai_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        le=300,
    )
    ai_max_output_tokens: int = Field(
        default=1000,
        ge=1,
        le=100_000,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_provider_settings(self) -> "Settings":
        if self.ai_provider == "openai":
            if self.openai_api_key is None:
                raise ValueError(
                    "AI_PROVIDER가 openai이면 "
                    "OPENAI_API_KEY가 필요합니다."
                )

            if not self.openai_model:
                raise ValueError(
                    "AI_PROVIDER가 openai이면 "
                    "OPENAI_MODEL이 필요합니다."
                )

        if self.ai_provider == "ollama" and not self.ollama_model:
            raise ValueError(
                "AI_PROVIDER가 ollama이면 "
                "OLLAMA_MODEL이 필요합니다."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

### 9. 설정 모델 코드 분석
#### 9.1 `BaseSettings`
```text
class Settings(BaseSettings):
```

`BaseSettings`는 일반 Pydantic 모델과 비슷하지만 환경변수에서 값을 읽을 수 있다.

일반 `BaseModel`:

```text
Python 코드가 값을 전달
```

`BaseSettings`:

```text
Python 기본값
환경변수
.env 파일
실행환경 설정
```

등에서 값을 가져올 수 있다.

---

#### 9.2 애플리케이션 기본 정보
```python
app_name: str = "AIKOS AI Backend"
app_version: str = "1.0.0"
```

애플리케이션 이름과 버전이다.

FastAPI 인스턴스를 생성할 때 사용할 수 있다.

```python
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
```

---

#### 9.3 실행 환경 제한
```python
app_env: Literal[
    "development",
    "test",
    "staging",
    "production",
] = "development"
```

`Literal`은 허용되는 값을 제한한다.

정상:

```env
APP_ENV=production
```

오류:

```env
APP_ENV=real-server
```

`real-server`는 허용된 값이 아니므로 설정 객체 생성이 실패한다.

문자열을 자유롭게 받는 것보다 안전하다.

```text
아무 문자열
   ↓ Literal
허용된 값만 통과
```

---

#### 9.4 Provider 제한
```python
ai_provider: Literal["fake", "openai", "ollama"] = "fake"
```

현재 애플리케이션이 사용할 AI Provider를 지정한다.

```env
AI_PROVIDER=openai
```

또는 로컬 개발 중에는 다음과 같이 설정할 수 있다.

```env
AI_PROVIDER=fake
```

Provider를 설정으로 분리하면 코드를 수정하지 않고 구현을 교체할 수 있다.

```text
AI_PROVIDER=fake
       ↓ 설정 변경
AI_PROVIDER=openai
```

---

#### 9.5 `SecretStr`
```python
openai_api_key: SecretStr | None = None
```

API Key는 일반 문자열이 아니라 `SecretStr`로 선언한다.

일반 문자열:

```python
api_key = "secret-value"
print(api_key)
```

출력:

```text
secret-value
```

`SecretStr`:

```python
print(settings.openai_api_key)
```

출력은 실제 값을 그대로 보여주지 않고 마스킹된다.

```text
**********
```

이는 다음 상황에서 실수로 Key가 노출되는 위험을 줄인다.

- 디버깅 출력
    
- 객체 `repr`
    
- 로그 출력
    
- 오류 메시지
    

단, `SecretStr`이 Key를 암호화해서 저장하는 것은 아니다.

```text
SecretStr
=
표시 과정에서 비밀값 노출을 줄이는 타입
```

실제 값을 Provider Client에 전달할 때는 다음과 같이 꺼낸다.

```python
api_key = settings.openai_api_key.get_secret_value()
```

---

#### 9.6 API Key를 선택값으로 둔 이유
```python
openai_api_key: SecretStr | None = None
```

무조건 필수값으로 만들지 않았다.

왜냐하면 Provider가 `fake`나 `ollama`라면 OpenAI API Key가 필요하지 않기 때문이다.

잘못된 설계:

```python
openai_api_key: SecretStr
```

이렇게 선언하면 `AI_PROVIDER=fake` 환경에서도 OpenAI Key가 필요하다.

Provider별 조건부 필수값은 Validator에서 검사한다.

```text
Provider=openai
   ↓
OpenAI Key 필수

Provider=fake
   ↓
OpenAI Key 불필요
```

---

#### 9.7 Timeout 범위 검증
```python
ai_timeout_seconds: float = Field(
    default=30.0,
    gt=0,
    le=300,
)
```

의미:

```text
기본값 = 30초
0보다 커야 함
300초 이하여야 함
```

잘못된 설정:

```env
AI_TIMEOUT_SECONDS=-10
```

또는

```env
AI_TIMEOUT_SECONDS=1000
```

설정 객체 생성 단계에서 실패한다.

Timeout에 상한을 두는 이유는 잘못된 설정으로 요청이 지나치게 오래 대기하는 것을 막기 위해서다.

현재 300초는 교육용 정책 예시다. 실제 상한은 서비스 요구사항에 따라 결정한다.

---

#### 9.8 최대 출력 토큰 범위
```python
ai_max_output_tokens: int = Field(
    default=1000,
    ge=1,
    le=100_000,
)
```

최대 출력량을 설정으로 관리한다.

```text
1 이상
100,000 이하
```

주의할 점은 이 값이 모든 모델에서 그대로 허용된다는 뜻은 아니다.

실제 허용 범위는 사용하는 Provider와 모델의 사양에 따라 달라질 수 있다.

따라서 이 설정은 다음 두 제한을 모두 고려해야 한다.

```text
우리 서비스 정책
        ∩
Provider/Model의 실제 제한
```

---

### 10. `SettingsConfigDict`
```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)
```

---

#### 10.1 `env_file`
```python
env_file=".env"
```

설정을 만들 때 `.env` 파일을 읽도록 지정한다.

```text
Settings()
   ↓
.env 파일 검색
   ↓
환경변수 형식으로 값 읽기
```

---

#### 10.2 `env_file_encoding`
```python
env_file_encoding="utf-8"
```

`.env` 파일을 UTF-8로 읽는다.

한글 설정값이나 설명이 포함되는 경우 인코딩 문제를 줄일 수 있다.

---

#### 10.3 `case_sensitive`
```python
case_sensitive=False
```

환경변수 이름의 대소문자를 엄격히 구분하지 않도록 설정한다.

일반적으로 환경변수는 다음과 같이 대문자로 작성한다.

```env
OPENAI_API_KEY=...
```

Python 필드는 Snake Case 소문자로 작성한다.

```python
openai_api_key
```

Pydantic Settings가 두 이름을 연결한다.

---

#### 10.4 `extra="ignore"`
`.env`에 Settings 모델이 모르는 값이 있어도 무시하도록 설정한다.

예:

```env
UNRELATED_SETTING=value
```

현재 Settings 클래스에 해당 필드가 없어도 오류를 발생시키지 않는다.

다만 엄격한 운영 정책이 필요하다면 `forbid`를 고려할 수 있다.

```text
ignore
장점: 여러 도구가 공유하는 .env 사용이 편함
단점: 환경변수 이름 오타를 놓칠 수 있음

forbid
장점: 알 수 없는 설정을 빠르게 발견
단점: 공용 .env에서 불편할 수 있음
```

프로젝트 정책에 따라 선택한다.

---

### 11. Provider별 조건부 검증
```text
@model_validator(mode="after")
def validate_provider_settings(self) -> "Settings":
```

각 필드의 개별 타입 검증이 끝난 뒤 전체 설정의 관계를 검증한다.

---

#### 11.1 OpenAI 설정 검증
```python
if self.ai_provider == "openai":
    if self.openai_api_key is None:
        raise ValueError(
            "AI_PROVIDER가 openai이면 "
            "OPENAI_API_KEY가 필요합니다."
        )

    if not self.openai_model:
        raise ValueError(
            "AI_PROVIDER가 openai이면 "
            "OPENAI_MODEL이 필요합니다."
        )
```

다음 설정은 잘못되었다.

```env
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=
```

Provider는 OpenAI인데 필수 연결 정보가 없다.

설정 객체가 생성될 때 즉시 실패한다.

---

#### 11.2 Ollama 설정 검증
```python
if self.ai_provider == "ollama" and not self.ollama_model:
    raise ValueError(
        "AI_PROVIDER가 ollama이면 "
        "OLLAMA_MODEL이 필요합니다."
    )
```

Ollama를 사용한다면 실행할 모델 이름이 필요하다.

```env
AI_PROVIDER=ollama
OLLAMA_MODEL=설치된-로컬-모델
```

Ollama 자체의 설치와 모델 관리 방법은 이후 AI Integration의 Ollama 학습 범위에서 자세히 다룬다.

현재 Unit에서는 Provider별 설정 구조만 이해한다.

---

### 12. `@lru_cache`로 설정 객체 재사용
```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

#### 12.1 Cache가 없을 때
다음과 같이 작성할 수 있다.

```python
def get_settings() -> Settings:
    return Settings()
```

FastAPI Dependency로 사용할 경우 요청마다 함수가 호출될 수 있다.

```text
Request 1 → Settings 생성
Request 2 → Settings 생성
Request 3 → Settings 생성
```

`Settings()`가 생성될 때마다 `.env` 파일을 다시 읽고 값을 검증할 수 있다.

설정은 요청마다 변하는 데이터가 아니다.

---

#### 12.2 Cache가 있을 때
```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

첫 번째 호출:

```text
get_settings()
   ↓
Settings 생성
   ↓
Cache 저장
```

이후 호출:

```text
get_settings()
   ↓
기존 Settings 반환
```

전체 흐름:

```text
Request 1 ──→ Settings 생성 ──→ Cache
Request 2 ────────────────────→ Cache
Request 3 ────────────────────→ Cache
```

FastAPI 공식 설정 문서에서도 `@lru_cache`를 사용하면 요청마다 `.env`를 다시 읽는 것을 피하면서 테스트에서는 의존성을 교체할 수 있다고 설명한다.

---

#### 12.3 전역변수와 무엇이 다른가?
다음과 같이 전역 설정을 생성할 수도 있다.

```python
settings = Settings()
```

이 방법도 한 번만 생성된다는 장점이 있다.

하지만 `get_settings()` Dependency 패턴은 테스트에서 교체하기 쉽다.

```python
app.dependency_overrides[get_settings] = override_settings
```

따라서 FastAPI에서는 Dependency 기반 접근이 유연하다.

---

### 13. `.env` 파일 작성
프로젝트 루트:

```text
.env
```

개발 초기에는 Fake Provider를 사용한다.

```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true

AI_PROVIDER=fake

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

이 설정에서는 OpenAI API Key가 필요하지 않다.

---

#### 13.1 OpenAI 사용 설정 예시
실제 값은 직접 입력하되 저장소에는 Commit하지 않는다.

```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true

AI_PROVIDER=openai

OPENAI_API_KEY=실제-API-Key
OPENAI_MODEL=사용할-모델-이름

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

OpenAI 공식 Python SDK는 `OPENAI_API_KEY` 환경변수를 사용할 수 있으며, 클라이언트 생성 시 해당 값을 자동으로 읽는 기본 사용 패턴도 제공한다.

현재 Unit에서는 모델 이름을 설정값으로만 다룬다. 실제 모델 선택과 호출 코드는 Unit 34에서 공식 API 문서를 기준으로 구현한다.

---

#### 13.2 Ollama 사용 설정 예시
```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true

AI_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=설치된-로컬-모델

AI_TIMEOUT_SECONDS=60
AI_MAX_OUTPUT_TOKENS=1000
```

---

### 14. `.env.example` 작성
파일:

```text
.env.example
```

```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=false

### fake | openai | ollamaAI_PROVIDER=fake

### OpenAI를 선택할 때 입력OPENAI_API_KEY=
OPENAI_MODEL=

### Ollama를 선택할 때 입력OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

`.env.example`의 목적은 실제 값을 공유하는 것이 아니다.

다른 개발자에게 다음 정보를 알려준다.

```text
어떤 설정이 필요한가?
설정 이름은 무엇인가?
기본 형식은 무엇인가?
어떤 Provider를 선택할 수 있는가?
```

---

### 15. `.gitignore` 작성
```gitignore
### Python__pycache__/
*.py[cod]
.pytest_cache/

### Virtual environment.venv/
venv/

### Environment files.env
.env.*
!.env.example

### IDE.vscode/
.idea/

### OS.DS_Store
```

---

#### 15.1 왜 `.env.*`도 제외하는가?
다음 파일에도 비밀정보가 있을 수 있다.

```text
.env.local
.env.development
.env.production
.env.staging
```

따라서 패턴으로 제외한다.

```gitignore
.env.*
```

다만 예제 파일은 저장소에 포함해야 하므로 다시 허용한다.

```gitignore
!.env.example
```

---

### 16. FastAPI 애플리케이션에서 Settings 사용
파일:

```text
app/main.py
```

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.ai import router as ai_router
from app.api.v1.system import router as system_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    print(
        f"Starting {settings.app_name} "
        f"in {settings.app_env} environment"
    )

    yield

    print(f"Stopping {settings.app_name}")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(
    system_router,
    prefix="/api/v1",
)

app.include_router(
    ai_router,
    prefix="/api/v1",
)
```

---

### 17. 애플리케이션 시작 시 검증
다음 코드가 모듈 로딩 과정에서 호출된다.

```python
settings = get_settings()
```

설정이 잘못되면 FastAPI 서버가 정상적으로 시작되지 않는다.

예를 들어 다음 `.env`를 작성했다고 하자.

```env
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=
```

서버 실행:

```bash
uvicorn app.main:app --reload
```

설정 검증 오류가 발생한다.

개념적으로 다음과 같다.

```text
Uvicorn 실행
    ↓
app.main import
    ↓
get_settings()
    ↓
Provider 설정 검증 실패
    ↓
애플리케이션 시작 중단
```

이것이 Fail Fast다.

---

### 18. 안전한 설정 확인 API
개발 중 현재 설정이 제대로 적용되었는지 확인하고 싶을 수 있다.

하지만 API Key를 반환하면 안 된다.

파일:

```text
app/api/v1/system.py
```

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings


router = APIRouter(
    prefix="/system",
    tags=["System"],
)


class SystemConfigResponse(BaseModel):
    app_name: str
    app_version: str
    app_env: str
    debug: bool
    ai_provider: str
    ai_model: str | None
    ai_timeout_seconds: float
    ai_max_output_tokens: int
    credential_configured: bool


@router.get(
    "/config",
    response_model=SystemConfigResponse,
)
async def read_system_config(
    settings: Settings = Depends(get_settings),
) -> SystemConfigResponse:
    if settings.ai_provider == "openai":
        ai_model = settings.openai_model
        credential_configured = settings.openai_api_key is not None
    elif settings.ai_provider == "ollama":
        ai_model = settings.ollama_model
        credential_configured = True
    else:
        ai_model = None
        credential_configured = True

    return SystemConfigResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        app_env=settings.app_env,
        debug=settings.debug,
        ai_provider=settings.ai_provider,
        ai_model=ai_model,
        ai_timeout_seconds=settings.ai_timeout_seconds,
        ai_max_output_tokens=settings.ai_max_output_tokens,
        credential_configured=credential_configured,
    )
```

---

#### 18.1 예상 응답
```json
{
  "app_name": "AIKOS AI Backend",
  "app_version": "1.0.0",
  "app_env": "development",
  "debug": true,
  "ai_provider": "fake",
  "ai_model": null,
  "ai_timeout_seconds": 30.0,
  "ai_max_output_tokens": 1000,
  "credential_configured": true
}
```

---

#### 18.2 왜 API Key 자체를 반환하지 않는가?
잘못된 코드:

```python
return {
    "api_key": settings.openai_api_key.get_secret_value()
}
```

이 API에 접근할 수 있는 사람에게 Key가 노출된다.

로그, 브라우저 기록, Proxy, Network 탭에도 남을 수 있다.

안전한 방식:

```python
credential_configured = settings.openai_api_key is not None
```

실제 값을 반환하지 않고 설정 여부만 반환한다.

```text
API Key 값
   X 반환하지 않음

API Key 존재 여부
   O 필요하다면 반환
```

운영환경에서는 설정 확인 API 자체를 관리자 전용으로 제한하거나 제공하지 않는 것이 좋다.

---

### 19. Provider 선택 Dependency
Unit 32에서는 `FakeAIService`를 직접 반환했다.

```python
def get_ai_service() -> AIServiceProtocol:
    return FakeAIService()
```

이제 설정에 따라 구현을 선택하도록 개선한다.

파일:

```text
app/core/dependencies.py
```

```python
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.ai_service import (
    AIServiceProtocol,
    FakeAIService,
)


def get_ai_service(
    settings: Settings = Depends(get_settings),
) -> AIServiceProtocol:
    if settings.ai_provider == "fake":
        return FakeAIService()

    if settings.ai_provider == "openai":
        raise NotImplementedError(
            "OpenAI Provider는 Unit 34에서 구현합니다."
        )

    if settings.ai_provider == "ollama":
        raise NotImplementedError(
            "Ollama Provider는 이후 AI Integration에서 구현합니다."
        )

    raise ValueError(
        f"지원하지 않는 AI Provider입니다: "
        f"{settings.ai_provider}"
    )
```

Router 수정:

```python
from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_ai_service
from app.schemas.summary import (
    SummaryCreateRequest,
    SummaryResponse,
)
from app.services.ai_service import AIServiceProtocol


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/summaries",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def create_summary(
    request: SummaryCreateRequest,
    ai_service: AIServiceProtocol = Depends(get_ai_service),
) -> SummaryResponse:
    summary = await ai_service.summarize(request.text)

    return SummaryResponse(
        summary=summary,
        input_length=len(request.text),
        status="completed",
    )
```

---

### 20. 전체 의존성 흐름
```text
HTTP Request
     ↓
AI Router
     ↓ Depends(get_ai_service)
get_ai_service
     ↓ Depends(get_settings)
Settings
     ↓
AI_PROVIDER 확인
     ├─ fake   → FakeAIService
     ├─ openai → OpenAIService
     └─ ollama → OllamaService
```

Unit 34가 완료되면 다음 구조가 된다.

```text
AI_PROVIDER=openai
        ↓
get_ai_service()
        ↓
OpenAIService
        ↓
OpenAIClient
        ↓
OpenAI API
```

---

### 21. Client 생성과 Settings 전달 원칙
앞으로 OpenAI Client를 만들 때 다음 두 방법을 생각할 수 있다.

---

#### 21.1 좋지 않은 방법 — Client 내부에서 Settings 직접 조회
```python
class OpenAIClient:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.openai_api_key
```

간단하지만 Client가 전역 설정 시스템에 직접 의존한다.

테스트에서 원하는 값으로 Client를 만들기 어려워질 수 있다.

---

#### 21.2 권장 방법 — 필요한 값을 생성자에 전달
```python
class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
```

Dependency 함수가 Settings를 해석하고 필요한 값만 전달한다.

```python
def get_openai_client(
    settings: Settings = Depends(get_settings),
) -> OpenAIClient:
    if settings.openai_api_key is None:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다."
        )

    if settings.openai_model is None:
        raise RuntimeError(
            "OPENAI_MODEL이 설정되지 않았습니다."
        )

    return OpenAIClient(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.openai_model,
        timeout_seconds=settings.ai_timeout_seconds,
    )
```

구조:

```text
Settings
   ↓ 설정 해석
Dependency
   ↓ 필요한 값만 전달
OpenAIClient
```

이 방식의 장점:

- Client를 독립적으로 테스트하기 쉽다.
    
- Client가 `.env`의 존재를 몰라도 된다.
    
- 설정 시스템과 Provider 통신 책임이 분리된다.
    
- 생성자 인자만 보면 Client에 필요한 정보가 드러난다.
    

---

### 22. 환경별 설정 분리
#### 22.1 개발환경
```env
APP_ENV=development
DEBUG=true

AI_PROVIDER=fake
AI_TIMEOUT_SECONDS=60
AI_MAX_OUTPUT_TOKENS=500
```

목적:

- 외부 API 없이 개발
    
- 빠른 반복
    
- 비용 방지
    
- 상세 오류 확인
    

---

#### 22.2 테스트환경
```env
APP_ENV=test
DEBUG=false

AI_PROVIDER=fake
AI_TIMEOUT_SECONDS=1
AI_MAX_OUTPUT_TOKENS=100
```

목적:

- 항상 일정한 결과
    
- 빠른 실패
    
- 외부 네트워크 제거
    
- 비용 없는 자동 테스트
    

---

#### 22.3 운영환경
```text
APP_ENV=production
DEBUG=false
AI_PROVIDER=openai
OPENAI_API_KEY=<Secret Manager에서 주입>
OPENAI_MODEL=<운영 정책에서 선택>
AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

운영환경에서는 실제 값을 `.env` 파일에 직접 저장하기보다 배포 시스템의 Secret 기능으로 주입하는 방법을 우선 고려한다.

---

### 23. 설정 우선순위 이해
설정값은 여러 위치에서 제공될 수 있다.

```text
코드 기본값
.env 파일
운영체제 환경변수
테스트에서 직접 전달한 값
```

실무에서는 어떤 값이 최종 적용되는지 명확히 알아야 한다.

예를 들어 코드 기본값은 다음과 같다.

```python
ai_timeout_seconds: float = 30.0
```

`.env`:

```env
AI_TIMEOUT_SECONDS=60
```

운영환경:

```bash
export AI_TIMEOUT_SECONDS=20
```

일반적인 설정 목적은 더 구체적인 실행환경의 값을 우선하는 것이다.

```text
코드 기본값
   ↓ 덮어쓰기
.env
   ↓ 덮어쓰기
실제 환경변수
```

정확한 설정 소스 우선순위는 사용하는 Pydantic Settings 버전과 사용자 정의 설정에 따라 달라질 수 있으므로 운영 배포 전 공식 문서와 테스트로 확인해야 한다.

---

### 24. 테스트에서 Settings 교체
#### 24.1 테스트용 Settings 생성
```python
from app.core.config import Settings


def get_test_settings() -> Settings:
    return Settings(
        app_env="test",
        debug=False,
        ai_provider="fake",
        ai_timeout_seconds=1,
        ai_max_output_tokens=100,
    )
```

---

#### 24.2 Dependency Override
```python
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


app.dependency_overrides[get_settings] = get_test_settings

client = TestClient(app)
```

테스트가 끝난 뒤 Override를 정리한다.

```python
app.dependency_overrides.clear()
```

---

#### 24.3 설정 API 테스트
```python
def test_read_system_config() -> None:
    response = client.get("/api/v1/system/config")

    assert response.status_code == 200

    data = response.json()

    assert data["app_env"] == "test"
    assert data["ai_provider"] == "fake"
    assert data["ai_timeout_seconds"] == 1.0
```

---

#### 24.4 테스트에서 실제 `.env`에 의존하면 안 되는 이유
개발자의 `.env`는 사람마다 다를 수 있다.

```text
개발자 A → AI_PROVIDER=fake
개발자 B → AI_PROVIDER=openai
CI Server → .env 없음
```

테스트가 `.env`에 의존하면 실행 환경에 따라 결과가 달라진다.

좋은 테스트는 필요한 설정을 명시적으로 제공한다.

```text
테스트 코드
   ↓
테스트 전용 Settings
   ↓
일관된 결과
```

---

### 25. 설정 Cache와 테스트 주의사항
`get_settings()`에는 `@lru_cache`가 적용되어 있다.

따라서 환경변수를 변경한 뒤 다시 호출해도 이전 객체가 반환될 수 있다.

```python
settings1 = get_settings()

### 환경변수 변경
settings2 = get_settings()
```

```text
settings1 is settings2
```

동일한 Cache 객체일 수 있다.

테스트에서 환경변수를 직접 바꾸는 경우 Cache를 비워야 한다.

```python
get_settings.cache_clear()
```

예:

```python
def test_environment_setting(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "fake")

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ai_provider == "fake"

    get_settings.cache_clear()
```

하지만 가능하면 환경변수 조작보다 `Settings(...)`를 직접 생성하거나 Dependency Override를 사용하는 방법이 더 명확하다.

---

### 26. 설정을 로그에 출력할 때 주의할 점
다음 코드는 위험하다.

```python
print(settings.model_dump())
```

설정 객체 전체를 Dictionary로 변환하면서 비밀정보 처리 방식을 제대로 확인하지 않으면 Key가 노출될 가능성을 만들어 낸다.

더 나쁜 예:

```python
print(
    settings.openai_api_key.get_secret_value()
)
```

운영 로그에 실제 Key가 기록될 수 있다.

안전한 로그는 필요한 비민감 정보만 선택한다.

```python
print(
    {
        "app_env": settings.app_env,
        "ai_provider": settings.ai_provider,
        "openai_model": settings.openai_model,
        "api_key_configured": (
            settings.openai_api_key is not None
        ),
    }
)
```

원칙:

```text
비밀값 자체를 기록하지 않는다.
설정 여부만 필요하면 Boolean으로 기록한다.
```

---

### 27. API Key를 함수 인자로 전달할 때의 주의사항
다음 코드는 실제 값이 Traceback이나 Debugger에 보일 가능성을 높일 수 있다.

```python
def call_ai(api_key: str, prompt: str):
    ...
```

그렇다고 API Key를 인자로 전달하면 안 된다는 뜻은 아니다.

중요한 것은 다음이다.

- API Key를 로그에 출력하지 않는다.
    
- Exception 메시지에 포함하지 않는다.
    
- 응답 객체에 넣지 않는다.
    
- 디버그 API로 반환하지 않는다.
    
- Prompt와 함께 저장하지 않는다.
    
- 모니터링 시스템의 Attribute로 기록하지 않는다.
    

---

### 28. API Key Rotation
API Key는 영구적으로 같은 값을 사용해야 하는 것이 아니다.

다음 상황에서는 Key를 교체할 수 있다.

- Key 노출 의심
    
- 정기 보안 정책
    
- 직원 또는 서비스 계정 변경
    
- 프로젝트 분리
    
- 권한 정책 변경
    
- 운영환경 재구성
    

환경변수 기반 구조라면 코드를 수정하지 않고 Key를 바꿀 수 있다.

```text
기존 Key 폐기
   ↓
Secret 값 변경
   ↓
애플리케이션 재시작 또는 재배포
   ↓
새 Key 사용
```

코드에 Key가 하드코딩되어 있으면 Key 교체가 코드 변경과 배포 작업으로 연결된다.

---

### 29. 프로젝트별 Key 분리
가능하다면 하나의 API Key를 모든 환경과 애플리케이션에서 공유하지 않는다.

잘못된 구조:

```text
개발환경 ─┐
테스트환경 ├→ 하나의 공용 Key
운영환경 ─┘
```

권장 방향:

```text
개발환경 → 개발용 Credential
테스트환경 → Fake 또는 테스트용 Credential
운영환경 → 운영용 Credential
```

장점:

- 환경별 사용량 확인
    
- 특정 환경만 Key 폐기 가능
    
- 비용 추적 용이
    
- 권한 분리
    
- 사고 영향 범위 축소
    

---

### 30. AI 설정을 하나의 거대한 클래스에 계속 넣어도 될까?
현재는 학습을 위해 하나의 `Settings` 클래스에 작성했다.

```python
class Settings(BaseSettings):
    app_name: str
    app_env: str
    ai_provider: str
    openai_api_key: SecretStr | None
    ollama_base_url: str
```

설정이 커지면 중첩 모델로 분리할 수 있다.

개념 예시:

```python
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings


class OpenAISettings(BaseModel):
    api_key: SecretStr | None = None
    model: str | None = None


class OllamaSettings(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str | None = None


class Settings(BaseSettings):
    app_env: str = "development"
    ai_provider: str = "fake"

    openai: OpenAISettings = OpenAISettings()
    ollama: OllamaSettings = OllamaSettings()
```

다만 중첩 환경변수 구문과 설정 구조가 복잡해지므로 현재 과정에서는 평면 구조를 먼저 사용한다.

```text
초기 프로젝트
→ 평면 Settings

설정 규모 증가
→ 그룹별 Settings 분리
```

---

### 31. 자주 발생하는 실수
#### 실수 1 — API Key를 Python 파일에 작성
```python
OPENAI_API_KEY = "실제-Key"
```

##### 문제
소스 저장소와 Git 기록에 남을 수 있다.

##### 해결
환경변수나 Secret Manager를 사용한다.

---

#### 실수 2 — `.env`를 Git에 Commit
```text
.env
```

##### 문제
파일을 소스 코드에서 분리했더라도 저장소에 올리면 비밀정보가 노출된다.

##### 해결
`.gitignore`에 추가하고 `.env.example`만 공유한다.

---

#### 실수 3 — `.env.example`에 실제 Key 작성
```env
OPENAI_API_KEY=실제-Key
```

##### 문제
예제 파일은 저장소에 포함되므로 Key가 노출된다.

##### 해결
```env
OPENAI_API_KEY=
```

빈 값이나 설명용 Placeholder만 작성한다.

---

#### 실수 4 — 설정 객체를 요청마다 생성
```python
def get_settings() -> Settings:
    return Settings()
```

##### 문제
요청마다 설정 파일을 다시 읽고 검증할 수 있다.

##### 해결
```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

#### 실수 5 — API Key를 응답으로 반환
```python
return {
    "api_key": settings.openai_api_key
}
```

##### 문제
브라우저와 네트워크를 통해 인증정보가 노출된다.

##### 해결
필요하다면 설정 여부만 반환한다.

```python
return {
    "api_key_configured": (
        settings.openai_api_key is not None
    )
}
```

---

#### 실수 6 — 모든 설정을 `str`로 선언
```python
ai_timeout_seconds: str = "30"
```

##### 문제
계산과 비교 시 수동 변환이 필요하며 잘못된 값을 늦게 발견한다.

##### 해결
```python
ai_timeout_seconds: float = Field(gt=0)
```

---

#### 실수 7 — Provider와 관계없이 모든 Key를 필수로 지정
```python
openai_api_key: SecretStr
ollama_api_key: SecretStr
```

##### 문제
사용하지 않는 Provider의 Credential까지 요구한다.

##### 해결
선택값으로 선언한 뒤 Provider 조건에 따라 검증한다.

---

#### 실수 8 — 환경에 따라 코드를 수정
```python
if production:
    model = "운영 모델"
else:
    model = "개발 모델"
```

여러 파일에 이런 조건이 퍼지면 관리가 어렵다.

##### 해결
환경별 값을 설정에서 주입한다.

---

#### 실수 9 — 실제 Secret을 로그에 출력
```python
logger.info(
    settings.openai_api_key.get_secret_value()
)
```

##### 문제
로그 저장소에 Key가 장기간 남을 수 있다.

##### 해결
비민감 정보와 설정 여부만 기록한다.

---

#### 실수 10 — 잘못된 설정으로 서버가 시작되게 둠
```text
Provider=openai
API Key 없음
Model 없음
서버 시작 성공
```

##### 문제
사용자 요청 시점에야 오류를 발견한다.

##### 해결
애플리케이션 시작 과정에서 Settings 검증을 수행한다.

---

### 32. 실무 Best Practice
#### 32.1 Configuration과 Secret을 구분한다
모든 설정이 비밀정보인 것은 아니다.

##### 일반 Configuration
```text
APP_NAME
APP_ENV
AI_PROVIDER
AI_TIMEOUT_SECONDS
AI_MAX_OUTPUT_TOKENS
```

##### Secret
```text
OPENAI_API_KEY
DATABASE_PASSWORD
JWT_SECRET_KEY
```

일반 설정은 로그나 문서에 노출해도 되는 경우가 많지만, Secret은 별도로 보호해야 한다.

---

#### 32.2 설정의 소유권을 명확히 한다
```text
core/config.py
```

를 설정의 단일 진입점으로 사용한다.

다른 모듈은 환경변수 이름을 직접 읽지 않는다.

잘못된 구조:

```python
os.getenv("OPENAI_MODEL")
```

권장 구조:

```python
settings.openai_model
```

---

#### 32.3 Provider Client에는 필요한 설정만 전달한다
```text
전체 Settings 객체
     X 무조건 전달하지 않음

필요한 설정값
     O 명시적으로 전달
```

예:

```python
OpenAIClient(
    api_key=...,
    model=...,
    timeout_seconds=...,
)
```

---

#### 32.4 운영 Secret은 배포환경에서 주입한다
운영환경에서는 다음 구조를 고려한다.

```text
Secret Manager
      ↓
Deployment Environment
      ↓
Application Process
      ↓
Pydantic Settings
```

소스 저장소에는 Secret의 이름과 구조만 남긴다.

---

#### 32.5 설정 오류는 시작 단계에서 발견한다
```text
잘못된 Provider
필수 Key 누락
지원하지 않는 환경 이름
잘못된 Timeout
```

모두 사용자 요청을 처리하기 전에 검증한다.

---

#### 32.6 모델 이름을 코드와 분리한다
```python
model=settings.openai_model
```

이렇게 하면 모델 변경 시 Service 코드가 바뀌지 않는다.

다만 모델별로 기능과 파라미터 지원 범위가 다를 수 있으므로 단순히 이름만 바꾸면 항상 호환된다고 가정해서는 안 된다.

---

#### 32.7 개발 기본값은 안전한 Provider로 둔다
```python
ai_provider: Literal[
    "fake",
    "openai",
    "ollama",
] = "fake"
```

기본값을 `fake`로 두면 Key가 없는 개발환경에서 실수로 외부 API를 호출하지 않는다.

```text
기본 실행
   ↓
Fake Provider
   ↓
비용 발생 없음
```

---

### 33. 실습
#### 실습 목표
- Pydantic Settings로 애플리케이션 설정을 정의한다.
    
- `.env` 파일에서 설정을 읽는다.
    
- API Key를 `SecretStr`로 관리한다.
    
- Provider별 필수 설정을 검증한다.
    
- `@lru_cache`로 설정 객체를 재사용한다.
    
- 설정에 따라 AI Service 구현을 선택한다.
    
- 비밀값을 노출하지 않는 설정 확인 API를 만든다.
    

---

#### 실습 환경
```text
Python 3.12
FastAPI
Uvicorn
Pydantic 2
pydantic-settings
```

설치:

```bash
pip install fastapi "uvicorn[standard]" pydantic-settings
```

---

#### 실습 절차
##### 1단계 — 설정 파일 작성
```text
app/core/config.py
```

```python
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AIKOS AI Backend"
    app_version: str = "1.0.0"
    app_env: Literal[
        "development",
        "test",
        "staging",
        "production",
    ] = "development"
    debug: bool = False

    ai_provider: Literal[
        "fake",
        "openai",
        "ollama",
    ] = "fake"

    openai_api_key: SecretStr | None = None
    openai_model: str | None = None

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str | None = None

    ai_timeout_seconds: float = Field(
        default=30,
        gt=0,
        le=300,
    )
    ai_max_output_tokens: int = Field(
        default=1000,
        ge=1,
        le=100_000,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_provider_settings(self) -> "Settings":
        if self.ai_provider == "openai":
            if self.openai_api_key is None:
                raise ValueError(
                    "OPENAI_API_KEY가 필요합니다."
                )

            if not self.openai_model:
                raise ValueError(
                    "OPENAI_MODEL이 필요합니다."
                )

        if (
            self.ai_provider == "ollama"
            and not self.ollama_model
        ):
            raise ValueError(
                "OLLAMA_MODEL이 필요합니다."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

##### 2단계 — `.env` 작성
```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true

AI_PROVIDER=fake

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

---

##### 3단계 — `.env.example` 작성
```env
APP_NAME=AIKOS AI Backend
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=false

AI_PROVIDER=fake

OPENAI_API_KEY=
OPENAI_MODEL=

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

---

##### 4단계 — `.gitignore` 작성
```gitignore
.env
.env.*
!.env.example

__pycache__/
*.py[cod]
.venv/
.pytest_cache/
```

---

##### 5단계 — Provider Dependency 작성
```text
app/core/dependencies.py
```

```python
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.ai_service import (
    AIServiceProtocol,
    FakeAIService,
)


def get_ai_service(
    settings: Settings = Depends(get_settings),
) -> AIServiceProtocol:
    if settings.ai_provider == "fake":
        return FakeAIService()

    if settings.ai_provider == "openai":
        raise NotImplementedError(
            "OpenAI Provider는 Unit 34에서 구현합니다."
        )

    if settings.ai_provider == "ollama":
        raise NotImplementedError(
            "Ollama Provider는 이후 구현합니다."
        )

    raise ValueError(
        f"지원하지 않는 Provider: "
        f"{settings.ai_provider}"
    )
```

---

##### 6단계 — System Router 작성
```text
app/api/v1/system.py
```

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings


router = APIRouter(
    prefix="/system",
    tags=["System"],
)


class SystemConfigResponse(BaseModel):
    app_name: str
    app_version: str
    app_env: str
    debug: bool
    ai_provider: str
    ai_model: str | None
    credential_configured: bool


@router.get(
    "/config",
    response_model=SystemConfigResponse,
)
async def read_system_config(
    settings: Settings = Depends(get_settings),
) -> SystemConfigResponse:
    if settings.ai_provider == "openai":
        ai_model = settings.openai_model
        credential_configured = (
            settings.openai_api_key is not None
        )
    elif settings.ai_provider == "ollama":
        ai_model = settings.ollama_model
        credential_configured = True
    else:
        ai_model = None
        credential_configured = True

    return SystemConfigResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        app_env=settings.app_env,
        debug=settings.debug,
        ai_provider=settings.ai_provider,
        ai_model=ai_model,
        credential_configured=credential_configured,
    )
```

---

##### 7단계 — Router 등록
```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.ai import router as ai_router
from app.api.v1.system import router as system_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(
    system_router,
    prefix="/api/v1",
)

app.include_router(
    ai_router,
    prefix="/api/v1",
)
```

---

##### 8단계 — 서버 실행
```bash
uvicorn app.main:app --reload
```

---

##### 9단계 — 설정 확인
```text
GET /api/v1/system/config
```

예상 응답:

```json
{
  "app_name": "AIKOS AI Backend",
  "app_version": "1.0.0",
  "app_env": "development",
  "debug": true,
  "ai_provider": "fake",
  "ai_model": null,
  "credential_configured": true
}
```

---

##### 10단계 — 잘못된 설정 검증
`.env`를 다음과 같이 변경한다.

```env
AI_PROVIDER=openai

OPENAI_API_KEY=
OPENAI_MODEL=
```

서버를 다시 실행한다.

예상 결과:

```text
설정 검증 오류
OPENAI_API_KEY가 필요합니다.
```

잘못된 설정 상태에서 서버가 정상 시작되지 않아야 한다.

---

### 34. 예상 결과
#### 정상 설정
```text
AI_PROVIDER=fake
```

결과:

- 서버가 정상적으로 시작된다.
    
- `/api/v1/system/config`가 HTTP 200을 반환한다.
    
- AI 요약 API는 `FakeAIService`를 사용한다.
    
- 외부 API 호출 비용이 발생하지 않는다.
    

---

#### 잘못된 OpenAI 설정
```text
AI_PROVIDER=openai
OPENAI_API_KEY 없음
```

결과:

- Settings 검증이 실패한다.
    
- 애플리케이션이 시작되지 않는다.
    
- 사용자 요청 전에 설정 문제를 발견한다.
    

---

#### 잘못된 Timeout
```env
AI_TIMEOUT_SECONDS=-10
```

결과:

- Pydantic 검증이 실패한다.
    
- `gt=0` 조건 위반 오류가 발생한다.
    

---

### 35. 실습 확인
-  `pydantic-settings`가 설치되었는가?
    
-  설정이 `app/core/config.py`에 모여 있는가?
    
-  `.env`가 `.gitignore`에 포함되었는가?
    
-  `.env.example`에는 실제 Secret이 없는가?
    
-  API Key가 `SecretStr`로 선언되었는가?
    
-  Provider 값이 `Literal`로 제한되어 있는가?
    
-  Timeout 값에 범위 검증이 적용되었는가?
    
-  OpenAI 선택 시 Key와 Model을 검증하는가?
    
-  `get_settings()`에 `@lru_cache`가 적용되었는가?
    
-  System Config API가 실제 API Key를 반환하지 않는가?
    
-  AI Service가 설정에 따라 선택되는가?
    
-  잘못된 설정에서 애플리케이션 시작이 실패하는가?
    

---

### 36. 응용 과제
#### 과제 1 — 운영환경 Debug 차단
다음 규칙을 추가한다.

```text
APP_ENV=production
DEBUG=true
```

이면 설정 검증 오류를 발생시킨다.

예:

```python
if self.app_env == "production" and self.debug:
    raise ValueError(
        "운영환경에서는 DEBUG를 활성화할 수 없습니다."
    )
```

---

#### 과제 2 — Provider별 기본 Timeout
Provider에 따라 기본 Timeout 정책을 만든다.

```text
fake   → 1초
openai → 30초
ollama → 60초
```

다만 사용자가 `AI_TIMEOUT_SECONDS`를 명시한 경우에는 해당 값을 우선하도록 설계한다.

---

#### 과제 3 — 설정 상태 Health Check
다음 API를 만든다.

```text
GET /api/v1/system/readiness
```

정상 응답:

```json
{
  "ready": true,
  "provider": "fake"
}
```

필수 설정이 부족하면 서버가 시작되지 않도록 했으므로 기본적으로 `ready=true`를 반환할 수 있다.

이후 Unit 34에서는 실제 Provider 연결 상태를 확인하는 기능으로 확장한다.

---

#### 과제 4 — 테스트 설정 Override
다음 설정으로 Dependency Override 테스트를 작성한다.

```python
Settings(
    app_env="test",
    ai_provider="fake",
    ai_timeout_seconds=1,
)
```

테스트에서 실제 `.env`와 무관하게 `app_env="test"`가 반환되는지 확인한다.

---

#### 과제 5 — Secret 노출 방지 테스트
System Config API의 응답 문자열에 실제 테스트 Key가 포함되지 않는지 확인한다.

```python
assert "test-secret-key" not in response.text
```

---

### 37. 이해도 확인
#### 질문 1
API Key를 소스 코드에 직접 작성하면 왜 안 되는가?

##### 모범 답안
API Key가 Git Commit History, 원격 저장소, 코드 리뷰, 로그와 배포 결과에 남을 수 있기 때문이다. Key가 노출되면 제3자가 무단으로 API를 호출해 비용과 보안 문제가 발생할 수 있다.

---

#### 질문 2
`.env` 파일을 사용하면 무조건 안전한가?

##### 모범 답안
아니다. `.env`는 소스 코드와 설정을 분리하는 개발 편의 수단일 뿐이다. `.env`를 Git에 Commit하거나 다른 사람에게 노출하면 비밀정보도 함께 노출된다. 운영환경에서는 Secret Manager나 배포 플랫폼의 Secret 기능을 고려해야 한다.

---

#### 질문 3
Pydantic Settings는 `os.getenv()`와 비교해 어떤 장점이 있는가?

##### 모범 답안
환경변수를 타입이 있는 설정 객체로 변환하고, 기본값과 값의 범위, 필수값, Provider별 조건을 한곳에서 검증할 수 있다. 또한 애플리케이션 전체에서 환경변수 이름을 직접 반복하지 않아도 된다.

---

#### 질문 4
OpenAI API Key를 Settings에서 무조건 필수로 만들지 않은 이유는 무엇인가?

##### 모범 답안
Fake나 Ollama Provider를 사용할 때는 OpenAI API Key가 필요하지 않기 때문이다. 따라서 선택값으로 선언하고 `AI_PROVIDER=openai`인 경우에만 Validator에서 필수 여부를 검사한다.

---

#### 질문 5
`SecretStr`은 API Key를 암호화하는가?

##### 모범 답안
아니다. `SecretStr`은 객체 출력이나 로그에서 실제 값이 쉽게 노출되는 것을 줄이는 타입이다. 실제 값을 암호화 저장하는 Secret Manager나 암호화 시스템을 대체하지 않는다.

---

#### 질문 6
`@lru_cache`를 사용하는 이유는 무엇인가?

##### 모범 답안
Settings 객체를 첫 호출 때 한 번만 생성하고 이후에는 재사용하기 위해서다. 이를 통해 요청마다 `.env` 파일을 다시 읽고 설정을 검증하는 불필요한 작업을 방지한다.

---

#### 질문 7
설정 오류를 사용자 요청 시점이 아니라 서버 시작 시점에 확인하는 이유는 무엇인가?

##### 모범 답안
잘못된 설정으로 서비스가 실행되는 것을 막고 문제를 빠르게 발견하기 위해서다. 필수 API Key나 모델 설정이 없다면 서버 시작 단계에서 명확하게 실패하는 것이 운영상 안전하다.

---

#### 질문 8
Provider Client가 `get_settings()`를 직접 호출하지 않고 생성자에서 값을 받도록 하는 장점은 무엇인가?

##### 모범 답안
Client가 환경변수와 설정 시스템에 직접 결합되지 않는다. 필요한 의존성이 생성자에 명확하게 드러나며, 테스트에서 임의의 Key, 모델, Timeout을 전달해 독립적으로 검증하기 쉽다.

---

### 38. 핵심 내용 정리
#### 핵심 1
AI Provider는 AI 모델을 API와 운영 환경을 통해 사용할 수 있도록 제공하는 외부 시스템이다.

```text
FastAPI
   ↓
AI Provider
   ↓
AI Model
```

---

#### 핵심 2
API Key와 설정값을 코드에 직접 작성하지 않는다.

```text
Source Code
    ↓
Settings
    ↓
Environment / Secret
```

---

#### 핵심 3
`.env`는 로컬 개발 편의를 위한 설정 파일이며 저장소에 포함하지 않는다.

```text
.env         → Git 제외
.env.example → Git 포함
```

---

#### 핵심 4
Pydantic Settings를 사용하면 환경변수를 타입이 있는 설정 객체로 변환하고 검증할 수 있다.

```text
문자열 환경변수
      ↓
Pydantic 검증
      ↓
타입이 있는 Settings
```

---

#### 핵심 5
API Key는 `SecretStr`로 선언하여 실수로 출력되는 위험을 줄인다.

```text
실제 Key
   ↓ SecretStr
**********
```

---

#### 핵심 6
Provider에 따라 필요한 설정이 다르므로 조건부 검증을 사용한다.

```text
Provider=openai
  → OpenAI Key와 Model 필요

Provider=ollama
  → Ollama Model 필요

Provider=fake
  → 외부 Credential 불필요
```

---

#### 핵심 7
`@lru_cache`를 사용해 Settings 객체를 한 번만 생성하고 재사용한다.

```text
첫 호출 → Settings 생성
이후 호출 → Cache 재사용
```

---

#### 핵심 8
설정 오류는 애플리케이션 시작 단계에서 발견한다.

```text
시작
 ↓
설정 검증
 ├─ 정상 → 실행
 └─ 오류 → 시작 중단
```

---

#### 핵심 9
설정에 따라 AI Provider 구현을 선택한다.

```text
AI_PROVIDER
   ├─ fake   → FakeAIService
   ├─ openai → OpenAIService
   └─ ollama → OllamaService
```

---

### 39. 한 문장으로 설명하기
> FastAPI의 환경 설정 계층은 API Key, AI Provider, 모델, Timeout과 같은 실행 정보를 소스 코드에서 분리하고, Pydantic Settings로 타입과 관계를 검증하여 개발·테스트·운영 환경에서 안전하고 일관되게 AI Backend를 실행하도록 만든다.

---

### FastAPI Part 5. AI Backend Integration

## Module 37. OpenAI API 연동


### Module 실습 예제

- [예제 1: fake_openai_client.py](examples/module_37/fake_openai_client.py) — OpenAI와 같은 비동기 계약을 Fake Client로 연습합니다.
- [예제 2: optional_openai_client.py](examples/module_37/optional_openai_client.py) — API Key가 있을 때만 실제 OpenAI Responses API를 호출합니다.



#### 프로젝트 연결 학습
- **문제 상황:** OpenAI 요청을 공식 SDK 계약에 맞게 보낸다.
- **오늘 만드는 것:** AsyncOpenAI 기반 호출과 내부 응답 변환을 구현한다.
- **AI 플랫폼의 위치:** AI Client 계층의 실제 Provider Adapter다.
- **실무에서 많이 하는 실수:** SDK 응답 객체를 API 밖으로 그대로 노출한다.
- **5분 실습:** Provider 응답에서 필요한 텍스트와 사용량만 추출한다.

> **AIKOS Phase 1**
> 
> Part 5. AI Backend Integration
> 
> Unit 32. AI Backend Integration 이해
> 
> Unit 33. AI Provider와 환경설정
> 
> **Unit 34. OpenAI API 연동**

---

### 이번 Unit의 학습 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 한다.

- OpenAI Python SDK는 어떤 역할을 하는가?
    
- HTTP 호출과 SDK는 무엇이 다른가?
    
- AsyncOpenAI를 사용하는 이유는 무엇인가?
    
- OpenAI Client와 AI Service를 왜 분리하는가?
    
- Prompt는 어디에서 만들어야 하는가?
    
- OpenAI 응답을 왜 그대로 반환하면 안 되는가?
    
- OpenAI SDK를 교체 가능한 구조로 만드는 방법은 무엇인가?
    

---

### 1. Why
#### 지금까지의 구조
Unit32에서는 FakeAIService를 만들었다.

```text
Router
    ↓
AIService
    ↓
Fake Summary
```

이 구조는 API 계약을 만들기에는 충분했다.

하지만 실제 AI는 전혀 호출하지 않는다.

---

이제 실제 구조는 다음과 같다.

```text
React
    ↓
FastAPI
    ↓
Summary Service
    ↓
OpenAI Client
    ↓
OpenAI API
```

여기서 가장 중요한 변화는

**Service가 OpenAI SDK를 직접 사용하지 않는다는 것**이다.

---

### 왜 Client를 또 만드는가?
처음 학습할 때는 대부분 이렇게 작성한다.

```python
response = await client.responses.create(...)
```

를 Service 안에서 바로 호출한다.

하지만 실무에서는 거의 사용하지 않는 구조다.

왜냐하면

Service는

- 요약
    
- 번역
    
- 분류
    
- QA
    

등의 업무를 담당해야 하고,

OpenAI SDK는

- 인증
    
- HTTP
    
- Retry
    
- Timeout
    
- Provider API
    

만 담당해야 하기 때문이다.

즉

```text
업무(Service)

≠

외부 통신(Client)
```

---

### 2. AI Backend 내부 구조
AIKOS에서는 아래 구조를 사용한다.

```text
Router
    ↓
Application Service
    ↓
OpenAI Client
    ↓
OpenAI SDK
    ↓
OpenAI API
```

각자의 역할은 명확하다.

Router

↓

HTTP

Service

↓

Business

Client

↓

Provider

SDK

↓

HTTP

OpenAI

↓

LLM

---

### Client란 무엇인가?
Client는

"외부 시스템과 통신하는 코드"

이다.

예를 들면

```text
Database

↓

Database Client
```

```text
Redis

↓

Redis Client
```

```text
S3

↓

S3 Client
```

OpenAI 역시 동일하다.

```text
OpenAI

↓

OpenAI Client
```

---

### 3. OpenAI Python SDK
설치

```bash
pip install openai
```

공식 SDK에는

두 개의 Client가 있다.

```python
OpenAI()
```

동기

```python
AsyncOpenAI()
```

비동기

FastAPI는 동기 `def`와 비동기 `async def`를 모두 지원한다. 이 과정의 OpenAI 예제는 긴 네트워크 대기 중에 다른 요청을 처리할 수 있도록 `AsyncOpenAI`를 사용한다.

---

### 왜 AsyncOpenAI인가?
FastAPI는 ASGI 기반이며, Path Operation과 Dependency에서 `def`와 `async def`를 함께 사용할 수 있다.

AI 요청은

CPU 작업이 아니라

대부분

네트워크 대기 시간이다.

```text
FastAPI
    ↓
HTTP
    ↓
OpenAI
```

이 시간은

1~20초

까지 걸릴 수도 있다.

동기 Client를 `async def` 내부에서 직접 호출하면

```text
Worker

↓

기다림
```

비동기 Client를 `await`하면

```text
Worker

↓

다른 요청 처리
```

즉

동시에 더 많은 요청을 처리할 수 있다.

---

### 4. 프로젝트 구조
이번 Unit부터

AI Provider 전용 Client를 만든다.

```text
app/

clients/

    base.py

    openai_client.py

services/

    summary_service.py

core/

    config.py
```

여기서

Client는

Provider 통신만 담당한다.

---

### 5. OpenAI Client 구현
```python
from openai import AsyncOpenAI

class OpenAIClient:

    def __init__(
        self,
        api_key: str,
    ):

        self.client = AsyncOpenAI(
            api_key=api_key,
        )
```

여기서 중요한 점은

Client 생성 시

Settings를 직접 읽지 않는다.

```python
get_settings()
```

도 호출하지 않는다.

---

왜?

Settings는

Dependency가 해석한다.

Client는

필요한 값만 받는다.

```python
api_key

model

timeout
```

이것이

Dependency Injection이다.

---

### 6. Responses API
OpenAI Python SDK의 현재 권장 텍스트 생성 API는 **Responses API**이다.

```python
response = await self.client.responses.create(
    model=self.model,
    input=prompt,
)
```

여기서

prompt는 문자열일 수도 있고,

구조화된 입력일 수도 있다.

현재 AIKOS에서는

문자열 Prompt부터 시작한다.

---

### 7. Prompt는 어디에서 만드는가?
많은 사람이

Client에서 Prompt를 만든다.

잘못된 예

```python
prompt = f"""
문서를 요약해줘

{text}
"""
```

Client 내부

---

이것은 좋지 않다.

왜냐하면

Prompt는

업무 로직이다.

Client는

HTTP만 알아야 한다.

---

올바른 구조

```text
Summary Service

↓

Prompt 생성

↓

Client

↓

OpenAI
```

즉

```python
summary = await client.generate(prompt)
```

만 수행한다.

---

### 8. OpenAI Client는 무엇을 반환해야 하는가?
SDK Response 전체?

아니다.

예를 들어

```python
return response
```

이렇게 반환하면

Service가

OpenAI SDK 구조를 알아야 한다.

이것은

강한 결합이다.

---

Client는

필요한 데이터만 추출한다.

예시

```python
return response.output_text
```

그러면

Service는

문자열만 받는다.

```python
summary = await client.generate(...)
```

---

### 9. Prompt와 Model
Model은

Prompt와 다르다.

```text
Prompt

↓

무엇을 시킬 것인가
```

```text
Model

↓

누가 수행할 것인가
```

Prompt

↓

요약

Model

↓

LLM

---

Model은

Settings에서 가져온다.

```python
self.model
```

Prompt는

Service가 만든다.

---

### 10. 전체 흐름
```text
Request

↓

Router

↓

Summary Service

↓

Prompt 생성

↓

OpenAI Client

↓

Responses API

↓

output_text

↓

Service

↓

ResponseModel

↓

React
```

---

### 11. Service 예시
```python
prompt = f"""
다음 문서를 3줄로 요약하세요.

{text}
"""

summary = await client.generate(
    prompt
)
```

Service는

업무를 이해한다.

Client는

Prompt를 이해하지 않는다.

---

### 12. Client 예시
```python
async def generate(
    self,
    prompt: str,
) -> str:

    response = await self.client.responses.create(
        model=self.model,
        input=prompt,
    )

    return response.output_text
```

굉장히 단순하다.

Client는

HTTP를 감춘다.

---

### 13. Prompt Injection
이번 Unit에서 반드시 알아야 한다.

Prompt는

사용자가 만드는 것이 아니다.

예를 들어

```text
이전 지시를 모두 무시해
```

이런 입력이 들어올 수 있다.

따라서 Service는 신뢰할 수 있는 지시와 사용자·문서에서 온 신뢰할 수 없는 데이터를 구조적으로 분리해야 한다.

하지만 System Prompt와 User Input을 분리하는 것만으로 Prompt Injection이 방지되는 것은 아니다. 실제 서비스에서는 다음과 같은 다층 방어가 필요하다.

- Model이 접근할 수 있는 Tool과 데이터를 최소화한다.
- Model 출력을 신뢰하지 말고 Schema와 업무 규칙으로 검증한다.
- 민감한 작업은 사용자 확인이나 별도의 권한 검사를 거친다.
- Prompt와 응답에 비밀정보를 불필요하게 포함하지 않는다.
- 실패와 이상 행동을 로그와 모니터링으로 추적한다.

이 단원에서는 지시와 데이터의 분리를 출발점으로 삼고, 세부 위협 모델은 생성형 AI 보안 과정에서 다룬다.

---

### 14. 전체 계층 정리
```text
Router

↓

Request 검증

↓

Summary Service

↓

Prompt 생성

↓

OpenAI Client

↓

Responses API

↓

output_text

↓

Response Model
```

---

### 실무 Best Practice
✅ Router에서 SDK 호출 금지

✅ Prompt 생성은 Service

✅ HTTP는 Client

✅ Settings는 Dependency

✅ Provider Response는 Client에서 변환

✅ Service는 문자열만 받는다.

---

### 자주 하는 실수
❌ Router에서 OpenAI 호출

❌ Prompt 생성을 Client에서 수행

❌ API Key를 Client 내부에서 읽음

❌ SDK Response 그대로 반환

❌ Prompt를 Router에서 작성

---

### 핵심 요약
이번 Unit에서 가장 중요한 것은

OpenAI SDK를 사용하는 것이 아니다.

**OpenAI를 교체 가능한 구조로 사용하는 방법**이다.

AIKOS에서는

```text
Business

↓

Service

↓

Client

↓

Provider
```

라는 계층을 유지한다.

Provider가

OpenAI에서

Ollama로

Gemini로

바뀌더라도

Service는 수정되지 않는다.

---

### FastAPI Part 5. AI Backend Integration

## Module 38. AI Service Layer 설계


### Module 실습 예제

- [예제 1: summary_service.py](examples/module_38/summary_service.py) — Prompt 조립과 Client 호출을 AI Service에 둡니다.
- [예제 2: fake_service_test.py](examples/module_38/fake_service_test.py) — Fake Client로 Service를 외부 호출 없이 검증합니다.



#### 프로젝트 연결 학습
- **문제 상황:** Prompt 조립·정책·Provider 호출을 하나의 유스케이스로 묶는다.
- **오늘 만드는 것:** AI Service의 generate 메서드를 만든다.
- **AI 플랫폼의 위치:** 도메인 규칙과 외부 Client 사이의 조정 계층이다.
- **실무에서 많이 하는 실수:** Service가 SDK 타입과 HTTPException에 직접 결합한다.
- **5분 실습:** Client를 Fake로 바꿔 Service 단위 테스트를 작성한다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI Service Layer는 왜 필요한가?
    
- Application Service와 AI Provider Client는 무엇이 다른가?
    
- Router가 OpenAI Client를 직접 사용하면 왜 안 되는가?
    
- Protocol을 사용하면 어떤 장점이 있는가?
    
- Provider 추상화는 무엇이며 왜 필요한가?
    
- OpenAI와 Fake Provider를 어떻게 동일한 계약으로 다루는가?
    
- FastAPI Dependency Injection으로 객체를 어떻게 조립하는가?
    
- 테스트에서 실제 OpenAI API 호출을 제거하는 방법은 무엇인가?
    
- 하나의 거대한 `AIService`를 만들면 어떤 문제가 발생하는가?
    
- AI 기능별 Service와 Provider Client는 어떻게 분리해야 하는가?
    

---

### 2. 문제 이해 — Why
#### 2.1 Unit 34까지 완성된 구조
Unit 34에서는 OpenAI API를 호출하는 Client를 만들었다.

```text
FastAPI
   ↓
OpenAIClient
   ↓
OpenAI Python SDK
   ↓
OpenAI API
```

개념적인 Client 코드는 다음과 같았다.

```python
from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
    ) -> None:
        self._model = model
        self._max_output_tokens = max_output_tokens

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        instructions: str,
        input_text: str,
    ) -> str:
        response = await self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=self._max_output_tokens,
        )

        return response.output_text
```

OpenAI 공식 Python 라이브러리는 Responses API를 주요 텍스트 생성 인터페이스로 제공하며, 동기 `OpenAI`와 비동기 `AsyncOpenAI` 클라이언트를 지원한다.

하지만 아직 중요한 질문이 남아 있다.

> 이 Client를 애플리케이션의 어디에서, 어떤 방식으로 사용해야 하는가?

---

#### 2.2 Router에서 Client를 직접 사용하면 안 될까?
다음처럼 Router에서 OpenAI Client를 직접 주입받을 수 있다.

```python
@router.post("/summaries")
async def create_summary(
    request: SummaryCreateRequest,
    client: OpenAIClient = Depends(get_openai_client),
) -> SummaryResponse:
    result = await client.generate(
        instructions="문서를 요약하세요.",
        input_text=request.text,
    )

    return SummaryResponse(
        summary=result,
        status="completed",
    )
```

코드가 짧고 작동도 한다.

하지만 Router가 다음 내용을 알아야 한다.

```text
요약을 위한 Instruction
OpenAI Client 사용법
AI 응답 호출 순서
요약 결과 처리 방법
```

Router의 원래 책임은 HTTP 처리다.

```text
HTTP 요청 수신
요청 모델 검증
Service 호출
HTTP 응답 반환
```

그런데 위 Router는 요약 업무와 AI 호출 방법까지 담당한다.

```text
Router
 ├─ HTTP 처리
 ├─ Prompt 구성
 ├─ OpenAI 호출
 └─ 결과 처리
```

책임이 섞이기 시작한 것이다.

---

#### 2.3 요약 기능이 복잡해지면 어떻게 되는가?
실제 문서 요약 기능은 단순히 입력을 OpenAI에 보내는 것으로 끝나지 않는다.

```text
사용자 요청
   ↓
사용자 인증 확인
   ↓
문서 조회
   ↓
문서 접근 권한 확인
   ↓
텍스트 전처리
   ↓
문서 길이 확인
   ↓
요약 전략 선택
   ↓
Prompt 생성
   ↓
AI 호출
   ↓
출력 검증
   ↓
결과 저장
   ↓
응답 반환
```

이를 Router에 모두 작성하면 다음과 같은 코드가 된다.

```python
@router.post("/documents/{document_id}/summary")
async def summarize_document(
    document_id: int,
    user: CurrentUser,
    repository: DocumentRepository = Depends(...),
    openai_client: OpenAIClient = Depends(...),
):
    document = await repository.get_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="문서를 찾을 수 없습니다.",
        )

    if document.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="문서 접근 권한이 없습니다.",
        )

    normalized_text = normalize_text(document.content)

    prompt = f"""
    다음 문서를 요약하세요.

    {normalized_text}
    """

    summary = await openai_client.generate(
        instructions="전문 문서 요약가로 동작하세요.",
        input_text=prompt,
    )

    await repository.save_summary(
        document_id=document.id,
        summary=summary,
    )

    return {
        "document_id": document.id,
        "summary": summary,
    }
```

이 Router는 너무 많은 책임을 가진다.

---

#### 2.4 OpenAI를 다른 Provider로 바꾸면 어떻게 되는가?
현재 Service가 OpenAI 전용 Client를 직접 사용한다고 생각해 보자.

```python
class SummaryService:
    def __init__(
        self,
        client: OpenAIClient,
    ) -> None:
        self._client = client
```

이 코드는 명확해 보이지만 `SummaryService`가 OpenAI라는 특정 Provider를 알게 된다.

```text
SummaryService
      ↓ 직접 의존
OpenAIClient
```

이후 Provider를 다음과 같이 변경하려면 Service도 수정해야 할 수 있다.

```text
OpenAI
  ↓
Ollama
```

또는 운영 중 장애가 발생하여 Provider별 Fallback을 구현하려면 더 많은 수정이 필요하다.

```text
OpenAI 실패
    ↓
Ollama 호출
```

업무 로직인 요약 기능이 Provider 선택과 구현 세부사항에 종속된 것이다.

---

### 3. 개념 이해 — Concept
#### 3.1 Service Layer란 무엇인가?
Service Layer는 애플리케이션이 수행해야 하는 **업무 흐름과 사용 사례**를 표현하는 계층이다.

예를 들어 요약 Service는 다음 질문을 이해한다.

```text
무엇을 요약해야 하는가?
어떤 형식으로 요약해야 하는가?
사용자가 해당 문서에 접근할 수 있는가?
결과를 저장해야 하는가?
어떤 Prompt 정책을 적용해야 하는가?
```

반면 OpenAI Client는 다음 질문을 이해한다.

```text
OpenAI API를 어떻게 호출하는가?
어떤 SDK 메서드를 사용하는가?
API Key를 어떻게 전달하는가?
Provider 응답에서 텍스트를 어떻게 추출하는가?
```

둘의 역할은 다르다.

```text
Service
=
우리 서비스의 업무

Client
=
외부 시스템과의 통신
```

---

#### 3.2 AI Service Layer의 정의
> AI Service Layer는 AI 모델을 이용해 수행하는 요약, 번역, 분류, 질의응답과 같은 애플리케이션 사용 사례의 흐름을 관리하는 계층이다.

AI Service Layer는 일반적으로 다음 작업을 담당한다.

- 입력 데이터 준비
    
- 업무 규칙 검증
    
- Prompt 구성
    
- AI Client 호출
    
- 출력 검증
    
- 결과 후처리
    
- Repository 호출
    
- 결과 저장
    
- 여러 AI 호출의 순서 제어
    

AI Service Layer는 외부 Provider와 직접 통신하는 저수준 HTTP 계층이 아니다.

---

#### 3.3 Client와 Service의 차이
|구분|Application Service|Provider Client|
|---|---|---|
|관심사|업무 흐름|외부 API 통신|
|예시|문서 요약 생성|OpenAI 요청 전송|
|Prompt|생성하거나 선택|전달받아 사용|
|Provider 인식|가능하면 모름|특정 Provider를 앎|
|Repository|사용할 수 있음|일반적으로 사용하지 않음|
|HTTP SDK|직접 사용하지 않음|사용함|
|결과 저장|담당 가능|담당하지 않음|
|오류|업무 예외로 해석|Provider 오류를 변환|

한 문장으로 정리하면 다음과 같다.

```text
Service는 무엇을 할지 결정하고,
Client는 외부 시스템에 어떻게 요청할지 처리한다.
```

---

### 4. 구조 이해 — Architecture
#### 4.1 권장 계층 구조
```text
┌────────────────────────────────────┐
│ API Layer                          │
│ Router / Request / Response        │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ Application Layer                  │
│ SummaryService                     │
│ 요약 사용 사례와 업무 흐름          │
└─────────┬─────────────────┬────────┘
          │                 │
          ▼                 ▼
┌───────────────────┐  ┌───────────────────┐
│ Repository        │  │ AI Client Protocol│
│ 문서 조회·저장     │  │ 생성 기능 계약     │
└─────────┬─────────┘  └─────────┬─────────┘
          │                       │
          ▼                       ▼
┌───────────────────┐  ┌───────────────────┐
│ Database          │  │ OpenAI Client     │
└───────────────────┘  │ Ollama Client     │
                       │ Fake Client       │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ AI Provider       │
                       └───────────────────┘
```

---

#### 4.2 의존성 방향
중요한 원칙은 내부 업무 계층이 외부 Provider의 구체적인 구현에 직접 의존하지 않도록 하는 것이다.

잘못된 방향:

```text
SummaryService
      ↓
OpenAIClient
```

권장 방향:

```text
SummaryService
      ↓
TextGenerationClient Protocol
      ↑
OpenAIClient
```

이 구조에서는 Service와 OpenAI Client가 모두 계약을 중심으로 연결된다.

```text
        TextGenerationClient
          ▲             ▲
          │             │
SummaryService     OpenAIClient
```

이를 의존성 역전 원칙의 관점에서 이해할 수 있다.

```text
업무 로직
   ↓
구현체가 아니라 추상화에 의존
```

---

### 5. 왜 `AIService` 하나로 만들지 않는가?
다음 구조는 처음에는 편해 보인다.

```python
class AIService:
    async def summarize(self, text: str) -> str:
        ...

    async def translate(self, text: str) -> str:
        ...

    async def classify(self, text: str) -> str:
        ...

    async def answer(self, question: str) -> str:
        ...

    async def extract_keywords(self, text: str) -> list[str]:
        ...
```

그러나 시간이 지나면 클래스가 지나치게 커진다.

```text
AIService
 ├─ 요약 Prompt
 ├─ 번역 Prompt
 ├─ 분류 규칙
 ├─ RAG 검색
 ├─ 답변 생성
 ├─ 키워드 추출
 ├─ Repository 접근
 └─ Provider 호출
```

이런 클래스는 흔히 God Object가 된다.

문제:

- 변경 범위가 커진다.
    
- 테스트가 복잡해진다.
    
- 기능 간 결합이 증가한다.
    
- 여러 개발자가 같은 파일을 수정한다.
    
- 기능별 의존성이 섞인다.
    
- Provider 호출 방식과 업무 로직이 혼합된다.
    

따라서 기능별 Service로 분리하는 것이 좋다.

```text
services/
├── summary_service.py
├── translation_service.py
├── classification_service.py
├── keyword_service.py
└── answer_service.py
```

각 Service는 하나의 사용 사례 또는 관련된 사용 사례 묶음을 담당한다.

---

### 6. AI Client Protocol 설계
#### 6.1 Protocol이 필요한 이유
`SummaryService`가 필요한 기능은 복잡하지 않다.

```text
Instruction과 입력을 전달하면
생성된 문자열을 반환한다.
```

Service는 OpenAI SDK의 구체적인 객체 구조를 알 필요가 없다.

따라서 다음 계약을 만든다.

파일:

```text
app/clients/base.py
```

```python
from typing import Protocol


class TextGenerationClient(Protocol):
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...
```

---

#### 6.2 이 Protocol이 의미하는 것
다음 메서드를 가진 객체라면 `TextGenerationClient` 역할을 수행할 수 있다.

```text
async def generate(
    *,
    instructions: str,
    input_text: str,
) -> str:
```

구현체는 달라도 된다.

```python
class OpenAITextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...


class OllamaTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...


class FakeTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...
```

구조:

```text
TextGenerationClient
       ▲
       ├── OpenAITextGenerationClient
       ├── OllamaTextGenerationClient
       └── FakeTextGenerationClient
```

---

#### 6.3 왜 Protocol 이름을 `AIClient`라고 하지 않는가?
다음과 같은 이름도 사용할 수 있다.

```python
class AIClient(Protocol):
    ...
```

하지만 `AIClient`는 범위가 너무 넓다.

AI 기능에는 다음이 포함될 수 있다.

```text
텍스트 생성
Embedding
이미지 생성
음성 인식
음성 합성
이미지 분석
Moderation
```

모든 기능을 하나의 계약에 넣으면 다시 거대한 인터페이스가 된다.

따라서 능력별로 나누는 것이 좋다.

```text
TextGenerationClient
EmbeddingClient
ImageGenerationClient
SpeechToTextClient
TextToSpeechClient
```

이는 인터페이스 분리 원칙과도 연결된다.

```text
사용하지 않는 기능까지
의존하지 않도록 계약을 작게 만든다.
```

---

### 7. OpenAI Client 구현
파일:

```text
app/clients/openai_client.py
```

```python
from openai import AsyncOpenAI

from app.clients.base import TextGenerationClient


class OpenAITextGenerationClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
    ) -> None:
        self._model = model
        self._max_output_tokens = max_output_tokens

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        response = await self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=self._max_output_tokens,
        )

        output_text = response.output_text.strip()

        if not output_text:
            raise RuntimeError(
                "AI Provider가 비어 있는 응답을 반환했습니다."
            )

        return output_text
```

---

#### 7.1 Protocol을 명시적으로 상속해야 하는가?
다음과 같이 작성할 수 있다.

```python
class OpenAITextGenerationClient(TextGenerationClient):
    ...
```

하지만 Python의 `Protocol`은 구조적 타이핑을 지원한다.

즉, 명시적으로 상속하지 않아도 필요한 메서드 구조를 만족하면 계약에 맞는 것으로 타입 검사기가 판단할 수 있다.

```text
class OpenAITextGenerationClient:
    async def generate(...):
        ...
```

이 방식은 구현체가 Protocol에 강하게 결합되지 않는 장점이 있다.

교육 코드에서는 관계를 명확히 보여주기 위해 상속을 사용할 수도 있지만, 실무에서는 프로젝트의 타입 검사 정책에 따라 선택한다.

---

#### 7.2 빈 응답을 검사하는 이유
```python
output_text = response.output_text.strip()

if not output_text:
    raise RuntimeError(
        "AI Provider가 비어 있는 응답을 반환했습니다."
    )
```

외부 Provider 호출이 HTTP 수준에서 성공했다고 해서 서비스에서 사용할 수 있는 결과가 반드시 존재한다고 가정해서는 안 된다.

```text
HTTP 요청 성공
      ≠
업무적으로 유효한 응답
```

Client는 Provider 응답에서 최소한의 기술적 유효성을 검사할 수 있다.

다만 구체적인 요약 품질이나 형식 검증은 Service 또는 별도 Output Validator가 담당하는 것이 좋다.

---

### 8. Fake Client 구현
실제 API를 호출하지 않고 테스트하기 위한 Client를 만든다.

파일:

```text
app/clients/fake_client.py
```

```python
class FakeTextGenerationClient:
    def __init__(
        self,
        *,
        response_text: str = "테스트용 AI 응답",
    ) -> None:
        self._response_text = response_text
        self.last_instructions: str | None = None
        self.last_input_text: str | None = None

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        self.last_instructions = instructions
        self.last_input_text = input_text

        return self._response_text
```

---

#### 8.1 단순히 고정 문자열만 반환하면 안 되는가?
다음 코드도 가능하다.

```python
class FakeTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        return "테스트 응답"
```

그러나 테스트에서는 Service가 올바른 Instruction과 입력을 전달했는지도 확인하고 싶다.

따라서 마지막 요청을 기록한다.

```python
self.last_instructions = instructions
self.last_input_text = input_text
```

테스트에서 다음을 확인할 수 있다.

```python
assert fake_client.last_instructions is not None
assert "요약" in fake_client.last_instructions
assert fake_client.last_input_text == original_text
```

---

### 9. 요청·응답 모델 개선
파일:

```text
app/schemas/summary.py
```

```python
from typing import Literal

from pydantic import BaseModel, Field, field_validator


SummaryLength = Literal["short", "medium", "long"]
SummaryTone = Literal["neutral", "professional", "friendly"]


class SummaryCreateRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
        description="요약할 원문",
    )
    length: SummaryLength = "medium"
    tone: SummaryTone = "neutral"

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "요약할 텍스트가 필요합니다."
            )

        return normalized


class SummaryResponse(BaseModel):
    summary: str
    length: SummaryLength
    tone: SummaryTone
    status: Literal["completed"]
```

---

### 10. Summary Service 설계
파일:

```text
app/services/summary_service.py
```

```python
from dataclasses import dataclass

from app.clients.base import TextGenerationClient
from app.schemas.summary import (
    SummaryLength,
    SummaryTone,
)


@dataclass(frozen=True)
class SummaryCommand:
    text: str
    length: SummaryLength
    tone: SummaryTone


@dataclass(frozen=True)
class SummaryResult:
    summary: str
    length: SummaryLength
    tone: SummaryTone


class SummaryService:
    def __init__(
        self,
        *,
        text_generation_client: TextGenerationClient,
    ) -> None:
        self._text_generation_client = (
            text_generation_client
        )

    async def summarize(
        self,
        command: SummaryCommand,
    ) -> SummaryResult:
        instructions = self._build_instructions(
            length=command.length,
            tone=command.tone,
        )

        input_text = self._prepare_input(command.text)

        generated_text = (
            await self._text_generation_client.generate(
                instructions=instructions,
                input_text=input_text,
            )
        )

        summary = self._validate_output(generated_text)

        return SummaryResult(
            summary=summary,
            length=command.length,
            tone=command.tone,
        )

    def _build_instructions(
        self,
        *,
        length: SummaryLength,
        tone: SummaryTone,
    ) -> str:
        length_instruction = {
            "short": "핵심 내용을 3문장 이내로 요약하세요.",
            "medium": "핵심 내용을 5개 문장 안팎으로 요약하세요.",
            "long": (
                "핵심 논리와 중요한 세부사항을 포함하여 "
                "충분히 자세히 요약하세요."
            ),
        }[length]

        tone_instruction = {
            "neutral": "중립적이고 객관적인 문체를 사용하세요.",
            "professional": (
                "업무 보고서에 적합한 전문적인 문체를 사용하세요."
            ),
            "friendly": (
                "비전문가도 이해하기 쉬운 친근한 문체를 사용하세요."
            ),
        }[tone]

        return "\n".join(
            [
                "당신은 문서 요약을 수행하는 AI입니다.",
                length_instruction,
                tone_instruction,
                "원문에 없는 사실을 추가하지 마세요.",
                "요약 결과만 반환하세요.",
            ]
        )

    def _prepare_input(self, text: str) -> str:
        return text.strip()

    def _validate_output(self, output: str) -> str:
        normalized = output.strip()

        if not normalized:
            raise ValueError(
                "생성된 요약 결과가 비어 있습니다."
            )

        return normalized
```

---

### 11. Summary Service 코드 분석
#### 11.1 생성자 의존성
```text
def __init__(
    self,
    *,
    text_generation_client: TextGenerationClient,
) -> None:
```

`SummaryService`는 `OpenAITextGenerationClient`에 직접 의존하지 않는다.

```text
SummaryService
      ↓
TextGenerationClient
```

따라서 다음 구현을 모두 전달할 수 있다.

```text
OpenAITextGenerationClient
FakeTextGenerationClient
OllamaTextGenerationClient
```

---

#### 11.2 Command 객체
```python
@dataclass(frozen=True)
class SummaryCommand:
    text: str
    length: SummaryLength
    tone: SummaryTone
```

Router의 Pydantic Request를 Service에 그대로 전달하지 않고 Service 전용 입력 객체로 변환한다.

```text
HTTP Request Model
        ↓ 변환
Application Command
```

이렇게 하면 Service가 FastAPI와 Pydantic HTTP 모델에 직접 종속되지 않는다.

다만 소규모 프로젝트에서는 Pydantic Request를 Service에 직접 전달할 수도 있다.

선택 기준:

```text
작은 프로젝트
→ Request Model 직접 전달 가능

규모가 커지고 계층 분리가 중요
→ Command/DTO로 분리
```

---

#### 11.3 `frozen=True`
```text
@dataclass(frozen=True)
```

Command와 Result 객체를 생성 후 변경할 수 없도록 한다.

```python
command.length = "long"
```

이런 변경은 허용되지 않는다.

사용 사례의 입력과 결과를 불변 객체로 다루면 처리 흐름을 추적하기 쉬워진다.

---

#### 11.4 Instruction 구성
```python
instructions = self._build_instructions(
    length=command.length,
    tone=command.tone,
)
```

Prompt 정책은 Service에 위치한다.

그 이유는 다음과 같다.

- 요약 길이는 업무 요구사항이다.
    
- 문체 선택은 서비스 기능이다.
    
- 사실 추가 금지는 품질 정책이다.
    
- 출력 형식은 API 요구사항과 연결된다.
    

Client는 이러한 업무 규칙을 알지 않는다.

```text
SummaryService
→ 요약 Prompt 정책을 앎

OpenAIClient
→ 전달받은 Prompt를 Provider에 전송
```

---

#### 11.5 입력 전처리
```python
input_text = self._prepare_input(command.text)
```

현재는 앞뒤 공백만 제거한다.

이후 실제 문서 서비스에서는 다음 처리가 추가될 수 있다.

- 제어문자 제거
    
- 문서 형식 정규화
    
- HTML 제거
    
- 페이지 번호 제거
    
- 반복 Header/Footer 제거
    
- 너무 긴 문서 분할
    
- 개인정보 마스킹
    

이 로직은 Provider Client가 아니라 업무 Service 또는 별도의 전처리 컴포넌트에 위치해야 한다.

---

#### 11.6 출력 검증
```python
summary = self._validate_output(generated_text)
```

Client도 빈 문자열을 확인했지만 Service에서도 업무 관점의 검증을 수행한다.

두 검증의 의미는 다르다.

```text
Client 검증
→ Provider 응답에 텍스트가 존재하는가?

Service 검증
→ 요약 기능의 결과로 사용할 수 있는가?
```

이후에는 다음 검증으로 확장할 수 있다.

- 최대 길이
    
- 문장 수
    
- 금지된 형식
    
- JSON 구조
    
- 필수 항목
    
- 언어
    
- 민감정보 포함 여부
    

---

### 12. FastAPI Dependency 구성
이제 객체를 조립한다.

파일:

```text
app/core/dependencies.py
```

```python
from typing import Annotated

from fastapi import Depends

from app.clients.base import TextGenerationClient
from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.core.config import Settings, get_settings
from app.services.summary_service import SummaryService


def get_text_generation_client(
    settings: Annotated[
        Settings,
        Depends(get_settings),
    ],
) -> TextGenerationClient:
    if settings.ai_provider == "fake":
        return FakeTextGenerationClient(
            response_text="Fake Provider가 생성한 요약입니다.",
        )

    if settings.ai_provider == "openai":
        if settings.openai_api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY가 설정되지 않았습니다."
            )

        if settings.openai_model is None:
            raise RuntimeError(
                "OPENAI_MODEL이 설정되지 않았습니다."
            )

        return OpenAITextGenerationClient(
            api_key=(
                settings.openai_api_key.get_secret_value()
            ),
            model=settings.openai_model,
            timeout_seconds=settings.ai_timeout_seconds,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )

    if settings.ai_provider == "ollama":
        raise NotImplementedError(
            "Ollama Client는 이후 Unit에서 구현합니다."
        )

    raise RuntimeError(
        f"지원하지 않는 AI Provider입니다: "
        f"{settings.ai_provider}"
    )


def get_summary_service(
    client: Annotated[
        TextGenerationClient,
        Depends(get_text_generation_client),
    ],
) -> SummaryService:
    return SummaryService(
        text_generation_client=client,
    )
```

FastAPI의 Dependency Injection은 callable을 통해 의존성을 제공하며, 의존성 안에 다른 의존성을 선언하는 Sub-dependency 구조도 지원한다.

---

### 13. Dependency 그래프 이해
FastAPI는 다음 그래프를 해결한다.

```text
create_summary()
       ↓ Depends
get_summary_service()
       ↓ Depends
get_text_generation_client()
       ↓ Depends
get_settings()
```

최종적으로 생성되는 객체:

```text
Settings
   ↓
OpenAITextGenerationClient
   ↓
SummaryService
   ↓
Router
```

Fake Provider를 선택하면 다음과 같다.

```text
Settings
AI_PROVIDER=fake
   ↓
FakeTextGenerationClient
   ↓
SummaryService
   ↓
Router
```

Router와 SummaryService 코드는 변경되지 않는다.

---

### 14. Router 구현
파일:

```text
app/api/v1/summaries.py
```

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_summary_service
from app.schemas.summary import (
    SummaryCreateRequest,
    SummaryResponse,
)
from app.services.summary_service import (
    SummaryCommand,
    SummaryService,
)


router = APIRouter(
    prefix="/summaries",
    tags=["Summaries"],
)


@router.post(
    "",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def create_summary(
    request: SummaryCreateRequest,
    service: Annotated[
        SummaryService,
        Depends(get_summary_service),
    ],
) -> SummaryResponse:
    command = SummaryCommand(
        text=request.text,
        length=request.length,
        tone=request.tone,
    )

    result = await service.summarize(command)

    return SummaryResponse(
        summary=result.summary,
        length=result.length,
        tone=result.tone,
        status="completed",
    )
```

---

### 15. Router가 얇아졌는지 확인
Router가 수행하는 일은 다음뿐이다.

```text
1. HTTP 요청 모델 수신
2. Command 객체 생성
3. Service 호출
4. Result를 Response로 변환
```

Router는 다음을 모른다.

```text
OpenAI SDK
API Key
모델 이름
Prompt 내용
Timeout
Provider 응답 구조
Fake Provider 여부
```

이것이 얇은 Router다.

---

### 16. Router 등록
파일:

```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.summaries import (
    router as summaries_router,
)
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(
    summaries_router,
    prefix="/api/v1",
)
```

최종 API:

```text
POST /api/v1/summaries
```

---

### 17. 전체 요청 흐름
```text
1. React
   POST /api/v1/summaries
                │
                ▼
2. Summary Router
   Request 검증 및 Command 생성
                │
                ▼
3. SummaryService
   Instruction과 입력 준비
                │
                ▼
4. TextGenerationClient
   Provider 독립 계약
                │
                ▼
5. OpenAITextGenerationClient
   Responses API 호출
                │
                ▼
6. OpenAI API
   생성 결과 반환
                │
                ▼
7. OpenAI Client
   output_text 추출
                │
                ▼
8. SummaryService
   결과 검증 및 Result 생성
                │
                ▼
9. Router
   SummaryResponse 반환
```

---

### 18. 실행 설정
#### 18.1 Fake Provider
`.env`:

```env
APP_ENV=development
DEBUG=true

AI_PROVIDER=fake

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

이 설정에서는 실제 OpenAI API를 호출하지 않는다.

---

#### 18.2 OpenAI Provider
`.env`:

```env
APP_ENV=development
DEBUG=true

AI_PROVIDER=openai

OPENAI_API_KEY=실제-API-Key
OPENAI_MODEL=사용할-모델-이름

AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=1000
```

실제 모델 이름은 프로젝트가 사용할 수 있는 모델과 기능 요구사항을 기준으로 설정하며, 모델 지원 범위는 최신 OpenAI 공식 문서에서 확인해야 한다.

---

### 19. API 실행
```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

요청:

```json
{
  "text": "FastAPI의 Dependency Injection은 객체 생성과 의존성 연결을 Router 밖으로 분리할 수 있도록 돕습니다. 이를 사용하면 AI Provider Client와 Application Service를 테스트 가능한 구조로 조립할 수 있습니다.",
  "length": "short",
  "tone": "professional"
}
```

응답 예시:

```json
{
  "summary": "FastAPI의 Dependency Injection은 객체 생성과 연결 책임을 분리합니다. 이를 통해 AI Provider와 Service를 느슨하게 결합하고 테스트 가능한 구조를 만들 수 있습니다.",
  "length": "short",
  "tone": "professional",
  "status": "completed"
}
```

실제 생성 내용은 모델과 설정에 따라 달라질 수 있다.

---

### 20. Service 단위 테스트
#### 20.1 실제 Provider 없이 테스트
파일:

```text
tests/services/test_summary_service.py
```

```python
import pytest

from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.services.summary_service import (
    SummaryCommand,
    SummaryService,
)


@pytest.mark.asyncio
async def test_summary_service_returns_generated_text() -> None:
    fake_client = FakeTextGenerationClient(
        response_text="테스트 요약 결과",
    )

    service = SummaryService(
        text_generation_client=fake_client,
    )

    command = SummaryCommand(
        text=(
            "FastAPI는 Python 기반의 비동기 웹 "
            "애플리케이션을 구현할 수 있도록 지원합니다."
        ),
        length="short",
        tone="neutral",
    )

    result = await service.summarize(command)

    assert result.summary == "테스트 요약 결과"
    assert result.length == "short"
    assert result.tone == "neutral"
```

---

#### 20.2 Prompt 전달 확인
```python
@pytest.mark.asyncio
async def test_summary_service_builds_prompt() -> None:
    fake_client = FakeTextGenerationClient(
        response_text="요약 결과",
    )

    service = SummaryService(
        text_generation_client=fake_client,
    )

    command = SummaryCommand(
        text="테스트할 문서 내용입니다.",
        length="long",
        tone="professional",
    )

    await service.summarize(command)

    assert fake_client.last_instructions is not None
    assert "자세히" in fake_client.last_instructions
    assert "전문적인" in fake_client.last_instructions

    assert (
        fake_client.last_input_text
        == "테스트할 문서 내용입니다."
    )
```

이 테스트는 다음을 확인한다.

```text
Service가 길이 옵션을 Prompt에 반영했는가?
Service가 문체 옵션을 Prompt에 반영했는가?
원문을 Client에 정확히 전달했는가?
```

---

### 21. 빈 출력 테스트
```python
import pytest


@pytest.mark.asyncio
async def test_summary_service_rejects_empty_output() -> None:
    fake_client = FakeTextGenerationClient(
        response_text="   ",
    )

    service = SummaryService(
        text_generation_client=fake_client,
    )

    command = SummaryCommand(
        text="충분히 긴 테스트 문서 내용입니다.",
        length="medium",
        tone="neutral",
    )

    with pytest.raises(
        ValueError,
        match="요약 결과가 비어",
    ):
        await service.summarize(command)
```

현재 Fake Client는 빈 값을 그대로 반환하므로 Service의 출력 검증을 테스트할 수 있다.

---

### 22. Router 통합 테스트
#### 22.1 Dependency Override
FastAPI는 `app.dependency_overrides` Dictionary를 통해 원래 Dependency 함수를 테스트용 함수로 교체할 수 있다.

파일:

```text
tests/api/test_summaries.py
```

```python
from fastapi.testclient import TestClient

from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.core.dependencies import get_summary_service
from app.main import app
from app.services.summary_service import SummaryService


def override_summary_service() -> SummaryService:
    return SummaryService(
        text_generation_client=(
            FakeTextGenerationClient(
                response_text="API 테스트 요약",
            )
        ),
    )


def test_create_summary() -> None:
    app.dependency_overrides[
        get_summary_service
    ] = override_summary_service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/summaries",
                json={
                    "text": (
                        "FastAPI 테스트에서 Dependency를 "
                        "교체하면 외부 AI API 호출 없이 "
                        "Router를 검증할 수 있습니다."
                    ),
                    "length": "short",
                    "tone": "neutral",
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "summary": "API 테스트 요약",
            "length": "short",
            "tone": "neutral",
            "status": "completed",
        }
    finally:
        app.dependency_overrides.clear()
```

---

### 23. 왜 Service를 Override하는가?
다음 두 가지 방법이 가능하다.

```text
방법 1
get_text_generation_client를 Override

방법 2
get_summary_service를 Override
```

#### Client Dependency Override
```python
app.dependency_overrides[
    get_text_generation_client
] = get_fake_client
```

장점:

- 실제 SummaryService 로직을 테스트한다.
    
- Prompt 구성과 결과 검증이 포함된다.
    

#### Service Dependency Override
```python
app.dependency_overrides[
    get_summary_service
] = get_fake_summary_service
```

장점:

- Router만 독립적으로 테스트할 수 있다.
    
- 테스트 범위를 좁힐 수 있다.
    

테스트 목적에 따라 선택한다.

```text
Router 단위 테스트
→ Service Override

Router + Service 통합 테스트
→ Client Override
```

---

### 24. Repository까지 연결되는 실무 구조
현재 실습은 사용자가 직접 텍스트를 전달한다.

실무에서는 문서 ID를 전달할 수 있다.

요청:

```json
{
  "document_id": 10,
  "length": "medium",
  "tone": "professional"
}
```

Service:

```python
class DocumentSummaryService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        summary_repository: SummaryRepository,
        text_generation_client: TextGenerationClient,
    ) -> None:
        self._document_repository = document_repository
        self._summary_repository = summary_repository
        self._text_generation_client = (
            text_generation_client
        )

    async def summarize_document(
        self,
        command: DocumentSummaryCommand,
    ) -> DocumentSummaryResult:
        document = (
            await self._document_repository.get_by_id(
                command.document_id
            )
        )

        if document is None:
            raise DocumentNotFoundError(
                command.document_id
            )

        if document.owner_id != command.user_id:
            raise DocumentAccessDeniedError(
                command.document_id
            )

        instructions = self._build_instructions(
            command.length
        )

        summary = (
            await self._text_generation_client.generate(
                instructions=instructions,
                input_text=document.content,
            )
        )

        saved_summary = (
            await self._summary_repository.create(
                document_id=document.id,
                content=summary,
                created_by=command.user_id,
            )
        )

        return DocumentSummaryResult(
            summary_id=saved_summary.id,
            document_id=document.id,
            summary=saved_summary.content,
        )
```

전체 흐름:

```text
Router
   ↓
DocumentSummaryService
   ├─→ DocumentRepository
   ├─→ TextGenerationClient
   └─→ SummaryRepository
```

Application Service가 여러 컴포넌트의 호출 순서를 조율한다.

---

### 25. Domain Exception 사용
Service에서 `HTTPException`을 직접 발생시키지 않는 것이 좋다.

잘못된 예:

```python
raise HTTPException(
    status_code=404,
    detail="문서를 찾을 수 없습니다.",
)
```

이 코드는 Service가 HTTP를 알게 만든다.

대신 애플리케이션 예외를 만든다.

```python
class DocumentNotFoundError(Exception):
    def __init__(self, document_id: int) -> None:
        super().__init__(
            f"문서를 찾을 수 없습니다: {document_id}"
        )
        self.document_id = document_id
```

Service:

```python
if document is None:
    raise DocumentNotFoundError(document_id)
```

FastAPI 예외 처리기:

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(DocumentNotFoundError)
async def handle_document_not_found(
    request: Request,
    exc: DocumentNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "document_id": exc.document_id,
        },
    )
```

구조:

```text
Service
   ↓ Domain/Application Exception
FastAPI Exception Handler
   ↓ HTTP Response
```

이렇게 하면 Service를 CLI, Worker, Batch에서도 재사용할 수 있다.

---

### 26. Provider별 Client 선택 구조
현재 Dependency는 조건문을 사용한다.

```python
if provider == "fake":
    ...

if provider == "openai":
    ...

if provider == "ollama":
    ...
```

Provider가 몇 개 없을 때는 충분히 명확하다.

Provider가 많아지면 Factory로 분리할 수 있다.

```python
class TextGenerationClientFactory:
    @staticmethod
    def create(
        settings: Settings,
    ) -> TextGenerationClient:
        if settings.ai_provider == "fake":
            return FakeTextGenerationClient()

        if settings.ai_provider == "openai":
            return OpenAITextGenerationClient(...)

        if settings.ai_provider == "ollama":
            return OllamaTextGenerationClient(...)

        raise UnsupportedAIProviderError(
            settings.ai_provider
        )
```

Dependency:

```python
def get_text_generation_client(
    settings: Settings = Depends(get_settings),
) -> TextGenerationClient:
    return TextGenerationClientFactory.create(
        settings
    )
```

다만 Factory를 너무 일찍 도입하면 코드만 복잡해질 수 있다.

```text
Provider 2~3개
→ Dependency 조건문도 충분

Provider가 늘고 생성 로직이 복잡
→ Factory 분리 검토
```

---

### 27. Client 인스턴스의 생명주기
현재 Dependency 함수는 요청마다 Client 객체를 만들 수 있다.

```text
Request 1 → AsyncOpenAI Client 생성
Request 2 → AsyncOpenAI Client 생성
Request 3 → AsyncOpenAI Client 생성
```

네트워크 Client는 내부적으로 연결 Pool을 사용할 수 있으므로 애플리케이션 수준에서 재사용하는 구조가 효율적일 수 있다.

개념 구조:

```text
Application Startup
      ↓
AsyncOpenAI Client 생성
      ↓
여러 요청에서 재사용
      ↓
Application Shutdown
      ↓
Client 종료
```

FastAPI는 `yield`를 사용하는 Dependency를 통해 사용 전 생성과 사용 후 정리 작업을 표현할 수 있다.

다만 이 내용은 객체 생명주기와 비동기 연결 관리를 더 깊게 다루므로 Unit 36에서 이어서 학습한다.

현재 Unit의 핵심은 다음이다.

```text
Service가 Client 구현체에 직접 종속되지 않도록 한다.
```

---

### 28. Prompt Template을 별도 컴포넌트로 분리해야 할까?
현재 Prompt 생성은 Service 메서드에 있다.

```text
def _build_instructions(...):
    ...
```

기능이 단순할 때는 적절하다.

Prompt가 복잡해지면 별도 클래스로 분리할 수 있다.

```text
prompts/
└── summary_prompt.py
```

```python
class SummaryPromptBuilder:
    def build(
        self,
        *,
        length: SummaryLength,
        tone: SummaryTone,
    ) -> str:
        ...
```

Service:

```python
class SummaryService:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
        prompt_builder: SummaryPromptBuilder,
    ) -> None:
        self._client = client
        self._prompt_builder = prompt_builder
```

분리 기준:

```text
Prompt가 짧고 Service 하나에서만 사용
→ Service 내부

Prompt 버전 관리가 필요
여러 Service에서 재사용
다국어 Prompt
복잡한 Template
A/B Test
→ Prompt Builder 분리
```

---

### 29. Provider 독립성의 한계
모든 Provider를 완전히 동일하게 다룰 수 있다고 생각하면 안 된다.

Provider와 모델마다 다음 차이가 있을 수 있다.

- 지원 입력 형식
    
- 구조화된 출력 기능
    
- Tool Calling 방식
    
- Streaming 이벤트
    
- Token 계산 방식
    
- 최대 Context
    
- 이미지 입력 지원
    
- 추론 옵션
    
- 안전 정책
    
- 오류 코드
    
- 모델별 Parameter
    

따라서 추상화는 공통 기능에만 적용하는 것이 좋다.

```text
공통 기능
→ TextGenerationClient

Provider 전용 기능
→ 별도 Client 또는 확장 인터페이스
```

잘못된 추상화:

```python
class AIClient:
    async def generate(
        self,
        every_possible_provider_option: dict,
    ):
        ...
```

모든 Provider 옵션을 하나의 Dictionary에 넣으면 타입 안정성과 명확성이 사라진다.

---

### 30. 자주 발생하는 실수
#### 실수 1 — Router에서 OpenAI Client 직접 호출
```python
@router.post("/summaries")
async def create_summary(
    request: SummaryCreateRequest,
    client: OpenAITextGenerationClient = Depends(...),
):
    return await client.generate(...)
```

##### 문제
Router가 Prompt와 Provider 호출을 이해한다.

##### 해결
```text
Router → SummaryService → TextGenerationClient
```

---

#### 실수 2 — Service가 구체적인 Provider에 의존
```python
class SummaryService:
    def __init__(
        self,
        client: OpenAITextGenerationClient,
    ):
        ...
```

##### 문제
Provider 교체와 테스트가 어려워진다.

##### 해결
```python
client: TextGenerationClient
```

계약에 의존한다.

---

#### 실수 3 — 하나의 AIService에 모든 기능 추가
```python
class AIService:
    summarize()
    translate()
    classify()
    answer()
    embed()
    generate_image()
```

##### 문제
책임이 너무 많아진다.

##### 해결
기능별 Service와 능력별 Client로 분리한다.

---

#### 실수 4 — Prompt를 Provider Client에서 생성
```python
class OpenAIClient:
    async def summarize(self, text: str):
        prompt = "다음 문서를 요약하세요..."
```

##### 문제
OpenAI Client가 요약 업무를 알게 된다.

##### 해결
Service에서 Prompt를 만들고 Client에는 생성 요청만 전달한다.

---

#### 실수 5 — OpenAI Response 전체를 Service에 반환
```python
return response
```

##### 문제
Service가 OpenAI SDK 객체 구조에 종속된다.

##### 해결
```python
return response.output_text
```

또는 Provider 독립적인 결과 객체로 변환한다.

---

#### 실수 6 — 테스트에서 실제 OpenAI API 호출
```text
pytest
  ↓
실제 OpenAI API
```

##### 문제
- 비용 발생
    
- 네트워크 의존
    
- 느린 테스트
    
- 결과 비결정성
    
- Rate Limit 영향
    
- Credential 필요
    

##### 해결
Fake Client와 Dependency Override를 사용한다.

---

#### 실수 7 — Service에서 HTTPException 사용
```python
raise HTTPException(...)
```

##### 문제
업무 계층이 FastAPI와 HTTP에 종속된다.

##### 해결
Application Exception을 발생시키고 API 계층에서 HTTP로 변환한다.

---

#### 실수 8 — Protocol에 모든 AI 기능을 넣음
```python
class AIClient(Protocol):
    generate_text()
    embed()
    generate_image()
    transcribe()
```

##### 문제
구현체가 사용하지 않는 기능까지 제공해야 한다.

##### 해결
능력별 Protocol로 나눈다.

---

#### 실수 9 — Dependency 생성 로직이 여러 Router에 중복
```python
### summaries.pyOpenAITextGenerationClient(...)

### translations.pyOpenAITextGenerationClient(...)
```

##### 문제
설정 해석과 객체 생성 정책이 분산된다.

##### 해결
`core/dependencies.py`에서 조립한다.

---

#### 실수 10 — Fake Client가 테스트 입력을 기록하지 않음
고정 응답만 반환하면 Service가 올바른 Prompt를 보냈는지 확인하기 어렵다.

##### 해결
Fake Client에 마지막 요청을 기록하거나 Mock을 사용한다.

---

### 31. 실무 Best Practice
#### 31.1 업무 기능별 Service를 만든다
```text
SummaryService
TranslationService
ClassificationService
AnswerService
```

Service 이름만으로 어떤 사용 사례를 담당하는지 알 수 있어야 한다.

---

#### 31.2 Provider 통신은 Client 계층에 둔다
```text
clients/
├── openai_client.py
├── ollama_client.py
└── fake_client.py
```

SDK Import는 Client 계층에 제한한다.

---

#### 31.3 Service는 추상화에 의존한다
```python
TextGenerationClient
```

와 같은 작은 Protocol을 사용한다.

---

#### 31.4 Prompt는 업무 로직으로 취급한다
Prompt는 단순 문자열이 아니라 서비스 품질과 정책을 결정하는 코드다.

다음을 관리해야 한다.

- 목적
    
- 입력 범위
    
- 출력 형식
    
- 금지 규칙
    
- 버전
    
- 테스트
    
- 변경 이력
    

---

#### 31.5 Request와 Service 입력을 분리할 수 있다
```text
Pydantic Request
      ↓
Command
      ↓
Service
```

규모가 커질수록 HTTP 계층과 Application 계층의 독립성이 높아진다.

---

#### 31.6 테스트에서는 가장 바깥 의존성을 제거한다
```text
SummaryService 테스트
→ Fake Client

Router 테스트
→ Fake Service 또는 Fake Client

운영
→ OpenAI Client
```

---

#### 31.7 Provider 오류를 그대로 노출하지 않는다
OpenAI SDK 예외나 내부 응답을 사용자에게 그대로 반환하지 않는다.

```text
Provider Exception
       ↓
Application Exception
       ↓
HTTP Error Response
```

자세한 오류 변환과 Retry 정책은 Unit 38에서 다룬다.

---

#### 31.8 처음부터 과도한 추상화를 만들지 않는다
```text
현재 필요한 공통 기능
→ 작은 Protocol

언젠가 필요할 것 같은 모든 기능
→ 미리 구현하지 않음
```

추상화의 목적은 복잡성을 숨기는 것이지 새로운 복잡성을 추가하는 것이 아니다.

---

### 32. 실습
#### 실습 목표
- Text Generation Client Protocol을 정의한다.
    
- OpenAI Client와 Fake Client를 동일한 계약으로 구현한다.
    
- SummaryService에 Prompt와 업무 흐름을 배치한다.
    
- FastAPI Dependency로 객체를 조립한다.
    
- Router를 얇게 유지한다.
    
- 실제 AI API 없이 Service와 Router를 테스트한다.
    

---

#### 실습 환경
```text
Python 3.12
FastAPI
Pydantic 2
pydantic-settings
OpenAI Python SDK
pytest
pytest-asyncio
httpx
```

설치:

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  pydantic-settings \
  openai \
  pytest \
  pytest-asyncio \
  httpx
```

---

#### 실습 프로젝트 구조
```text
app/
├── api/
│   └── v1/
│       └── summaries.py
│
├── clients/
│   ├── __init__.py
│   ├── base.py
│   ├── fake_client.py
│   └── openai_client.py
│
├── core/
│   ├── config.py
│   └── dependencies.py
│
├── schemas/
│   └── summary.py
│
├── services/
│   └── summary_service.py
│
└── main.py

tests/
├── api/
│   └── test_summaries.py
└── services/
    └── test_summary_service.py
```

---

#### 실습 절차
##### 1단계 — Client Protocol 작성
```text
app/clients/base.py
```

```python
from typing import Protocol


class TextGenerationClient(Protocol):
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...
```

---

##### 2단계 — Fake Client 작성
```text
app/clients/fake_client.py
```

```python
class FakeTextGenerationClient:
    def __init__(
        self,
        *,
        response_text: str = "테스트 AI 응답",
    ) -> None:
        self._response_text = response_text
        self.last_instructions: str | None = None
        self.last_input_text: str | None = None

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        self.last_instructions = instructions
        self.last_input_text = input_text

        return self._response_text
```

---

##### 3단계 — OpenAI Client 작성
```text
app/clients/openai_client.py
```

```python
from openai import AsyncOpenAI


class OpenAITextGenerationClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
    ) -> None:
        self._model = model
        self._max_output_tokens = max_output_tokens

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        response = await self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=self._max_output_tokens,
        )

        output_text = response.output_text.strip()

        if not output_text:
            raise RuntimeError(
                "AI Provider 응답이 비어 있습니다."
            )

        return output_text
```

---

##### 4단계 — Schema 작성
```text
app/schemas/summary.py
```

```python
from typing import Literal

from pydantic import BaseModel, Field


SummaryLength = Literal[
    "short",
    "medium",
    "long",
]

SummaryTone = Literal[
    "neutral",
    "professional",
    "friendly",
]


class SummaryCreateRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
    )
    length: SummaryLength = "medium"
    tone: SummaryTone = "neutral"


class SummaryResponse(BaseModel):
    summary: str
    length: SummaryLength
    tone: SummaryTone
    status: Literal["completed"]
```

---

##### 5단계 — SummaryService 작성
```text
app/services/summary_service.py
```

```python
from dataclasses import dataclass

from app.clients.base import TextGenerationClient
from app.schemas.summary import (
    SummaryLength,
    SummaryTone,
)


@dataclass(frozen=True)
class SummaryCommand:
    text: str
    length: SummaryLength
    tone: SummaryTone


@dataclass(frozen=True)
class SummaryResult:
    summary: str
    length: SummaryLength
    tone: SummaryTone


class SummaryService:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
    ) -> None:
        self._client = client

    async def summarize(
        self,
        command: SummaryCommand,
    ) -> SummaryResult:
        instructions = self._build_instructions(
            length=command.length,
            tone=command.tone,
        )

        summary = await self._client.generate(
            instructions=instructions,
            input_text=command.text.strip(),
        )

        normalized_summary = summary.strip()

        if not normalized_summary:
            raise ValueError(
                "생성된 요약 결과가 비어 있습니다."
            )

        return SummaryResult(
            summary=normalized_summary,
            length=command.length,
            tone=command.tone,
        )

    def _build_instructions(
        self,
        *,
        length: SummaryLength,
        tone: SummaryTone,
    ) -> str:
        length_rule = {
            "short": "3문장 이내로 요약하세요.",
            "medium": "5문장 안팎으로 요약하세요.",
            "long": (
                "중요한 세부사항을 포함하여 "
                "자세히 요약하세요."
            ),
        }[length]

        tone_rule = {
            "neutral": "중립적인 문체를 사용하세요.",
            "professional": (
                "전문적인 보고서 문체를 사용하세요."
            ),
            "friendly": (
                "쉽고 친근한 문체를 사용하세요."
            ),
        }[tone]

        return "\n".join(
            [
                "당신은 전문 문서 요약가입니다.",
                length_rule,
                tone_rule,
                "원문에 없는 사실을 추가하지 마세요.",
                "요약 결과만 반환하세요.",
            ]
        )
```

---

##### 6단계 — Dependency 작성
```text
app/core/dependencies.py
```

```python
from typing import Annotated

from fastapi import Depends

from app.clients.base import TextGenerationClient
from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.core.config import Settings, get_settings
from app.services.summary_service import SummaryService


def get_text_generation_client(
    settings: Annotated[
        Settings,
        Depends(get_settings),
    ],
) -> TextGenerationClient:
    if settings.ai_provider == "fake":
        return FakeTextGenerationClient(
            response_text="Fake Provider 요약 결과",
        )

    if settings.ai_provider == "openai":
        if settings.openai_api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY가 필요합니다."
            )

        if settings.openai_model is None:
            raise RuntimeError(
                "OPENAI_MODEL이 필요합니다."
            )

        return OpenAITextGenerationClient(
            api_key=(
                settings.openai_api_key.get_secret_value()
            ),
            model=settings.openai_model,
            timeout_seconds=settings.ai_timeout_seconds,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )

    raise RuntimeError(
        f"지원하지 않는 Provider: "
        f"{settings.ai_provider}"
    )


def get_summary_service(
    client: Annotated[
        TextGenerationClient,
        Depends(get_text_generation_client),
    ],
) -> SummaryService:
    return SummaryService(
        client=client,
    )
```

---

##### 7단계 — Router 작성
```text
app/api/v1/summaries.py
```

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_summary_service
from app.schemas.summary import (
    SummaryCreateRequest,
    SummaryResponse,
)
from app.services.summary_service import (
    SummaryCommand,
    SummaryService,
)


router = APIRouter(
    prefix="/summaries",
    tags=["Summaries"],
)


@router.post(
    "",
    response_model=SummaryResponse,
)
async def create_summary(
    request: SummaryCreateRequest,
    service: Annotated[
        SummaryService,
        Depends(get_summary_service),
    ],
) -> SummaryResponse:
    result = await service.summarize(
        SummaryCommand(
            text=request.text,
            length=request.length,
            tone=request.tone,
        )
    )

    return SummaryResponse(
        summary=result.summary,
        length=result.length,
        tone=result.tone,
        status="completed",
    )
```

---

##### 8단계 — Router 등록
```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.summaries import (
    router as summaries_router,
)
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(
    summaries_router,
    prefix="/api/v1",
)
```

---

##### 9단계 — Fake Provider 실행
`.env`:

```env
AI_PROVIDER=fake
```

서버 실행:

```bash
uvicorn app.main:app --reload
```

요청:

```json
{
  "text": "FastAPI의 Service Layer는 Router와 외부 AI Provider 사이에서 애플리케이션의 업무 흐름과 Prompt 정책을 관리합니다.",
  "length": "short",
  "tone": "professional"
}
```

예상 응답:

```json
{
  "summary": "Fake Provider 요약 결과",
  "length": "short",
  "tone": "professional",
  "status": "completed"
}
```

---

##### 10단계 — OpenAI Provider 실행
`.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=실제-API-Key
OPENAI_MODEL=사용할-모델-이름
```

같은 API 요청을 보낸다.

Router와 Service 코드는 변경하지 않는다.

변경되는 것은 Dependency가 선택하는 Client뿐이다.

```text
FakeTextGenerationClient
          ↓ 설정 변경
OpenAITextGenerationClient
```

---

### 33. 예상 결과
#### Fake Provider
```text
AI_PROVIDER=fake
```

- 외부 네트워크를 사용하지 않는다.
    
- 비용이 발생하지 않는다.
    
- 고정된 응답이 반환된다.
    
- Router와 Service 구조를 테스트할 수 있다.
    

#### OpenAI Provider
```text
AI_PROVIDER=openai
```

- OpenAI Client가 선택된다.
    
- SummaryService가 Instruction을 구성한다.
    
- Client가 Responses API를 호출한다.
    
- 생성된 텍스트가 SummaryResponse로 변환된다.
    

---

### 34. 실습 확인
-  `TextGenerationClient` Protocol이 정의되었는가?
    
-  OpenAI Client가 Protocol과 같은 메서드 계약을 제공하는가?
    
-  Fake Client가 실제 API 없이 응답을 반환하는가?
    
-  SummaryService가 OpenAI 구현체를 직접 참조하지 않는가?
    
-  Prompt가 Service 계층에 위치하는가?
    
-  Provider SDK는 Client 계층에서만 Import되는가?
    
-  Router가 Prompt 내용을 모르는가?
    
-  Router가 Client를 직접 호출하지 않는가?
    
-  Dependency가 설정에 따라 Client를 선택하는가?
    
-  Service 테스트에서 실제 OpenAI API를 호출하지 않는가?
    
-  Router 테스트에서 Dependency Override를 사용할 수 있는가?
    
-  Provider 응답 객체를 API 응답으로 그대로 반환하지 않는가?
    

---

### 35. 응용 과제
#### 과제 1 — TranslationService 추가
다음 API를 구현한다.

```text
POST /api/v1/translations
```

요청:

```json
{
  "text": "안녕하세요.",
  "target_language": "English"
}
```

구조:

```text
TranslationRouter
      ↓
TranslationService
      ↓
TextGenerationClient
```

OpenAI Client를 새로 만들지 않고 기존 `TextGenerationClient`를 재사용한다.

---

#### 과제 2 — PromptBuilder 분리
다음 구조를 만든다.

```text
app/prompts/
└── summary_prompt.py
```

```python
class SummaryPromptBuilder:
    def build(
        self,
        *,
        length: SummaryLength,
        tone: SummaryTone,
    ) -> str:
        ...
```

`SummaryService`가 PromptBuilder를 주입받도록 수정한다.

---

#### 과제 3 — 실패하는 Fake Client
```python
class FailingTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        raise RuntimeError(
            "AI Provider 테스트 오류"
        )
```

이를 이용해 Provider 오류 발생 시 API가 어떻게 동작하는지 확인한다.

현재는 500 오류가 발생할 수 있다. Unit 38에서 이를 안전한 API 오류로 변환한다.

---

#### 과제 4 — 호출 기록 Fake Client
Fake Client에 호출 횟수를 추가한다.

```python
self.call_count = 0
```

```python
self.call_count += 1
```

Service 호출 후 다음을 검증한다.

```python
assert fake_client.call_count == 1
```

---

#### 과제 5 — 문서 Repository 연결
요청에서 텍스트 대신 `document_id`를 받는다.

```json
{
  "document_id": 10,
  "length": "medium",
  "tone": "neutral"
}
```

`DocumentRepository`로 원문을 조회한 뒤 AI Client를 호출하고 결과를 저장한다.

---

### 36. 이해도 확인
#### 질문 1
AI Service Layer가 필요한 이유는 무엇인가?

##### 모범 답안
Router와 외부 AI Provider 사이에서 요약, 번역, 분류 같은 애플리케이션의 업무 흐름을 관리하기 위해서다. Service는 Prompt 구성, 데이터 준비, Client 호출, 출력 검증, 결과 저장 등을 담당하며 Router와 Provider 통신 코드를 분리한다.

---

#### 질문 2
SummaryService가 OpenAIClient에 직접 의존하면 어떤 문제가 생기는가?

##### 모범 답안
요약 업무 로직이 특정 Provider에 종속된다. OpenAI를 Ollama나 Fake Provider로 교체하려면 Service 코드도 수정해야 하며, 실제 API 없이 단위 테스트하기 어려워진다.

---

#### 질문 3
`TextGenerationClient` Protocol의 역할은 무엇인가?

##### 모범 답안
텍스트 생성 Client가 제공해야 하는 메서드 계약을 정의한다. SummaryService는 이 계약에만 의존하므로 OpenAI, Ollama, Fake Client 등 서로 다른 구현체를 같은 방식으로 사용할 수 있다.

---

#### 질문 4
Prompt를 OpenAI Client가 아니라 SummaryService에서 만드는 이유는 무엇인가?

##### 모범 답안
요약 길이, 문체, 사실 추가 금지, 출력 형식 같은 Prompt 규칙은 요약 업무의 정책이기 때문이다. Client는 특정 업무를 알지 않고 전달받은 입력을 Provider에 전송하는 역할만 담당해야 한다.

---

#### 질문 5
Fake Client가 필요한 이유는 무엇인가?

##### 모범 답안
실제 OpenAI API를 호출하지 않고 Service와 Router를 테스트하기 위해서다. 테스트 비용과 네트워크 의존성을 제거하고 일정한 결과를 얻을 수 있으며, Service가 올바른 Prompt와 입력을 전달했는지도 검증할 수 있다.

---

#### 질문 6
Router가 얇아야 한다는 것은 무슨 뜻인가?

##### 모범 답안
Router는 HTTP 요청 수신, 요청 모델 검증, Service 호출, 응답 모델 반환만 담당해야 한다는 뜻이다. Prompt 생성, Provider 선택, SDK 호출, 데이터 저장 같은 업무 로직은 Router 밖에 있어야 한다.

---

#### 질문 7
Service에서 `HTTPException`을 직접 발생시키지 않는 것이 좋은 이유는 무엇인가?

##### 모범 답안
Service가 FastAPI와 HTTP에 종속되지 않도록 하기 위해서다. Service에서는 업무 또는 애플리케이션 예외를 발생시키고, API 계층의 Exception Handler가 이를 HTTP 응답으로 변환하는 것이 계층 분리에 적합하다.

---

#### 질문 8
모든 AI 기능을 하나의 Protocol에 넣으면 왜 문제가 되는가?

##### 모범 답안
텍스트 생성만 필요한 구현체도 Embedding, 이미지 생성, 음성 인식과 같은 사용하지 않는 기능까지 구현해야 하기 때문이다. 기능별로 작은 Protocol을 만들면 각 Service가 필요한 능력에만 의존할 수 있다.

---

### 37. 핵심 내용 정리
#### 핵심 1
Service Layer는 AI를 이용하는 애플리케이션의 사용 사례와 업무 흐름을 관리한다.

```text
Router
   ↓
Application Service
   ↓
AI Client
```

---

#### 핵심 2
Service와 Client의 책임은 다르다.

```text
Service
→ 무엇을 수행할지 결정

Client
→ 외부 Provider에 어떻게 요청할지 처리
```

---

#### 핵심 3
Service는 특정 Provider 구현체가 아니라 Protocol에 의존한다.

```text
SummaryService
      ↓
TextGenerationClient
      ↑
OpenAI / Ollama / Fake
```

---

#### 핵심 4
Prompt는 업무 정책이므로 Service 또는 Prompt Builder에서 관리한다.

```text
Service
   ↓ Prompt 구성
Client
   ↓ API 호출
Provider
```

---

#### 핵심 5
Provider 응답은 Client에서 애플리케이션이 사용할 수 있는 값으로 변환한다.

```text
OpenAI Response
      ↓
output_text
      ↓
Service
```

---

#### 핵심 6
FastAPI Dependency Injection은 객체 생성과 연결을 담당한다.

```text
Settings
   ↓
TextGenerationClient
   ↓
SummaryService
   ↓
Router
```

---

#### 핵심 7
테스트에서는 Fake Client와 Dependency Override를 사용한다.

```text
운영
SummaryService → OpenAIClient

테스트
SummaryService → FakeClient
```

---

#### 핵심 8
AI 기능은 하나의 거대한 AIService가 아니라 기능별 Service로 분리한다.

```text
SummaryService
TranslationService
ClassificationService
AnswerService
```

---

### 38. 한 문장으로 설명하기
> FastAPI의 AI Service Layer는 요약과 번역 같은 AI 사용 사례의 업무 흐름과 Prompt 정책을 담당하며, Provider 독립적인 Client Protocol과 Dependency Injection을 통해 OpenAI, Ollama, Fake 구현을 교체 가능한 구조로 연결하는 계층이다.

---

### FastAPI Part 5. AI Backend Integration

## Module 39. 비동기 AI 요청 처리


### Module 실습 예제

- [예제 1: concurrent_ai.py](examples/module_39/concurrent_ai.py) — 여러 AI 요청을 asyncio.gather로 동시에 처리합니다.
- [예제 2: semaphore_limit.py](examples/module_39/semaphore_limit.py) — Semaphore로 동시 AI 호출 수를 제한합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 외부 AI I/O를 기다리는 동안 서버 자원을 효율적으로 사용한다.
- **오늘 만드는 것:** 비동기 Endpoint와 Client 호출 흐름을 구현한다.
- **AI 플랫폼의 위치:** 동시 AI 요청 처리의 핵심 실행 방식이다.
- **실무에서 많이 하는 실수:** CPU 작업이나 동기 SDK 호출 앞에 async만 붙인다.
- **5분 실습:** blocking 함수가 포함된 코드를 찾아 격리 방법을 제안한다.

> **학습 층위 — AI 연결**  
> Python의 `async`/`await` 문법을 다시 학습하는 것이 아니라, FastAPI Endpoint와 외부 AI SDK 사이의 대기·Timeout·동시성 경계에 적용한다. 요청 수명주기보다 긴 작업의 분리는 후속 운영 과정에서 다룬다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI Backend에서 비동기 처리가 중요한 이유는 무엇인가?
    
- 동기, 비동기, 동시성, 병렬성은 무엇이 다른가?
    
- `async def`와 `await`는 실제로 어떤 역할을 하는가?
    
- AI API 응답을 기다리는 동안 FastAPI는 무엇을 하는가?
    
- 비동기 함수를 호출하면서 `await`를 생략하면 어떻게 되는가?
    
- 여러 AI 요청을 동시에 실행하려면 어떻게 해야 하는가?
    
- `asyncio.gather()`와 `TaskGroup`은 어떤 상황에 사용하는가?
    
- 비동기 요청을 무제한으로 동시에 실행하면 왜 위험한가?
    
- `asyncio.Semaphore`는 어떤 문제를 해결하는가?
    
- OpenAI Client를 요청마다 생성하지 않고 재사용하는 이유는 무엇인가?
    
- FastAPI의 `lifespan`은 AI Client 수명주기를 어떻게 관리하는가?
    
- 비동기 코드 안에 동기 블로킹 작업을 넣으면 어떤 문제가 생기는가?
    
- 사용자가 연결을 취소했을 때 AI 요청은 어떻게 다뤄야 하는가?
    

---

### 2. 문제 이해 — Why
#### 2.1 일반적인 API와 AI API의 처리 시간 차이
일반적인 백엔드 API는 다음과 같은 작업을 수행할 수 있다.

```text
사용자 조회
게시글 조회
설정값 반환
간단한 데이터 저장
```

이러한 요청은 환경에 따라 차이가 있지만 비교적 빠르게 완료되는 경우가 많다.

반면 AI 요청은 다음 과정을 거친다.

```text
FastAPI
   ↓ 네트워크 요청
AI Provider
   ↓ 입력 처리
Model Inference
   ↓ 출력 Token 생성
AI Provider
   ↓ 네트워크 응답
FastAPI
```

특히 LLM은 출력 전체를 한 번에 계산해 즉시 반환하는 단순 함수가 아니다.

개념적으로는 다음 Token을 반복적으로 생성한다.

```text
입력
 ↓
Token 1 생성
 ↓
Token 2 생성
 ↓
Token 3 생성
 ↓
...
 ↓
응답 완료
```

따라서 출력이 길거나 모델의 처리량이 높거나 네트워크가 느리면 요청 시간이 길어질 수 있다.

---

#### 2.2 동기 방식으로 기다리면 무엇이 문제인가?
하나의 직원이 있는 음식점을 생각해 보자.

첫 번째 고객이 주문했다.

직원은 주방에 주문을 전달한 뒤 음식이 완성될 때까지 주방 앞에 서 있다.

```text
고객 A 주문
   ↓
주방 전달
   ↓
직원 대기
   ↓
음식 완성
   ↓
고객 B 주문 접수
```

주방이 음식을 만드는 동안 직원이 할 수 있는 다른 일이 있어도 아무 일도 하지 않는다.

이것이 네트워크 I/O를 동기 방식으로 기다리는 상황과 비슷하다.

```text
AI 요청 전송
   ↓
응답이 올 때까지 실행 흐름 점유
   ↓
다음 작업
```

AI 요청 하나가 10초 걸린다면 그 실행 흐름은 10초 동안 대부분 응답을 기다린다.

---

#### 2.3 비동기 방식은 어떻게 다른가?
비동기 방식에서는 직원이 주방에 주문을 전달한 뒤 다른 고객의 주문을 받는다.

```text
고객 A 주문
   ↓
주방 전달
   ↓
고객 B 주문 접수
   ↓
주방 전달
   ↓
고객 C 주문 접수
   ↓
A 음식 완성 알림
   ↓
고객 A에게 전달
```

직원이 음식을 직접 동시에 여러 개 조리하는 것은 아니다.

기다리는 시간을 이용해 다른 요청을 처리하는 것이다.

FastAPI의 비동기 요청도 같은 관점으로 이해할 수 있다.

```text
Request A
   ↓ AI 요청 전송
   ↓ await
Event Loop가 다른 작업 실행
   ↓
Request B 처리
   ↓
A의 AI 응답 도착
   ↓
Request A 계속 실행
```

Python의 `asyncio`는 `async`와 `await` 문법을 이용해 동시성 코드를 작성하기 위한 표준 라이브러리이며, 여러 Python 비동기 프레임워크의 기반으로 사용된다.

---

### 3. 핵심 개념 — Concept
#### 3.1 동기란 무엇인가?
동기 코드는 앞의 작업이 끝난 후 다음 작업을 실행한다.

```python
result = slow_function()
print(result)
```

실행 흐름:

```text
slow_function 시작
       ↓
완료될 때까지 기다림
       ↓
결과 반환
       ↓
print 실행
```

동기 자체가 나쁜 것은 아니다.

다음과 같은 작업에는 자연스럽고 단순하다.

- 짧은 계산
    
- 순차 실행이 반드시 필요한 로직
    
- 동기 라이브러리만 제공되는 작업
    
- 작은 스크립트
    
- 이해하기 쉬운 직렬 처리
    

문제는 오래 기다리는 I/O 작업을 동기 방식으로 처리할 때 발생한다.

---

#### 3.2 비동기란 무엇인가?
비동기 코드는 특정 작업이 완료되기를 기다리는 동안 실행 제어권을 다른 작업에 넘길 수 있다.

```python
result = await slow_async_function()
print(result)
```

`await`는 단순히 다음 의미가 아니다.

```text
여기에서 아무것도 하지 않고 멈춘다.
```

더 정확히는 다음과 같다.

```text
이 작업의 완료를 기다려야 하지만,
기다리는 동안 Event Loop는
실행 가능한 다른 작업을 처리할 수 있다.
```

---

#### 3.3 동시성과 병렬성
두 개념은 구분해야 한다.

##### 동시성
여러 작업이 같은 기간 안에 번갈아 진행되는 구조다.

```text
시간 ─────────────────────────→

Task A  실행 ─ 대기 ─ 실행 ─ 대기
Task B       실행 ─ 대기 ─ 실행
Task C            실행 ─ 대기 ─ 실행
```

한 명의 직원이 여러 주문을 효율적으로 관리하는 것과 비슷하다.

##### 병렬성
여러 작업이 실제로 같은 시점에 실행되는 구조다.

```text
CPU Core 1 → Task A
CPU Core 2 → Task B
CPU Core 3 → Task C
```

여러 명의 직원이 각각 작업하는 것과 비슷하다.

##### AI Backend에서 주로 필요한 것
외부 AI API 호출은 대부분 네트워크 I/O 대기다.

따라서 핵심은 CPU 병렬 계산보다 **I/O 동시성**이다.

```text
AI 요청 전송
   ↓
응답 대기 중
   ↓
다른 요청 처리
```

---

#### 3.4 I/O Bound와 CPU Bound
#### I/O Bound
외부 입출력을 기다리는 시간이 많은 작업이다.

예:

- AI Provider API 호출
    
- 데이터베이스 조회
    
- Redis 호출
    
- HTTP 요청
    
- 비동기 파일 저장
    
- 외부 Object Storage 호출
    

```text
실제 CPU 계산 시간 < 대기 시간
```

비동기 처리의 효과가 크다.

---

#### CPU Bound
CPU가 계산하는 시간이 많은 작업이다.

예:

- 대규모 이미지 변환
    
- 복잡한 수치 계산
    
- 로컬 모델 추론
    
- 대용량 압축
    
- 일부 PDF 렌더링
    
- 머신러닝 학습
    

```text
실제 CPU 계산 시간 > I/O 대기 시간
```

이 작업을 단순히 `async def` 안에 넣는다고 빨라지지 않는다.

```python
async def process_image():
    heavy_cpu_calculation()
```

함수 이름은 비동기이지만 내부의 CPU 계산은 Event Loop를 계속 점유할 수 있다.

---

### 4. `async def`와 Coroutine
#### 4.1 일반 함수
```python
def add(a: int, b: int) -> int:
    return a + b
```

호출:

```python
result = add(10, 20)
```

결과:

```text
30
```

함수를 호출하면 즉시 코드가 실행되고 반환값을 받는다.

---

#### 4.2 비동기 함수
```python
async def add_async(a: int, b: int) -> int:
    return a + b
```

다음처럼 호출하면 어떻게 될까?

```python
result = add_async(10, 20)
```

`result`에는 `30`이 바로 들어가지 않는다.

비동기 함수 호출은 Coroutine 객체를 만든다.

```text
<coroutine object add_async at ...>
```

실제 결과를 얻으려면 `await`해야 한다.

```python
result = await add_async(10, 20)
```

---

#### 4.3 Coroutine이란 무엇인가?
Coroutine은 중간에 실행을 일시 중지하고 나중에 다시 이어서 실행할 수 있는 함수 실행 단위다.

```text
Coroutine 시작
   ↓
일부 코드 실행
   ↓
await에서 제어권 반환
   ↓
다른 Coroutine 실행
   ↓
대기 작업 완료
   ↓
이전 위치부터 실행 재개
```

Python 공식 문서는 Coroutine, Task, 취소, Timeout과 동시 실행을 `asyncio`의 핵심 고수준 API로 설명한다.

---

### 5. Event Loop
#### 5.1 Event Loop란 무엇인가?
Event Loop는 현재 실행할 수 있는 비동기 작업을 선택하고 실행하는 관리자다.

```text
┌────────────────────────────┐
│         Event Loop         │
│                            │
│ 실행 가능한 Task 선택      │
│ I/O 완료 여부 확인          │
│ 중단된 Coroutine 재개       │
│ Task 취소와 Timeout 처리    │
└────────────────────────────┘
```

비유하면 식당의 주문 관리 담당자다.

```text
주문 A → 주방 대기
주문 B → 결제 대기
주문 C → 포장 완료
```

Event Loop는 지금 실행 가능한 작업을 골라 진행한다.

---

#### 5.2 `await`는 양보 지점이다
다음 코드를 보자.

```python
async def create_summary(
    service: SummaryService,
    text: str,
) -> str:
    result = await service.summarize(text)
    return result
```

`service.summarize()` 내부에서 외부 AI API를 기다리면 Event Loop가 다른 Task를 실행할 기회를 얻는다.

```text
await 이전
→ 현재 Coroutine 실행

await에서 I/O 대기
→ 제어권을 Event Loop에 반환

I/O 완료
→ 해당 Coroutine 재개
```

주의할 점은 모든 `await`가 반드시 긴 대기를 만든다는 뜻은 아니다.

`await` 대상이 즉시 완료되면 바로 이어서 실행될 수도 있다.

---

### 6. FastAPI에서 `async def` 사용
FastAPI Router는 다음과 같이 작성할 수 있다.

```python
@router.post("/summaries")
async def create_summary(
    request: SummaryCreateRequest,
    service: SummaryService = Depends(get_summary_service),
) -> SummaryResponse:
    result = await service.summarize(
        SummaryCommand(
            text=request.text,
            length=request.length,
            tone=request.tone,
        )
    )

    return SummaryResponse(
        summary=result.summary,
        length=result.length,
        tone=result.tone,
        status="completed",
    )
```

호출 계층 전체가 비동기로 이어진다.

```text
FastAPI Router
   ↓ await
SummaryService
   ↓ await
TextGenerationClient
   ↓ await
AsyncOpenAI
   ↓
OpenAI API
```

이를 흔히 비동기 호출 체인이라고 볼 수 있다.

---

#### 6.1 호출 체인 중 한 곳이 동기라면?
```text
Router async
   ↓
Service async
   ↓
동기 HTTP Client
```

가장 안쪽에서 동기 네트워크 호출을 사용하면 해당 호출이 끝날 때까지 Event Loop를 막을 수 있다.

예:

```python
async def generate(self, prompt: str) -> str:
    response = requests.post(
        "https://example.com/ai",
        json={"prompt": prompt},
    )

    return response.json()["text"]
```

함수는 `async def`지만 `requests.post()`는 동기 호출이다.

```text
async def 사용
      ≠
내부 코드가 자동으로 비동기가 됨
```

비동기 함수에서는 비동기 HTTP Client나 비동기 SDK를 사용해야 한다.

---

### 7. 잘못된 비동기 사용
#### 7.1 `await` 생략
잘못된 코드:

```python
summary = service.summarize(command)
```

여기서 `summary`는 결과 객체가 아니다.

```text
Coroutine Object
```

따라서 다음 코드는 실패할 수 있다.

```python
return SummaryResponse(
    summary=summary.summary,
)
```

올바른 코드:

```python
summary = await service.summarize(command)
```

---

#### 7.2 비동기가 아닌 값에 `await`
잘못된 코드:

```python
value = await 10
```

`await`는 Awaitable 객체에만 사용할 수 있다.

예:

- Coroutine
    
- Task
    
- Future
    
- `__await__()`를 구현한 객체
    

---

#### 7.3 일반 함수에서 `await`
잘못된 코드:

```python
def create_summary():
    result = await service.summarize(...)
```

`await`는 일반 `def` 내부에서 사용할 수 없다.

올바른 코드:

```python
async def create_summary():
    result = await service.summarize(...)
```

---

#### 7.4 `asyncio.run()`을 Router 내부에서 호출
잘못된 코드:

```text
@router.post("/summaries")
async def create_summary(...):
    result = asyncio.run(
        service.summarize(command)
    )
```

FastAPI 애플리케이션은 이미 Event Loop 안에서 실행되고 있다.

실행 중인 Event Loop 내부에서 다시 `asyncio.run()`으로 새로운 Loop를 시작하려 하면 오류가 발생할 수 있다.

Router 내부에서는 단순히 `await`한다.

```python
result = await service.summarize(command)
```

---

### 8. 순차 실행과 동시 실행
두 개의 독립적인 AI 작업을 실행한다고 가정하자.

```text
문서 요약
키워드 추출
```

두 작업이 서로의 결과를 필요로 하지 않는다면 동시에 시작할 수 있다.

---

#### 8.1 순차 실행
```python
summary = await client.generate(
    instructions=summary_instructions,
    input_text=text,
)

keywords = await client.generate(
    instructions=keyword_instructions,
    input_text=text,
)
```

실행 흐름:

```text
요약 시작
 ↓
요약 완료
 ↓
키워드 시작
 ↓
키워드 완료
```

요약이 5초, 키워드가 4초라면 전체 시간은 대략 두 시간을 합한 값에 가까워질 수 있다.

```text
5초 + 4초 ≈ 9초
```

실제 시간은 네트워크와 Provider 상태에 따라 달라진다.

---

#### 8.2 `asyncio.gather()`를 이용한 동시 실행
```python
import asyncio


summary, keywords = await asyncio.gather(
    client.generate(
        instructions=summary_instructions,
        input_text=text,
    ),
    client.generate(
        instructions=keyword_instructions,
        input_text=text,
    ),
)
```

실행 흐름:

```text
요약 시작 ─────────────→ 완료
키워드 시작 ────────→ 완료
```

독립 작업이 겹쳐 실행되므로 전체 시간은 가장 오래 걸린 작업 시간에 가까워질 수 있다.

```text
max(5초, 4초) ≈ 5초
```

Python 공식 asyncio API는 `gather()`를 여러 Awaitable의 동시 실행에 사용하는 고수준 기능으로 제공한다.

---

#### 8.3 모든 작업을 동시에 실행해도 되는가?
아니다.

다음 작업은 순서가 필요하다.

```text
문서 검색
   ↓
검색 결과 획득
   ↓
검색 결과를 Prompt에 포함
   ↓
답변 생성
```

RAG에서 검색 결과가 있어야 답변 Prompt를 만들 수 있다.

```python
documents = await search_service.search(question)

answer = await client.generate(
    instructions=answer_instructions,
    input_text=build_context(
        question=question,
        documents=documents,
    ),
)
```

이 두 작업은 의존 관계가 있으므로 동시 실행할 수 없다.

판단 기준:

```text
작업 B가 작업 A의 결과를 필요로 하는가?

Yes → 순차 실행
No  → 동시 실행 검토
```

---

### 9. `asyncio.gather()`의 오류 처리
다음 코드를 생각해 보자.

```python
summary, keywords = await asyncio.gather(
    create_summary(),
    extract_keywords(),
)
```

두 작업 중 하나가 예외를 발생시키면 호출 측에서도 예외를 처리해야 한다.

```python
try:
    summary, keywords = await asyncio.gather(
        create_summary(),
        extract_keywords(),
    )
except Exception as exc:
    ...
```

AI 작업에서는 각 작업이 부분적으로 성공할 수 있는지도 결정해야 한다.

예:

```text
요약 성공
키워드 실패
```

정책 선택:

```text
정책 A
하나라도 실패하면 전체 요청 실패

정책 B
성공한 결과만 반환

정책 C
실패한 작업만 Retry

정책 D
핵심 작업과 부가 작업 구분
```

단순히 `gather()`를 사용하는 것보다 실패 정책을 먼저 설계해야 한다.

---

### 10. `TaskGroup`
Python 3.11 이상에서는 `asyncio.TaskGroup`을 사용해 관련 Task를 구조적으로 관리할 수 있다.

```python
import asyncio


async with asyncio.TaskGroup() as task_group:
    summary_task = task_group.create_task(
        create_summary()
    )

    keyword_task = task_group.create_task(
        extract_keywords()
    )

summary = summary_task.result()
keywords = keyword_task.result()
```

구조:

```text
TaskGroup
 ├─ Summary Task
 └─ Keyword Task
```

TaskGroup 블록은 내부 Task들의 수명주기를 한 범위에서 관리한다.

Python 공식 문서는 Task 생성, 취소, Task Group, Timeout과 동시 실행을 Coroutine·Task API의 일부로 제공한다.

---

#### 10.1 `gather()`와 `TaskGroup` 선택
학습 초기에는 `gather()`가 간단하다.

```python
result1, result2 = await asyncio.gather(
    task1(),
    task2(),
)
```

여러 관련 Task의 실패와 취소를 구조적으로 관리하려면 `TaskGroup`을 검토한다.

```text
간단한 독립 작업 몇 개
→ gather()

관련 Task 묶음과 구조적 수명주기
→ TaskGroup
```

---

### 11. 동시 요청을 무제한으로 실행하면 안 되는 이유
문서가 100개 있다고 가정하자.

다음 코드는 100개의 AI 요청을 한꺼번에 시작할 수 있다.

```python
results = await asyncio.gather(
    *[
        summarize_document(document)
        for document in documents
    ]
)
```

문제:

- Provider Rate Limit 초과
    
- 순간 비용 급증
    
- 네트워크 연결 급증
    
- 메모리 사용 증가
    
- Timeout 증가
    
- 실패 요청 급증
    
- 다른 사용자 요청 지연
    
- 서버 자원 고갈
    

비동기 처리는 무한 동시 실행을 의미하지 않는다.

```text
비동기
≠
제한 없이 모든 요청 동시 실행
```

---

### 12. Semaphore를 이용한 동시성 제한
#### 12.1 Semaphore란 무엇인가?
Semaphore는 동시에 특정 작업을 실행할 수 있는 개수를 제한한다.

```text
동시 실행 제한 = 3

Task A → 실행
Task B → 실행
Task C → 실행
Task D → 대기
Task E → 대기
```

작업 하나가 끝나면 대기 중인 작업이 진입한다.

```text
Task B 완료
   ↓
Task D 실행 시작
```

Python의 `asyncio.Semaphore`는 내부 Counter를 관리하며, 사용 가능한 허가가 없을 때 `acquire()` 호출을 기다리게 한다.

---

#### 12.2 기본 예제
```python
import asyncio


semaphore = asyncio.Semaphore(3)


async def limited_generate(
    client: TextGenerationClient,
    instructions: str,
    input_text: str,
) -> str:
    async with semaphore:
        return await client.generate(
            instructions=instructions,
            input_text=input_text,
        )
```

동시에 최대 세 개의 `client.generate()`만 실행된다.

---

#### 12.3 AI Client Decorator로 분리
동시성 제한을 Service마다 반복하지 않도록 Client Decorator로 만들 수 있다.

파일:

```text
app/clients/limited_client.py
```

```python
import asyncio

from app.clients.base import TextGenerationClient


class ConcurrencyLimitedTextGenerationClient:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
        max_concurrency: int,
    ) -> None:
        if max_concurrency < 1:
            raise ValueError(
                "max_concurrency는 1 이상이어야 합니다."
            )

        self._client = client
        self._semaphore = asyncio.Semaphore(
            max_concurrency
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        async with self._semaphore:
            return await self._client.generate(
                instructions=instructions,
                input_text=input_text,
            )
```

구조:

```text
SummaryService
     ↓
ConcurrencyLimitedClient
     ↓
OpenAIClient
     ↓
OpenAI API
```

Service는 동시성 제한의 존재를 몰라도 된다.

---

### 13. 동시성 제한 설정 추가
파일:

```text
app/core/config.py
```

```python
from pydantic import Field


class Settings(BaseSettings):
    # 기존 설정 생략

    ai_max_concurrency: int = Field(
        default=5,
        ge=1,
        le=100,
    )
```

`.env.example`:

```env
AI_MAX_CONCURRENCY=5
```

주의:

```text
AI_MAX_CONCURRENCY=100
```

이 값이 항상 더 높은 성능을 의미하지 않는다.

최적값은 다음 요소에 따라 달라진다.

- AI Provider Rate Limit
    
- 모델 처리량
    
- 서버 Worker 수
    
- 사용자 수
    
- 평균 응답 시간
    
- 비용 제한
    
- 네트워크 환경
    
- 요청당 Token 수
    

---

### 14. 요청별 Semaphore와 애플리케이션 공용 Semaphore
#### 14.1 요청마다 Semaphore 생성
잘못된 구조:

```text
async def summarize_many(...):
    semaphore = asyncio.Semaphore(5)
```

한 요청 안에서는 다섯 개로 제한되지만 사용자 요청이 열 개 들어오면 최대 50개가 실행될 수 있다.

```text
HTTP 요청 1 → 최대 5개
HTTP 요청 2 → 최대 5개
...
HTTP 요청 10 → 최대 5개

총 최대 50개
```

---

#### 14.2 애플리케이션 공용 제한
Client를 애플리케이션 전체에서 재사용하면서 하나의 Semaphore를 공유하면 전체 AI 호출 수를 제한할 수 있다.

```text
모든 사용자 요청
      ↓
공용 ConcurrencyLimitedClient
      ↓
Semaphore(5)
      ↓
동시에 최대 5개 Provider 호출
```

이 구조를 만들려면 Client 객체의 수명주기를 요청 단위보다 길게 관리해야 한다.

---

### 15. 요청마다 OpenAI Client를 생성하는 문제
Unit 35의 Dependency는 요청마다 Client를 생성할 가능성이 있었다.

```python
def get_text_generation_client(
    settings: Settings = Depends(get_settings),
) -> TextGenerationClient:
    return OpenAITextGenerationClient(...)
```

요청 흐름:

```text
Request A
   ↓ Client 생성
Request B
   ↓ Client 생성
Request C
   ↓ Client 생성
```

외부 HTTP Client는 내부적으로 연결 관리 자원을 사용할 수 있다.

따라서 애플리케이션 시작 시 Client를 생성하고 여러 요청에서 재사용하는 구조를 고려할 수 있다.

```text
Application Startup
   ↓
AI Client 생성
   ↓
Request A/B/C에서 공유
   ↓
Application Shutdown
   ↓
AI Client 종료
```

---

### 16. FastAPI Lifespan
#### 16.1 Lifespan이란 무엇인가?
Lifespan은 FastAPI 애플리케이션이 시작될 때 필요한 자원을 만들고 종료될 때 정리하는 구조다.

```text
애플리케이션 시작
   ↓
Client 생성
Database Pool 생성
Model Loading
Cache 연결
   ↓
요청 처리
   ↓
애플리케이션 종료
   ↓
Client 종료
Pool 종료
자원 정리
```

FastAPI 공식 문서는 `asynccontextmanager`와 `yield`를 이용해 시작 전 로직과 종료 후 정리 로직을 작성하는 Lifespan 방식을 제공한다.

---

#### 16.2 기본 Lifespan
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션 시작")

    yield

    print("애플리케이션 종료")


app = FastAPI(
    lifespan=lifespan,
)
```

`yield` 이전:

```text
Startup Logic
```

`yield` 이후:

```text
Shutdown Logic
```

---

### 17. OpenAI Client 종료 기능 추가
파일:

```text
app/clients/openai_client.py
```

```python
from openai import AsyncOpenAI


class OpenAITextGenerationClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
    ) -> None:
        self._model = model
        self._max_output_tokens = max_output_tokens

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        response = await self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=self._max_output_tokens,
        )

        output_text = response.output_text.strip()

        if not output_text:
            raise RuntimeError(
                "AI Provider 응답이 비어 있습니다."
            )

        return output_text

    async def close(self) -> None:
        await self._client.close()
```

Provider Client의 공개 계약에 종료 기능까지 포함할지는 프로젝트 구조에 따라 결정한다.

텍스트 생성 능력과 자원 종료 능력을 분리하려면 별도 Protocol을 둘 수 있다.

```python
from typing import Protocol


class AsyncClosable(Protocol):
    async def close(self) -> None:
        ...
```

---

### 18. Lifespan에서 Client 생성
#### 18.1 App State 사용
FastAPI 애플리케이션 객체에는 애플리케이션 수명 동안 공유할 상태를 저장할 수 있다.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.clients.limited_client import (
    ConcurrencyLimitedTextGenerationClient,
)
from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    if settings.ai_provider == "fake":
        base_client = FakeTextGenerationClient(
            response_text="Fake AI 응답",
        )

    elif settings.ai_provider == "openai":
        if settings.openai_api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY가 필요합니다."
            )

        if settings.openai_model is None:
            raise RuntimeError(
                "OPENAI_MODEL이 필요합니다."
            )

        base_client = OpenAITextGenerationClient(
            api_key=(
                settings.openai_api_key.get_secret_value()
            ),
            model=settings.openai_model,
            timeout_seconds=settings.ai_timeout_seconds,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )

    else:
        raise RuntimeError(
            f"지원하지 않는 Provider: "
            f"{settings.ai_provider}"
        )

    limited_client = (
        ConcurrencyLimitedTextGenerationClient(
            client=base_client,
            max_concurrency=(
                settings.ai_max_concurrency
            ),
        )
    )

    app.state.text_generation_client = (
        limited_client
    )
    app.state.base_text_generation_client = (
        base_client
    )

    yield

    close_method = getattr(
        base_client,
        "close",
        None,
    )

    if close_method is not None:
        await close_method()
```

---

#### 18.2 Main 애플리케이션
```python
from fastapi import FastAPI

from app.api.v1.summaries import (
    router as summaries_router,
)
from app.core.config import get_settings
from app.core.lifespan import lifespan


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(
    summaries_router,
    prefix="/api/v1",
)
```

---

### 19. Request에서 App State 접근
Dependency에서 `Request`를 이용해 공유 Client를 가져온다.

```python
from typing import cast

from fastapi import Request

from app.clients.base import TextGenerationClient


def get_text_generation_client(
    request: Request,
) -> TextGenerationClient:
    return cast(
        TextGenerationClient,
        request.app.state.text_generation_client,
    )
```

Service Dependency:

```python
from typing import Annotated

from fastapi import Depends

from app.clients.base import TextGenerationClient
from app.services.summary_service import SummaryService


def get_summary_service(
    client: Annotated[
        TextGenerationClient,
        Depends(get_text_generation_client),
    ],
) -> SummaryService:
    return SummaryService(
        client=client,
    )
```

전체 흐름:

```text
Application Startup
   ↓
OpenAI Client 생성
   ↓
ConcurrencyLimitedClient로 감쌈
   ↓
app.state에 저장
   ↓
각 Request Dependency에서 조회
   ↓
SummaryService에 주입
```

---

### 20. App State 사용의 장단점
#### 장점
- 애플리케이션 수준 Client 재사용
    
- 공용 Semaphore 공유
    
- Startup과 Shutdown 관리
    
- Router가 전역 객체를 직접 참조하지 않음
    
- FastAPI Dependency와 연결 가능
    

#### 주의사항
- `app.state`는 동적 속성이므로 타입 추론이 약할 수 있다.
    
- 테스트에서 Lifespan을 실행해야 한다.
    
- 필요한 객체가 State에 없으면 Runtime Error가 발생할 수 있다.
    
- 너무 많은 전역 상태를 넣으면 구조 파악이 어려워진다.
    

대규모 프로젝트에서는 별도 Application Container 객체를 만들어 State에 하나만 저장할 수도 있다.

---

### 21. Application Container
#### 21.1 Container란 무엇인가?
애플리케이션에서 공유하는 주요 객체를 하나의 구조로 묶는다.

```python
from dataclasses import dataclass

from app.clients.base import TextGenerationClient


@dataclass
class ApplicationContainer:
    text_generation_client: TextGenerationClient
```

Lifespan:

```python
app.state.container = ApplicationContainer(
    text_generation_client=limited_client,
)
```

Dependency:

```python
from fastapi import Request


def get_text_generation_client(
    request: Request,
) -> TextGenerationClient:
    container: ApplicationContainer = (
        request.app.state.container
    )

    return container.text_generation_client
```

구조:

```text
app.state
   ↓
ApplicationContainer
   ├─ TextGenerationClient
   ├─ Database Session Factory
   ├─ Cache Client
   └─ 기타 공유 자원
```

처음부터 Container를 지나치게 복잡하게 만들 필요는 없다.

공유 자원이 늘어날 때 도입한다.

---

### 22. Dependency에서 `yield` 사용
Client를 요청마다 생성하고 요청 종료 후 닫고 싶다면 `yield` Dependency를 사용할 수 있다.

```python
from collections.abc import AsyncIterator


async def get_client() -> AsyncIterator[
    OpenAITextGenerationClient
]:
    client = OpenAITextGenerationClient(...)

    try:
        yield client
    finally:
        await client.close()
```

실행 흐름:

```text
Dependency 진입
   ↓
Client 생성
   ↓
yield로 Router에 전달
   ↓
요청 처리
   ↓
finally
   ↓
Client 종료
```

FastAPI 공식 문서는 `yield` Dependency를 이용해 사용 전 자원을 만들고 요청 처리 후 정리 코드를 실행할 수 있다고 설명한다.

하지만 AI HTTP Client는 요청마다 생성·종료하기보다 애플리케이션 수명 동안 재사용하는 편이 적절할 수 있다.

선택 기준:

```text
요청마다 독립된 짧은 자원
→ yield Dependency

애플리케이션 전체에서 공유할 Client
→ Lifespan
```

---

### 23. Blocking Code 문제
#### 23.1 잘못된 예
```python
import time


async def generate_summary() -> str:
    time.sleep(10)

    return "완료"
```

`time.sleep(10)`은 현재 Thread를 동기적으로 멈춘다.

그동안 Event Loop가 같은 Thread에서 다른 Coroutine을 실행하기 어려워진다.

비동기 대기라면 다음을 사용한다.

```python
import asyncio


async def generate_summary() -> str:
    await asyncio.sleep(10)

    return "완료"
```

`asyncio.sleep()`은 기다리는 동안 제어권을 Event Loop에 돌려준다.

---

#### 23.2 동기 라이브러리를 반드시 사용해야 한다면?
동기 함수가 I/O를 오래 점유하고 비동기 대체 라이브러리가 없다면 Thread로 옮기는 방법을 고려할 수 있다.

```python
import asyncio


result = await asyncio.to_thread(
    blocking_function,
    argument,
)
```

예:

```python
text = await asyncio.to_thread(
    legacy_pdf_extractor.extract,
    file_path,
)
```

단, `to_thread()`는 만능 해결책이 아니다.

- Thread 수 증가
    
- Thread 안전성
    
- Context 전달
    
- 취소 처리
    
- CPU Bound 성능
    
- 메모리 사용
    

등을 고려해야 한다.

---

### 24. CPU Bound 작업은 어떻게 처리하는가?
로컬 모델 추론이나 대규모 문서 변환처럼 CPU 또는 GPU를 오래 사용하는 작업을 FastAPI Event Loop에서 직접 실행하면 API 응답성이 저하될 수 있다.

```text
FastAPI Request
   ↓
로컬 대형 모델 추론
   ↓
Event Loop 또는 Worker 장시간 점유
```

실무에서는 다음 구조를 고려할 수 있다.

```text
FastAPI
   ↓ 작업 요청 저장
Task Queue
   ↓
Worker Process
   ↓
AI 처리
   ↓
결과 저장
```

예:

- 별도 Worker
    
- Process Pool
    
- Task Queue
    
- 전용 Inference Server
    
- GPU Model Server
    

현재 Unit에서는 외부 AI Provider 호출에 초점을 맞추므로 Worker 시스템의 상세 구현은 다루지 않는다.

---

### 25. Timeout과 취소의 기초
#### 25.1 무기한 기다리면 안 된다
AI Provider 응답이 오지 않는 상황을 생각해 보자.

```text
FastAPI
   ↓ AI 요청
Provider 장애 또는 네트워크 문제
   ↓
응답 없음
```

무기한 기다리면 다음 문제가 생긴다.

- 연결 누적
    
- 메모리 점유
    
- 사용자 대기 증가
    
- 서버 처리량 저하
    
- 장애 확산
    

따라서 Timeout이 필요하다.

Python `asyncio`는 Task Timeout과 취소를 다루는 API를 제공한다.

---

#### 25.2 `asyncio.timeout()`
Python 3.11 이상:

```python
import asyncio


async with asyncio.timeout(30):
    result = await client.generate(
        instructions=instructions,
        input_text=text,
    )
```

30초를 초과하면 Timeout 관련 예외가 발생한다.

다만 OpenAI SDK 자체의 Timeout 설정과 애플리케이션 수준 Timeout은 목적이 조금 다를 수 있다.

```text
SDK Timeout
→ Provider HTTP 요청의 제한

Application Timeout
→ 전체 사용 사례 실행시간 제한
```

상세한 Timeout과 Retry 정책은 Unit 38에서 다룬다.

---

### 26. 사용자 요청 취소
사용자가 브라우저를 닫거나 요청을 취소할 수 있다.

```text
React 요청
   ↓
FastAPI
   ↓
AI Provider 호출 중
   ↓
사용자가 페이지 이동 또는 취소
```

이때 서버 작업을 계속 수행할지 취소할지는 서비스 정책에 따라 다르다.

#### 즉시 응답형 요청
사용자에게 결과를 바로 반환하는 요청이라면 연결 취소 시 내부 Task도 취소할 수 있다.

#### 비동기 Job
결과를 데이터베이스에 저장하고 나중에 조회하는 작업이라면 사용자가 연결을 끊어도 Worker가 계속 처리할 수 있다.

```text
HTTP 연결 수명
≠
백그라운드 Job 수명
```

중요한 작업을 단순한 Request Coroutine에만 묶어 두지 않아야 한다.

---

### 27. 여러 문서 요약 구현
#### 27.1 요청 모델
```python
from pydantic import BaseModel, Field


class BatchSummaryRequest(BaseModel):
    texts: list[str] = Field(
        min_length=1,
        max_length=20,
    )
```

한 번에 최대 20개로 제한한다.

---

#### 27.2 Service 구현
```python
import asyncio
from dataclasses import dataclass

from app.clients.base import TextGenerationClient


@dataclass(frozen=True)
class BatchSummaryResult:
    summaries: list[str]


class BatchSummaryService:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
    ) -> None:
        self._client = client

    async def summarize_many(
        self,
        texts: list[str],
    ) -> BatchSummaryResult:
        tasks = [
            self._client.generate(
                instructions=(
                    "원문의 핵심 내용을 "
                    "3문장 이내로 요약하세요."
                ),
                input_text=text,
            )
            for text in texts
        ]

        summaries = await asyncio.gather(
            *tasks
        )

        return BatchSummaryResult(
            summaries=list(summaries),
        )
```

Client에 공용 Semaphore가 적용되어 있다면 입력이 20개여도 설정된 개수까지만 동시에 Provider를 호출한다.

```text
20개 요청 생성
   ↓
Semaphore(5)
   ↓
동시에 최대 5개 실행
   ↓
완료되는 대로 다음 요청 실행
```

---

### 28. Batch API Router
```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_batch_summary_service,
)
from app.schemas.batch_summary import (
    BatchSummaryRequest,
    BatchSummaryResponse,
)
from app.services.batch_summary_service import (
    BatchSummaryService,
)


router = APIRouter(
    prefix="/batch-summaries",
    tags=["Batch Summaries"],
)


@router.post("")
async def create_batch_summaries(
    request: BatchSummaryRequest,
    service: Annotated[
        BatchSummaryService,
        Depends(get_batch_summary_service),
    ],
) -> BatchSummaryResponse:
    result = await service.summarize_many(
        request.texts
    )

    return BatchSummaryResponse(
        summaries=result.summaries,
        count=len(result.summaries),
    )
```

---

### 29. Batch 처리에서 고려해야 할 문제
#### 29.1 요청 개수 제한
```python
max_length=20
```

요청 하나가 수천 개의 AI 호출을 만들지 않게 한다.

---

#### 29.2 각 문서 크기 제한
목록 크기만 제한하면 부족하다.

```text
20개 × 각 100만 자
```

가 들어올 수 있다.

각 문자열에도 길이 검증이 필요하다.

```python
from typing import Annotated

from pydantic import StringConstraints


SummaryText = Annotated[
    str,
    StringConstraints(
        min_length=10,
        max_length=20_000,
        strip_whitespace=True,
    ),
]


class BatchSummaryRequest(BaseModel):
    texts: list[SummaryText] = Field(
        min_length=1,
        max_length=20,
    )
```

---

#### 29.3 부분 실패 정책
문서 세 개 중 하나가 실패할 수 있다.

```text
문서 A 성공
문서 B 실패
문서 C 성공
```

응답 정책을 정해야 한다.

예:

```json
{
  "results": [
    {
      "index": 0,
      "status": "completed",
      "summary": "..."
    },
    {
      "index": 1,
      "status": "failed",
      "error": "AI 요청 처리 실패"
    },
    {
      "index": 2,
      "status": "completed",
      "summary": "..."
    }
  ]
}
```

부분 실패를 구현하려면 각 Task 내부에서 예외를 결과 객체로 변환할 수 있다.

---

### 30. 부분 실패 구현 예시
```python
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class BatchItemResult:
    index: int
    status: Literal[
        "completed",
        "failed",
    ]
    summary: str | None = None
    error: str | None = None
```

```python
class BatchSummaryService:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
    ) -> None:
        self._client = client

    async def _summarize_one(
        self,
        *,
        index: int,
        text: str,
    ) -> BatchItemResult:
        try:
            summary = await self._client.generate(
                instructions=(
                    "문서의 핵심 내용을 요약하세요."
                ),
                input_text=text,
            )

            return BatchItemResult(
                index=index,
                status="completed",
                summary=summary,
            )

        except Exception:
            return BatchItemResult(
                index=index,
                status="failed",
                error="요약 처리에 실패했습니다.",
            )

    async def summarize_many(
        self,
        texts: list[str],
    ) -> list[BatchItemResult]:
        tasks = [
            self._summarize_one(
                index=index,
                text=text,
            )
            for index, text in enumerate(texts)
        ]

        return list(
            await asyncio.gather(*tasks)
        )
```

주의:

```text
except Exception:
```

에서 실제 예외를 완전히 무시하면 운영 분석이 어렵다.

실무에서는 내부 로그에 예외를 기록하되 사용자 응답에는 안전한 오류 메시지만 반환해야 한다.

Unit 38에서 예외 유형과 오류 변환을 자세히 다룬다.

---

### 31. 비동기 테스트
#### 31.1 지연 Fake Client
비동기 동작을 테스트하기 위해 지연되는 Fake Client를 만든다.

```python
import asyncio


class DelayedFakeTextGenerationClient:
    def __init__(
        self,
        *,
        delay_seconds: float,
    ) -> None:
        self._delay_seconds = delay_seconds

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        await asyncio.sleep(
            self._delay_seconds
        )

        return f"요약: {input_text}"
```

`time.sleep()`이 아니라 `asyncio.sleep()`을 사용한다.

---

#### 31.2 동시 실행 테스트
```python
import time

import pytest


@pytest.mark.asyncio
async def test_batch_summary_runs_concurrently() -> None:
    client = DelayedFakeTextGenerationClient(
        delay_seconds=0.1,
    )

    service = BatchSummaryService(
        client=client,
    )

    started_at = time.perf_counter()

    result = await service.summarize_many(
        [
            "첫 번째 문서 내용입니다.",
            "두 번째 문서 내용입니다.",
            "세 번째 문서 내용입니다.",
        ]
    )

    elapsed = time.perf_counter() - started_at

    assert len(result.summaries) == 3

    # 순차 실행이라면 약 0.3초가 필요하지만,
    # 동시 실행이면 그보다 짧아야 한다.
    assert elapsed < 0.25
```

시간 기반 테스트는 CI 환경의 부하에 따라 불안정할 수 있다.

따라서 너무 엄격한 시간 경계를 사용하지 않아야 한다.

더 안정적인 테스트는 동시 실행 중인 작업 수를 직접 기록하는 방식이다.

---

### 32. Semaphore 테스트용 Fake Client
```python
import asyncio


class ConcurrencyTrackingFakeClient:
    def __init__(self) -> None:
        self.current_concurrency = 0
        self.max_observed_concurrency = 0
        self._lock = asyncio.Lock()

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        async with self._lock:
            self.current_concurrency += 1

            self.max_observed_concurrency = max(
                self.max_observed_concurrency,
                self.current_concurrency,
            )

        try:
            await asyncio.sleep(0.05)
            return f"요약: {input_text}"

        finally:
            async with self._lock:
                self.current_concurrency -= 1
```

테스트:

```python
@pytest.mark.asyncio
async def test_concurrency_is_limited() -> None:
    base_client = ConcurrencyTrackingFakeClient()

    limited_client = (
        ConcurrencyLimitedTextGenerationClient(
            client=base_client,
            max_concurrency=2,
        )
    )

    await asyncio.gather(
        *[
            limited_client.generate(
                instructions="요약하세요.",
                input_text=f"문서 {index}",
            )
            for index in range(10)
        ]
    )

    assert (
        base_client.max_observed_concurrency
        <= 2
    )
```

---

### 33. Lifespan 테스트
FastAPI의 Lifespan을 테스트하려면 `TestClient`를 Context Manager로 사용하는 것이 중요하다.

```python
from fastapi.testclient import TestClient

from app.main import app


def test_application_lifespan() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
```

Context Manager 진입 시 Startup이 실행되고 종료 시 Shutdown이 실행된다.

```text
with TestClient(app)
   ↓ Startup
테스트 요청
   ↓
Context 종료
   ↓ Shutdown
```

---

### 34. Worker 수와 Client 공유 범위
Uvicorn 또는 운영 서버에서 Worker를 여러 개 실행할 수 있다.

```bash
uvicorn app.main:app --workers 4
```

각 Worker는 별도의 Process다.

따라서 각 Process마다 다음 자원이 따로 만들어진다.

```text
Worker 1 → Client + Semaphore(5)
Worker 2 → Client + Semaphore(5)
Worker 3 → Client + Semaphore(5)
Worker 4 → Client + Semaphore(5)
```

전체 최대 동시 호출은 개념적으로 다음처럼 늘어날 수 있다.

```text
Worker 4개 × Worker당 동시성 5
= 최대 20개
```

따라서 `AI_MAX_CONCURRENCY`는 Process 하나의 제한인지 전체 시스템 제한인지 명확히 이해해야 한다.

시스템 전체 제한이 필요하면 다음과 같은 외부 조정 장치가 필요할 수 있다.

- Queue
    
- Redis 기반 제한
    
- API Gateway Rate Limit
    
- 중앙 작업 Scheduler
    
- Provider 프로젝트별 Rate Limit
    
- 별도 AI Gateway
    

---

### 35. 동시성과 Rate Limit의 차이
두 개념은 다르다.

#### 동시성 제한
현재 실행 중인 요청 수를 제한한다.

```text
동시에 최대 5개
```

#### Rate Limit
일정 시간 동안의 요청 수를 제한한다.

```text
분당 최대 100개
```

예를 들어 각 요청이 매우 빠르면 동시성 5를 지켜도 분당 1,000번 호출할 수 있다.

따라서 실무에서는 두 정책이 모두 필요할 수 있다.

```text
Concurrency Limit
+
Rate Limit
+
Token/Cost Budget
```

---

### 36. Backpressure
#### 36.1 Backpressure란 무엇인가?
처리 시스템이 감당할 수 있는 양보다 요청이 빠르게 들어올 때 입력 속도를 제어하는 개념이다.

```text
들어오는 요청: 초당 100개
처리 가능 요청: 초당 10개
```

계속 받아들이기만 하면 대기 Queue가 증가한다.

```text
10
100
1,000
10,000 대기 요청
```

결과:

- 메모리 증가
    
- 응답시간 증가
    
- Timeout
    
- 장애 확산
    

Semaphore는 실행 동시성을 제한하지만 대기 요청 수 자체를 제한하지는 않는다.

실무에서는 다음 정책도 고려한다.

```text
대기 Queue 크기 제한
과부하 시 429 또는 503
비동기 Job Queue 전환
사용자별 호출 제한
우선순위 Queue
```

---

### 37. 즉시 처리 API와 Job API
#### 즉시 처리
```text
POST /summaries
   ↓
AI 호출 완료까지 연결 유지
   ↓
결과 반환
```

적합한 경우:

- 짧은 입력
    
- 빠른 응답
    
- 단순한 생성
    
- 사용자가 기다릴 수 있음
    

---

#### Job 처리
```text
POST /summary-jobs
   ↓
Job ID 즉시 반환
   ↓
Worker에서 AI 처리
   ↓
GET /summary-jobs/{id}
   ↓
상태와 결과 조회
```

응답:

```json
{
  "job_id": "job_123",
  "status": "pending"
}
```

적합한 경우:

- 긴 문서
    
- 여러 AI 호출
    
- OCR과 요약 결합
    
- 수십 초 이상 소요
    
- 재시도가 필요
    
- 결과를 저장해야 함
    
- 사용자가 연결을 유지할 필요 없음
    

이번 Unit에서는 즉시 처리 구조를 다룬다.

Job Queue는 이후 AI 서비스 아키텍처와 프로젝트 구현에서 확장할 수 있다.

---

### 38. 자주 발생하는 실수
#### 실수 1 — `async def`만 붙이면 비동기가 된다고 생각
```python
async def generate():
    requests.post(...)
```

##### 문제
내부 동기 HTTP 호출이 Event Loop를 막을 수 있다.

##### 해결
비동기 SDK 또는 비동기 HTTP Client를 사용한다.

---

#### 실수 2 — `await` 생략
```python
result = service.summarize(command)
```

##### 문제
최종 결과가 아니라 Coroutine 객체를 받는다.

##### 해결
```python
result = await service.summarize(command)
```

---

#### 실수 3 — Router에서 `asyncio.run()` 사용
```python
asyncio.run(service.summarize(...))
```

##### 문제
이미 실행 중인 Event Loop와 충돌할 수 있다.

##### 해결
Router에서는 `await`를 사용한다.

---

#### 실수 4 — `time.sleep()` 사용
```python
async def handler():
    time.sleep(5)
```

##### 문제
현재 Thread와 Event Loop를 막는다.

##### 해결
비동기 대기라면 다음을 사용한다.

```python
await asyncio.sleep(5)
```

---

#### 실수 5 — 모든 AI 요청을 무제한 동시 실행
```python
await asyncio.gather(
    *[call_ai(item) for item in items]
)
```

##### 문제
Rate Limit, 비용, 연결과 메모리 문제가 발생할 수 있다.

##### 해결
Semaphore, 요청 개수 제한, Queue를 사용한다.

---

#### 실수 6 — 의존 관계가 있는 작업을 동시에 실행
```text
검색 결과 필요
   ↓
답변 생성
```

을 동시에 시작한다.

##### 문제
답변 생성에 필요한 Context가 아직 없다.

##### 해결
의존 작업은 순차 실행한다.

---

#### 실수 7 — Client를 요청마다 생성하고 정리하지 않음
##### 문제
연결 관리가 비효율적이고 자원 정리가 누락될 수 있다.

##### 해결
애플리케이션 Lifespan에서 생성·재사용·종료한다.

---

#### 실수 8 — Semaphore를 요청마다 생성
##### 문제
전체 애플리케이션 동시성은 제한되지 않는다.

##### 해결
공용 Client와 공용 Semaphore를 애플리케이션 수준에서 공유한다.

---

#### 실수 9 — Worker 수를 고려하지 않음
##### 문제
Worker마다 Semaphore가 따로 존재하므로 전체 동시 호출이 예상보다 커질 수 있다.

##### 해결
Worker 수와 Process당 동시성의 곱을 계산하고 필요하면 중앙 제한 시스템을 둔다.

---

#### 실수 10 — 시간 기반 테스트를 지나치게 엄격하게 작성
```python
assert elapsed < 0.101
```

##### 문제
CI 부하와 운영체제 Scheduling에 따라 불안정하다.

##### 해결
충분한 여유를 두거나 실제 동시 실행 수를 추적한다.

---

#### 실수 11 — 외부 요청을 무기한 대기
##### 문제
장애 시 요청과 자원이 계속 누적된다.

##### 해결
SDK Timeout과 애플리케이션 Timeout을 적용한다.

---

#### 실수 12 — Client 종료를 누락
##### 문제
애플리케이션 종료 과정에서 네트워크 자원이 적절히 정리되지 않을 수 있다.

##### 해결
Lifespan의 종료 영역에서 `close()`를 호출한다.

---

### 39. 실무 Best Practice
#### 39.1 비동기 호출 체인을 끝까지 유지한다
```text
Router
  async/await
Service
  async/await
Client
  async/await
Async SDK
```

중간에 동기 네트워크 라이브러리를 섞지 않는다.

---

#### 39.2 독립적인 작업만 동시에 실행한다
```text
서로 결과가 필요 없음
→ gather 또는 TaskGroup 검토

앞 작업의 결과가 필요
→ 순차 실행
```

---

#### 39.3 동시 실행 수를 명시적으로 제한한다
```python
asyncio.Semaphore(
    settings.ai_max_concurrency
)
```

기본값을 안전하게 작게 시작하고 측정 후 조정한다.

---

#### 39.4 Client를 애플리케이션 수명 동안 재사용한다
```text
Startup → Client 생성
Request → Client 재사용
Shutdown → Client 종료
```

---

#### 39.5 공유 자원은 Lifespan에서 관리한다
- AI HTTP Client
    
- Database Pool
    
- Redis Client
    
- Model Loader
    
- Cache Client
    

등을 시작과 종료 시점에 관리한다.

---

#### 39.6 CPU Bound 작업을 Event Loop에서 직접 실행하지 않는다
다음으로 분리한다.

```text
Thread
Process
Worker
Inference Server
```

작업 특성에 맞는 방식을 선택한다.

---

#### 39.7 Batch 크기를 제한한다
```text
문서 개수 제한
각 문서 길이 제한
총 입력 크기 제한
예상 Token 제한
```

을 함께 적용한다.

---

#### 39.8 동시성 제한과 Rate Limit을 구분한다
```text
Concurrency
→ 동시에 몇 개?

Rate Limit
→ 일정 시간에 몇 개?

Cost Limit
→ 얼마까지?
```

세 정책을 각각 설계한다.

---

#### 39.9 과부하를 숨기지 않는다
처리할 수 없는 요청까지 모두 받아 무한 대기시키지 않는다.

필요하면 다음 응답을 고려한다.

```text
429 Too Many Requests
503 Service Unavailable
202 Accepted + Job ID
```

---

#### 39.10 취소와 Timeout을 정상 흐름으로 취급한다
취소와 Timeout은 예외적인 버그가 아니라 네트워크 서비스에서 발생 가능한 정상적인 운영 상황이다.

```text
사용자 취소
Provider 지연
네트워크 단절
서버 종료
```

에 대한 정책을 설계한다.

---

### 40. 실습
#### 실습 목표
- 비동기 AI 호출 체인을 구현한다.
    
- 독립적인 AI 작업을 동시에 실행한다.
    
- Semaphore로 Provider 동시 호출 수를 제한한다.
    
- AI Client를 애플리케이션 Lifespan에서 생성한다.
    
- 여러 요청에서 Client를 재사용한다.
    
- 애플리케이션 종료 시 Client를 정리한다.
    
- Batch 요청을 안전하게 처리한다.
    
- 실제 Provider 없이 동시성 동작을 테스트한다.
    

---

#### 실습 환경
```text
Python 3.12
FastAPI
Uvicorn
Pydantic 2
pydantic-settings
OpenAI Python SDK
pytest
pytest-asyncio
httpx
```

설치:

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  pydantic-settings \
  openai \
  pytest \
  pytest-asyncio \
  httpx
```

---

#### 실습 프로젝트 구조
```text
app/
├── api/
│   └── v1/
│       ├── summaries.py
│       └── batch_summaries.py
│
├── clients/
│   ├── base.py
│   ├── fake_client.py
│   ├── limited_client.py
│   └── openai_client.py
│
├── core/
│   ├── config.py
│   ├── container.py
│   ├── dependencies.py
│   └── lifespan.py
│
├── schemas/
│   ├── summary.py
│   └── batch_summary.py
│
├── services/
│   ├── summary_service.py
│   └── batch_summary_service.py
│
└── main.py

tests/
├── clients/
│   └── test_limited_client.py
├── services/
│   └── test_batch_summary_service.py
└── test_lifespan.py
```

---

### 41. 실습 절차
#### 1단계 — 설정 추가
```python
ai_max_concurrency: int = Field(
    default=5,
    ge=1,
    le=100,
)
```

`.env.example`:

```env
AI_MAX_CONCURRENCY=5
```

---

#### 2단계 — 동시성 제한 Client 작성
```text
app/clients/limited_client.py
```

```python
import asyncio

from app.clients.base import TextGenerationClient


class ConcurrencyLimitedTextGenerationClient:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
        max_concurrency: int,
    ) -> None:
        if max_concurrency < 1:
            raise ValueError(
                "max_concurrency는 1 이상이어야 합니다."
            )

        self._client = client
        self._semaphore = asyncio.Semaphore(
            max_concurrency
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        async with self._semaphore:
            return await self._client.generate(
                instructions=instructions,
                input_text=input_text,
            )
```

---

#### 3단계 — Container 작성
```text
app/core/container.py
```

```python
from dataclasses import dataclass

from app.clients.base import TextGenerationClient


@dataclass
class ApplicationContainer:
    text_generation_client: TextGenerationClient
    base_text_generation_client: (
        TextGenerationClient
    )
```

---

#### 4단계 — Lifespan 작성
```text
app/core/lifespan.py
```

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.clients.base import TextGenerationClient
from app.clients.fake_client import (
    FakeTextGenerationClient,
)
from app.clients.limited_client import (
    ConcurrencyLimitedTextGenerationClient,
)
from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.core.config import get_settings
from app.core.container import ApplicationContainer


def create_base_client() -> TextGenerationClient:
    settings = get_settings()

    if settings.ai_provider == "fake":
        return FakeTextGenerationClient(
            response_text="Fake AI 요약 결과",
        )

    if settings.ai_provider == "openai":
        if settings.openai_api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY가 필요합니다."
            )

        if settings.openai_model is None:
            raise RuntimeError(
                "OPENAI_MODEL이 필요합니다."
            )

        return OpenAITextGenerationClient(
            api_key=(
                settings.openai_api_key.get_secret_value()
            ),
            model=settings.openai_model,
            timeout_seconds=settings.ai_timeout_seconds,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )

    raise RuntimeError(
        f"지원하지 않는 Provider: "
        f"{settings.ai_provider}"
    )


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings = get_settings()

    base_client = create_base_client()

    limited_client = (
        ConcurrencyLimitedTextGenerationClient(
            client=base_client,
            max_concurrency=(
                settings.ai_max_concurrency
            ),
        )
    )

    app.state.container = ApplicationContainer(
        text_generation_client=limited_client,
        base_text_generation_client=base_client,
    )

    try:
        yield

    finally:
        close_method = getattr(
            base_client,
            "close",
            None,
        )

        if close_method is not None:
            await close_method()
```

---

#### 5단계 — Dependency 수정
```text
app/core/dependencies.py
```

```python
from typing import Annotated

from fastapi import Depends, Request

from app.clients.base import TextGenerationClient
from app.core.container import ApplicationContainer
from app.services.batch_summary_service import (
    BatchSummaryService,
)
from app.services.summary_service import SummaryService


def get_container(
    request: Request,
) -> ApplicationContainer:
    return request.app.state.container


def get_text_generation_client(
    container: Annotated[
        ApplicationContainer,
        Depends(get_container),
    ],
) -> TextGenerationClient:
    return container.text_generation_client


def get_summary_service(
    client: Annotated[
        TextGenerationClient,
        Depends(get_text_generation_client),
    ],
) -> SummaryService:
    return SummaryService(
        client=client,
    )


def get_batch_summary_service(
    client: Annotated[
        TextGenerationClient,
        Depends(get_text_generation_client),
    ],
) -> BatchSummaryService:
    return BatchSummaryService(
        client=client,
    )
```

---

#### 6단계 — Batch Schema 작성
```text
app/schemas/batch_summary.py
```

```python
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)


SummaryText = Annotated[
    str,
    StringConstraints(
        min_length=10,
        max_length=20_000,
        strip_whitespace=True,
    ),
]


class BatchSummaryRequest(BaseModel):
    texts: list[SummaryText] = Field(
        min_length=1,
        max_length=20,
    )


class BatchSummaryResponse(BaseModel):
    summaries: list[str]
    count: int
```

---

#### 7단계 — Batch Service 작성
```text
app/services/batch_summary_service.py
```

```python
import asyncio
from dataclasses import dataclass

from app.clients.base import TextGenerationClient


@dataclass(frozen=True)
class BatchSummaryResult:
    summaries: list[str]


class BatchSummaryService:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
    ) -> None:
        self._client = client

    async def summarize_many(
        self,
        texts: list[str],
    ) -> BatchSummaryResult:
        tasks = [
            self._client.generate(
                instructions=(
                    "원문의 핵심 내용을 "
                    "3문장 이내로 요약하세요. "
                    "원문에 없는 사실을 "
                    "추가하지 마세요."
                ),
                input_text=text,
            )
            for text in texts
        ]

        summaries = await asyncio.gather(
            *tasks
        )

        return BatchSummaryResult(
            summaries=list(summaries),
        )
```

---

#### 8단계 — Batch Router 작성
```text
app/api/v1/batch_summaries.py
```

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_batch_summary_service,
)
from app.schemas.batch_summary import (
    BatchSummaryRequest,
    BatchSummaryResponse,
)
from app.services.batch_summary_service import (
    BatchSummaryService,
)


router = APIRouter(
    prefix="/batch-summaries",
    tags=["Batch Summaries"],
)


@router.post(
    "",
    response_model=BatchSummaryResponse,
)
async def create_batch_summaries(
    request: BatchSummaryRequest,
    service: Annotated[
        BatchSummaryService,
        Depends(get_batch_summary_service),
    ],
) -> BatchSummaryResponse:
    result = await service.summarize_many(
        request.texts
    )

    return BatchSummaryResponse(
        summaries=result.summaries,
        count=len(result.summaries),
    )
```

---

#### 9단계 — Main 수정
```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.v1.batch_summaries import (
    router as batch_summaries_router,
)
from app.api.v1.summaries import (
    router as summaries_router,
)
from app.core.config import get_settings
from app.core.lifespan import lifespan


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(
    summaries_router,
    prefix="/api/v1",
)

app.include_router(
    batch_summaries_router,
    prefix="/api/v1",
)
```

---

#### 10단계 — Fake Provider 실행
`.env`:

```env
AI_PROVIDER=fake
AI_MAX_CONCURRENCY=2
```

실행:

```bash
uvicorn app.main:app --reload
```

요청:

```json
{
  "texts": [
    "FastAPI는 Python 기반의 API 서버를 구현할 수 있도록 지원하는 프레임워크이며 타입 힌트를 활용한 요청 검증 기능을 제공합니다.",
    "비동기 처리는 외부 네트워크 응답을 기다리는 동안 다른 요청을 처리할 수 있도록 하여 I/O 중심 서버의 처리 효율을 높입니다.",
    "Semaphore는 동시에 실행할 수 있는 비동기 작업 수를 제한하여 외부 AI Provider와 서버 자원을 보호할 수 있습니다."
  ]
}
```

예상 응답:

```json
{
  "summaries": [
    "Fake AI 요약 결과",
    "Fake AI 요약 결과",
    "Fake AI 요약 결과"
  ],
  "count": 3
}
```

---

### 42. 예상 결과
#### 단일 요약 요청
```text
Router
  ↓ await
SummaryService
  ↓ await
공용 Limited Client
  ↓ Semaphore 획득
OpenAI/Fake Client
```

#### 여러 요청
```text
Task 1 ─┐
Task 2 ─┼→ Semaphore(2) → Provider
Task 3 ─┘        ↓
              2개 실행
              1개 대기
```

#### 애플리케이션 수명주기
```text
Startup
  ↓ Client 생성
Request 처리
  ↓ Client 재사용
Shutdown
  ↓ Client 종료
```

---

### 43. 실습 확인
-  Router부터 Provider Client까지 `async`와 `await`가 이어지는가?
    
-  비동기 함수를 호출할 때 `await`를 사용했는가?
    
-  비동기 함수 안에서 `requests`나 `time.sleep()`을 사용하지 않는가?
    
-  독립적인 Batch 작업을 `asyncio.gather()`로 실행하는가?
    
-  Batch 요청 개수에 상한이 있는가?
    
-  각 입력 텍스트 길이에도 상한이 있는가?
    
-  Semaphore로 AI 동시 호출 수를 제한하는가?
    
-  Semaphore가 요청마다 생성되지 않는가?
    
-  AI Client를 Lifespan에서 한 번 생성하는가?
    
-  여러 HTTP 요청이 같은 Client를 재사용하는가?
    
-  애플리케이션 종료 시 Client를 닫는가?
    
-  테스트에서 `asyncio.sleep()` 기반 Fake를 사용하는가?
    
-  Worker 수에 따라 전체 동시성이 증가할 수 있음을 이해했는가?
    
-  Timeout과 취소 정책이 필요함을 설명할 수 있는가?
    

---

### 44. 응용 과제
#### 과제 1 — Summary와 Keyword 동시 생성
다음 API를 만든다.

```text
POST /api/v1/document-analyses
```

응답:

```json
{
  "summary": "...",
  "keywords": [
    "FastAPI",
    "비동기",
    "AI Backend"
  ]
}
```

두 작업을 `asyncio.gather()`로 동시에 실행한다.

---

#### 과제 2 — 부분 실패 Batch
각 문서 결과에 다음 상태를 포함한다.

```json
{
  "index": 0,
  "status": "completed",
  "summary": "..."
}
```

또는

```json
{
  "index": 1,
  "status": "failed",
  "error": "요약 처리에 실패했습니다."
}
```

한 문서 실패가 전체 요청 실패로 이어지지 않도록 구현한다.

---

#### 과제 3 — 동시성 추적 테스트
`ConcurrencyTrackingFakeClient`를 이용해 다음을 확인한다.

```python
assert max_observed_concurrency <= 2
```

---

#### 과제 4 — Application Timeout
Batch 전체 처리에 10초 제한을 적용한다.

```python
async with asyncio.timeout(10):
    result = await service.summarize_many(
        request.texts
    )
```

Timeout 발생 시 현재는 오류가 어떻게 노출되는지 확인한다.

안전한 HTTP 오류 변환은 Unit 38에서 구현한다.

---

#### 과제 5 — Worker별 동시성 계산
다음 설정을 가정한다.

```text
Worker = 4
AI_MAX_CONCURRENCY = 5
```

시스템 전체에서 동시에 실행될 수 있는 Provider 요청의 이론적 최대치를 계산하고 운영 위험을 설명한다.

---

#### 과제 6 — Job API 설계
긴 문서를 위한 API 계약을 설계한다.

```text
POST /api/v1/summary-jobs
GET /api/v1/summary-jobs/{job_id}
```

구현은 하지 않고 다음만 정의한다.

- Request Model
    
- Response Model
    
- Job Status
    
- 전체 데이터 흐름
    
- 즉시 처리 API와의 차이
    

---

### 45. 이해도 확인
#### 질문 1
AI Backend에서 비동기 처리가 중요한 이유는 무엇인가?

##### 모범 답안
외부 AI Provider 호출은 CPU 계산보다 네트워크와 모델 응답을 기다리는 시간이 길 수 있기 때문이다. 비동기 처리를 사용하면 한 요청이 응답을 기다리는 동안 Event Loop가 다른 요청을 처리할 수 있어 I/O 중심 서버의 동시 처리 효율을 높일 수 있다.

---

#### 질문 2
`async def`를 사용하면 내부의 모든 코드가 자동으로 비동기가 되는가?

##### 모범 답안
아니다. `async def` 내부에서 `requests.post()`나 `time.sleep()` 같은 동기 블로킹 함수를 호출하면 Event Loop를 막을 수 있다. 비동기 처리 효과를 얻으려면 내부 I/O 호출도 비동기 SDK나 비동기 라이브러리를 사용해야 한다.

---

#### 질문 3
비동기 함수를 호출할 때 `await`를 생략하면 무엇을 받는가?

##### 모범 답안
최종 결과가 아니라 Coroutine 객체를 받는다. Coroutine을 실제로 실행하고 결과가 준비될 때까지 기다리려면 `await`해야 한다.

---

#### 질문 4
동시성과 병렬성은 무엇이 다른가?

##### 모범 답안
동시성은 여러 작업이 같은 기간에 번갈아 진행되는 구조이고, 병렬성은 여러 작업이 실제로 같은 시점에 실행되는 구조다. 외부 AI API 호출에서는 네트워크 대기 시간을 활용하는 동시성이 중요하다.

---

#### 질문 5
두 AI 작업을 `asyncio.gather()`로 동시에 실행해도 되는 기준은 무엇인가?

##### 모범 답안
두 작업이 서로의 결과를 필요로 하지 않아야 한다. 작업 B가 작업 A의 결과를 사용해야 한다면 순차 실행해야 하고, 서로 독립적이라면 동시 실행을 검토할 수 있다.

---

#### 질문 6
Semaphore가 필요한 이유는 무엇인가?

##### 모범 답안
비동기 요청을 무제한으로 동시에 시작하면 Provider Rate Limit, 순간 비용, 연결 수, 메모리 사용과 장애가 증가할 수 있기 때문이다. Semaphore는 동시에 실행할 수 있는 AI 호출 수를 제한한다.

---

#### 질문 7
Semaphore를 요청마다 만들면 어떤 문제가 있는가?

##### 모범 답안
각 HTTP 요청 내부의 동시성만 제한되고 애플리케이션 전체의 동시 호출 수는 제한되지 않는다. 여러 사용자가 동시에 요청하면 요청별 제한이 합쳐져 실제 Provider 호출 수가 크게 증가할 수 있다.

---

#### 질문 8
AI Client를 Lifespan에서 생성하는 이유는 무엇인가?

##### 모범 답안
애플리케이션 시작 시 Client를 한 번 만들고 여러 요청에서 재사용하며, 종료 시 명시적으로 정리하기 위해서다. 이를 통해 객체 생성 정책, 공용 Semaphore와 네트워크 자원 수명주기를 한곳에서 관리할 수 있다.

---

#### 질문 9
CPU Bound 작업을 단순히 `async def` 안에 넣으면 왜 해결되지 않는가?

##### 모범 답안
CPU Bound 작업은 네트워크를 기다리는 것이 아니라 CPU를 계속 사용한다. 따라서 Event Loop의 실행 Thread를 장시간 점유할 수 있으며, Thread, Process, Worker 또는 별도 Inference Server로 분리해야 할 수 있다.

---

#### 질문 10
Worker가 네 개이고 각 Worker의 Semaphore가 5라면 전체 동시 호출은 어떻게 될 수 있는가?

##### 모범 답안
각 Worker가 별도 Process이고 별도의 Semaphore를 가지므로 이론적으로 최대 20개의 Provider 호출이 동시에 실행될 수 있다. 전체 시스템 제한이 필요하면 Process 외부의 중앙 제한 장치가 필요하다.

---

### 46. 핵심 내용 정리
#### 핵심 1
외부 AI API 호출은 대표적인 I/O Bound 작업이다.

```text
요청 전송
  ↓
응답 대기
  ↓
다른 Task 실행 가능
```

---

#### 핵심 2
`async def`는 Coroutine을 정의하고 `await`는 대기 중 실행 제어권을 Event Loop에 돌려줄 수 있는 지점이다.

```text
Coroutine
  ↓ await
Event Loop
  ↓
다른 Task
```

---

#### 핵심 3
비동기 호출 체인은 끝까지 유지해야 한다.

```text
Router
  ↓ await
Service
  ↓ await
Client
  ↓ await
Async Provider SDK
```

---

#### 핵심 4
독립적인 AI 작업은 동시에 실행할 수 있다.

```python
await asyncio.gather(
    summarize(),
    extract_keywords(),
)
```

의존 관계가 있다면 순차 실행한다.

---

#### 핵심 5
비동기는 무제한 동시 실행을 의미하지 않는다.

```text
Concurrency
   ↓
Semaphore로 제한
```

---

#### 핵심 6
AI Client와 Semaphore는 애플리케이션 수준에서 공유할 수 있다.

```text
Startup
  ↓
공용 Client + Semaphore
  ↓
여러 Request
```

---

#### 핵심 7
FastAPI Lifespan은 공유 자원의 생성과 정리를 담당한다.

```text
Startup → 생성
Request → 사용
Shutdown → 정리
```

---

#### 핵심 8
비동기 함수 안에서 동기 블로킹 코드를 사용하면 Event Loop를 막을 수 있다.

```text
async def
+
동기 Blocking I/O
=
비동기 효과 저하
```

---

#### 핵심 9
Batch API에는 동시성 제한뿐 아니라 요청 개수와 입력 크기 제한이 필요하다.

```text
문서 수
각 문서 크기
총 Token
동시 호출 수
```

을 함께 관리한다.

---

#### 핵심 10
긴 AI 작업은 HTTP 요청 안에서 계속 기다리게 하기보다 Job Queue 구조가 더 적절할 수 있다.

```text
POST Job
  ↓
Job ID
  ↓
Worker 처리
  ↓
결과 조회
```

---

### 47. 한 문장으로 설명하기
> FastAPI의 비동기 AI 요청 처리는 `async`와 `await`를 이용해 AI Provider 응답을 기다리는 동안 다른 요청을 처리하고, 공용 비동기 Client와 Semaphore를 Lifespan에서 관리하여 연결 재사용과 동시성 제한을 함께 적용하는 구조다.

---

### FastAPI Part 5. AI Backend Integration

## Module 40. Prompt와 Request Model 설계


### Module 실습 예제

- [예제 1: prompt_builder.py](examples/module_40/prompt_builder.py) — System 규칙과 사용자 입력을 분리해 Prompt를 구성합니다.
- [예제 2: prompt_request_model.py](examples/module_40/prompt_request_model.py) — Pydantic으로 Prompt 요청의 허용 범위를 검증합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 사용자 입력과 시스템 지시를 분리하고 요청 계약을 명확히 한다.
- **오늘 만드는 것:** Prompt Template과 AI Request Model을 설계한다.
- **AI 플랫폼의 위치:** 검증된 입력이 Provider 메시지로 바뀌는 지점이다.
- **실무에서 많이 하는 실수:** 문자열 연결만으로 Prompt Injection이 해결된다고 생각한다.
- **5분 실습:** 입력·권한·출력 검증을 포함한 방어 계층을 적는다.

> AIKOS Phase 1

```
Part 5. AI Backend Integration

Unit 32. AI Backend Integration
Unit 33. AI Provider 설정
Unit 34. OpenAI API 연동
Unit 35. AI Service Layer
Unit 36. Async AI Processing
👉 Unit 37. Prompt & Request Model
Unit 38. Error / Retry / Timeout
Unit 39. Streaming Response
```

---

### 이번 Unit의 목표
이번 Unit이 끝나면 다음 질문에 답할 수 있어야 한다.

- Prompt는 왜 코드와 분리해야 하는가?
    
- Prompt Engineering과 Backend는 어떤 관계인가?
    
- Request Model은 왜 필요한가?
    
- DTO와 Command는 무엇이 다른가?
    
- Prompt Template은 어떻게 설계하는가?
    
- Prompt Injection은 무엇인가?
    
- Prompt를 어디에 저장하는 것이 좋은가?
    
- Prompt를 테스트 가능한 구조로 만드는 방법은 무엇인가?
    
- Prompt Builder는 어떤 역할을 하는가?
    
- AI Backend에서 Prompt를 어떻게 관리하는가?
    

---

### 1. Why
#### AI API를 호출하는 것만으로는 서비스가 아니다.
많은 사람들이 AI 서비스를 다음처럼 생각한다.

```python
client.responses.create(
    model="gpt-5",
    input=user_input
)
```

그리고 끝이다.

하지만 실제 서비스는 그렇지 않다.

실제 AI 서비스는

```
사용자 입력

↓

검증

↓

Prompt 생성

↓

AI 호출

↓

응답 검증

↓

후처리

↓

Response 반환
```

이다.

AI 호출은 이 중 한 단계일 뿐이다.

---

#### Prompt는 프로그램이다.
많은 사람이 Prompt를 단순한 문자열이라고 생각한다.

하지만 실무에서는 다르다.

Prompt는

```
AI에게

무엇을

어떻게

얼마나

어떤 형식으로

답할지

정의하는 프로그램
```

이라고 생각한다.

즉

Prompt는

AI의 비즈니스 로직이다.

---

예를 들어

같은 입력이라도

Prompt가 다르면

결과가 완전히 달라진다.

사용자 입력

```
FastAPI 설명해줘
```

Prompt A

```
친절하게 설명
```

↓

입문자 대상의 친절한 설명

Prompt B

```
3줄 요약
```

↓

짧은 요약

Prompt C

```
학생에게 강의하듯 설명
```

↓

강의 형태

Prompt D

```
JSON으로 출력
```

↓

JSON 출력

---

즉

Prompt가

AI의 동작을 결정한다.

---

### AI 서비스 구조
```
React

↓

FastAPI

↓

Request Model

↓

Prompt Builder

↓

Prompt

↓

OpenAI

↓

Response Parser

↓

Response Model
```

Prompt Builder가

AI Backend의 핵심이다.

---

### Prompt는 문자열이 아니다.
처음 학습할 때는

```python
prompt = f"""
{user_input}
"""
```

정도로 작성한다.

하지만

실무에서는

```
Prompt

=

Instructions

+

Context

+

User Input

+

Output Format

+

Constraint
```

이다.

즉

Prompt는

여러 조각으로 만들어진다.

---

### Prompt의 구성 요소
예를 들어

문서 요약 서비스

```
Instructions

↓

너는 문서 요약 전문가다.

↓

Context

↓

회사 내부 문서이다.

↓

Constraint

↓

3문장 이내

↓

Output

↓

Markdown

↓

User Input

↓

문서 내용
```

최종 Prompt

```
너는 문서 요약 전문가다.

회사 내부 문서를

3문장 이내로

Markdown 형식으로

요약하라.

문서

...

```

---

Prompt를

이렇게 분리해야

유지보수가 쉬워진다.

---

### Prompt Template
Prompt는

매번 새로 작성하지 않는다.

Template을 만든다.

예

```
당신은 {role} 입니다.

다음 내용을

{style} 방식으로

{length} 길이로

작성하세요.

입력

{text}
```

실제 값

```
role

=

문서 요약 전문가

style

=

학생에게 설명

length

=

3문장

text

=

...
```

↓

최종 Prompt 생성

---

Prompt는

HTML Template처럼 생각하면 쉽다.

```
Template

+

Data

=

Prompt
```

---

### Backend에서 Prompt를 직접 문자열로 만들면?
예

```python
prompt = f"""
너는...

{text}

...
"""
```

처음에는 괜찮다.

하지만

Prompt가

100줄

200줄

500줄

되면

코드를 읽을 수 없어진다.

---

실무에서는

Prompt를

분리한다.

예

```
app/

prompts/

summary.py

chat.py

translate.py

review.py

```

또는

```
prompts/

summary.md

```

처럼 관리하기도 한다.

---

### Prompt Builder
Prompt는

Builder가 만든다.

```
Request

↓

Builder

↓

Prompt

↓

Client

↓

OpenAI
```

Builder의 역할은

```
Prompt 생성
```

이다.

예

```python
builder.build(command)
```

↓

Prompt 반환

---

Builder는

AI 호출을 하지 않는다.

OpenAI도 모른다.

Prompt만 만든다.

---

예

```python
class SummaryPromptBuilder:

    def build(self, command):
        ...
```

---

Service

↓

Builder

↓

Prompt

↓

Client

↓

OpenAI

역할이 분리된다.

---

### Builder가 필요한 이유
Builder가 없으면

Service가

```
Prompt 생성

+

AI 호출

+

응답 처리
```

를 모두 담당한다.

SRP가 깨진다.

Builder를 만들면

Service는

```
Builder에게 Prompt 요청

↓

Client 호출

↓

응답 반환
```

만 담당한다.

---

### Request Model은 왜 필요한가?
React에서

```json
{
  "text":"...",
  "length":"short",
  "tone":"friendly"
}
```

를 보낸다.

FastAPI는

Request Model로 받는다.

```python
class SummaryRequest(BaseModel):

    text:str

    length:str

    tone:str
```

이 모델은

HTTP용이다.

---

Service는

HTTP를 몰라야 한다.

그래서

Command를 만든다.

```
SummaryRequest

↓

SummaryCommand

↓

SummaryService
```

---

Request

=

HTTP

Command

=

Business

이다.

---

왜 분리하는가?

나중에

CLI

Batch

Worker

에서도

SummaryService를

사용할 수 있기 때문이다.

---

CLI

↓

SummaryCommand

↓

Service

Worker

↓

SummaryCommand

↓

Service

HTTP가 없어도

Service는 그대로 동작한다.

---

### Command는 Immutable가 좋다.
예

```python
@dataclass(frozen=True)

class SummaryCommand:

    text:str

    tone:str

    length:str
```

Immutable는

실수로 변경되는 것을 막는다.

---

### Prompt Builder 입력
Builder는

Request가 아니라

Command를 받는다.

```
HTTP

↓

Request

↓

Command

↓

Prompt Builder
```

이렇게 해야

Builder도

HTTP와 분리된다.

---

### Prompt Builder 결과
Builder는

Prompt 객체를 반환한다.

단순 문자열보다

객체가 좋다.

예

```python
Prompt(
    instructions=...,
    input=...
)
```

이렇게 하면

OpenAI Responses API에도

그대로 연결하기 쉽다.

---

### 현재 구조
```
Router

↓

Request Model

↓

Command

↓

SummaryService

↓

Prompt Builder

↓

TextGenerationClient

↓

OpenAI
```

이 구조가

AI Backend에서 가장 많이 사용하는 구조이다.

---

### 여기까지의 핵심
학생은 이제 다음을 설명할 수 있어야 한다.

- Prompt는 AI의 비즈니스 로직이다.
    
- Prompt는 문자열이 아니라 설계 대상이다.
    
- Prompt Template을 사용해야 한다.
    
- Prompt Builder가 Prompt를 생성한다.
    
- Request Model과 Command를 분리해야 한다.
    
- Builder는 Command를 입력받는다.
    
- Service는 Prompt 생성과 AI 호출을 분리해야 한다.
    
- Prompt는 향후 테스트와 재사용을 고려하여 별도 계층으로 관리한다.
    

---

다음 Unit(38)에서는 **AI 서비스에서 반드시 필요한 Timeout, Retry, 예외 처리, Provider 오류 변환, 안정적인 Error Handling 구조**를 구현하여 실제 운영 가능한 AI Backend 구조를 완성한다.

---

### FastAPI Part 5. AI Backend Integration

## Module 41. AI 오류·Timeout·Retry 처리


### Module 실습 예제

- [예제 1: timeout.py](examples/module_41/timeout.py) — asyncio.timeout으로 Provider 응답 대기 시간을 제한합니다.
- [예제 2: retry.py](examples/module_41/retry.py) — 재시도 가능한 오류만 제한된 횟수로 재시도합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 느리거나 불안정한 Provider 실패를 예측 가능한 응답으로 바꾼다.
- **오늘 만드는 것:** Timeout·Retry·오류 변환 정책을 구현한다.
- **AI 플랫폼의 위치:** AI Client와 Service의 장애 경계다.
- **실무에서 많이 하는 실수:** 모든 오류를 재시도해 비용과 지연을 키우거나 무한 재시도한다.
- **5분 실습:** 재시도 가능 오류와 즉시 실패 오류를 분류한다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI Provider 호출은 왜 일반 함수 호출보다 실패 가능성이 높은가?
    
- Timeout은 무엇이며 왜 반드시 설정해야 하는가?
    
- Retry는 모든 오류에 적용해도 되는가?
    
- 재시도 가능한 오류와 재시도하면 안 되는 오류는 무엇이 다른가?
    
- OpenAI SDK의 오류를 Service와 Router에 그대로 전달하면 왜 안 되는가?
    
- Provider Exception을 Application Exception으로 변환하는 이유는 무엇인가?
    
- 오류를 HTTP 상태 코드로 어떻게 변환하는가?
    
- `429`, `502`, `503`, `504`는 어떤 상황에서 사용하는가?
    
- 지수 백오프와 Jitter는 무엇인가?
    
- SDK Retry와 애플리케이션 Retry를 중복 적용하면 어떤 문제가 생기는가?
    
- 사용자에게 보여줄 오류와 내부 로그에 남길 오류는 어떻게 구분하는가?
    
- Request ID와 Provider Request ID는 왜 필요한가?
    
- Retry 중복 실행으로 비용이나 데이터 중복이 발생하는 것을 어떻게 막는가?
    
- Circuit Breaker와 Fallback은 언제 필요한가?
    

---

### 2. 문제 이해 — Why
#### 2.1 지금까지의 코드는 성공만 가정했다
Unit 35와 Unit 36에서는 다음과 같은 AI 호출 코드를 작성했다.

```python
result = await client.generate(
    instructions=instructions,
    input_text=input_text,
)
```

이 코드는 AI Provider가 정상적으로 응답한다면 잘 동작한다.

하지만 실제 네트워크 서비스에서는 다음 상황이 발생할 수 있다.

```text
API Key 오류
권한 부족
잘못된 모델 이름
잘못된 요청 형식
입력 크기 초과
Provider Rate Limit
사용량 한도 초과
네트워크 연결 실패
DNS 오류
TLS 연결 오류
응답 지연
Provider 내부 오류
Provider 점검
응답 내용 누락
사용자 요청 취소
```

즉, 실제 AI Backend는 다음 구조로 생각해야 한다.

```text
AI 호출
 ├─ 성공
 ├─ 일시적인 실패
 ├─ 영구적인 실패
 ├─ 잘못된 요청
 └─ 응답 여부를 알 수 없는 실패
```

---

#### 2.2 외부 API는 우리 코드 밖에 있다
다음 코드는 우리 애플리케이션 내부의 계산이다.

```python
total = price * quantity
```

입력 타입과 값이 정상이라면 결과를 예측하기 쉽다.

반면 AI Provider 호출은 여러 시스템을 통과한다.

```text
FastAPI
  ↓
운영체제 네트워크
  ↓
인터넷
  ↓
Provider Gateway
  ↓
인증 시스템
  ↓
요청 Queue
  ↓
AI Model Server
  ↓
응답 반환
```

이 경로 중 하나만 문제가 생겨도 호출이 실패할 수 있다.

따라서 외부 API 호출은 다음 전제를 가져야 한다.

> 외부 시스템 호출은 언젠가 실패한다.

오류 처리는 부가 기능이 아니라 AI 연동 기능의 일부다.

---

#### 2.3 오류를 그대로 사용자에게 보여주면 안 된다
잘못된 구현:

```python
try:
    result = await client.generate(...)
except Exception as exc:
    return {
        "error": str(exc),
    }
```

이 방식은 다음 문제를 만들 수 있다.

- Provider 내부 오류 메시지 노출
    
- 모델 이름 노출
    
- Request URL 노출
    
- SDK 객체 정보 노출
    
- 서버 구성 정보 노출
    
- 일관되지 않은 응답 구조
    
- 모든 오류가 HTTP 200으로 반환
    
- 프론트엔드의 오류 처리 어려움
    

예를 들어 다음 응답은 잘못된 API 설계다.

```json
{
  "error": "Connection error."
}
```

HTTP 상태가 `200 OK`라면 클라이언트는 요청 성공으로 인식할 수 있다.

---

#### 2.4 모든 오류를 Retry하면 안 된다
다음 오류를 생각해 보자.

```text
API Key가 잘못됨
```

같은 Key로 다시 요청해도 성공하지 않는다.

```text
1차 요청 → 인증 실패
2차 요청 → 인증 실패
3차 요청 → 인증 실패
```

Retry는 문제를 해결하지 못하고 응답 시간만 늘린다.

반면 다음 오류는 잠시 후 성공할 수 있다.

```text
일시적인 네트워크 단절
Provider의 순간적인 500 오류
일시적인 Rate Limit
```

따라서 오류를 구분해야 한다.

```text
재시도 가능한 오류
        vs
재시도하면 안 되는 오류
```

---

### 3. 개념 이해 — Concept
### 3.1 오류 계층
AI Backend에서는 오류를 세 계층으로 구분할 수 있다.

```text
Provider Error
      ↓ 변환
Application Error
      ↓ 변환
HTTP Error Response
```

---

#### Provider Error
OpenAI SDK나 외부 AI Client가 발생시키는 오류다.

예:

```text
APITimeoutError
APIConnectionError
RateLimitError
AuthenticationError
BadRequestError
InternalServerError
```

현재 OpenAI Python SDK는 연결 오류, Timeout, HTTP 상태 오류 등을 예외 클래스로 구분하며, `APITimeoutError`, `APIConnectionError`, `RateLimitError`, `AuthenticationError`, `BadRequestError`, `InternalServerError` 등의 예외 타입을 노출한다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

---

#### Application Error
우리 애플리케이션이 이해하는 오류다.

예:

```text
AIProviderTimeoutError
AIProviderUnavailableError
AIProviderRateLimitError
AIAuthenticationError
AIInvalidRequestError
AIEmptyResponseError
```

Application Service는 OpenAI의 예외 이름을 알 필요가 없다.

---

#### HTTP Error Response
클라이언트에 반환하는 API 응답이다.

예:

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다.",
    "request_id": "req_123"
  }
}
```

---

### 3.2 왜 중간에 Application Error가 필요한가?
OpenAI Exception을 바로 FastAPI Router까지 전달한다고 생각해 보자.

```text
OpenAI SDK
   ↓
OpenAI RateLimitError
   ↓
Router
```

이 구조에서는 Router가 OpenAI SDK를 알아야 한다.

```text
except openai.RateLimitError:
    ...
```

Provider를 Ollama나 다른 서비스로 교체하면 Router도 수정해야 한다.

권장 구조:

```text
OpenAI RateLimitError
        ↓ Client에서 변환
AIProviderRateLimitError
        ↓ Handler에서 변환
HTTP 429 또는 503
```

Provider가 바뀌어도 Application Error 계약은 유지할 수 있다.

```text
OpenAI RateLimitError ─┐
Ollama Overload Error ─┼→ AIProviderRateLimitError
기타 Provider 오류 ───┘
```

---

### 3.3 Timeout이란 무엇인가?
Timeout은 작업이 완료되기를 기다리는 최대 시간을 제한하는 정책이다.

```text
AI 요청 시작
   ↓
최대 30초 대기
   ├─ 30초 안에 응답 → 정상 처리
   └─ 30초 초과 → Timeout 오류
```

Timeout이 없으면 Provider가 응답하지 않을 때 요청이 장시간 대기할 수 있다.

```text
대기 요청 증가
   ↓
연결과 메모리 점유
   ↓
새로운 요청 지연
   ↓
전체 서비스 장애
```

---

### 3.4 Timeout의 종류
AI Backend에는 여러 수준의 Timeout이 존재할 수 있다.

#### 연결 Timeout
Provider 서버와 연결을 만드는 데 허용하는 시간이다.

```text
FastAPI
   ↓ 연결 시도
AI Provider
```

#### 읽기 Timeout
연결 후 응답 데이터를 기다리는 시간이다.

```text
연결 완료
   ↓
응답 대기
```

#### 전체 요청 Timeout
AI 호출 전체에 허용되는 시간이다.

```text
연결
+
요청 전송
+
Provider 처리
+
응답 수신
```

#### Application Timeout
Repository 조회, Prompt 생성, AI 호출, 결과 저장까지 전체 사용 사례에 허용되는 시간이다.

```text
전체 SummaryService 실행 시간
```

---

### 3.5 SDK Timeout과 Application Timeout
OpenAI Client 설정:

```python
AsyncOpenAI(
    api_key=api_key,
    timeout=30.0,
)
```

이는 Provider HTTP 요청에 대한 Timeout이다.

Application Service에서도 전체 작업 시간을 제한할 수 있다.

```python
import asyncio


async with asyncio.timeout(40):
    result = await service.summarize(command)
```

구조:

```text
Application Timeout: 40초
 ├─ DB 조회
 ├─ Prompt 구성
 ├─ AI SDK Timeout: 30초
 └─ 결과 저장
```

일반적으로 내부 작업의 Timeout은 외부 전체 Timeout보다 작아야 한다.

```text
Provider Timeout
<
Application Timeout
<
Gateway 또는 Client Timeout
```

예:

```text
AI Provider SDK: 25초
FastAPI 사용 사례: 30초
Reverse Proxy: 35초
React 요청: 40초
```

이 값은 예시이며 실제 서비스 요구사항과 인프라에 맞게 결정해야 한다.

---

### 3.6 Retry란 무엇인가?
Retry는 실패한 작업을 다시 시도하는 정책이다.

```text
1차 호출 실패
   ↓ 잠시 대기
2차 호출 실패
   ↓ 더 오래 대기
3차 호출 성공
```

Retry는 일시적인 오류를 회복하는 데 유용하다.

그러나 다음 비용이 있다.

- 응답 시간 증가
    
- AI 호출 비용 증가 가능성
    
- Provider 부하 증가
    
- 중복 작업 가능성
    
- 장애 확대 가능성
    
- 사용자 취소 이후에도 요청 지속 가능성
    

---

### 3.7 재시도 가능한 오류
일반적으로 다음 오류는 제한적으로 Retry를 검토할 수 있다.

```text
일시적인 연결 실패
일부 Timeout
HTTP 408
HTTP 409의 일부 상황
HTTP 429 Rate Limit
HTTP 500
HTTP 502
HTTP 503
HTTP 504
```

하지만 실제 Retry 가능 여부는 Provider의 공식 정책과 요청 특성을 확인해야 한다.

---

### 3.8 재시도하면 안 되는 오류
다음 오류는 보통 같은 요청을 그대로 반복해도 해결되지 않는다.

```text
잘못된 API Key
권한 부족
존재하지 않는 모델
잘못된 요청 형식
입력 검증 실패
지원하지 않는 Parameter
금지된 콘텐츠
요청 크기 초과
```

예:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Validation Error
```

이 경우 Retry보다 요청이나 설정을 수정해야 한다.

---

### 4. OpenAI SDK의 기본 Retry 이해
OpenAI Python SDK는 특정 오류를 기본적으로 자동 재시도하며, 기본 재시도 횟수는 두 번이다. 공식 SDK 문서에는 연결 오류, `408`, `409`, `429`, 그리고 `5xx` 오류가 기본 재시도 대상이라고 설명되어 있다. Timeout 역시 `APITimeoutError`로 발생하며 기본적으로 재시도 대상에 포함된다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

따라서 다음 코드는 내부적으로 한 번만 요청한다고 단정할 수 없다.

```python
response = await client.responses.create(...)
```

개념적으로 다음과 같이 동작할 수 있다.

```text
애플리케이션 호출 1번
        ↓
SDK 최초 요청
        ↓ 실패
SDK 자동 Retry
        ↓ 실패
SDK 자동 Retry
```

---

#### 4.1 SDK Retry 설정
Client 수준에서 재시도 횟수를 지정할 수 있다.

```python
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key=api_key,
    max_retries=2,
)
```

재시도를 비활성화할 수도 있다.

```python
client = AsyncOpenAI(
    api_key=api_key,
    max_retries=0,
)
```

요청별로 옵션을 다르게 사용할 수도 있다.

```python
response = await client.with_options(
    max_retries=1,
    timeout=20.0,
).responses.create(
    model=model,
    input=input_text,
)
```

현재 SDK의 정확한 기본값과 지원 옵션은 배포 전에 사용하는 SDK 버전의 공식 문서를 다시 확인해야 한다.

---

### 4.2 SDK Retry와 Application Retry 중복 문제
다음 구조를 생각해 보자.

```text
Application Retry 3회
        ↓
각 호출마다 SDK Retry 2회
```

최악의 경우 실제 요청 횟수는 예상보다 크게 늘어난다.

개념적으로:

```text
Application 최초 시도
 ├─ SDK 최초 요청
 ├─ SDK Retry 1
 └─ SDK Retry 2

Application Retry 1
 ├─ SDK 최초 요청
 ├─ SDK Retry 1
 └─ SDK Retry 2

Application Retry 2
 ├─ SDK 최초 요청
 ├─ SDK Retry 1
 └─ SDK Retry 2
```

총 9번의 Provider 요청이 발생할 수 있다.

따라서 Retry 책임을 명확히 해야 한다.

권장 방향:

```text
단순 Provider 통신 오류
→ SDK Retry 활용

업무 흐름 전체 재시도
→ Application Layer에서 신중하게 설계

두 계층에서 모두 Retry
→ 전체 시도 횟수와 Timeout Budget 계산
```

---

### 5. 지수 백오프
#### 5.1 즉시 Retry의 문제
잘못된 Retry:

```text
실패
→ 즉시 재시도
→ 즉시 재시도
→ 즉시 재시도
```

Provider가 과부하 상태라면 수많은 Client가 동시에 Retry하면서 더 큰 부하를 만들 수 있다.

이를 Retry Storm이라고 부를 수 있다.

---

#### 5.2 고정 대기
```text
실패
→ 1초 대기
→ 재시도
→ 1초 대기
→ 재시도
```

단순하지만 많은 Client가 같은 간격으로 재시도하면 다시 요청이 몰릴 수 있다.

---

#### 5.3 지수 백오프
재시도할수록 대기 시간을 늘린다.

```text
1차 실패 → 1초
2차 실패 → 2초
3차 실패 → 4초
4차 실패 → 8초
```

기본식:

```text
delay = base_delay × 2^attempt
```

---

#### 5.4 Jitter
모든 서버가 정확히 같은 시간에 Retry하지 않도록 무작위 시간을 추가한다.

```text
기본 대기 2초
+
무작위 0~0.5초
```

예:

```text
Server A → 2.13초 후
Server B → 2.42초 후
Server C → 2.07초 후
```

이렇게 요청 시점을 분산한다.

---

### 6. Application Exception 설계
파일:

```text
app/core/exceptions.py
```

```python
class AIApplicationError(Exception):
    """AI 기능에서 발생하는 애플리케이션 오류의 기본 클래스."""

    error_code = "AI_APPLICATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.retryable = retryable


class AIProviderTimeoutError(AIApplicationError):
    error_code = "AI_PROVIDER_TIMEOUT"

    def __init__(
        self,
        message: str = "AI 응답 시간이 초과되었습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=True,
        )


class AIProviderConnectionError(AIApplicationError):
    error_code = "AI_PROVIDER_CONNECTION_ERROR"

    def __init__(
        self,
        message: str = "AI Provider에 연결할 수 없습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=True,
        )


class AIProviderRateLimitError(AIApplicationError):
    error_code = "AI_PROVIDER_RATE_LIMIT"

    def __init__(
        self,
        message: str = "AI 요청이 일시적으로 제한되었습니다.",
        *,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(
            message,
            retryable=True,
        )
        self.retry_after_seconds = retry_after_seconds


class AIProviderUnavailableError(AIApplicationError):
    error_code = "AI_PROVIDER_UNAVAILABLE"

    def __init__(
        self,
        message: str = "AI 서비스를 일시적으로 사용할 수 없습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=True,
        )


class AIAuthenticationError(AIApplicationError):
    error_code = "AI_AUTHENTICATION_ERROR"

    def __init__(
        self,
        message: str = "AI Provider 인증에 실패했습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=False,
        )


class AIPermissionError(AIApplicationError):
    error_code = "AI_PERMISSION_ERROR"

    def __init__(
        self,
        message: str = "AI Provider 사용 권한이 없습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=False,
        )


class AIInvalidRequestError(AIApplicationError):
    error_code = "AI_INVALID_REQUEST"

    def __init__(
        self,
        message: str = "AI 요청 형식이 올바르지 않습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=False,
        )


class AIEmptyResponseError(AIApplicationError):
    error_code = "AI_EMPTY_RESPONSE"

    def __init__(
        self,
        message: str = "AI가 유효한 응답을 반환하지 않았습니다.",
    ) -> None:
        super().__init__(
            message,
            retryable=False,
        )
```

---

### 7. Provider 오류를 Client에서 변환
파일:

```text
app/clients/openai_client.py
```

```python
import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

from app.core.exceptions import (
    AIAuthenticationError,
    AIEmptyResponseError,
    AIInvalidRequestError,
    AIPermissionError,
    AIProviderConnectionError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)


logger = logging.getLogger(__name__)


class OpenAITextGenerationClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
        max_retries: int,
    ) -> None:
        self._model = model
        self._max_output_tokens = max_output_tokens

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        try:
            response = await self._client.responses.create(
                model=self._model,
                instructions=instructions,
                input=input_text,
                max_output_tokens=self._max_output_tokens,
            )

        except APITimeoutError as exc:
            logger.warning(
                "OpenAI request timed out",
                exc_info=exc,
            )
            raise AIProviderTimeoutError() from exc

        except APIConnectionError as exc:
            logger.warning(
                "OpenAI connection failed",
                exc_info=exc,
            )
            raise AIProviderConnectionError() from exc

        except RateLimitError as exc:
            logger.warning(
                "OpenAI rate limit reached",
                exc_info=exc,
            )
            raise AIProviderRateLimitError() from exc

        except AuthenticationError as exc:
            logger.error(
                "OpenAI authentication failed",
                exc_info=exc,
            )
            raise AIAuthenticationError() from exc

        except PermissionDeniedError as exc:
            logger.error(
                "OpenAI permission denied",
                exc_info=exc,
            )
            raise AIPermissionError() from exc

        except BadRequestError as exc:
            logger.warning(
                "OpenAI rejected the request",
                exc_info=exc,
            )
            raise AIInvalidRequestError() from exc

        except InternalServerError as exc:
            logger.warning(
                "OpenAI internal server error",
                exc_info=exc,
            )
            raise AIProviderUnavailableError() from exc

        except APIStatusError as exc:
            logger.exception(
                "Unexpected OpenAI API status error",
            )
            raise AIProviderUnavailableError() from exc

        output_text = response.output_text.strip()

        if not output_text:
            raise AIEmptyResponseError()

        return output_text

    async def close(self) -> None:
        await self._client.close()
```

---

### 8. 예외 순서가 중요한 이유
다음 예외는 더 넓은 예외보다 먼저 처리해야 한다.

```text
except RateLimitError:
    ...

except APIStatusError:
    ...
```

`RateLimitError`가 `APIStatusError` 계열이라면 넓은 예외를 먼저 작성할 경우 세부 오류가 먼저 잡히지 않을 수 있다.

잘못된 순서:

```text
except APIStatusError:
    ...

except RateLimitError:
    ...
```

원칙:

```text
구체적인 Exception
        ↓ 먼저
일반적인 Exception
        ↓ 나중
```

---

### 9. 알 수 없는 Exception 처리
다음처럼 Client에서 모든 예외를 잡을 수도 있다.

```text
except Exception as exc:
    raise AIProviderUnavailableError() from exc
```

하지만 무조건 모든 예외를 변환하면 코드 버그도 Provider 오류로 숨겨질 수 있다.

예:

```python
response.ouput_text
```

필드 이름 오타로 `AttributeError`가 발생했는데 이를 `AIProviderUnavailableError`로 바꾸면 실제 코드 버그를 찾기 어려워진다.

권장 방향:

- 예상 가능한 Provider 예외만 변환한다.
    
- 예상하지 못한 Exception은 상위 공통 Handler에서 기록한다.
    
- 프로그래밍 오류를 Provider 장애로 위장하지 않는다.
    

---

### 10. HTTP 오류 모델 설계
파일:

```text
app/schemas/error.py
```

```python
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
```

응답 예:

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다.",
    "retryable": true,
    "request_id": "req_8f42a1"
  }
}
```

---

### 11. HTTP 상태 코드 매핑
Application Error를 HTTP로 변환한다.

|Application Error|권장 HTTP 상태 예시|의미|
|---|--:|---|
|`AIInvalidRequestError`|400|AI Provider에 전달할 요청 자체가 잘못됨|
|`AIAuthenticationError`|500 또는 503|서버의 Provider Credential 설정 문제|
|`AIPermissionError`|500 또는 503|서버의 Provider 권한 설정 문제|
|`AIProviderRateLimitError`|429 또는 503|요청량 제한 또는 Provider 용량 제한|
|`AIProviderConnectionError`|502 또는 503|외부 Provider 연결 실패|
|`AIProviderUnavailableError`|503|Provider 일시 장애|
|`AIProviderTimeoutError`|504|외부 Provider 응답 Timeout|
|`AIEmptyResponseError`|502|Provider가 유효하지 않은 응답 반환|

---

#### 11.1 상태 코드는 정책에 따라 달라질 수 있다
예를 들어 Provider의 Rate Limit이 발생했을 때 사용자 개인의 호출 제한이 원인이라면 `429 Too Many Requests`가 자연스럽다.

하지만 우리 서버 전체의 Provider 할당량이나 Provider 과부하가 원인이라면 사용자의 잘못이 아니므로 `503 Service Unavailable`을 사용할 수도 있다.

```text
사용자별 제한 초과
→ 429

Provider 또는 서버 전체 한도
→ 503 검토
```

따라서 단순히 Provider 상태 코드를 그대로 전달하지 않고 우리 API의 의미에 맞게 결정한다.

---

### 12. FastAPI Exception Handler
파일:

```text
app/api/exception_handlers.py
```

```python
import logging
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AIApplicationError,
    AIAuthenticationError,
    AIEmptyResponseError,
    AIInvalidRequestError,
    AIPermissionError,
    AIProviderConnectionError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)


logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    existing_request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    if existing_request_id:
        return str(existing_request_id)

    return f"req_{uuid4().hex[:12]}"


def status_code_for_exception(
    exc: AIApplicationError,
) -> int:
    if isinstance(exc, AIInvalidRequestError):
        return status.HTTP_400_BAD_REQUEST

    if isinstance(
        exc,
        (
            AIAuthenticationError,
            AIPermissionError,
        ),
    ):
        return status.HTTP_503_SERVICE_UNAVAILABLE

    if isinstance(exc, AIProviderRateLimitError):
        return status.HTTP_429_TOO_MANY_REQUESTS

    if isinstance(exc, AIProviderConnectionError):
        return status.HTTP_502_BAD_GATEWAY

    if isinstance(exc, AIProviderTimeoutError):
        return status.HTTP_504_GATEWAY_TIMEOUT

    if isinstance(exc, AIProviderUnavailableError):
        return status.HTTP_503_SERVICE_UNAVAILABLE

    if isinstance(exc, AIEmptyResponseError):
        return status.HTTP_502_BAD_GATEWAY

    return status.HTTP_500_INTERNAL_SERVER_ERROR


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(AIApplicationError)
    async def handle_ai_application_error(
        request: Request,
        exc: AIApplicationError,
    ) -> JSONResponse:
        request_id = get_request_id(request)
        status_code = status_code_for_exception(exc)

        logger.warning(
            "AI application error",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "retryable": exc.retryable,
                "status_code": status_code,
            },
        )

        headers: dict[str, str] = {
            "X-Request-ID": request_id,
        }

        if isinstance(
            exc,
            AIProviderRateLimitError,
        ):
            retry_after = exc.retry_after_seconds

            if retry_after is not None:
                headers["Retry-After"] = str(
                    max(1, int(retry_after))
                )

        return JSONResponse(
            status_code=status_code,
            headers=headers,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "retryable": exc.retryable,
                    "request_id": request_id,
                }
            },
        )
```

FastAPI는 `@app.exception_handler(...)`를 이용해 사용자 정의 Exception을 원하는 응답으로 변환할 수 있으며, `HTTPException`과 요청 검증 오류에 대한 기본 Handler도 제공한다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/ "Handling Errors"))

---

### 13. Main에 Handler 등록
파일:

```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.exception_handlers import (
    register_exception_handlers,
)
from app.api.v1.summaries import (
    router as summaries_router,
)
from app.core.config import get_settings
from app.core.lifespan import lifespan


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(
    summaries_router,
    prefix="/api/v1",
)
```

---

### 14. HTTPException을 Service에서 사용하지 않는 이유
FastAPI의 `HTTPException`은 API 요청을 중단하고 지정한 HTTP 오류를 반환하는 예외다. FastAPI 공식 문서에서도 `HTTPException`은 `return`하는 값이 아니라 `raise`하는 예외라고 설명한다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/ "Handling Errors"))

Router에서 간단한 HTTP 오류를 발생시키는 것은 가능하다.

```python
raise HTTPException(
    status_code=404,
    detail="문서를 찾을 수 없습니다.",
)
```

하지만 Application Service나 Provider Client에서 직접 사용하면 계층이 HTTP에 종속된다.

잘못된 구조:

```text
OpenAI Client
   ↓
HTTPException(504)
```

권장 구조:

```text
OpenAI Client
   ↓
AIProviderTimeoutError
   ↓
FastAPI Exception Handler
   ↓
HTTP 504
```

---

### 15. Request ID
#### 15.1 왜 필요한가?
사용자가 다음 오류를 받았다고 하자.

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다."
  }
}
```

같은 시간에 수백 개의 요청이 있었다면 어떤 요청의 로그를 봐야 하는지 찾기 어렵다.

Request ID를 추가한다.

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다.",
    "request_id": "req_7a82f190b4d1"
  }
}
```

로그:

```text
request_id=req_7a82f190b4d1
error_code=AI_PROVIDER_TIMEOUT
```

사용자 응답과 서버 로그를 연결할 수 있다.

---

#### 15.2 Request ID Middleware
파일:

```text
app/api/middleware.py
```

```python
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        incoming_request_id = request.headers.get(
            "X-Request-ID"
        )

        request_id = (
            incoming_request_id
            or f"req_{uuid4().hex[:12]}"
        )

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response
```

등록:

```python
app.add_middleware(RequestIDMiddleware)
```

주의:

외부 사용자가 전달한 Request ID를 그대로 신뢰할지, 형식과 길이를 검증할지 정책이 필요하다.

---

### 16. Provider Request ID
외부 Provider가 응답이나 오류에 고유 Request ID를 제공하는 경우 이를 내부 로그에 기록하면 Provider 지원팀과 장애를 분석할 때 도움이 된다.

```text
우리 Request ID
+
Provider Request ID
```

예:

```text
request_id=req_123
provider_request_id=provider_abc
```

사용자에게 Provider Request ID를 반드시 노출할 필요는 없다.

로그나 관찰성 시스템에 저장할 수 있다.

주의할 점:

- Provider SDK 버전에 따라 접근 방식이 달라질 수 있다.
    
- 존재하지 않을 수 있다.
    
- 응답 전체를 로그에 저장하지 않는다.
    
- API Key나 Prompt가 함께 기록되지 않게 한다.
    

---

### 17. 로그 수준 설계
#### DEBUG
개발 중 상세 흐름을 확인한다.

```text
Prompt Builder 선택
모델 Alias
Retry 횟수
처리 단계
```

운영에서 민감한 Prompt 전체를 DEBUG로 남기지 않도록 주의한다.

#### INFO
정상적인 주요 이벤트다.

```text
AI 요청 완료
처리 시간
모델
입력 크기
출력 크기
```

#### WARNING
일시적이거나 예상 가능한 장애다.

```text
Timeout
Rate Limit
일시적 Provider 오류
Retry 발생
```

#### ERROR
설정이나 권한 문제처럼 운영자의 조치가 필요한 오류다.

```text
인증 실패
권한 실패
모델 설정 오류
```

#### EXCEPTION
예상하지 못한 코드 오류와 Stack Trace가 필요한 상황이다.

```python
logger.exception(
    "Unexpected AI processing error"
)
```

---

### 18. 로그에 남기면 안 되는 정보
다음 값은 기본적으로 로그에 그대로 기록하지 않는 것이 좋다.

```text
API Key
Authorization Header
전체 Prompt
사용자 개인정보
문서 원문 전체
모델의 민감한 응답
파일 원본
비밀번호
Session Token
```

대신 다음 메타데이터를 기록한다.

```text
request_id
user_id 또는 익명화된 식별자
provider
model alias
input_character_count
estimated_token_count
output_character_count
duration_ms
retry_count
error_code
HTTP status
```

---

### 19. Retry Decorator 구현
SDK Retry 외에 Provider 독립적인 Retry가 필요한 경우 Decorator Client를 만들 수 있다.

파일:

```text
app/clients/retry_client.py
```

```python
import asyncio
import random

from app.clients.base import TextGenerationClient
from app.core.exceptions import (
    AIApplicationError,
)


class RetryingTextGenerationClient:
    def __init__(
        self,
        *,
        client: TextGenerationClient,
        max_attempts: int,
        base_delay_seconds: float,
        max_delay_seconds: float,
        jitter_seconds: float,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts는 1 이상이어야 합니다."
            )

        self._client = client
        self._max_attempts = max_attempts
        self._base_delay_seconds = (
            base_delay_seconds
        )
        self._max_delay_seconds = (
            max_delay_seconds
        )
        self._jitter_seconds = jitter_seconds

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        last_error: AIApplicationError | None = None

        for attempt in range(self._max_attempts):
            try:
                return await self._client.generate(
                    instructions=instructions,
                    input_text=input_text,
                )

            except AIApplicationError as exc:
                last_error = exc

                is_last_attempt = (
                    attempt == self._max_attempts - 1
                )

                if (
                    not exc.retryable
                    or is_last_attempt
                ):
                    raise

                delay = min(
                    self._base_delay_seconds
                    * (2**attempt),
                    self._max_delay_seconds,
                )

                jitter = random.uniform(
                    0,
                    self._jitter_seconds,
                )

                await asyncio.sleep(
                    delay + jitter
                )

        if last_error is not None:
            raise last_error

        raise RuntimeError(
            "Retry 실행 상태가 올바르지 않습니다."
        )
```

---

### 20. Retry Client의 위치
전체 Client 조립 순서가 중요하다.

```text
Service
   ↓
ConcurrencyLimitedClient
   ↓
RetryingClient
   ↓
OpenAIClient
```

또는

```text
Service
   ↓
RetryingClient
   ↓
ConcurrencyLimitedClient
   ↓
OpenAIClient
```

두 구조는 동작 의미가 다르다.

---

#### 20.1 Semaphore 안에서 Retry
```text
Semaphore 획득
   ↓
최초 호출
   ↓ 실패
대기
   ↓
Retry
   ↓
Semaphore 반환
```

장점:

- 하나의 업무 요청이 Retry 전체 동안 호출 슬롯을 유지한다.
    

단점:

- Backoff 대기 중에도 Semaphore를 점유할 수 있다.
    
- 다른 요청이 불필요하게 대기할 수 있다.
    

---

#### 20.2 Retry마다 Semaphore 획득
```text
최초 호출 전 Semaphore 획득
   ↓
실패 후 반환
   ↓ Backoff
Retry 전 다시 Semaphore 획득
```

장점:

- Backoff 대기 중에는 슬롯을 점유하지 않는다.
    

단점:

- 재시도 요청도 새롭게 경쟁한다.
    
- 요청 완료 순서가 달라질 수 있다.
    

일반적으로 Backoff 중 Semaphore를 점유하지 않도록 다음 구조를 고려할 수 있다.

```text
Service
   ↓
RetryingClient
   ↓
ConcurrencyLimitedClient
   ↓
Provider Client
```

각 Retry 시도마다 Semaphore를 획득한다.

---

### 21. SDK Retry와 Custom Retry 조합
Application Retry를 직접 구현한다면 SDK Retry를 줄이거나 비활성화해 전체 정책을 명확히 할 수 있다.

예:

```python
OpenAITextGenerationClient(
    max_retries=0,
)
```

그 위에:

```python
RetryingTextGenerationClient(
    client=openai_client,
    max_attempts=3,
    base_delay_seconds=0.5,
    max_delay_seconds=4.0,
    jitter_seconds=0.2,
)
```

반대로 SDK Retry만 사용한다면 Custom Retry Client를 추가하지 않는다.

권장 원칙:

```text
Retry 정책은 가능한 한 한 계층에서 명확하게 관리한다.
```

---

### 22. Retry Budget
Retry 횟수만 결정하면 부족하다.

전체 허용 시간을 계산해야 한다.

예:

```text
요청 Timeout = 10초
최대 3회 시도
Backoff = 1초 + 2초
```

최악의 경우:

```text
10초 + 1초 + 10초 + 2초 + 10초
= 33초
```

Application Timeout이 20초라면 세 번째 시도까지 완료되지 못할 수 있다.

따라서 다음을 함께 설계한다.

```text
시도별 Timeout
재시도 횟수
Backoff
전체 Application Timeout
Gateway Timeout
Client Timeout
```

---

### 23. Retry와 중복 비용
AI 요청이 Timeout으로 끝났다고 해서 Provider가 실제로 처리를 시작하지 않았다고 단정할 수 없다.

```text
Provider가 응답 생성 완료
   ↓
네트워크 응답 전달 중 실패
   ↓
우리 서버는 Timeout으로 판단
   ↓
Retry
```

결과적으로 같은 AI 요청이 두 번 처리되고 비용이 두 번 발생할 수 있다.

따라서 Retry는 무료가 아니다.

특히 다음 작업은 더 신중해야 한다.

- 이미지 생성
    
- 긴 문서 처리
    
- 고비용 모델 호출
    
- Tool Calling
    
- 외부 시스템 변경
    
- 결과 저장과 결제 연결
    

---

### 24. Idempotency
#### 24.1 Idempotency란 무엇인가?
같은 요청을 여러 번 수행해도 최종 상태가 한 번 수행한 것과 같도록 만드는 성질이다.

문서 요약 결과 저장:

```text
같은 요청을 두 번 수행
   ↓
요약 결과 두 개 생성
```

중복이 문제가 될 수 있다.

---

#### 24.2 Idempotency Key
클라이언트가 요청마다 고유 Key를 보낸다.

```http
Idempotency-Key: summary-doc-10-user-7-v1
```

서버는 이전에 처리한 Key인지 확인한다.

```text
처음 요청
→ 처리 후 결과 저장

같은 Key 재요청
→ 기존 결과 반환
```

우리 API 수준에서 구현할 수 있다.

```text
Idempotency Key
   ↓
Database 또는 Cache 확인
   ├─ 존재 → 기존 결과
   └─ 없음 → AI 호출 후 저장
```

Provider 자체의 Idempotency 지원 여부와 방법은 Provider 공식 문서를 따로 확인해야 한다.

---

### 25. Application Timeout 구현
Service 전체에 Timeout을 적용할 수 있다.

```python
import asyncio

from app.core.exceptions import (
    AIProviderTimeoutError,
)


class TimedSummaryService:
    def __init__(
        self,
        *,
        service: SummaryService,
        timeout_seconds: float,
    ) -> None:
        self._service = service
        self._timeout_seconds = timeout_seconds

    async def summarize(
        self,
        command: SummaryCommand,
    ) -> SummaryResult:
        try:
            async with asyncio.timeout(
                self._timeout_seconds
            ):
                return await self._service.summarize(
                    command
                )

        except TimeoutError as exc:
            raise AIProviderTimeoutError(
                "요약 처리 제한 시간을 초과했습니다."
            ) from exc
```

주의:

Application Timeout이 발생했다고 해서 반드시 Provider Timeout만 원인인 것은 아니다.

```text
DB 조회 지연
Semaphore 대기
Retry Backoff
Provider 호출
결과 저장
```

전체 시간이 포함될 수 있다.

따라서 예외 이름을 더 일반적으로 만들 수도 있다.

```text
AIProcessingTimeoutError
```

---

### 26. 오류 응답에 내부 원인을 노출하지 않는다
내부 로그:

```text
AuthenticationError:
Incorrect API key provided
```

사용자 응답:

```json
{
  "error": {
    "code": "AI_SERVICE_CONFIGURATION_ERROR",
    "message": "AI 서비스를 일시적으로 사용할 수 없습니다.",
    "retryable": false,
    "request_id": "req_123"
  }
}
```

왜 구분하는가?

- API Key 상태 노출 방지
    
- Provider 정보 노출 방지
    
- 공격자에게 구성 정보 제공 방지
    
- 사용자에게 필요한 행동만 전달
    
- 내부 구현 변경에도 API 계약 유지
    

---

### 27. 사용자 메시지 설계
좋지 않은 메시지:

```text
APIStatusError 429 from upstream
```

사용자는 무엇을 해야 하는지 알기 어렵다.

좋은 메시지:

```text
요청이 일시적으로 많습니다.
잠시 후 다시 시도해 주세요.
```

개발자용 정보는 Error Code와 Request ID로 제공한다.

```json
{
  "code": "AI_PROVIDER_RATE_LIMIT",
  "message": "요청이 일시적으로 많습니다. 잠시 후 다시 시도해 주세요.",
  "retryable": true,
  "request_id": "req_123"
}
```

---

### 28. Retry-After Header
재시도 가능 시간이 알려진 경우 HTTP Header로 전달할 수 있다.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 5
```

React는 이를 읽고 5초 후 재시도를 안내할 수 있다.

하지만 다음에 주의한다.

- Provider Header를 무조건 그대로 전달하지 않는다.
    
- 우리 서버의 정책에 맞게 값의 상한을 둔다.
    
- 자동 Retry와 사용자 안내를 구분한다.
    
- 여러 계층의 Retry가 겹치지 않게 한다.
    

---

### 29. Fallback Provider
OpenAI 호출 실패 시 다른 Provider를 사용할 수 있다.

```text
Primary Provider
   ↓ 실패
Secondary Provider
   ↓ 성공
```

Decorator 예시:

```python
from app.clients.base import TextGenerationClient
from app.core.exceptions import (
    AIApplicationError,
)


class FallbackTextGenerationClient:
    def __init__(
        self,
        *,
        primary: TextGenerationClient,
        fallback: TextGenerationClient,
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        try:
            return await self._primary.generate(
                instructions=instructions,
                input_text=input_text,
            )

        except AIApplicationError as exc:
            if not exc.retryable:
                raise

            return await self._fallback.generate(
                instructions=instructions,
                input_text=input_text,
            )
```

---

#### 29.1 Fallback의 문제
Provider만 바꾸면 항상 같은 결과가 나오는 것은 아니다.

다음이 다를 수 있다.

- Prompt 해석
    
- 출력 형식
    
- 모델 성능
    
- Context 크기
    
- 지원 옵션
    
- 안전 정책
    
- Token 비용
    
- 응답 속도
    
- Structured Output 지원
    

Fallback은 단순한 Client 교체가 아니라 품질 정책이다.

---

### 30. Circuit Breaker
#### 30.1 문제
Provider가 장애 중인데 모든 요청이 계속 호출된다.

```text
Request A → 실패
Request B → 실패
Request C → 실패
Request D → 실패
```

Retry까지 적용하면 장애 Provider에 더 많은 요청이 몰릴 수 있다.

---

#### 30.2 Circuit Breaker 개념
일정 횟수 이상 연속 실패하면 잠시 호출을 차단한다.

```text
Closed
→ 정상 호출

실패 누적
→ Open

Open
→ Provider 호출 없이 즉시 실패

일정 시간 후
→ Half-Open

시험 호출 성공
→ Closed

시험 호출 실패
→ Open
```

---

#### 30.3 언제 필요한가?
- 외부 Provider 장애가 반복될 때
    
- 호출량이 많을 때
    
- 장애 전파를 막아야 할 때
    
- Fallback Provider가 있을 때
    
- 빠른 실패가 긴 Timeout보다 나을 때
    

초기 프로젝트에서는 지나친 복잡성이 될 수 있으므로 Retry와 Timeout을 먼저 정확히 구현한 후 도입한다.

---

### 31. 오류 처리 전체 Architecture
```text
React
  ↓
FastAPI Router
  ↓
SummaryService
  ↓
Retry Client
  ↓
Concurrency Limited Client
  ↓
OpenAI Client
  ↓
OpenAI SDK
  ↓
OpenAI API
```

오류 흐름:

```text
OpenAI RateLimitError
        ↓
OpenAI Client
        ↓ 변환
AIProviderRateLimitError
        ↓
Retry Client
        ├─ Retry 가능 → Backoff 후 재시도
        └─ 최종 실패
              ↓
FastAPI Exception Handler
              ↓
HTTP 429 ErrorResponse
              ↓
React
```

---

### 32. Client 조립
파일:

```text
app/core/lifespan.py
```

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.clients.limited_client import (
    ConcurrencyLimitedTextGenerationClient,
)
from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.clients.retry_client import (
    RetryingTextGenerationClient,
)
from app.core.config import get_settings
from app.core.container import ApplicationContainer


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings = get_settings()

    provider_client = OpenAITextGenerationClient(
        api_key=(
            settings.openai_api_key.get_secret_value()
        ),
        model=settings.openai_model,
        timeout_seconds=settings.ai_timeout_seconds,
        max_output_tokens=(
            settings.ai_max_output_tokens
        ),
        # Application Retry를 사용할 경우
        # SDK Retry는 명확한 정책에 따라 조정한다.
        max_retries=0,
    )

    limited_client = (
        ConcurrencyLimitedTextGenerationClient(
            client=provider_client,
            max_concurrency=(
                settings.ai_max_concurrency
            ),
        )
    )

    retrying_client = RetryingTextGenerationClient(
        client=limited_client,
        max_attempts=settings.ai_max_attempts,
        base_delay_seconds=(
            settings.ai_retry_base_delay_seconds
        ),
        max_delay_seconds=(
            settings.ai_retry_max_delay_seconds
        ),
        jitter_seconds=(
            settings.ai_retry_jitter_seconds
        ),
    )

    app.state.container = ApplicationContainer(
        text_generation_client=retrying_client,
        base_text_generation_client=provider_client,
    )

    try:
        yield

    finally:
        await provider_client.close()
```

---

### 33. 설정 추가
파일:

```text
app/core/config.py
```

```python
from pydantic import Field


class Settings(BaseSettings):
    # 기존 설정 생략

    ai_max_attempts: int = Field(
        default=3,
        ge=1,
        le=5,
    )

    ai_retry_base_delay_seconds: float = Field(
        default=0.5,
        ge=0,
        le=10,
    )

    ai_retry_max_delay_seconds: float = Field(
        default=4.0,
        ge=0,
        le=60,
    )

    ai_retry_jitter_seconds: float = Field(
        default=0.2,
        ge=0,
        le=5,
    )
```

`.env.example`:

```env
AI_MAX_ATTEMPTS=3
AI_RETRY_BASE_DELAY_SECONDS=0.5
AI_RETRY_MAX_DELAY_SECONDS=4
AI_RETRY_JITTER_SECONDS=0.2
```

---

### 34. Retry 설정 검증
다음 관계를 검증할 수 있다.

```python
from pydantic import model_validator


@model_validator(mode="after")
def validate_retry_settings(self) -> "Settings":
    if (
        self.ai_retry_max_delay_seconds
        < self.ai_retry_base_delay_seconds
    ):
        raise ValueError(
            "AI_RETRY_MAX_DELAY_SECONDS는 "
            "AI_RETRY_BASE_DELAY_SECONDS보다 "
            "크거나 같아야 합니다."
        )

    return self
```

---

### 35. Router의 오류 응답 문서화
FastAPI Router에 가능한 오류 응답을 문서화할 수 있다.

```text
from fastapi import APIRouter

from app.schemas.error import ErrorResponse


@router.post(
    "",
    response_model=SummaryResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "잘못된 AI 요청",
        },
        429: {
            "model": ErrorResponse,
            "description": "AI 요청 제한",
        },
        502: {
            "model": ErrorResponse,
            "description": "AI Provider 연결 또는 응답 오류",
        },
        503: {
            "model": ErrorResponse,
            "description": "AI Provider 사용 불가",
        },
        504: {
            "model": ErrorResponse,
            "description": "AI Provider Timeout",
        },
    },
)
async def create_summary(...):
    ...
```

FastAPI는 `response_model`을 통해 출력 직렬화, 검증, 문서화를 지원한다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/response-model/ "Response Model - Return Type"))

---

### 36. 테스트용 실패 Client
파일:

```text
tests/fakes/ai_clients.py
```

```python
from app.core.exceptions import (
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)


class TimeoutTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        raise AIProviderTimeoutError()


class RateLimitedTextGenerationClient:
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        raise AIProviderRateLimitError(
            retry_after_seconds=3,
        )


class FailThenSucceedClient:
    def __init__(
        self,
        *,
        failures_before_success: int,
    ) -> None:
        self._failures_before_success = (
            failures_before_success
        )
        self.call_count = 0

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        self.call_count += 1

        if (
            self.call_count
            <= self._failures_before_success
        ):
            raise AIProviderTimeoutError()

        return "재시도 후 성공"
```

---

### 37. Retry Client 단위 테스트
```python
import pytest

from app.clients.retry_client import (
    RetryingTextGenerationClient,
)


@pytest.mark.asyncio
async def test_retry_succeeds_after_temporary_failures() -> None:
    base_client = FailThenSucceedClient(
        failures_before_success=2,
    )

    retry_client = RetryingTextGenerationClient(
        client=base_client,
        max_attempts=3,
        base_delay_seconds=0,
        max_delay_seconds=0,
        jitter_seconds=0,
    )

    result = await retry_client.generate(
        instructions="요약하세요.",
        input_text="테스트 문서입니다.",
    )

    assert result == "재시도 후 성공"
    assert base_client.call_count == 3
```

---

### 38. 재시도 불가능 오류 테스트
```python
from app.core.exceptions import (
    AIInvalidRequestError,
)


class InvalidRequestClient:
    def __init__(self) -> None:
        self.call_count = 0

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        self.call_count += 1
        raise AIInvalidRequestError()
```

```python
@pytest.mark.asyncio
async def test_non_retryable_error_is_not_retried() -> None:
    base_client = InvalidRequestClient()

    retry_client = RetryingTextGenerationClient(
        client=base_client,
        max_attempts=3,
        base_delay_seconds=0,
        max_delay_seconds=0,
        jitter_seconds=0,
    )

    with pytest.raises(AIInvalidRequestError):
        await retry_client.generate(
            instructions="요약하세요.",
            input_text="테스트 문서입니다.",
        )

    assert base_client.call_count == 1
```

---

### 39. 최종 실패 테스트
```python
class AlwaysTimeoutClient:
    def __init__(self) -> None:
        self.call_count = 0

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        self.call_count += 1
        raise AIProviderTimeoutError()
```

```python
@pytest.mark.asyncio
async def test_retry_stops_at_max_attempts() -> None:
    base_client = AlwaysTimeoutClient()

    retry_client = RetryingTextGenerationClient(
        client=base_client,
        max_attempts=3,
        base_delay_seconds=0,
        max_delay_seconds=0,
        jitter_seconds=0,
    )

    with pytest.raises(AIProviderTimeoutError):
        await retry_client.generate(
            instructions="요약하세요.",
            input_text="테스트 문서입니다.",
        )

    assert base_client.call_count == 3
```

---

### 40. API Timeout 오류 테스트
```python
from fastapi.testclient import TestClient

from app.clients.base import TextGenerationClient
from app.core.dependencies import (
    get_text_generation_client,
)
from app.main import app


def override_timeout_client() -> (
    TextGenerationClient
):
    return TimeoutTextGenerationClient()


def test_timeout_error_response() -> None:
    app.dependency_overrides[
        get_text_generation_client
    ] = override_timeout_client

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/summaries",
                json={
                    "text": (
                        "Timeout 오류 응답을 테스트하기 "
                        "위한 충분히 긴 문장입니다."
                    ),
                    "length": "short",
                    "tone": "neutral",
                },
            )

        assert response.status_code == 504

        body = response.json()

        assert (
            body["error"]["code"]
            == "AI_PROVIDER_TIMEOUT"
        )
        assert body["error"]["retryable"] is True
        assert body["error"]["request_id"]

    finally:
        app.dependency_overrides.clear()
```

---

### 41. Rate Limit 오류 테스트
```python
def override_rate_limited_client() -> (
    TextGenerationClient
):
    return RateLimitedTextGenerationClient()


def test_rate_limit_error_response() -> None:
    app.dependency_overrides[
        get_text_generation_client
    ] = override_rate_limited_client

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/summaries",
                json={
                    "text": (
                        "Rate Limit 오류 응답을 테스트하기 "
                        "위한 충분히 긴 문장입니다."
                    ),
                    "length": "short",
                    "tone": "neutral",
                },
            )

        assert response.status_code == 429
        assert response.headers["Retry-After"] == "3"

        body = response.json()

        assert (
            body["error"]["code"]
            == "AI_PROVIDER_RATE_LIMIT"
        )

    finally:
        app.dependency_overrides.clear()
```

---

### 42. 예상하지 못한 오류 Handler
운영환경에서는 처리하지 않은 Exception에 대한 공통 Handler도 고려할 수 있다.

```python
@app.exception_handler(Exception)
async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.exception(
        "Unhandled application error",
        extra={
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=500,
        headers={
            "X-Request-ID": request_id,
        },
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": (
                    "요청 처리 중 오류가 발생했습니다."
                ),
                "retryable": False,
                "request_id": request_id,
            }
        },
    )
```

주의:

개발환경에서 모든 Exception을 같은 응답으로 감추면 디버깅이 불편할 수 있다.

```text
development
→ 상세 Traceback 활용

production
→ 안전한 공통 응답
```

정책을 분리할 수 있다.

---

### 43. 자주 발생하는 실수
#### 실수 1 — 모든 Exception을 Retry
```text
except Exception:
    retry()
```

##### 문제
인증 오류, 입력 오류, 코드 버그까지 반복한다.

##### 해결
명시적으로 `retryable`한 Application Error만 재시도한다.

---

#### 실수 2 — Retry 횟수만 보고 전체 요청 수를 계산하지 않음
##### 문제
SDK Retry와 Application Retry가 중첩되어 실제 Provider 호출이 예상보다 많아진다.

##### 해결
각 계층의 Retry 횟수를 문서화하고 전체 최악 시도 횟수를 계산한다.

---

#### 실수 3 — Timeout을 너무 길게 설정
```text
AI Timeout = 10분
```

##### 문제
장애 시 요청이 장시간 누적된다.

##### 해결
사용자 경험과 작업 유형을 기준으로 합리적인 제한을 둔다. 긴 작업은 Job Queue로 전환한다.

---

#### 실수 4 — Timeout을 지나치게 짧게 설정
```text
AI Timeout = 1초
```

##### 문제
정상적인 응답도 대부분 실패할 수 있다.

##### 해결
실제 처리 시간의 분포를 측정해 설정한다.

---

#### 실수 5 — Provider Exception을 Router에서 직접 처리
```text
except openai.RateLimitError:
    ...
```

##### 문제
Router가 OpenAI SDK에 종속된다.

##### 해결
Client에서 Application Error로 변환하고 FastAPI Handler에서 HTTP 응답으로 변환한다.

---

#### 실수 6 — 모든 오류를 HTTP 500으로 반환
##### 문제
클라이언트가 Timeout, Rate Limit, 잘못된 요청을 구분할 수 없다.

##### 해결
의미에 맞는 상태 코드와 안정적인 Error Code를 정의한다.

---

#### 실수 7 — 오류 내용을 그대로 사용자에게 반환
```python
message=str(exc)
```

##### 문제
내부 구성과 Provider 정보가 노출될 수 있다.

##### 해결
사용자용 메시지와 내부 로그를 분리한다.

---

#### 실수 8 — 오류를 HTTP 200으로 반환
```json
{
  "success": false,
  "error": "Timeout"
}
```

##### 문제
HTTP 계층에서는 성공으로 보인다.

##### 해결
적절한 4xx 또는 5xx 상태를 사용한다.

---

#### 실수 9 — Retry Backoff 없이 즉시 반복
##### 문제
장애 상태의 Provider에 부하를 추가한다.

##### 해결
지수 백오프와 Jitter를 적용한다.

---

#### 실수 10 — Backoff 중 Semaphore를 점유
##### 문제
Retry 대기 중에도 다른 요청이 Provider 호출 슬롯을 사용하지 못한다.

##### 해결
Decorator 순서를 검토해 각 Retry 시도에서만 Semaphore를 획득한다.

---

#### 실수 11 — Request ID가 없음
##### 문제
사용자 오류와 서버 로그를 연결하기 어렵다.

##### 해결
모든 요청과 오류 응답에 Request ID를 포함한다.

---

#### 실수 12 — Prompt 원문을 오류 로그에 저장
##### 문제
개인정보나 기밀 문서가 로그 시스템에 남을 수 있다.

##### 해결
길이, Hash, 문서 ID 같은 최소 메타데이터만 기록한다.

---

#### 실수 13 — Timeout 후 무조건 안전하게 실패했다고 생각
##### 문제
Provider가 이미 처리를 완료했을 수 있으며 Retry가 중복 비용을 만들 수 있다.

##### 해결
비용이 큰 작업과 상태 변경 작업에는 Idempotency와 결과 중복 방지 정책을 적용한다.

---

#### 실수 14 — Fallback 결과가 동일하다고 가정
##### 문제
Provider별 기능과 출력 품질이 다를 수 있다.

##### 해결
Fallback Provider별 Prompt와 출력 검증, 품질 기준을 테스트한다.

---

### 44. 실무 Best Practice
#### 44.1 오류를 계층별로 변환한다
```text
Provider Error
→ Application Error
→ HTTP Error Response
```

외부 구현을 API 계층까지 노출하지 않는다.

---

#### 44.2 Retry는 오류 유형에 따라 제한적으로 적용한다
```text
일시적인 오류
→ Retry 검토

영구적인 오류
→ 즉시 실패
```

---

#### 44.3 Retry 책임을 한곳에 명확히 둔다
```text
SDK Retry
또는
Application Retry
```

두 개를 같이 쓴다면 전체 요청 수와 Timeout Budget을 계산한다.

---

#### 44.4 Timeout을 여러 계층에서 설계한다
```text
Provider SDK Timeout
Application Timeout
Gateway Timeout
Frontend Timeout
```

안쪽 Timeout이 바깥 Timeout보다 작도록 구성한다.

---

#### 44.5 오류 응답 계약을 고정한다
```json
{
  "error": {
    "code": "STABLE_ERROR_CODE",
    "message": "사용자용 메시지",
    "retryable": true,
    "request_id": "req_..."
  }
}
```

프론트엔드는 문자열 메시지가 아니라 `code`를 기준으로 동작하게 한다.

---

#### 44.6 로그에는 원인이, 응답에는 안전한 메시지가 있어야 한다
```text
Internal Log
→ Exception type, Stack Trace, Request ID

External Response
→ Stable code, Safe message, Request ID
```

---

#### 44.7 장애를 빠르게 감지할 수 있는 지표를 수집한다
- AI 요청 성공률
    
- Timeout 비율
    
- Rate Limit 비율
    
- 평균 응답 시간
    
- P95/P99 응답 시간
    
- Retry 횟수
    
- Provider별 오류율
    
- 모델별 오류율
    
- 사용자별 호출량
    
- 추정 비용
    
- Semaphore 대기 시간
    

---

#### 44.8 긴 작업은 Retry보다 Job 시스템을 검토한다
긴 문서 처리를 HTTP 요청 안에서 여러 번 Retry하면 사용자는 매우 오래 기다리게 된다.

```text
긴 작업
→ Job 생성
→ Worker Retry
→ 상태 저장
→ 결과 조회
```

구조가 더 적절할 수 있다.

---

### 45. 실습
#### 실습 목표
- OpenAI SDK 오류를 Application Exception으로 변환한다.
    
- Timeout, 연결 오류, Rate Limit, 인증 오류를 구분한다.
    
- 안정적인 ErrorResponse 모델을 만든다.
    
- FastAPI Exception Handler로 HTTP 오류를 반환한다.
    
- Retry 가능한 오류에만 지수 백오프를 적용한다.
    
- SDK Retry와 Application Retry의 중복을 제거한다.
    
- Request ID를 응답과 로그에 연결한다.
    
- 실제 OpenAI API 없이 오류와 Retry를 테스트한다.
    

---

#### 실습 환경
```text
Python 3.12
FastAPI
Uvicorn
Pydantic 2
pydantic-settings
OpenAI Python SDK
pytest
pytest-asyncio
httpx
```

설치:

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  pydantic-settings \
  openai \
  pytest \
  pytest-asyncio \
  httpx
```

---

#### 실습 프로젝트 구조
```text
app/
├── api/
│   ├── exception_handlers.py
│   ├── middleware.py
│   └── v1/
│       └── summaries.py
│
├── clients/
│   ├── base.py
│   ├── limited_client.py
│   ├── openai_client.py
│   └── retry_client.py
│
├── core/
│   ├── config.py
│   ├── container.py
│   ├── exceptions.py
│   ├── dependencies.py
│   └── lifespan.py
│
├── schemas/
│   ├── error.py
│   └── summary.py
│
├── services/
│   └── summary_service.py
│
└── main.py

tests/
├── api/
│   └── test_ai_errors.py
├── clients/
│   └── test_retry_client.py
└── fakes/
    └── ai_clients.py
```

---

### 46. 실습 절차
#### 1단계 — Application Exception 작성
```text
app/core/exceptions.py
```

다음 예외를 구현한다.

```text
AIApplicationError
AIProviderTimeoutError
AIProviderConnectionError
AIProviderRateLimitError
AIProviderUnavailableError
AIAuthenticationError
AIPermissionError
AIInvalidRequestError
AIEmptyResponseError
```

각 Exception에 다음 정보를 포함한다.

```text
error_code
message
retryable
```

---

#### 2단계 — OpenAI 오류 변환
```text
app/clients/openai_client.py
```

다음 오류를 변환한다.

```text
APITimeoutError
→ AIProviderTimeoutError

APIConnectionError
→ AIProviderConnectionError

RateLimitError
→ AIProviderRateLimitError

AuthenticationError
→ AIAuthenticationError

PermissionDeniedError
→ AIPermissionError

BadRequestError
→ AIInvalidRequestError

InternalServerError
→ AIProviderUnavailableError
```

---

#### 3단계 — Retry Client 구현
```text
app/clients/retry_client.py
```

다음을 적용한다.

- `retryable=True`인 오류만 Retry
    
- 최대 시도 횟수
    
- 지수 백오프
    
- Jitter
    
- 최종 실패 시 원래 Application Error 재발생
    

---

#### 4단계 — Error Schema 작성
```text
app/schemas/error.py
```

```python
class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
```

---

#### 5단계 — Request ID Middleware 작성
모든 요청에 다음 Header를 추가한다.

```text
X-Request-ID
```

Request State에도 저장한다.

```python
request.state.request_id = request_id
```

---

#### 6단계 — Exception Handler 작성
```text
app/api/exception_handlers.py
```

다음을 구현한다.

```text
AIProviderTimeoutError
→ 504

AIProviderConnectionError
→ 502

AIProviderRateLimitError
→ 429

AIProviderUnavailableError
→ 503

AIInvalidRequestError
→ 400
```

---

#### 7단계 — Main에 등록
```python
app.add_middleware(
    RequestIDMiddleware
)

register_exception_handlers(app)
```

---

#### 8단계 — Lifespan Client 조립
```text
OpenAI Client
   ↓
Concurrency Limited Client
   ↓
Retrying Client
   ↓
Application Container
```

SDK Retry와 Custom Retry를 동시에 사용할 경우 전체 시도 횟수를 계산한다.

실습에서는 Custom Retry를 확인하기 위해 SDK의 `max_retries=0`을 사용한다.

---

#### 9단계 — Timeout Fake 테스트
Fake Client가 다음 오류를 발생시키게 한다.

```python
raise AIProviderTimeoutError()
```

예상 응답:

```http
HTTP/1.1 504 Gateway Timeout
```

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "AI 응답 시간이 초과되었습니다.",
    "retryable": true,
    "request_id": "req_..."
  }
}
```

---

#### 10단계 — Rate Limit Fake 테스트
Fake Client:

```python
raise AIProviderRateLimitError(
    retry_after_seconds=3
)
```

예상 응답:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3
```

---

#### 11단계 — Retry 성공 테스트
처음 두 번 Timeout, 세 번째 성공하는 Fake Client를 만든다.

예상 결과:

```text
Call 1 → Timeout
Call 2 → Timeout
Call 3 → Success
```

검증:

```python
assert call_count == 3
assert result == "재시도 후 성공"
```

---

#### 12단계 — Retry 금지 오류 테스트
```python
raise AIInvalidRequestError()
```

검증:

```python
assert call_count == 1
```

잘못된 요청은 Retry하지 않아야 한다.

---

### 47. 예상 결과
#### Timeout
```text
OpenAI APITimeoutError
   ↓
AIProviderTimeoutError
   ↓
Exception Handler
   ↓
HTTP 504
```

#### Rate Limit
```text
OpenAI RateLimitError
   ↓
AIProviderRateLimitError
   ↓
Retry Client
   ├─ 재시도 성공
   └─ 최종 실패 → HTTP 429
```

#### 인증 오류
```text
OpenAI AuthenticationError
   ↓
AIAuthenticationError
   ↓
Retry하지 않음
   ↓
HTTP 503
```

#### 잘못된 요청
```text
OpenAI BadRequestError
   ↓
AIInvalidRequestError
   ↓
Retry하지 않음
   ↓
HTTP 400
```

---

### 48. 실습 확인
-  Provider SDK Exception이 Client 밖으로 직접 나오지 않는가?
    
-  Application Exception에 안정적인 Error Code가 있는가?
    
-  Retry 가능한 오류와 불가능한 오류가 구분되는가?
    
-  Timeout이 설정되어 있는가?
    
-  Retry에 지수 백오프와 Jitter가 적용되는가?
    
-  SDK Retry와 Custom Retry가 중복되지 않는가?
    
-  최악의 전체 요청 횟수를 계산했는가?
    
-  ErrorResponse 구조가 모든 AI 오류에서 일관적인가?
    
-  사용자 응답에 내부 Exception 문자열이 노출되지 않는가?
    
-  Request ID가 응답 Header와 Body에 포함되는가?
    
-  API Key와 Prompt 원문이 로그에 남지 않는가?
    
-  Rate Limit 응답에 필요한 경우 `Retry-After`가 포함되는가?
    
-  재시도 불가능 오류는 한 번만 호출되는가?
    
-  Timeout 후 중복 비용 가능성을 이해했는가?
    
-  긴 작업에 Job Queue가 더 적합할 수 있음을 설명할 수 있는가?
    

---

### 49. 응용 과제
#### 과제 1 — Retry 횟수 응답 기록
내부 로그에 다음 값을 기록한다.

```text
retry_attempt
max_attempts
request_id
provider
```

사용자 응답에는 내부 Retry 횟수를 반드시 노출할 필요는 없다.

---

#### 과제 2 — Application Timeout 추가
SummaryService 전체에 30초 Timeout을 적용한다.

```python
async with asyncio.timeout(30):
    ...
```

Provider SDK Timeout은 25초로 설정한다.

두 Timeout의 역할 차이를 설명한다.

---

#### 과제 3 — Error Code별 React 처리 정의
다음 Error Code에 대한 UI 동작을 설계한다.

```text
AI_PROVIDER_TIMEOUT
→ 다시 시도 버튼

AI_PROVIDER_RATE_LIMIT
→ 잠시 후 자동 재시도 안내

AI_INVALID_REQUEST
→ 입력 수정 안내

AI_PROVIDER_UNAVAILABLE
→ 서비스 점검 메시지
```

---

#### 과제 4 — Idempotency Key 설계
문서 요약 요청에 다음 Header를 추가한다.

```http
Idempotency-Key: ...
```

같은 Key 요청이 다시 들어오면 기존 결과를 반환하도록 Repository 구조를 설계한다.

---

#### 과제 5 — Fallback Provider
Primary Client 실패 시 Fake Client가 아닌 실제 Secondary Provider로 전환하는 구조를 설계한다.

다음을 문서화한다.

- 전환 대상 오류
    
- Retry 후 Fallback인지 즉시 Fallback인지
    
- 품질 차이 처리
    
- 비용 차이 처리
    
- 결과에 Provider 정보를 저장할지 여부
    
- Structured Output 호환성
    

---

#### 과제 6 — Circuit Breaker 상태 설계
다음 상태를 정의한다.

```text
CLOSED
OPEN
HALF_OPEN
```

다음을 결정한다.

- 몇 번 실패하면 Open하는가?
    
- 얼마나 기다린 후 Half-Open으로 전환하는가?
    
- 시험 요청은 몇 개 허용하는가?
    
- 여러 Worker에서 상태를 공유할 것인가?
    

---

### 50. 이해도 확인
#### 질문 1
AI Provider Exception을 Application Exception으로 변환하는 이유는 무엇인가?

##### 모범 답안
Application Service와 FastAPI Router가 특정 Provider SDK에 종속되지 않게 하기 위해서다. OpenAI의 `RateLimitError`를 `AIProviderRateLimitError`로 변환하면 다른 Provider를 사용하더라도 같은 Application Error 계약과 HTTP Handler를 유지할 수 있다.

---

#### 질문 2
모든 오류를 Retry하면 안 되는 이유는 무엇인가?

##### 모범 답안
API Key 오류, 권한 부족, 잘못된 요청처럼 같은 조건으로 반복해도 성공하지 않는 오류가 있기 때문이다. 이런 오류를 Retry하면 응답 시간과 부하만 증가한다. 일시적인 연결 실패, Timeout, 일부 5xx나 Rate Limit처럼 회복 가능성이 있는 오류에만 제한적으로 적용해야 한다.

---

#### 질문 3
SDK Retry와 Application Retry를 동시에 사용할 때 어떤 문제가 생기는가?

##### 모범 답안
각 Application 시도마다 SDK 내부 Retry가 다시 수행되어 실제 Provider 요청 횟수가 예상보다 크게 증가할 수 있다. 비용, 응답 시간과 Provider 부하가 증가하므로 각 계층의 시도 횟수를 계산하고 Retry 책임을 명확히 해야 한다.

---

#### 질문 4
지수 백오프와 Jitter를 사용하는 이유는 무엇인가?

##### 모범 답안
실패 직후 모든 Client가 동시에 재시도하면 Provider 장애를 더 악화시킬 수 있다. 지수 백오프는 시도할수록 대기 시간을 늘리고, Jitter는 서버마다 재시도 시간을 조금씩 다르게 만들어 요청이 한 시점에 몰리는 것을 줄인다.

---

#### 질문 5
Timeout이 발생하면 Provider가 요청을 처리하지 않았다고 볼 수 있는가?

##### 모범 답안
그렇지 않다. Provider가 이미 요청을 처리했지만 응답 전달 과정에서 Timeout이 발생했을 수 있다. 따라서 Retry 시 중복 비용이나 중복 결과가 발생할 수 있으며, 중요한 작업에는 Idempotency와 중복 저장 방지 정책이 필요하다.

---

#### 질문 6
왜 오류 응답에 Request ID를 포함하는가?

##### 모범 답안
사용자가 받은 오류와 서버 로그를 연결하기 위해서다. 동일한 시간에 많은 요청이 발생해도 Request ID를 이용하면 해당 요청의 Provider 오류, 처리 시간과 Retry 기록을 찾을 수 있다.

---

#### 질문 7
Provider Rate Limit은 항상 HTTP 429로 반환해야 하는가?

##### 모범 답안
반드시 그렇지는 않다. 사용자 개인의 요청 제한이 원인이라면 429가 적절할 수 있지만, 서버 전체 Provider 할당량이나 외부 Provider 장애가 원인이라면 사용자의 잘못이 아니므로 503을 사용할 수도 있다. 우리 API의 의미에 따라 결정해야 한다.

---

#### 질문 8
Application Timeout과 SDK Timeout의 차이는 무엇인가?

##### 모범 답안
SDK Timeout은 외부 Provider HTTP 요청 자체의 대기 시간을 제한한다. Application Timeout은 데이터 조회, Semaphore 대기, Retry, AI 호출과 결과 저장을 포함한 전체 사용 사례의 실행 시간을 제한한다.

---

#### 질문 9
사용자에게 Provider Exception 문자열을 그대로 보여주면 안 되는 이유는 무엇인가?

##### 모범 답안
API Key 상태, 모델 이름, SDK 구조와 내부 시스템 정보가 노출될 수 있고 응답 계약이 Provider 구현에 종속되기 때문이다. 내부 로그에는 구체적인 원인을 남기고 사용자에게는 안정적인 Error Code와 안전한 메시지를 반환해야 한다.

---

#### 질문 10
Retry와 Circuit Breaker의 차이는 무엇인가?

##### 모범 답안
Retry는 하나의 실패한 요청을 다시 시도하는 정책이다. Circuit Breaker는 Provider의 반복 장애를 감지한 뒤 일정 시간 동안 새로운 호출 자체를 차단해 장애 확산과 불필요한 대기를 막는 정책이다.

---

### 51. 핵심 내용 정리
#### 핵심 1
외부 AI Provider 호출은 반드시 실패할 수 있다고 가정한다.

```text
AI 호출
=
성공 가능성
+
실패 가능성
```

---

#### 핵심 2
오류는 계층별로 변환한다.

```text
Provider Error
→ Application Error
→ HTTP Error Response
```

---

#### 핵심 3
Timeout은 무기한 대기를 방지한다.

```text
Provider Timeout
Application Timeout
Gateway Timeout
Frontend Timeout
```

을 함께 설계한다.

---

#### 핵심 4
Retry는 일시적인 오류에만 적용한다.

```text
retryable=True
→ 제한적으로 Retry

retryable=False
→ 즉시 실패
```

---

#### 핵심 5
SDK Retry와 Application Retry를 중복 적용할 때 전체 요청 횟수를 계산한다.

```text
Application Attempts
×
SDK Attempts
=
실제 최대 Provider 요청 수
```

---

#### 핵심 6
Retry에는 지수 백오프와 Jitter를 사용한다.

```text
1초
2초
4초
8초
+
무작위 지연
```

---

#### 핵심 7
사용자 오류 응답과 내부 로그를 분리한다.

```text
사용자
→ 안전한 Message + Error Code

운영 로그
→ Exception + Request ID + 원인
```

---

#### 핵심 8
Request ID를 통해 API 응답과 서버 로그를 연결한다.

```text
React Error
   ↓ request_id
FastAPI Log
   ↓
Provider Log
```

---

#### 핵심 9
Timeout과 Retry는 중복 비용을 만들 수 있다.

```text
첫 요청 처리 여부 불명확
   ↓
Retry
   ↓
중복 호출 가능
```

중요한 작업에는 Idempotency를 검토한다.

---

#### 핵심 10
지속적인 Provider 장애에는 Fallback과 Circuit Breaker를 검토한다.

```text
Retry
→ 개별 요청 회복

Circuit Breaker
→ 장애 확산 방지

Fallback
→ 대체 Provider 사용
```

---

### 52. 한 문장으로 설명하기
> FastAPI AI Backend의 오류 처리 구조는 OpenAI와 같은 Provider의 Timeout, 연결 실패, Rate Limit과 인증 오류를 Application Exception으로 변환하고, 재시도 가능한 오류에만 제한적인 Backoff Retry를 적용한 뒤, FastAPI Exception Handler를 통해 안정적인 HTTP 상태 코드와 ErrorResponse로 반환하는 구조다.

---

### FastAPI Part 5. AI Backend Integration

## Module 42. Streaming Response


### Module 실습 예제

- [예제 1: streaming_plain.py](examples/module_42/streaming_plain.py) — Async Generator가 Chunk를 순서대로 생성하는지 확인합니다.
- [예제 2: streaming_response.py](examples/module_42/streaming_response.py) — FastAPI StreamingResponse로 NDJSON Event를 전송합니다.



#### 프로젝트 연결 학습
- **문제 상황:** 긴 AI 응답을 완료 전부터 사용자에게 전달한다.
- **오늘 만드는 것:** StreamingResponse와 취소 처리를 구현한다.
- **AI 플랫폼의 위치:** Provider 스트림을 HTTP 스트림으로 중계한다.
- **실무에서 많이 하는 실수:** 완료·오류·연결 취소를 무시하거나 DB Session을 오래 점유한다.
- **5분 실습:** 클라이언트가 중간에 끊겼을 때 정리할 자원을 적는다.


### 1. 이번 Unit의 학습 목표
이번 Unit을 마치면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

- AI 응답에서 Streaming이 필요한 이유는 무엇인가?
    
- 일반 Response와 Streaming Response는 무엇이 다른가?
    
- Streaming은 AI 모델의 전체 처리 시간을 줄이는가?
    
- Time to First Token과 전체 응답 시간은 무엇이 다른가?
    
- FastAPI의 `StreamingResponse`는 어떻게 동작하는가?
    
- Python의 `yield`와 Async Generator는 어떤 역할을 하는가?
    
- OpenAI의 Streaming Event에서 텍스트 Delta를 어떻게 추출하는가?
    
- SSE, 일반 텍스트 스트림, NDJSON은 무엇이 다른가?
    
- React의 `fetch()`로 Stream을 어떻게 읽는가?
    
- `EventSource`는 POST 요청에 적합한가?
    
- Streaming 중 오류가 발생하면 왜 일반 JSON 오류 응답을 보내기 어려운가?
    
- 사용자가 연결을 끊으면 Provider Stream도 중단해야 하는 이유는 무엇인가?
    
- Stream 결과는 언제 데이터베이스에 저장해야 하는가?
    
- Nginx와 같은 Proxy의 Buffering이 Streaming에 어떤 영향을 주는가?
    
- Streaming API를 테스트할 때 무엇을 확인해야 하는가?
    

---

### 2. 문제 이해 — Why
#### 2.1 일반 AI API의 사용자 경험
Streaming을 사용하지 않는 AI API는 전체 응답이 완성된 뒤 결과를 반환한다.

```text
사용자 질문
    ↓
FastAPI 요청 수신
    ↓
AI Provider 호출
    ↓
모델이 전체 답변 생성
    ↓
FastAPI가 전체 문자열 수신
    ↓
React에 한 번에 반환
```

사용자가 다음 질문을 보냈다고 가정하자.

```text
Transformer의 동작 원리를 자세히 설명해 주세요.
```

답변을 생성하는 데 15초가 걸린다면 사용자는 15초 동안 다음 화면만 볼 수 있다.

```text
Loading...
```

15초 후 전체 답변이 한 번에 표시된다.

```text
Loading...
      ↓ 15초
전체 답변 표시
```

서버가 실제로는 답변을 생성하고 있어도 사용자는 아무런 진행 상황을 볼 수 없다.

---

#### 2.2 Streaming을 사용하면 무엇이 달라지는가?
Streaming에서는 생성된 일부 결과를 즉시 클라이언트로 전달한다.

```text
사용자 질문
    ↓
AI Provider 호출
    ↓
첫 번째 텍스트 조각 생성
    ↓ 즉시 전송
React 화면에 표시
    ↓
다음 텍스트 조각 생성
    ↓ 즉시 전송
React 화면에 이어 붙임
```

화면에서는 다음처럼 보인다.

```text
Transformer는
Transformer는 입력
Transformer는 입력 토큰 사이의
Transformer는 입력 토큰 사이의 관계를 Attention으로
...
```

사용자는 전체 응답이 완성되기 전에 읽기 시작할 수 있다.

OpenAI의 공식 Python SDK는 Responses API의 스트리밍을 지원하며, `stream=True`로 요청한 뒤 Server-Sent Events 형태의 이벤트를 순회하는 방식을 제공한다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

---

#### 2.3 Streaming은 전체 생성 시간을 줄이는가?
반드시 그렇지는 않다.

Streaming의 주요 목적은 다음과 같다.

```text
전체 생성 시간을 획기적으로 단축
        X

첫 결과를 더 빠르게 사용자에게 표시
        O
```

예를 들어 전체 답변 생성 시간이 15초라고 하자.

##### 일반 응답
```text
0초 ───────────────────────── 15초
                              전체 응답 표시
```

##### Streaming 응답
```text
0초 ── 1초 ── 2초 ── 3초 ───────── 15초
        첫 글자   다음 조각           완료
```

전체 완료 시점은 비슷할 수 있지만 사용자가 기다린다고 느끼는 시간은 줄어든다.

---

#### 2.4 Time to First Token
Streaming AI 서비스에서 중요한 지표 중 하나는 첫 번째 생성 결과가 도착할 때까지 걸리는 시간이다.

```text
사용자 요청 시작
       ↓
첫 번째 Token 또는 Text Delta 수신
```

이를 개념적으로 다음과 같이 표현할 수 있다.

```text
Time to First Token
=
첫 생성 조각 도착 시각
-
요청 시작 시각
```

전체 처리 시간과는 다른 지표다.

```text
첫 응답 시간
→ 사용자가 언제 읽기 시작할 수 있는가?

전체 응답 시간
→ 언제 생성이 완전히 끝나는가?
```

---

### 3. 일반 Response와 Streaming Response
#### 3.1 일반 Response
일반 API는 전체 결과를 메모리에 만든 다음 한 번에 반환한다.

```text
@router.post("/summaries")
async def create_summary(...) -> SummaryResponse:
    result = await service.summarize(command)

    return SummaryResponse(
        summary=result.summary,
        status="completed",
    )
```

응답:

```json
{
  "summary": "전체 요약 결과입니다.",
  "status": "completed"
}
```

FastAPI는 일반적인 `response_model`을 사용하면 결과를 검증하고 직렬화한 뒤 응답한다. ([FastAPI](https://fastapi.tiangolo.com/tutorial/response-model/ "Response Model - Return Type"))

---

#### 3.2 Streaming Response
Streaming Response는 전체 결과가 준비될 때까지 기다리지 않고 여러 Chunk로 나누어 전송한다.

```text
Chunk 1
Chunk 2
Chunk 3
Chunk 4
...
```

FastAPI의 `StreamingResponse`는 Async Generator 또는 일반 Generator·Iterator가 `yield`하는 데이터를 응답 본문으로 순차 전송한다. ([FastAPI](https://fastapi.tiangolo.com/advanced/custom-response/ "Custom Response - HTML, Stream, File, others - FastAPI"))

```python
from fastapi.responses import StreamingResponse


async def generate_chunks():
    yield "첫 번째 조각"
    yield "두 번째 조각"
    yield "세 번째 조각"


return StreamingResponse(
    generate_chunks(),
    media_type="text/plain",
)
```

---

### 4. Streaming의 전체 Architecture
```text
┌───────────────────────────────────┐
│ React                             │
│ fetch() / ReadableStream          │
└────────────────┬──────────────────┘
                 │ HTTP Stream
                 ▼
┌───────────────────────────────────┐
│ FastAPI Router                    │
│ StreamingResponse                 │
└────────────────┬──────────────────┘
                 │ Async Iterator
                 ▼
┌───────────────────────────────────┐
│ Streaming Service                 │
│ Prompt 생성 / Stream 제어         │
└────────────────┬──────────────────┘
                 │ Async Iterator
                 ▼
┌───────────────────────────────────┐
│ Text Streaming Client             │
│ Provider Event → Text Delta 변환   │
└────────────────┬──────────────────┘
                 │ SSE Event Stream
                 ▼
┌───────────────────────────────────┐
│ OpenAI Responses API              │
└───────────────────────────────────┘
```

데이터 흐름:

```text
OpenAI Event
   ↓
Text Delta 추출
   ↓
Application Stream Event로 변환
   ↓
HTTP Chunk 또는 SSE Event로 변환
   ↓
React에서 수신
   ↓
현재 메시지 뒤에 이어 붙임
```

---

### 5. Generator와 `yield`
#### 5.1 일반 함수의 `return`
```python
def create_message() -> str:
    return "완성된 메시지"
```

`return`은 함수 실행을 종료하고 하나의 최종값을 반환한다.

```text
함수 시작
  ↓
전체 결과 생성
  ↓
return
  ↓
함수 종료
```

---

#### 5.2 Generator의 `yield`
```python
def generate_messages():
    yield "첫 번째"
    yield "두 번째"
    yield "세 번째"
```

`yield`는 값을 하나 반환한 뒤 함수의 실행 상태를 보존한다.

다음 값을 요청하면 이전 위치부터 실행을 이어간다.

```text
함수 시작
  ↓
yield "첫 번째"
  ↓ 일시 중지
다음 값 요청
  ↓
yield "두 번째"
  ↓ 일시 중지
다음 값 요청
  ↓
yield "세 번째"
  ↓
종료
```

호출:

```python
generator = generate_messages()

for message in generator:
    print(message)
```

---

#### 5.3 Async Generator
AI Provider Stream은 비동기 네트워크 I/O다.

따라서 Async Generator를 사용한다.

```python
async def generate_messages():
    yield "첫 번째"
    yield "두 번째"
```

사용:

```python
async for message in generate_messages():
    print(message)
```

차이:

```text
일반 Generator
→ for

Async Generator
→ async for
```

---

### 6. 가장 단순한 FastAPI Streaming 예제
```python
import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/stream",
    tags=["Streaming"],
)


async def generate_text():
    words = [
        "FastAPI는 ",
        "비동기 ",
        "Streaming Response를 ",
        "지원합니다.",
    ]

    for word in words:
        yield word
        await asyncio.sleep(0.5)


@router.get("")
async def stream_text() -> StreamingResponse:
    return StreamingResponse(
        generate_text(),
        media_type="text/plain; charset=utf-8",
    )
```

FastAPI는 Generator가 `yield`한 각 Chunk를 JSON으로 변환하지 않고 그대로 `StreamingResponse`에 전달한다. ([FastAPI](https://fastapi.tiangolo.com/advanced/stream-data/ "Stream Data"))

---

#### 6.1 실행 흐름
```text
GET /stream
   ↓
StreamingResponse 생성
   ↓
generate_text() 시작
   ↓
"FastAPI는 " 전송
   ↓ 0.5초
"비동기 " 전송
   ↓ 0.5초
"Streaming Response를 " 전송
   ↓
"지원합니다." 전송
   ↓
연결 종료
```

---

### 7. Streaming 데이터 형식
AI Streaming API를 설계할 때 어떤 형식으로 Chunk를 보낼지 결정해야 한다.

대표적인 방식은 다음과 같다.

```text
Plain Text
SSE
NDJSON
WebSocket
```

이번 Unit에서는 HTTP Response Streaming을 중심으로 다음 세 방식을 비교한다.

---

### 8. Plain Text Streaming
#### 8.1 형식
```text
안녕하세요. FastAPI Streaming입니다.
```

실제로는 여러 Chunk로 도착한다.

```text
"안녕"
"하세요."
" FastAPI"
" Streaming입니다."
```

FastAPI:

```python
return StreamingResponse(
    text_generator(),
    media_type="text/plain; charset=utf-8",
)
```

---

#### 8.2 장점
- 가장 단순하다.
    
- React에서 받은 문자열을 바로 이어 붙일 수 있다.
    
- 텍스트만 생성하는 간단한 Chat UI에 적합하다.
    
- 별도의 Event Parsing이 거의 필요 없다.
    

---

#### 8.3 단점
다음 상태를 표현하기 어렵다.

```text
생성 시작
텍스트 Delta
완료
오류
Token 사용량
Request ID
출처 문서
Tool Call
```

모든 데이터가 단순 문자열이므로 텍스트와 Metadata를 구분하기 어렵다.

---

### 9. Server-Sent Events
#### 9.1 SSE란 무엇인가?
SSE는 서버가 클라이언트로 이벤트를 지속적으로 보내는 텍스트 기반 HTTP 스트림 형식이다.

기본 형식:

```text
event: delta
data: {"text":"안녕하세요"}

event: completed
data: {"status":"completed"}
```

각 이벤트는 빈 줄로 구분한다.

```text
event: ...
data: ...

event: ...
data: ...

```

OpenAI Python SDK의 Streaming도 Server-Sent Events를 기반으로 이벤트를 전달한다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

---

#### 9.2 SSE 장점
다양한 Event Type을 구분할 수 있다.

```text
start
delta
completed
error
usage
citation
tool_call
```

예:

```text
event: start
data: {"request_id":"req_123"}

event: delta
data: {"text":"FastAPI는"}

event: delta
data: {"text":" 비동기 웹 프레임워크입니다."}

event: completed
data: {"status":"completed"}
```

---

#### 9.3 SSE Media Type
```python
media_type="text/event-stream"
```

권장 Header 예:

```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
```

`X-Accel-Buffering: no`는 일부 Nginx 환경에서 응답 Buffering을 비활성화하기 위해 사용할 수 있는 Header다. 실제 동작은 Proxy 설정에 따라 달라질 수 있다.

---

### 10. NDJSON
#### 10.1 NDJSON이란 무엇인가?
한 줄에 하나의 JSON 객체를 보내는 형식이다.

```text
{"type":"start","request_id":"req_123"}
{"type":"delta","text":"FastAPI는"}
{"type":"delta","text":" Streaming을 지원합니다."}
{"type":"completed"}
```

각 Record는 줄바꿈으로 구분한다.

```python
yield json.dumps(event) + "\n"
```

Media Type 예:

```text
application/x-ndjson
```

---

#### 10.2 장점
- 각 Chunk가 독립적인 JSON 객체다.
    
- 일반 `fetch()` Streaming과 잘 결합된다.
    
- Event Type과 Metadata를 포함하기 쉽다.
    
- POST 요청에서도 자연스럽게 사용할 수 있다.
    

FastAPI에는 JSON Lines 기반 Streaming을 다루는 별도 문서도 있으며, Streaming 데이터는 Chunk 그대로 전달된다. ([FastAPI](https://fastapi.tiangolo.com/advanced/stream-data/ "Stream Data"))

---

#### 10.3 단점
하나의 JSON 객체가 여러 네트워크 Chunk로 나뉠 수 있다.

따라서 클라이언트는 단순히 `reader.read()` 한 번의 결과를 JSON으로 Parsing하면 안 된다.

```text
네트워크 Chunk
≠
NDJSON 한 줄
```

버퍼에 누적하고 줄바꿈을 기준으로 분리해야 한다.

---

### 11. SSE와 NDJSON 선택
|항목|SSE|NDJSON|
|---|---|---|
|기본 형식|`event:` / `data:`|한 줄당 JSON|
|Event Type|기본 지원|JSON 필드로 표현|
|브라우저 `EventSource`|지원|지원하지 않음|
|POST Body|`EventSource`로는 어려움|`fetch()`로 가능|
|재연결 기능|EventSource가 일부 지원|직접 구현|
|Parsing|SSE Parser 필요|줄 단위 JSON Parser|
|Chat POST 요청|`fetch()` SSE 또는 NDJSON|적합|
|양방향 통신|불가능|불가능|

현재 AI Chat API처럼 Request Body를 POST로 전송해야 한다면 다음 방식을 사용할 수 있다.

```text
POST + fetch() + SSE 수동 Parsing
```

또는

```text
POST + fetch() + NDJSON
```

브라우저의 기본 `EventSource`는 일반적으로 GET 기반 연결을 사용하므로 JSON Body가 필요한 Chat POST 요청에는 그대로 적용하기 어렵다.

---

### 12. WebSocket과의 차이
Streaming Response:

```text
Client 요청
    ↓
Server가 응답 Stream 전송
```

주로 단방향이다.

WebSocket:

```text
Client ↔ Server
```

양방향으로 메시지를 주고받을 수 있다.

FastAPI는 WebSocket API도 지원하지만, 단순히 하나의 질문에 대해 생성 결과를 순차 전송하는 기능이라면 HTTP Streaming이 더 단순할 수 있다. ([FastAPI](https://fastapi.tiangolo.com/advanced/websockets/ "WebSockets"))

WebSocket이 유리한 예:

- 실시간 음성 대화
    
- 사용자가 생성 도중 추가 명령 전송
    
- 실시간 협업
    
- 여러 Server Event를 지속 수신
    
- 양방향 Agent Interaction
    

HTTP Streaming이 유리한 예:

- 질문 하나에 답변 하나
    
- 문서 요약 생성
    
- 보고서 생성
    
- 번역 결과 생성
    
- 기존 REST API와 함께 운영
    

---

### 13. Provider 독립적인 Streaming Protocol
Unit 35에서는 일반 텍스트 생성을 다음 Protocol로 추상화했다.

```python
class TextGenerationClient(Protocol):
    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> str:
        ...
```

Streaming은 반환값이 문자열 하나가 아니다.

여러 Delta를 비동기로 반환한다.

```python
from collections.abc import AsyncIterator
from typing import Protocol


class TextStreamingClient(Protocol):
    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[str]:
        ...
```

---

#### 13.1 왜 `async def stream()`이 아닌가?
다음 두 형태 모두 설계할 수 있다.

##### Async Generator Method
```text
async def stream(...) -> AsyncIterator[str]:
    yield "..."
```

##### Async Iterator 반환 Method
```text
def stream(...) -> AsyncIterator[str]:
    return self._stream(...)
```

교육 과정에서는 다음과 같이 Async Generator Method로 작성하는 것이 이해하기 쉽다.

```python
class TextStreamingClient(Protocol):
    async def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[str]:
        ...
```

다만 타입 검사기와 Protocol 설계에서는 Async Generator의 반환 Annotation과 호출 형태를 정확히 맞춰야 한다.

더 단순하게 Protocol을 다음처럼 정의할 수 있다.

```python
class TextStreamingClient(Protocol):
    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[str]:
        ...
```

구현체:

```python
class FakeTextStreamingClient:
    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[str]:
        yield "..."

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[str]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

이번 실습에서는 이 구조를 사용한다.

---

### 14. Stream Event 객체 설계
단순 문자열만 전달하면 완료나 오류 Metadata를 표현하기 어렵다.

Provider 독립적인 Event 객체를 정의한다.

파일:

```text
app/streaming/events.py
```

```python
from dataclasses import dataclass
from typing import Literal


StreamEventType = Literal[
    "start",
    "delta",
    "completed",
    "error",
]


@dataclass(frozen=True)
class StreamEvent:
    type: StreamEventType
    text: str | None = None
    request_id: str | None = None
    error_code: str | None = None
    message: str | None = None
```

이 구조는 OpenAI의 이벤트 객체를 그대로 노출하지 않는다.

```text
OpenAI Event
   ↓ Client에서 변환
Application StreamEvent
   ↓ Router에서 직렬화
SSE 또는 NDJSON
```

---

### 15. Streaming Protocol
```python
from collections.abc import AsyncIterator
from typing import Protocol

from app.streaming.events import StreamEvent


class TextStreamingClient(Protocol):
    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        ...
```

구현체:

```text
OpenAITextStreamingClient
FakeTextStreamingClient
OllamaTextStreamingClient
```

모두 동일한 `StreamEvent`를 생성한다.

---

### 16. Fake Streaming Client
파일:

```text
app/clients/fake_streaming_client.py
```

```python
import asyncio
from collections.abc import AsyncIterator

from app.streaming.events import StreamEvent


class FakeTextStreamingClient:
    def __init__(
        self,
        *,
        chunks: list[str] | None = None,
        delay_seconds: float = 0.1,
    ) -> None:
        self._chunks = chunks or [
            "FastAPI는 ",
            "비동기 ",
            "Streaming Response를 ",
            "지원합니다.",
        ]
        self._delay_seconds = delay_seconds

    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        yield StreamEvent(
            type="start",
        )

        for chunk in self._chunks:
            await asyncio.sleep(
                self._delay_seconds
            )

            yield StreamEvent(
                type="delta",
                text=chunk,
            )

        yield StreamEvent(
            type="completed",
        )

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

---

### 17. OpenAI Streaming Client
OpenAI 공식 Python SDK는 Responses API 호출에 `stream=True`를 지정하고 반환된 이벤트를 순회하는 방법을 지원한다. 비동기 Client에서는 비동기 순회 방식으로 이벤트를 처리한다. ([GitHub](https://github.com/openai/openai-python "The official Python library for the OpenAI API"))

파일:

```text
app/clients/openai_streaming_client.py
```

```python
from collections.abc import AsyncIterator

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.exceptions import (
    AIProviderConnectionError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)
from app.streaming.events import StreamEvent


class OpenAITextStreamingClient:
    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self._client = client
        self._model = model
        self._max_output_tokens = max_output_tokens

    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        try:
            stream = await self._client.responses.create(
                model=self._model,
                instructions=instructions,
                input=input_text,
                max_output_tokens=self._max_output_tokens,
                stream=True,
            )

            yield StreamEvent(
                type="start",
            )

            async for event in stream:
                if (
                    event.type
                    == "response.output_text.delta"
                ):
                    yield StreamEvent(
                        type="delta",
                        text=event.delta,
                    )

                elif (
                    event.type
                    == "response.completed"
                ):
                    yield StreamEvent(
                        type="completed",
                    )

                elif (
                    event.type
                    == "response.failed"
                ):
                    raise RuntimeError(
                        "AI 응답 생성이 실패했습니다."
                    )

        except APITimeoutError as exc:
            raise AIProviderTimeoutError() from exc

        except APIConnectionError as exc:
            raise AIProviderConnectionError() from exc

        except RateLimitError as exc:
            raise AIProviderRateLimitError() from exc

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

---

#### 17.1 Event Type을 문자열로 검사하는 이유
OpenAI Streaming은 단순한 텍스트 조각뿐 아니라 여러 종류의 이벤트를 전달할 수 있다.

개념 예:

```text
response.created
response.output_item.added
response.output_text.delta
response.output_text.done
response.completed
response.failed
```

텍스트 출력에 필요한 Delta만 선택한다.

```python
if event.type == "response.output_text.delta":
    text = event.delta
```

주의:

SDK의 이벤트 타입과 필드는 버전에 따라 확장되거나 변경될 수 있다. 실제 프로젝트에서는 고정된 SDK 버전을 사용하고 그 버전의 공식 타입 정의와 문서를 확인해야 한다.

---

### 18. Streaming Service
Prompt 생성과 Provider Stream 호출을 Application Service에 배치한다.

파일:

```text
app/services/streaming_summary_service.py
```

```python
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.clients.streaming_base import (
    TextStreamingClient,
)
from app.schemas.summary import (
    SummaryLength,
    SummaryTone,
)
from app.streaming.events import StreamEvent


@dataclass(frozen=True)
class StreamingSummaryCommand:
    text: str
    length: SummaryLength
    tone: SummaryTone


class StreamingSummaryService:
    def __init__(
        self,
        *,
        client: TextStreamingClient,
    ) -> None:
        self._client = client

    def stream_summary(
        self,
        command: StreamingSummaryCommand,
    ) -> AsyncIterator[StreamEvent]:
        instructions = self._build_instructions(
            length=command.length,
            tone=command.tone,
        )

        return self._client.stream(
            instructions=instructions,
            input_text=command.text.strip(),
        )

    def _build_instructions(
        self,
        *,
        length: SummaryLength,
        tone: SummaryTone,
    ) -> str:
        length_rule = {
            "short": "3문장 이내로 요약하세요.",
            "medium": "5문장 안팎으로 요약하세요.",
            "long": (
                "핵심 논리와 세부 내용을 포함하여 "
                "자세히 요약하세요."
            ),
        }[length]

        tone_rule = {
            "neutral": "중립적인 문체를 사용하세요.",
            "professional": (
                "업무 보고서에 적합한 "
                "전문적인 문체를 사용하세요."
            ),
            "friendly": (
                "비전문가도 이해하기 쉬운 "
                "친근한 문체를 사용하세요."
            ),
        }[tone]

        return "\n".join(
            [
                "당신은 전문 문서 요약가입니다.",
                length_rule,
                tone_rule,
                "원문에 없는 사실을 추가하지 마세요.",
                "요약 결과만 출력하세요.",
            ]
        )
```

---

### 19. SSE Serializer
Application Event를 SSE 문자열로 변환한다.

파일:

```text
app/streaming/sse.py
```

```python
import json

from app.streaming.events import StreamEvent


def serialize_sse_event(
    event: StreamEvent,
) -> str:
    payload: dict[str, object] = {
        "type": event.type,
    }

    if event.text is not None:
        payload["text"] = event.text

    if event.request_id is not None:
        payload["request_id"] = event.request_id

    if event.error_code is not None:
        payload["error_code"] = event.error_code

    if event.message is not None:
        payload["message"] = event.message

    data = json.dumps(
        payload,
        ensure_ascii=False,
    )

    return (
        f"event: {event.type}\n"
        f"data: {data}\n\n"
    )
```

출력:

```text
event: delta
data: {"type":"delta","text":"FastAPI는 "}

```

---

### 20. Streaming Router
파일:

```text
app/api/v1/streaming_summaries.py
```

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse

from app.core.dependencies import (
    get_streaming_summary_service,
)
from app.core.exceptions import (
    AIApplicationError,
)
from app.schemas.summary import (
    SummaryCreateRequest,
)
from app.services.streaming_summary_service import (
    StreamingSummaryCommand,
    StreamingSummaryService,
)
from app.streaming.events import StreamEvent
from app.streaming.sse import (
    serialize_sse_event,
)


router = APIRouter(
    prefix="/streaming-summaries",
    tags=["Streaming Summaries"],
)


@router.post("")
async def create_streaming_summary(
    request_body: SummaryCreateRequest,
    request: Request,
    service: Annotated[
        StreamingSummaryService,
        Depends(get_streaming_summary_service),
    ],
) -> StreamingResponse:
    command = StreamingSummaryCommand(
        text=request_body.text,
        length=request_body.length,
        tone=request_body.tone,
    )

    async def event_generator() -> AsyncIterator[str]:
        request_id = str(
            request.state.request_id
        )

        try:
            async for event in service.stream_summary(
                command
            ):
                if await request.is_disconnected():
                    break

                event_with_request_id = StreamEvent(
                    type=event.type,
                    text=event.text,
                    request_id=request_id,
                    error_code=event.error_code,
                    message=event.message,
                )

                yield serialize_sse_event(
                    event_with_request_id
                )

        except AIApplicationError as exc:
            error_event = StreamEvent(
                type="error",
                request_id=request_id,
                error_code=exc.error_code,
                message=exc.message,
            )

            yield serialize_sse_event(
                error_event
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Request-ID": str(
                request.state.request_id
            ),
        },
    )
```

Starlette의 Request 객체는 Streaming이나 Long Polling과 같은 상황에서 클라이언트 연결 종료 여부를 확인할 수 있는 `is_disconnected()`를 제공한다. ([Starlette](https://www.starlette.io/requests/ "Requests"))

---

### 21. 왜 Streaming Router 안에서 오류를 Event로 변환하는가?
일반 API에서는 오류 발생 시 Exception Handler가 JSONResponse를 만든다.

```text
Exception
  ↓
HTTP 504
  ↓
ErrorResponse JSON
```

하지만 Streaming은 응답 Header와 Status가 이미 전송된 뒤 오류가 발생할 수 있다.

```text
HTTP 200 Header 전송
   ↓
start Event 전송
   ↓
delta Event 전송
   ↓
Provider Timeout 발생
```

이 시점에는 HTTP 상태를 `504`로 변경할 수 없다.

이미 다음 응답이 시작되었기 때문이다.

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
```

따라서 Stream 시작 후 오류는 Stream Event로 전달한다.

```text
event: error
data: {
  "error_code": "AI_PROVIDER_TIMEOUT",
  "message": "AI 응답 시간이 초과되었습니다."
}
```

---

### 22. Stream 시작 전 오류와 시작 후 오류
두 상황을 구분해야 한다.

#### Stream 시작 전 오류
예:

- 요청 검증 실패
    
- 인증 실패
    
- 문서 조회 실패
    
- 접근 권한 없음
    
- Provider Client 생성 실패
    

아직 Response가 시작되지 않았다.

```text
정상적인 HTTP 4xx/5xx 응답 가능
```

#### Stream 시작 후 오류
예:

- 생성 중 Provider 연결 종료
    
- 중간 Timeout
    
- Rate Limit Event
    
- Server 내부 오류
    
- 응답 Parsing 실패
    

이미 HTTP 200이 전송되었다.

```text
Stream 내부 error Event로 전달
```

설계 원칙:

```text
가능한 검증은 Stream 시작 전에 완료한다.
```

---

### 23. HTTP Status만으로 Streaming 성공을 판단하면 안 된다
Streaming API의 HTTP 응답이 `200 OK`라고 해도 최종 생성이 성공했다고 보장할 수 없다.

```text
HTTP 200
   ↓
delta 수신
   ↓
error Event
```

따라서 React는 다음을 모두 확인해야 한다.

```text
HTTP Status
+
Stream Event Type
+
completed Event 수신 여부
```

완료 상태는 다음 이벤트를 기준으로 판단한다.

```text
event: completed
```

---

### 24. React에서 SSE Stream 읽기
`EventSource` 대신 POST Body를 보낼 수 있는 `fetch()`를 사용한다.

```javascript
export async function streamSummary({
  text,
  length = "medium",
  tone = "neutral",
  onStart,
  onDelta,
  onCompleted,
  onError,
  signal,
}) {
  const response = await fetch(
    "/api/v1/streaming-summaries",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        text,
        length,
        tone,
      }),
      signal,
    },
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(
      () => null,
    );

    throw new Error(
      errorBody?.error?.message
        ?? `요청에 실패했습니다: ${response.status}`,
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming Response Body가 없습니다.",
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(
      value,
      { stream: true },
    );

    const eventBlocks = buffer.split("\n\n");
    buffer = eventBlocks.pop() ?? "";

    for (const block of eventBlocks) {
      const event = parseSSEBlock(block);

      switch (event.type) {
        case "start":
          onStart?.(event.data);
          break;

        case "delta":
          onDelta?.(event.data.text ?? "");
          break;

        case "completed":
          onCompleted?.(event.data);
          break;

        case "error":
          onError?.(event.data);
          return;
      }
    }
  }
}


function parseSSEBlock(block) {
  let eventType = "message";
  const dataLines = [];

  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      eventType = line
        .slice("event:".length)
        .trim();
    }

    if (line.startsWith("data:")) {
      dataLines.push(
        line.slice("data:".length).trim(),
      );
    }
  }

  const dataText = dataLines.join("\n");

  return {
    type: eventType,
    data: dataText
      ? JSON.parse(dataText)
      : {},
  };
}
```

---

### 25. React State 연결
```javascript
import { useRef, useState } from "react";


export function SummaryPage() {
  const [summary, setSummary] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const abortControllerRef = useRef(null);

  const handleGenerate = async (text) => {
    setSummary("");
    setError(null);
    setStatus("loading");

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await streamSummary({
        text,
        signal: controller.signal,

        onStart: () => {
          setStatus("streaming");
        },

        onDelta: (delta) => {
          setSummary(
            (current) => current + delta,
          );
        },

        onCompleted: () => {
          setStatus("completed");
        },

        onError: (event) => {
          setStatus("failed");
          setError(
            event.message
              ?? "AI 응답 생성에 실패했습니다.",
          );
        },
      });

    } catch (requestError) {
      if (requestError.name === "AbortError") {
        setStatus("cancelled");
        return;
      }

      setStatus("failed");
      setError(requestError.message);

    } finally {
      abortControllerRef.current = null;
    }
  };

  const handleCancel = () => {
    abortControllerRef.current?.abort();
  };

  return null;
}
```

핵심 부분:

```javascript
setSummary(
  (current) => current + delta,
);
```

이전 문자열 뒤에 새 Delta를 이어 붙인다.

---

### 26. Streaming 취소
#### 26.1 React에서 취소
```javascript
const controller = new AbortController();

fetch(url, {
  signal: controller.signal,
});

controller.abort();
```

사용자가 생성 중지 버튼을 누르면 HTTP 연결을 취소할 수 있다.

---

#### 26.2 FastAPI에서 연결 종료 확인
```python
if await request.is_disconnected():
    break
```

클라이언트가 연결을 끊었는데도 Provider Stream을 계속 읽으면 다음 문제가 생긴다.

- 필요 없는 Token 생성
    
- 불필요한 비용
    
- Server 자원 사용
    
- Semaphore Slot 점유
    
- 저장할 수 없는 결과 생성
    

---

#### 26.3 `break`만 하면 충분한가?
Provider Stream 객체가 Context Manager나 명시적 종료 메서드를 제공한다면 종료 처리를 적용해야 한다.

개념 구조:

```python
stream = ...

try:
    async for event in stream:
        if disconnected:
            break

finally:
    await stream.close()
```

실제 종료 API는 사용하는 OpenAI SDK 버전과 Streaming 방식에 맞게 공식 타입 정의를 확인해야 한다.

---

### 27. Coroutine Cancellation
Streaming Task가 취소되면 Python에서는 `asyncio.CancelledError`가 전달될 수 있다.

```python
import asyncio


try:
    async for event in stream:
        yield event

except asyncio.CancelledError:
    raise

finally:
    await close_stream()
```

`CancelledError`를 일반 오류처럼 먹어버리면 취소가 제대로 전파되지 않을 수 있다.

잘못된 예:

```text
except Exception:
    yield error_event
```

취소도 일반 Exception으로 처리해 계속 작업할 위험이 있다.

권장 방향:

```text
except asyncio.CancelledError:
    raise

except AIApplicationError as exc:
    ...
```

---

### 28. Async Generator에 `await` 지점이 필요한 이유
취소는 Coroutine이 Event Loop에 제어권을 돌려주는 지점에서 처리된다.

Generator 내부에서 CPU 작업만 계속 수행하고 `await`가 전혀 없다면 취소 반응이 늦어질 수 있다.

FastAPI 공식 Streaming 문서도 Async Generator가 취소될 기회를 가질 수 있도록 `await` 지점이 중요하다고 설명한다. ([FastAPI](https://fastapi.tiangolo.com/zh/advanced/custom-response/ "自定义响应- HTML、流、文件等 - FastAPI"))

외부 AI Stream의 `async for`는 내부적으로 네트워크 I/O를 기다리므로 일반적으로 `await` 지점이 존재한다.

---

### 29. Streaming과 Dependency 수명주기
Streaming 중 필요한 자원이 너무 일찍 종료되면 안 된다.

예:

```text
Router
  ↓
DB Session Dependency
  ↓
StreamingResponse 반환
  ↓
DB Session 종료
  ↓
Stream Generator가 DB 접근 시도
  ↓
오류
```

FastAPI의 최신 Dependency 동작에서는 `yield` Dependency의 정리 코드가 Streaming Response 전송 이후 실행되도록 처리되지만, 사용 중인 FastAPI 버전과 자원의 수명주기를 확인해야 한다. FastAPI 문서에는 과거 버전에서 이 동작이 변경된 이력과 StreamingResponse에서의 주의점이 설명되어 있다. ([FastAPI](https://fastapi.tiangolo.com/advanced/advanced-dependencies/ "Advanced Dependencies"))

권장 원칙:

```text
Stream 중 필요한 자원
→ Stream 완료까지 살아 있어야 함

Stream 시작 전에만 필요한 자원
→ 미리 조회한 뒤 종료 가능
```

---

### 30. Streaming 중 데이터베이스 저장
#### 30.1 각 Delta를 저장하는 방법
```text
Delta 1 → DB UPDATE
Delta 2 → DB UPDATE
Delta 3 → DB UPDATE
...
```

문제:

- DB Write 횟수 증가
    
- Transaction 증가
    
- 성능 저하
    
- 부분 문자열 상태가 다수 저장
    
- 장애 복구 복잡
    

---

#### 30.2 메모리에 누적 후 완료 시 저장
```python
chunks: list[str] = []

async for event in client.stream(...):
    if event.type == "delta":
        chunks.append(event.text or "")
        yield event

    if event.type == "completed":
        final_text = "".join(chunks)
        await repository.save(final_text)
```

장점:

- DB 저장 횟수가 적다.
    
- 최종 결과만 저장할 수 있다.
    

단점:

- 매우 긴 결과는 메모리를 사용한다.
    
- Server 장애 시 중간 결과가 사라진다.
    
- 사용자가 연결을 끊었을 때 저장 정책이 필요하다.
    

---

#### 30.3 일정 크기별 Checkpoint
```text
Delta 누적
  ↓
1,000자마다 임시 저장
  ↓
완료 시 최종 상태 저장
```

긴 보고서 생성이나 장시간 Job에 적합할 수 있다.

상태 예:

```text
streaming
completed
failed
cancelled
```

---

### 31. 저장 상태 모델
```python
from typing import Literal

GenerationStatus = Literal[
    "pending",
    "streaming",
    "completed",
    "failed",
    "cancelled",
]
```

DB Record 예:

```text
id
user_id
request_id
status
partial_content
final_content
error_code
created_at
completed_at
```

즉시 Chat 응답에서는 DB 저장이 필수가 아닐 수 있지만, 대화 이력이나 보고서 생성 서비스에서는 상태 관리가 중요하다.

---

### 32. 사용자가 연결을 끊은 뒤 결과 저장 정책
두 가지 정책이 가능하다.

#### 정책 A — 사용자 연결 종료 시 생성 취소
```text
연결 종료
  ↓
Provider Stream 중단
  ↓
status=cancelled
```

적합:

- 일회성 Chat
    
- 사용자가 결과를 더 이상 필요로 하지 않음
    
- 비용 절감이 중요
    

#### 정책 B — Server에서 계속 생성
```text
연결 종료
  ↓
Worker에서 생성 계속
  ↓
DB에 결과 저장
  ↓
나중에 다시 조회
```

적합:

- 보고서 생성
    
- 긴 문서 처리
    
- 생성 결과가 중요한 자산
    
- Job 시스템을 사용
    

정책 B는 HTTP Request Coroutine에 의존하지 말고 Job Queue와 Worker로 분리하는 것이 안전하다.

---

### 33. Streaming 중 Retry 문제
일반 요청은 최종 결과가 아직 사용자에게 전달되지 않았으므로 전체 호출을 Retry할 수 있다.

Streaming은 일부 텍스트가 이미 사용자에게 보였을 수 있다.

```text
"FastAPI는 비동기"
   ↓
연결 오류
   ↓
처음부터 Retry
   ↓
"FastAPI는 Python..."
```

사용자 화면에는 중복되거나 서로 다른 문장이 이어질 수 있다.

```text
FastAPI는 비동기FastAPI는 Python...
```

따라서 Streaming 중간 Retry는 매우 신중해야 한다.

---

#### 33.1 Stream 시작 전 Retry
첫 Delta가 아직 전달되지 않았다면 Retry를 적용하기 상대적으로 쉽다.

```text
Provider 연결 실패
  ↓
아직 Client에 Delta 없음
  ↓
Retry
```

#### 33.2 Stream 시작 후 Retry
일부 Delta가 이미 전달된 뒤라면 다음 정책 중 하나를 정한다.

```text
정책 A
→ Error Event를 보내고 종료

정책 B
→ 전체 메시지를 초기화한다는 Event 전송 후 재시작

정책 C
→ 중간 상태를 기반으로 이어서 생성

정책 D
→ Job으로 전환
```

일반적인 Chat Streaming에서는 오류 Event를 보내고 사용자가 다시 시도하도록 하는 것이 단순하다.

---

### 34. Streaming 오류 응답 예시
```text
event: start
data: {"type":"start","request_id":"req_123"}

event: delta
data: {"type":"delta","text":"FastAPI는 "}

event: delta
data: {"type":"delta","text":"비동기 처리를 "}

event: error
data: {
  "type":"error",
  "error_code":"AI_PROVIDER_TIMEOUT",
  "message":"AI 응답 시간이 초과되었습니다.",
  "request_id":"req_123"
}

```

React는 이미 받은 부분 응답을 유지할지 제거할지 결정해야 한다.

가능한 UI:

```text
FastAPI는 비동기 처리를

[응답 생성이 중단되었습니다.]
[다시 시도]
```

---

### 35. SSE Heartbeat
긴 시간 동안 Delta가 생성되지 않으면 Proxy나 Load Balancer가 연결을 유휴 상태로 판단해 종료할 수 있다.

이를 막기 위해 주기적인 Heartbeat를 보낼 수 있다.

SSE Comment 형식:

```text
: ping

```

Serializer:

```python
def serialize_sse_heartbeat() -> str:
    return ": ping\n\n"
```

다만 Heartbeat를 구현하려면 Provider Stream 읽기와 Timer를 동시에 관리해야 하므로 Task 설계가 복잡해질 수 있다.

필요 여부는 다음에 따라 결정한다.

- Proxy Idle Timeout
    
- Provider의 최대 응답 지연
    
- Stream 지속 시간
    
- 인프라 정책
    
- 모바일 네트워크 환경
    

---

### 36. Proxy Buffering
FastAPI가 Chunk를 즉시 전송하더라도 중간 Proxy가 여러 Chunk를 모은 뒤 한 번에 보낼 수 있다.

```text
FastAPI
  ↓ 작은 Chunk
Nginx Buffer
  ↓ 모아서 전송
Browser
```

사용자 입장에서는 Streaming이 아닌 것처럼 보인다.

확인할 대상:

- Nginx Proxy Buffering
    
- CDN Buffering
    
- Load Balancer Idle Timeout
    
- GZip Middleware
    
- Reverse Proxy Response Buffer
    
- 브라우저와 네트워크 중간 장비
    

Starlette의 GZipMiddleware는 작은 Streaming Chunk를 즉시 압축하지 않고 일정 크기까지 Buffering할 수 있다고 문서화되어 있다. 따라서 실시간성이 중요한 Stream에서는 압축과 Buffering 영향을 확인해야 한다. ([Starlette](https://www.starlette.io/middleware/ "Middleware"))

---

### 37. GZip과 Streaming
작은 Delta마다 GZip 압축을 수행하면 비효율적일 수 있다.

Middleware가 다음처럼 동작할 수 있다.

```text
작은 Chunk 수신
  ↓
Buffer에 누적
  ↓
최소 크기 도달
  ↓
압축 후 전송
```

결과적으로 첫 Delta 표시가 늦어질 수 있다.

운영 전 다음을 측정한다.

```text
압축 적용 전 Time to First Token
압축 적용 후 Time to First Token
Chunk 전달 간격
전체 Traffic 크기
```

---

### 38. Cache 방지
Streaming 응답은 중간 Cache에 저장하거나 재사용하면 안 되는 경우가 많다.

권장 Header 예:

```python
headers={
    "Cache-Control": "no-cache, no-transform",
}
```

`no-transform`은 중간 Proxy가 응답 형식을 변환하지 않도록 의도를 표현할 수 있다.

실제 적용 여부는 인프라 구성과 HTTP Cache 정책에 따라 확인해야 한다.

---

### 39. CORS와 Streaming
React와 FastAPI가 서로 다른 Origin이라면 CORS 설정이 필요하다.

예:

```python
from fastapi.middleware.cors import (
    CORSMiddleware,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
    ],
)
```

React에서 `X-Request-ID` Header를 읽으려면 CORS의 `expose_headers` 설정이 필요할 수 있다.

---

### 40. Streaming과 인증
일반 `fetch()` Streaming은 Authorization Header를 사용할 수 있다.

```javascript
fetch(url, {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});
```

반면 기본 `EventSource`는 임의의 Authorization Header 사용이 제한적이므로 Cookie 인증이나 별도 Token 전달 방식이 필요할 수 있다.

POST 기반 AI Chat Streaming에서는 `fetch()`가 인증과 Request Body 처리에 더 유연하다.

---

### 41. Streaming Response와 `response_model`
다음과 같은 일반 Response Model을 StreamingResponse에 그대로 적용할 수 없다.

```python
response_model=SummaryResponse
```

StreamingResponse는 여러 Chunk를 직접 전송하며 FastAPI가 각 Chunk를 Pydantic Response Model로 자동 변환하지 않는다. FastAPI에서 Response 객체를 직접 반환하면 일반적인 자동 데이터 변환이 적용되지 않는다. ([FastAPI](https://fastapi.tiangolo.com/advanced/response-directly/ "Return a Response Directly"))

따라서 다음을 별도로 설계해야 한다.

```text
Stream Event Schema
Serializer
OpenAPI 문서 설명
Client Parser
```

---

### 42. OpenAPI 문서화
```text
@router.post(
    "",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": (
                "SSE 형식으로 AI 요약 생성 이벤트를 "
                "Streaming합니다."
            ),
            "content": {
                "text/event-stream": {
                    "example": (
                        "event: delta\n"
                        'data: {"text":"FastAPI"}\n\n'
                    )
                }
            },
        },
        400: {
            "model": ErrorResponse,
            "description": "잘못된 요청",
        },
        401: {
            "model": ErrorResponse,
            "description": "인증 실패",
        },
    },
)
async def create_streaming_summary(...):
    ...
```

Swagger UI가 Streaming Event를 Chat UI처럼 표시해 주지는 않으므로 실제 Streaming 동작은 브라우저 Client, curl 또는 전용 테스트 코드로 확인해야 한다.

---

### 43. curl 테스트
SSE Stream이 실시간으로 표시되도록 Buffering을 비활성화한다.

```bash
curl -N \
  -X POST \
  "http://127.0.0.1:8000/api/v1/streaming-summaries" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "text": "FastAPI Streaming Response의 동작 원리를 설명하는 충분히 긴 테스트 문장입니다.",
    "length": "short",
    "tone": "neutral"
  }'
```

예상 출력:

```text
event: start
data: {"type":"start","request_id":"req_123"}

event: delta
data: {"type":"delta","text":"FastAPI는 ","request_id":"req_123"}

event: delta
data: {"type":"delta","text":"Async Generator가 ","request_id":"req_123"}

event: completed
data: {"type":"completed","request_id":"req_123"}
```

---

### 44. Dependency 구성
```python
from typing import Annotated

from fastapi import Depends, Request

from app.clients.streaming_base import (
    TextStreamingClient,
)
from app.core.container import (
    ApplicationContainer,
)
from app.services.streaming_summary_service import (
    StreamingSummaryService,
)


def get_streaming_client(
    request: Request,
) -> TextStreamingClient:
    container: ApplicationContainer = (
        request.app.state.container
    )

    return container.text_streaming_client


def get_streaming_summary_service(
    client: Annotated[
        TextStreamingClient,
        Depends(get_streaming_client),
    ],
) -> StreamingSummaryService:
    return StreamingSummaryService(
        client=client,
    )
```

---

### 45. Application Container 확장
```python
from dataclasses import dataclass

from app.clients.base import (
    TextGenerationClient,
)
from app.clients.streaming_base import (
    TextStreamingClient,
)


@dataclass
class ApplicationContainer:
    text_generation_client: TextGenerationClient
    text_streaming_client: TextStreamingClient
```

동일한 `AsyncOpenAI` 인스턴스를 일반 Client와 Streaming Client가 공유할 수 있다.

```text
AsyncOpenAI
   ├─ OpenAITextGenerationClient
   └─ OpenAITextStreamingClient
```

---

### 46. Lifespan에서 Client 생성
```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from openai import AsyncOpenAI

from app.clients.openai_client import (
    OpenAITextGenerationClient,
)
from app.clients.openai_streaming_client import (
    OpenAITextStreamingClient,
)
from app.core.config import get_settings
from app.core.container import (
    ApplicationContainer,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings = get_settings()

    openai_client = AsyncOpenAI(
        api_key=(
            settings.openai_api_key.get_secret_value()
        ),
        timeout=settings.ai_timeout_seconds,
        max_retries=settings.ai_sdk_max_retries,
    )

    text_generation_client = (
        OpenAITextGenerationClient(
            client=openai_client,
            model=settings.openai_model,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )
    )

    text_streaming_client = (
        OpenAITextStreamingClient(
            client=openai_client,
            model=settings.openai_model,
            max_output_tokens=(
                settings.ai_max_output_tokens
            ),
        )
    )

    app.state.container = ApplicationContainer(
        text_generation_client=(
            text_generation_client
        ),
        text_streaming_client=(
            text_streaming_client
        ),
    )

    try:
        yield

    finally:
        await openai_client.close()
```

---

### 47. Streaming과 Semaphore
Streaming 요청은 일반 요청보다 Semaphore Slot을 오래 점유할 수 있다.

```text
일반 AI 요청
→ 결과 완료까지 Slot 점유

Streaming 요청
→ Stream 전체 완료까지 Slot 점유
```

동시 Stream 수가 많으면 Provider 연결과 Server 자원이 장시간 사용된다.

따라서 일반 생성과 Streaming 생성에 서로 다른 제한을 둘 수 있다.

```text
AI_MAX_CONCURRENCY=10
AI_STREAM_MAX_CONCURRENCY=5
```

Streaming 전용 Decorator:

```python
class ConcurrencyLimitedStreamingClient:
    def __init__(
        self,
        *,
        client: TextStreamingClient,
        max_concurrency: int,
    ) -> None:
        self._client = client
        self._semaphore = asyncio.Semaphore(
            max_concurrency
        )

    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        async with self._semaphore:
            async for event in self._client.stream(
                instructions=instructions,
                input_text=input_text,
            ):
                yield event

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

Semaphore는 Generator 전체 수명 동안 유지되어야 한다.

---

### 48. Streaming Timeout
일반 Timeout과 Streaming Timeout은 다르게 볼 수 있다.

#### 전체 Stream Timeout
```text
Stream 전체가 최대 60초
```

#### 첫 Delta Timeout
```text
첫 Delta가 10초 안에 도착해야 함
```

#### Delta 사이 Idle Timeout
```text
다음 Delta가 20초 동안 오지 않으면 종료
```

각 정책은 다른 문제를 해결한다.

```text
First Delta Timeout
→ 모델 시작 지연 감지

Idle Timeout
→ 중간 연결 멈춤 감지

Total Timeout
→ 전체 생성 시간 상한
```

---

### 49. 첫 Delta Timeout 개념 예제
```python
import asyncio


async def read_first_event(
    stream: AsyncIterator[StreamEvent],
    timeout_seconds: float,
) -> StreamEvent:
    try:
        async with asyncio.timeout(
            timeout_seconds
        ):
            return await anext(stream)

    except TimeoutError as exc:
        raise AIProviderTimeoutError(
            "AI 응답 시작 시간이 초과되었습니다."
        ) from exc
```

전체 구현에서는 첫 Event를 다시 Stream에 포함해야 하므로 Iterator 조립이 필요하다.

이는 고급 패턴이므로 초기 실습에서는 SDK Timeout과 전체 Streaming Timeout부터 적용한다.

---

### 50. Streaming 테스트용 Client
```python
import asyncio
from collections.abc import AsyncIterator

from app.streaming.events import StreamEvent


class RecordingFakeStreamingClient:
    def __init__(
        self,
        *,
        chunks: list[str],
    ) -> None:
        self._chunks = chunks
        self.call_count = 0
        self.cancelled = False

    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        self.call_count += 1

        try:
            yield StreamEvent(type="start")

            for chunk in self._chunks:
                await asyncio.sleep(0)

                yield StreamEvent(
                    type="delta",
                    text=chunk,
                )

            yield StreamEvent(
                type="completed",
            )

        except asyncio.CancelledError:
            self.cancelled = True
            raise

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

---

### 51. Service 단위 테스트
```python
import pytest

from app.services.streaming_summary_service import (
    StreamingSummaryCommand,
    StreamingSummaryService,
)


@pytest.mark.asyncio
async def test_streaming_summary_service() -> None:
    client = RecordingFakeStreamingClient(
        chunks=[
            "FastAPI는 ",
            "Streaming을 ",
            "지원합니다.",
        ]
    )

    service = StreamingSummaryService(
        client=client,
    )

    command = StreamingSummaryCommand(
        text=(
            "FastAPI Streaming 테스트를 위한 "
            "충분히 긴 문장입니다."
        ),
        length="short",
        tone="neutral",
    )

    events = []

    async for event in service.stream_summary(
        command
    ):
        events.append(event)

    assert events[0].type == "start"
    assert events[-1].type == "completed"

    text = "".join(
        event.text or ""
        for event in events
        if event.type == "delta"
    )

    assert text == (
        "FastAPI는 Streaming을 지원합니다."
    )
    assert client.call_count == 1
```

---

### 52. API Streaming 테스트
Streaming 전송의 실제 Chunk 경계는 Test Client와 HTTP Library의 Buffering에 영향을 받을 수 있다.

따라서 API 테스트에서는 다음을 분리한다.

```text
Service Test
→ Event 순서와 내용

Serializer Test
→ SSE 형식

API Test
→ Content-Type과 최종 Body

실제 통합 Test
→ 실시간 Chunk 도착과 취소
```

---

#### 52.1 Serializer 테스트
```python
def test_serialize_delta_event() -> None:
    event = StreamEvent(
        type="delta",
        text="FastAPI",
        request_id="req_123",
    )

    result = serialize_sse_event(event)

    assert result.startswith(
        "event: delta\n"
    )
    assert '"text": "FastAPI"' in result
    assert result.endswith("\n\n")
```

---

#### 52.2 API 최종 Body 테스트
```python
from fastapi.testclient import TestClient

from app.main import app


def test_streaming_summary_response() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/streaming-summaries",
            json={
                "text": (
                    "Streaming API 테스트를 위한 "
                    "충분히 긴 입력 문장입니다."
                ),
                "length": "short",
                "tone": "neutral",
            },
        )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith("text/event-stream")

    assert "event: start" in response.text
    assert "event: delta" in response.text
    assert "event: completed" in response.text
```

`TestClient`가 Response를 모두 수집한 뒤 제공할 수 있으므로 이 테스트만으로 실제 Chunk 도착 간격을 검증할 수는 없다.

Starlette의 TestClient는 애플리케이션 테스트를 지원하지만, 실시간 Streaming 특성은 별도의 HTTP 통합 테스트나 브라우저 테스트가 필요할 수 있다. ([Starlette](https://www.starlette.io/testclient/ "Testclient"))

---

### 53. Streaming Event 순서 검증
정상적인 Stream:

```text
start
  ↓
delta × N
  ↓
completed
```

오류 Stream:

```text
start
  ↓
delta × N
  ↓
error
```

다음 상황은 잘못된 상태다.

```text
completed 이후 delta
error 이후 completed
start 두 번
completed 두 번
```

Event 순서를 State Machine으로 검증할 수 있다.

---

### 54. Client UI 상태
React 상태 예:

```text
idle
requesting
streaming
completed
failed
cancelled
```

상태 전환:

```text
idle
  ↓ 요청
requesting
  ↓ start
streaming
  ├─ completed → completed
  ├─ error     → failed
  └─ abort     → cancelled
```

이 구조를 명확히 정의하면 Loading Indicator와 버튼 상태를 안정적으로 제어할 수 있다.

---

### 55. 자주 발생하는 실수
#### 실수 1 — 전체 응답을 받은 뒤 한 글자씩 보내기
```python
full_text = await client.generate(...)

for character in full_text:
    yield character
```

##### 문제
사용자에게는 글자가 순차 표시되지만 Provider의 실제 생성 Streaming은 아니다.

첫 결과를 받는 시간은 줄어들지 않는다.

##### 해결
Provider의 Stream Event를 생성 즉시 전달한다.

---

#### 실수 2 — Network Chunk 하나가 Event 하나라고 가정
```javascript
const text = decoder.decode(value);
const event = JSON.parse(text);
```

##### 문제
하나의 Event가 여러 Network Chunk로 나뉠 수 있고 여러 Event가 하나의 Chunk에 포함될 수도 있다.

##### 해결
Buffer에 누적하고 Event 경계 또는 줄바꿈 기준으로 Parsing한다.

---

#### 실수 3 — Stream 시작 후 HTTP 상태 코드를 바꾸려 함
##### 문제
Header가 이미 전송되었다.

##### 해결
Stream 내부 `error` Event를 전송한다.

---

#### 실수 4 — `completed` Event 없이 연결만 종료
##### 문제
클라이언트가 정상 완료인지 네트워크 단절인지 구분하기 어렵다.

##### 해결
정상 완료 시 명시적인 `completed` Event를 전송한다.

---

#### 실수 5 — 클라이언트 연결 종료를 무시
##### 문제
사용자가 떠난 뒤에도 AI 생성이 계속되어 비용과 자원을 소비한다.

##### 해결
`request.is_disconnected()`와 Task Cancellation을 처리한다.

---

#### 실수 6 — `CancelledError`를 일반 오류로 처리
##### 문제
취소가 제대로 전파되지 않고 작업이 계속될 수 있다.

##### 해결
`CancelledError`는 다시 발생시킨다.

---

#### 실수 7 — 각 Delta를 DB에 저장
##### 문제
DB Write가 지나치게 많아진다.

##### 해결
메모리 누적 후 완료 시 저장하거나 일정 크기별 Checkpoint를 사용한다.

---

#### 실수 8 — Streaming 중 전체 요청을 자동 Retry
##### 문제
이미 표시된 텍스트와 재시작된 텍스트가 중복되거나 충돌한다.

##### 해결
첫 Delta 전 Retry와 첫 Delta 후 오류 정책을 구분한다.

---

#### 실수 9 — Proxy Buffering을 확인하지 않음
##### 문제
Server에서는 Streaming하지만 Browser에서는 한 번에 표시될 수 있다.

##### 해결
Nginx, CDN, GZip, Load Balancer 설정과 Header를 확인한다.

---

#### 실수 10 — 일반 `response_model`이 Stream Event를 자동 검증한다고 생각
##### 문제
StreamingResponse는 Chunk를 직접 전송한다.

##### 해결
Event Dataclass·Pydantic Model과 Serializer를 직접 관리한다.

---

#### 실수 11 — Stream 전체를 로그에 기록
##### 문제
개인정보, 문서 내용과 모델 응답이 로그에 남는다.

##### 해결
Request ID, Event 수, 문자 수, 처리 시간과 오류 코드만 기록한다.

---

#### 실수 12 — 무제한 동시 Stream 허용
##### 문제
연결과 Semaphore Slot이 장시간 점유된다.

##### 해결
Streaming 전용 동시성 제한과 사용자별 Rate Limit을 적용한다.

---

#### 실수 13 — `EventSource`로 POST Body를 보내려 함
##### 문제
기본 EventSource API는 일반적인 POST JSON 요청 구조에 적합하지 않다.

##### 해결
`fetch()`와 `ReadableStream`으로 SSE 또는 NDJSON을 읽는다.

---

#### 실수 14 — Stream 완료 전에 생성 결과를 완료 상태로 저장
##### 문제
부분 응답이 완전한 결과처럼 저장될 수 있다.

##### 해결
`streaming`, `completed`, `failed`, `cancelled` 상태를 구분한다.

---

### 56. 실무 Best Practice
#### 56.1 Provider Event를 직접 API에 노출하지 않는다
```text
Provider Event
   ↓
Application StreamEvent
   ↓
SSE/NDJSON
```

Provider 교체와 SDK 변경에 대비한다.

---

#### 56.2 Event Type을 명확히 정의한다
최소 Event:

```text
start
delta
completed
error
```

필요하면 확장한다.

```text
usage
citation
tool_call
metadata
heartbeat
```

---

#### 56.3 완료 Event를 반드시 전송한다
연결 종료만으로 정상 완료를 표현하지 않는다.

```text
completed 수신
→ 정상 성공

completed 없이 연결 종료
→ 비정상 종료 가능성
```

---

#### 56.4 Stream 시작 전에 가능한 검증을 끝낸다
- 인증
    
- 권한
    
- 요청 검증
    
- 문서 존재 확인
    
- Provider 설정 확인
    
- 사용자 사용량 제한
    

오류를 정상 HTTP 상태로 반환할 수 있도록 한다.

---

#### 56.5 Stream 시작 후 오류는 Event로 전달한다
```text
event: error
```

안정적인 Error Code와 Request ID를 포함한다.

---

#### 56.6 클라이언트 취소를 처리한다
```text
React Abort
→ HTTP 연결 종료
→ FastAPI 감지
→ Provider Stream 종료
→ 자원 반환
```

---

#### 56.7 Streaming 전용 Timeout을 설계한다
```text
First Delta Timeout
Idle Timeout
Total Stream Timeout
```

을 구분한다.

---

#### 56.8 Proxy 환경에서 실제로 측정한다
로컬 FastAPI 테스트만으로 충분하지 않다.

```text
Browser
→ CDN
→ Load Balancer
→ Nginx
→ FastAPI
```

전체 경로에서 Chunk가 즉시 전달되는지 확인한다.

---

#### 56.9 Stream Event Schema를 Versioning한다
예:

```json
{
  "version": "1",
  "type": "delta",
  "text": "..."
}
```

Event 구조를 변경할 가능성이 크다면 버전을 포함할 수 있다.

---

#### 56.10 부분 결과 저장 정책을 명확히 한다
```text
Chat
→ 완료 시 저장

긴 보고서
→ Checkpoint 저장

취소
→ 부분 결과 폐기 또는 cancelled 상태 저장
```

서비스 요구사항에 따라 결정한다.

---

### 57. 실습
#### 실습 목표
- Async Generator와 `yield`의 동작을 이해한다.
    
- Provider 독립적인 `TextStreamingClient`를 정의한다.
    
- Fake Streaming Client를 구현한다.
    
- OpenAI Responses API의 Text Delta Event를 변환한다.
    
- FastAPI `StreamingResponse`로 SSE Event를 전송한다.
    
- React `fetch()`로 SSE Stream을 읽는다.
    
- 연결 종료와 Task 취소를 처리한다.
    
- Streaming 중 오류를 Event로 변환한다.
    
- Event 순서와 최종 결과를 테스트한다.
    

---

#### 실습 환경
```text
Python 3.12
FastAPI
Uvicorn
Pydantic 2
pydantic-settings
OpenAI Python SDK
pytest
pytest-asyncio
httpx
React
```

설치:

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  pydantic-settings \
  openai \
  pytest \
  pytest-asyncio \
  httpx
```

---

### 58. 실습 프로젝트 구조
```text
app/
├── api/
│   └── v1/
│       └── streaming_summaries.py
│
├── clients/
│   ├── streaming_base.py
│   ├── fake_streaming_client.py
│   ├── limited_streaming_client.py
│   └── openai_streaming_client.py
│
├── core/
│   ├── config.py
│   ├── container.py
│   ├── dependencies.py
│   └── lifespan.py
│
├── schemas/
│   ├── error.py
│   └── summary.py
│
├── services/
│   └── streaming_summary_service.py
│
├── streaming/
│   ├── events.py
│   └── sse.py
│
└── main.py

tests/
├── clients/
│   └── test_streaming_client.py
├── services/
│   └── test_streaming_summary_service.py
└── streaming/
    └── test_sse.py
```

---

### 59. 실습 절차
#### 1단계 — Stream Event 작성
```text
app/streaming/events.py
```

```python
from dataclasses import dataclass
from typing import Literal


StreamEventType = Literal[
    "start",
    "delta",
    "completed",
    "error",
]


@dataclass(frozen=True)
class StreamEvent:
    type: StreamEventType
    text: str | None = None
    request_id: str | None = None
    error_code: str | None = None
    message: str | None = None
```

---

#### 2단계 — Streaming Protocol 작성
```text
app/clients/streaming_base.py
```

```python
from collections.abc import AsyncIterator
from typing import Protocol

from app.streaming.events import StreamEvent


class TextStreamingClient(Protocol):
    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        ...
```

---

#### 3단계 — Fake Client 작성
```text
app/clients/fake_streaming_client.py
```

```python
import asyncio
from collections.abc import AsyncIterator

from app.streaming.events import StreamEvent


class FakeTextStreamingClient:
    async def _generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        yield StreamEvent(type="start")

        for chunk in [
            "FastAPI는 ",
            "AI 응답을 ",
            "Streaming할 수 있습니다.",
        ]:
            await asyncio.sleep(0.2)

            yield StreamEvent(
                type="delta",
                text=chunk,
            )

        yield StreamEvent(
            type="completed",
        )

    def stream(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> AsyncIterator[StreamEvent]:
        return self._generate(
            instructions=instructions,
            input_text=input_text,
        )
```

---

#### 4단계 — SSE Serializer 작성
```text
app/streaming/sse.py
```

```python
import json

from app.streaming.events import StreamEvent


def serialize_sse_event(
    event: StreamEvent,
) -> str:
    payload = {
        key: value
        for key, value in {
            "type": event.type,
            "text": event.text,
            "request_id": event.request_id,
            "error_code": event.error_code,
            "message": event.message,
        }.items()
        if value is not None
    }

    return (
        f"event: {event.type}\n"
        f"data: {json.dumps(payload, ensure_ascii=False)}"
        "\n\n"
    )
```

---

#### 5단계 — Streaming Service 작성
```text
app/services/streaming_summary_service.py
```

```python
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.clients.streaming_base import (
    TextStreamingClient,
)
from app.streaming.events import StreamEvent


@dataclass(frozen=True)
class StreamingSummaryCommand:
    text: str
    length: str
    tone: str


class StreamingSummaryService:
    def __init__(
        self,
        *,
        client: TextStreamingClient,
    ) -> None:
        self._client = client

    def stream_summary(
        self,
        command: StreamingSummaryCommand,
    ) -> AsyncIterator[StreamEvent]:
        instructions = (
            "당신은 전문 문서 요약가입니다.\n"
            f"요약 길이: {command.length}\n"
            f"문체: {command.tone}\n"
            "원문에 없는 사실을 추가하지 마세요."
        )

        return self._client.stream(
            instructions=instructions,
            input_text=command.text.strip(),
        )
```

---

#### 6단계 — Dependency 작성
```python
def get_streaming_summary_service(
    request: Request,
) -> StreamingSummaryService:
    container: ApplicationContainer = (
        request.app.state.container
    )

    return StreamingSummaryService(
        client=container.text_streaming_client,
    )
```

---

#### 7단계 — Streaming Router 작성
```text
app/api/v1/streaming_summaries.py
```

```python
import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse

from app.core.dependencies import (
    get_streaming_summary_service,
)
from app.core.exceptions import (
    AIApplicationError,
)
from app.schemas.summary import (
    SummaryCreateRequest,
)
from app.services.streaming_summary_service import (
    StreamingSummaryCommand,
    StreamingSummaryService,
)
from app.streaming.events import StreamEvent
from app.streaming.sse import serialize_sse_event


router = APIRouter(
    prefix="/streaming-summaries",
    tags=["Streaming Summaries"],
)


@router.post("")
async def create_streaming_summary(
    request_body: SummaryCreateRequest,
    request: Request,
    service: Annotated[
        StreamingSummaryService,
        Depends(get_streaming_summary_service),
    ],
) -> StreamingResponse:
    request_id = str(
        request.state.request_id
    )

    command = StreamingSummaryCommand(
        text=request_body.text,
        length=request_body.length,
        tone=request_body.tone,
    )

    async def generate_events() -> AsyncIterator[str]:
        try:
            async for event in service.stream_summary(
                command
            ):
                if await request.is_disconnected():
                    break

                yield serialize_sse_event(
                    StreamEvent(
                        type=event.type,
                        text=event.text,
                        request_id=request_id,
                    )
                )

        except asyncio.CancelledError:
            raise

        except AIApplicationError as exc:
            yield serialize_sse_event(
                StreamEvent(
                    type="error",
                    request_id=request_id,
                    error_code=exc.error_code,
                    message=exc.message,
                )
            )

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": (
                "no-cache, no-transform"
            ),
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id,
        },
    )
```

---

#### 8단계 — Router 등록
```python
from app.api.v1.streaming_summaries import (
    router as streaming_summaries_router,
)


app.include_router(
    streaming_summaries_router,
    prefix="/api/v1",
)
```

---

#### 9단계 — Fake Provider 실행
`.env`:

```env
AI_PROVIDER=fake
```

실행:

```bash
uvicorn app.main:app --reload
```

테스트:

```bash
curl -N \
  -X POST \
  "http://127.0.0.1:8000/api/v1/streaming-summaries" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "text": "FastAPI Streaming을 테스트하기 위한 충분히 긴 입력 문장입니다.",
    "length": "short",
    "tone": "neutral"
  }'
```

---

#### 10단계 — React 연결
다음 상태를 구현한다.

```text
idle
loading
streaming
completed
failed
cancelled
```

Delta 수신:

```javascript
setSummary(
  (previous) => previous + delta,
);
```

취소:

```javascript
abortController.abort();
```

---

### 60. 예상 결과
요청 직후:

```text
status = loading
```

`start` Event 수신:

```text
status = streaming
```

Delta 수신:

```text
FastAPI는
FastAPI는 AI 응답을
FastAPI는 AI 응답을 Streaming할 수 있습니다.
```

완료:

```text
status = completed
```

오류:

```text
status = failed
error_code = AI_PROVIDER_TIMEOUT
```

사용자 취소:

```text
status = cancelled
Provider Stream 종료
```

---

### 61. 실습 확인
-  `TextStreamingClient`가 Provider 독립적인가?
    
-  OpenAI Event 객체를 Router에 그대로 전달하지 않는가?
    
-  `start`, `delta`, `completed`, `error` Event가 정의되었는가?
    
-  Async Generator에서 `yield`로 Chunk를 반환하는가?
    
-  `StreamingResponse`의 Media Type이 `text/event-stream`인가?
    
-  SSE Event가 빈 줄로 구분되는가?
    
-  정상 완료 시 `completed` Event를 보내는가?
    
-  Stream 시작 후 오류를 `error` Event로 보내는가?
    
-  `CancelledError`를 다시 발생시키는가?
    
-  `request.is_disconnected()`로 연결 종료를 확인하는가?
    
-  React가 Network Chunk와 Event를 구분해 Buffering하는가?
    
-  React가 Delta를 기존 문자열 뒤에 이어 붙이는가?
    
-  `AbortController`로 취소할 수 있는가?
    
-  Proxy Buffering과 GZip 영향을 확인했는가?
    
-  Stream 동시성에 별도 제한이 있는가?
    
-  완료 전 결과를 `completed` 상태로 저장하지 않는가?
    
-  Prompt와 전체 응답을 운영 로그에 기록하지 않는가?
    

---

### 62. 응용 과제
#### 과제 1 — NDJSON Streaming
SSE 대신 다음 형식으로 반환한다.

```text
{"type":"start"}
{"type":"delta","text":"FastAPI"}
{"type":"completed"}
```

Media Type:

```text
application/x-ndjson
```

React에서 줄바꿈 기준 Buffer Parsing을 구현한다.

---

#### 과제 2 — Usage Event
완료 시 다음 Event를 추가한다.

```text
event: usage
data: {
  "input_tokens": 100,
  "output_tokens": 50
}
```

Provider 전용 Usage 객체를 Application Event로 변환한다.

---

#### 과제 3 — Citation Event
RAG 답변에서 다음 Event를 추가한다.

```text
event: citation
data: {
  "document_id": 10,
  "title": "FastAPI Guide",
  "page": 3
}
```

텍스트 Delta와 출처 Metadata를 별도 Event로 전달한다.

---

#### 과제 4 — Partial Result 저장
다음 정책을 구현한다.

```text
500자마다 partial_content 저장
completed Event 시 final_content 저장
오류 시 status=failed
취소 시 status=cancelled
```

---

#### 과제 5 — First Delta 측정
다음 시간을 기록한다.

```text
request_started_at
first_delta_at
completed_at
```

계산:

```text
time_to_first_delta_ms
total_duration_ms
```

---

#### 과제 6 — Heartbeat
10초 동안 Delta가 없으면 다음 SSE Comment를 보낸다.

```text
: ping

```

Provider Event와 Heartbeat Timer를 동시에 처리하는 구조를 설계한다.

---

#### 과제 7 — Streaming 동시성 제한
```env
AI_STREAM_MAX_CONCURRENCY=3
```

동시에 세 개의 Stream만 허용한다.

네 번째 요청에 대해 다음 중 하나를 선택한다.

```text
대기
429 반환
503 반환
Job Queue 전환
```

선택 이유를 설명한다.

---

### 63. 이해도 확인
#### 질문 1
Streaming Response를 사용하는 가장 중요한 이유는 무엇인가?

##### 모범 답안
전체 AI 응답이 완성되기 전에 생성된 일부 텍스트를 사용자에게 전달하기 위해서다. 전체 생성 시간이 반드시 줄어드는 것은 아니지만 사용자가 더 빠르게 결과를 읽기 시작할 수 있어 체감 대기 시간이 줄어든다.

---

#### 질문 2
일반 Response와 Streaming Response는 무엇이 다른가?

##### 모범 답안
일반 Response는 전체 결과를 완성한 뒤 한 번에 반환한다. Streaming Response는 Generator나 Async Generator가 생성하는 여러 Chunk를 연결이 유지되는 동안 순차적으로 전달한다.

---

#### 질문 3
`yield`는 `return`과 무엇이 다른가?

##### 모범 답안
`return`은 최종값을 반환하고 함수 실행을 종료한다. `yield`는 값을 하나 반환한 뒤 실행 상태를 보존하고, 다음 값이 요청되면 이전 위치부터 실행을 이어간다.

---

#### 질문 4
Network Chunk 하나를 SSE Event 하나로 가정하면 안 되는 이유는 무엇인가?

##### 모범 답안
TCP와 HTTP 전송 과정에서 하나의 Event가 여러 Chunk로 나뉘거나 여러 Event가 하나의 Chunk에 합쳐질 수 있기 때문이다. 클라이언트는 Buffer에 데이터를 누적한 뒤 SSE Event 구분자인 빈 줄을 기준으로 Parsing해야 한다.

---

#### 질문 5
Streaming 중 오류가 발생했을 때 HTTP 상태 코드를 504로 바꾸기 어려운 이유는 무엇인가?

##### 모범 답안
Stream이 시작되면서 HTTP Header와 상태 코드가 이미 클라이언트에 전송되었기 때문이다. 이후 발생한 오류는 Stream 내부의 `error` Event로 전달해야 한다.

---

#### 질문 6
정상적인 Stream에서 `completed` Event가 필요한 이유는 무엇인가?

##### 모범 답안
단순한 연결 종료만으로는 정상 완료인지 네트워크 단절인지 구분하기 어렵기 때문이다. 클라이언트는 명시적인 `completed` Event를 받아야 생성이 정상적으로 끝났다고 판단할 수 있다.

---

#### 질문 7
사용자가 연결을 끊었을 때 Provider Stream도 중단해야 하는 이유는 무엇인가?

##### 모범 답안
사용자에게 전달할 수 없는 응답을 계속 생성하면 불필요한 Token 비용과 Server 자원을 소비하고 동시성 Slot도 점유하기 때문이다. 연결 종료와 Task 취소를 감지해 Provider Stream을 정리해야 한다.

---

#### 질문 8
Streaming 중간에 전체 요청을 자동 Retry하기 어려운 이유는 무엇인가?

##### 모범 답안
일부 텍스트가 이미 사용자에게 표시되었을 수 있기 때문이다. 처음부터 다시 생성하면 이전 Delta와 새 결과가 중복되거나 서로 다른 내용이 이어질 수 있다. 첫 Delta 이전과 이후의 Retry 정책을 구분해야 한다.

---

#### 질문 9
FastAPI에서는 Streaming하지만 Browser에서 결과가 한 번에 표시되는 원인은 무엇일 수 있는가?

##### 모범 답안
Nginx, CDN, Load Balancer, GZip Middleware 등의 Buffering으로 여러 Chunk가 중간에서 누적될 수 있다. 전체 네트워크 경로의 Buffering 설정과 응답 Header를 확인해야 한다.

---

#### 질문 10
SSE와 WebSocket의 가장 큰 차이는 무엇인가?

##### 모범 답안
SSE 기반 HTTP Streaming은 주로 서버에서 클라이언트로 데이터를 보내는 단방향 구조다. WebSocket은 연결이 유지되는 동안 클라이언트와 서버가 양방향으로 메시지를 주고받을 수 있다.

---

### 64. 핵심 내용 정리
#### 핵심 1
Streaming은 전체 답변이 완성되기 전에 생성된 결과를 전달한다.

```text
Model 생성
  ↓
Delta
  ↓
FastAPI
  ↓
React 표시
```

---

#### 핵심 2
Streaming은 전체 생성 시간을 반드시 줄이지는 않지만 첫 결과 표시 시간을 줄인다.

```text
Time to First Token
≠
Total Generation Time
```

---

#### 핵심 3
FastAPI의 `StreamingResponse`는 Generator나 Async Generator가 `yield`한 Chunk를 순차 전송한다.

```python
async def generator():
    yield "chunk 1"
    yield "chunk 2"
```

---

#### 핵심 4
Provider Event를 Application Event로 변환한다.

```text
OpenAI Event
   ↓
StreamEvent
   ↓
SSE 또는 NDJSON
```

---

#### 핵심 5
최소 Event Type을 명확히 정의한다.

```text
start
delta
completed
error
```

---

#### 핵심 6
Stream이 시작된 뒤 발생한 오류는 HTTP 상태 코드가 아니라 Stream Event로 전달한다.

```text
HTTP 200 시작
  ↓
error Event
```

---

#### 핵심 7
클라이언트는 Network Chunk를 Buffering한 뒤 Event 경계로 Parsing해야 한다.

```text
Network Chunk
≠
Application Event
```

---

#### 핵심 8
사용자가 연결을 끊으면 Provider Stream과 관련 자원을 정리한다.

```text
Abort
  ↓
Disconnect 감지
  ↓
Provider Stream 중단
```

---

#### 핵심 9
Streaming 결과 저장에는 상태 관리가 필요하다.

```text
streaming
completed
failed
cancelled
```

---

#### 핵심 10
실제 운영에서는 Proxy Buffering, GZip, Idle Timeout과 CORS까지 확인한다.

```text
Browser
→ CDN
→ Proxy
→ FastAPI
→ AI Provider
```

---

### 65. 한 문장으로 설명하기
> FastAPI의 AI Streaming Response는 OpenAI와 같은 Provider가 전달하는 생성 이벤트를 Provider 독립적인 `StreamEvent`로 변환하고, Async Generator와 `StreamingResponse`를 이용해 SSE 또는 NDJSON 형식으로 React에 즉시 전달하면서 완료·오류·취소와 연결 수명주기를 함께 관리하는 구조다.

---

### FastAPI Part 5 완료
```text
Unit 32. AI Backend Integration의 이해
Unit 33. AI Provider와 환경 설정
Unit 34. OpenAI API 연동
Unit 35. AI Service Layer 설계
Unit 36. 비동기 AI 요청 처리
Unit 37. Prompt와 Request Model 설계
Unit 38. AI 오류·Timeout·Retry 처리
Unit 39. Streaming Response
```

Part 5를 통해 다음 전체 구조가 완성되었다.

```text
React
  ↓ HTTP / Stream
FastAPI Router
  ↓
Request Model
  ↓
Application Command
  ↓
AI Service Layer
  ↓
Prompt Builder
  ↓
Provider-independent Client Protocol
  ↓
Concurrency / Retry / Timeout
  ↓
OpenAI Async Client
  ↓
OpenAI Responses API
```

Streaming 구조:

```text
OpenAI Stream Event
  ↓
Application StreamEvent
  ↓
FastAPI StreamingResponse
  ↓
SSE / NDJSON
  ↓
React Streaming UI
```

오류 구조:

```text
Provider Exception
  ↓
Application Exception
  ↓
Retry 판단
  ↓
HTTP ErrorResponse 또는 Stream Error Event
```

이제 FastAPI는 단순한 CRUD 서버가 아니라 다음 기능을 갖춘 AI Backend가 되었다.

```text
API Key 보호
Provider 교체
Prompt 관리
비동기 AI 호출
동시성 제한
Client 재사용
Timeout
Retry
안정적인 오류 계약
Streaming Response
Client 취소 처리
```

**Unit 39 완료: Streaming Response**

**FastAPI Part 5. AI Backend Integration 완료**

---

### Part 5 Architecture Review
#### 5분 복습
```text
검증된 질문
→ AI Service
→ Prompt 조립
→ AI Client
→ Provider
→ 내부 결과 변환
→ 일반 응답 또는 Streaming 응답
```

- **따라 하기:** Fake Client와 실제 Client의 공통 인터페이스를 사용한다.
- **부분 완성:** Timeout·Retry·오류 변환 정책을 채운다.
- **독립 구현:** Provider 교체가 가능한 AI 기능과 테스트를 설계한다.

#### 학생 질문
1. Provider SDK 응답을 내부 모델로 변환하는 이유는 무엇인가?
2. 재시도 가능한 오류와 즉시 실패해야 하는 오류는 어떻게 구분하는가?
3. Prompt Injection 대응이 문자열 분리만으로 끝나지 않는 이유는 무엇인가?

#### 확인 퀴즈
1. 모든 FastAPI Endpoint를 `async def`로 작성해야 하는가?
2. 4xx 성격의 Provider 오류도 무조건 재시도해야 하는가?
3. Streaming 중 클라이언트 연결이 끊기면 무엇을 처리해야 하는가?

<details>
<summary>정답</summary>

1. 아니다. 사용하는 라이브러리와 작업의 blocking 여부에 맞춰 선택한다.
2. 아니다. 재시도로 회복 가능한 오류인지 먼저 분류해야 한다.
3. Provider 스트림 취소와 열린 리소스 정리를 처리해야 한다.

</details>

### 과정 마무리 — 목표 코드 다시 읽기

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.generate(request)
```

- `@router.post`: Decorator를 사용해 URL과 Endpoint를 연결합니다.
- `ChatRequest`: Pydantic이 Request Body를 변환하고 검증합니다.
- `Depends`: FastAPI가 Service 생성과 주입을 담당합니다.
- `async`와 `await`: 비동기 AI Provider 호출을 기다리는 동안 Event Loop를 막지 않습니다.
- `ChatResponse`: 외부에 공개할 응답 계약을 고정합니다.
- `service.generate`: Router와 AI Provider 사이의 Business Logic을 Service가 담당합니다.

이 과정의 최종 결과물은 Database 없이 동작하는 AI API입니다. 저장 기능이 필요한 경우에는 이후 과정에서 Repository와 SQLAlchemy를 추가할 수 있습니다.


---

# Part 5. React → FastAPI → AI 요청 전체 연결

## 전체 흐름

학생은 이제 다음 요청을 코드 수준에서 추적할 수 있어야 한다.

```text
1. 사용자가 React에서 질문을 입력한다.
2. React가 JSON Request를 보낸다.
3. Uvicorn이 ASGI Application으로 요청을 전달한다.
4. FastAPI Router가 Method와 Path가 일치하는 Endpoint를 찾는다.
5. Pydantic이 Path / Query / Body를 검증하고 Python 객체로 만든다.
6. Endpoint가 Service에 처리를 위임한다.
7. Service가 필요한 Repository 또는 AI Provider Client를 호출한다.
8. 외부 I/O가 있다면 async/await로 결과를 기다린다.
9. Service가 결과를 업무 데이터로 정리한다.
10. Response Model이 외부에 공개할 데이터 계약을 확인한다.
11. FastAPI가 JSON Response를 만든다.
12. React가 결과를 받아 State를 변경하고 화면을 다시 렌더링한다.
```

중요한 것은 FastAPI가 이 모든 책임을 직접 수행하는 것이 아니라는 점이다.

```text
FastAPI
= HTTP 요청을 Python 애플리케이션에 연결하는 Framework

Service
= 업무 흐름과 규칙

Repository
= 저장소 접근

Provider Client
= 외부 AI 서비스와 통신

Pydantic Model
= 입력/출력 데이터 계약과 Validation

Uvicorn
= ASGI Application을 실제 네트워크에서 실행하는 Server
```

## 최종 확인

다음 질문에 답할 수 있어야 한다.

1. FastAPI와 Uvicorn은 같은 프로그램인가?
2. ASGI는 Framework인가 Server인가, 아니면 Interface 규약인가?
3. `GET /notes/10?detail=true`에서 `10`과 `detail`은 각각 무엇인가?
4. Request Body를 Dictionary 하나로 받는 것보다 Pydantic Model이 나은 이유는 무엇인가?
5. Request Model과 Response Model을 분리하는 이유는 무엇인가?
6. Router 안에 SQL과 AI Provider 호출을 모두 넣으면 어떤 문제가 생기는가?
7. Service Layer는 HTTP Status Code를 결정하는 계층인가?
8. Dependency Injection을 사용하면 테스트가 쉬워지는 이유는 무엇인가?
9. API Key를 `.env`에 둔다고 해서 `.env`를 Git에 Commit해도 되는가?
10. `async` 함수 안에서 Blocking I/O를 실행하면 왜 문제가 될 수 있는가?
11. 429와 일시적인 5xx는 왜 제한된 Retry 대상이 될 수 있는가?
12. 400 계열 오류를 무조건 Retry하면 안 되는 이유는 무엇인가?
13. Streaming Response가 일반 JSON Response와 다른 점은 무엇인가?
14. React에서 CORS 오류가 발생할 때 Backend가 정상 실행 중이어도 통신이 실패할 수 있는 이유는 무엇인가?
15. AI Provider를 바꿔도 Router를 거의 수정하지 않으려면 어떤 책임 분리가 필요한가?

## 실무 팁

- Endpoint는 **얇게(thin)** 유지하고 업무 로직은 Service로 옮긴다.
- Request와 Response Model을 분리하면 입력 계약과 공개 데이터 계약을 독립적으로 바꿀 수 있다.
- 외부 API 호출에는 Timeout을 반드시 둔다.
- Retry는 "실패하면 다시"가 아니라 재시도 가능한 오류와 횟수, Backoff 정책을 정해서 사용한다.
- Secret은 소스와 분리하고 로그에도 출력하지 않는다.
- 테스트에서는 실제 유료 AI Provider 대신 Fake/Stub 구현을 주입할 수 있도록 설계한다.
- HTTP 오류와 내부 Domain 오류를 구분하면 예외 처리와 테스트가 쉬워진다.
- FastAPI 자동 문서가 생성된다고 해서 API 설계를 생략하지 않는다. 계약을 먼저 설계한 뒤 문서가 그 계약을 표현하게 한다.

## 주의사항

- `async def`라고 적었다고 CPU 작업이 자동으로 빨라지는 것은 아니다.
- Router, Service, Repository를 파일 이름만 나눠놓고 책임을 섞으면 Layered Architecture가 아니다.
- Pydantic Validation을 통과했다고 업무 규칙까지 모두 검증된 것은 아니다.
- `response_model`은 문서용 표시만이 아니라 외부 응답 계약을 통제하는 데 사용한다.
- 개발 편의를 위해 CORS를 `*`로 열어 둔 설정을 그대로 운영에 사용하지 않는다.
- 외부 Provider의 예외 메시지와 Stack Trace를 사용자에게 그대로 반환하지 않는다.

## 참고자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- FastAPI Release Notes: https://fastapi.tiangolo.com/release-notes/
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Pydantic 공식 문서: https://docs.pydantic.dev/latest/
- Uvicorn 공식 문서: https://www.uvicorn.org/
- ASGI Specification: https://asgi.readthedocs.io/

## 관련 Wiki Link

[[AI 애플리케이션 아키텍처]]  
[[React]]  
[[Python]]  
[[HTTP]]  
[[REST API]]  
[[ASGI]]  
[[Uvicorn]]  
[[FastAPI]]  
[[Pydantic]]  
[[Dependency Injection]]  
[[Layered Architecture]]  
[[OpenAI API]]  
[[Ollama]]  
[[AI Integration]]
