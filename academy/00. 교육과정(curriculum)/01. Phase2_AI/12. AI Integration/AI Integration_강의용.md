# Phase 2 — 12. AI Integration(AI 서비스 아키텍처)

> **과목 목적**  
> 지금까지 배운 React, FastAPI, LLM, Prompt Engineering, RAG, Agent, OCR/Multimodal을 실제 서비스 안에서 어떻게 연결하는지 이해한다.  
> 특히 **OpenAI API, Ollama, LangChain**을 단순 사용법으로 외우지 않고, Provider가 바뀌어도 유지되는 AI Service Architecture를 설계하는 것이 목표다.

---

# 0. 이번 과목의 위치

지금까지의 학습은 각각의 기술을 이해하는 과정이었다.

```text
React
↓
FastAPI
↓
LLM
↓
Prompt Engineering
↓
Embedding
↓
Vector DB
↓
RAG
↓
Agent
↓
Fine-tuning
↓
OCR / Multimodal
```

이제 질문은 다음과 같다.

> 이 기술들을 실제 하나의 AI 서비스 안에서 어떻게 조립할 것인가?

이 과목의 핵심은 특정 SDK 문법이 아니다.

```text
AI Integration
=
Model
+
Backend
+
Data
+
Tool
+
State
+
Policy
+
Evaluation
+
Observability
```

를 실제 Application Architecture로 연결하는 것이다.

---

# 1. 전체 학습 지도

```text
사용자
↓
React / Client
↓
FastAPI
↓
Authentication / Authorization
↓
Request Validation
↓
AI Service
↓
Provider Interface
├─ OpenAI
├─ Ollama
└─ LangChain 기반 실행
↓
Model / Tool / RAG
↓
Validation
↓
Logging / Metrics / Trace
↓
Response
```

이번 과목은 크게 다음 순서로 진행한다.

```text
Part 1
AI Integration Architecture

Part 2
OpenAI API

Part 3
안전한 AI Service 설계

Part 4
LangChain

Part 5
Ollama

Part 6
Multi-provider Architecture

Part 7
종합 프로젝트
```

---

# 2. 학습 목표

이번 과목이 끝나면 다음 질문에 답할 수 있어야 한다.

1. AI Integration과 Model Training은 무엇이 다른가?
2. 왜 Browser에서 AI Provider를 직접 호출하면 안 되는가?
3. Router, Service, Provider Adapter의 책임은 어떻게 다른가?
4. OpenAI Responses API는 애플리케이션에서 어디에 위치하는가?
5. Structured Output과 Business Validation은 무엇이 다른가?
6. Tool Calling에서 Model과 Application의 책임은 어떻게 다른가?
7. Streaming은 일반 Response와 무엇이 다른가?
8. Timeout, Retry, Rate Limit을 왜 Provider Adapter나 Service에서 다뤄야 하는가?
9. Provider 추상화가 왜 필요한가?
10. LangChain은 언제 유용하고 언제 불필요한가?
11. LangChain Agent와 OpenAI의 Managed Agent Runtime은 어떤 선택지 차이가 있는가?
12. Ollama를 Local Provider로 어떻게 연결하는가?
13. OpenAI와 Ollama를 같은 Interface 뒤에 둘 때 무엇을 공통화하고 무엇을 남겨야 하는가?
14. AI Application에서 Test와 Observability가 왜 중요한가?
15. Provider 장애가 발생했을 때 Fallback을 무조건 자동 적용하면 안 되는 이유는 무엇인가?

---

# Part 1. AI Integration Architecture

---

# Unit 1. AI Integration이란 무엇인가?

## 1-1. Model을 사용하는 것과 서비스를 만드는 것은 다르다

Model 하나를 호출하는 코드는 간단할 수 있다.

```python
response = client.responses.create(...)
```

하지만 실제 서비스는 이것보다 훨씬 많은 책임을 가진다.

```text
사용자 인증
권한
입력 검증
Prompt 정책
Model 선택
비용 제한
Timeout
Retry
Tool 권한
RAG
출력 검증
Log
Monitoring
Evaluation
```

따라서:

```text
Model
≠
Application
```

이다.

---

## 1-2. 전체 구조

```text
User
↓
Frontend
↓
Backend API
↓
AI Service
↓
Provider Adapter
↓
AI Provider
```

예를 들어:

```text
React
↓
POST /api/chat
↓
FastAPI Router
↓
AIService
↓
OpenAIProvider
↓
OpenAI Responses API
```

또는:

```text
React
↓
POST /api/chat
↓
FastAPI Router
↓
AIService
↓
OllamaProvider
↓
Local Ollama
```

가 될 수 있다.

---

# Unit 2. Browser가 Provider를 직접 호출하면 안 되는 이유

잘못된 구조:

```text
React
↓
OpenAI API
```

문제:

```text
API Key 노출 위험
사용자별 권한 통제 어려움
비용 정책 통제 어려움
Prompt 정책 분산
로그 분산
Provider 교체 어려움
Tool 권한 통제 어려움
```

더 적절한 구조:

```text
React
↓
FastAPI
↓
AI Service
↓
Provider
```

Backend가 다음 책임을 가진다.

```text
Credential
Authentication
Authorization
Rate Limit
Prompt Policy
Provider Selection
Tool Policy
Output Validation
Audit Log
```

---

# Unit 3. Router / Service / Provider의 책임

다음 구조를 기본 Mental Model로 사용한다.

```text
Router
→ HTTP 세계

Service
→ Application 업무 세계

Provider
→ 외부 AI SDK / Runtime 세계
```

## 3-1. Router

Router가 알아야 하는 것:

```text
HTTP Method
Path
Request DTO
Response DTO
Status Code
Authentication
```

Router가 몰라도 되는 것:

```text
OpenAI SDK 세부 구조
Ollama Response 객체
Prompt 조합 세부사항
Model별 Parameter
```

## 3-2. Service

Service가 담당한다.

```text
질문 정규화
Prompt 정책
RAG 사용 여부
Tool 사용 정책
Provider 선택
Output Business Validation
```

## 3-3. Provider Adapter

Provider Adapter가 담당한다.

```text
SDK Client
Model ID
Provider별 Request 변환
Provider별 Response 변환
Streaming Event
Provider Error
Usage 변환
```

---

# Unit 4. 내부 계약을 먼저 정의하라

Provider SDK를 Application 전체로 퍼뜨리지 않는다.

예:

```python
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class AIMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class AIRequest:
    messages: tuple[AIMessage, ...]


@dataclass(frozen=True)
class AIUsage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class AIResult:
    text: str
    usage: AIUsage


class AIProvider(Protocol):
    async def generate(self, request: AIRequest) -> AIResult:
        ...
```

핵심:

```text
Application 내부 계약
≠
Provider SDK 객체
```

이다.

---

# Unit 5. Provider 기능은 완전히 같지 않다

Provider 추상화를 한다고 해서:

```text
OpenAI
=
Ollama
=
모든 기능 동일
```

이 되는 것은 아니다.

공통 영역:

```text
Text Generation
Messages
Streaming
Usage 일부
```

Provider별 차이:

```text
Tool 기능
Response ID
Hosted Tool
Context 관리
Model 옵션
Reasoning 옵션
Usage 상세 항목
```

따라서:

> 공통 기능은 Interface로 묶고, 고유 기능까지 억지로 동일하게 만들지 않는다.

---

# Part 2. OpenAI API Integration

---

# Unit 6. OpenAI API의 기본 위치

현재 OpenAI의 직접 API 통합은 Responses API를 중심으로 이해할 수 있다.

기본 흐름:

```text
Application
↓
OpenAI SDK
↓
Responses API
↓
Model
↓
Response Object
```

Python 예:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    input="AI Integration을 한 문장으로 설명해줘.",
)

print(response.output_text)
```

> 실제 수업에서는 공식 문서에서 현재 사용 가능한 Model ID를 다시 확인하고 `.env`에 고정한다.

> 현재 OpenAI Model Family에서는 `gpt-6-astra`가 가장 높은 Capability, `gpt-6-sol`이 높은 성능과 비용의 균형, `gpt-6-luna`가 효율적인 대량 처리 역할을 맡는다. 이 강의의 기본 API 예시는 비용과 반복 실습을 고려해 `gpt-6-luna`를 사용하고, 복잡한 비교 실습에서 Astra/Sol로 교체한다.


---

# Unit 7. Credential과 Settings

Credential은 Source Code에 직접 넣지 않는다.

나쁜 예:

```python
api_key = "sk-..."
```

좋은 방향:

```text
Environment Variable
↓
Settings
↓
Client 생성
```

예:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-6-luna"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )
```

`.env.example`:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-6-luna
```

주의:

```text
.env
→ Git Commit 금지

.env.example
→ Key 값 없이 Commit 가능
```

---

# Unit 8. Async OpenAI Client

FastAPI에서는 비동기 Client를 사용할 수 있다.

```python
from openai import AsyncOpenAI


def create_openai_client(settings) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
    )
```

Service:

```python
response = await client.responses.create(
    model=model,
    input="안녕하세요",
)
```

중요한 점:

```text
async
≠
AI 추론 자체가 빨라짐
```

이다.

`async`는 Network I/O 대기 중 Server가 다른 요청을 처리할 수 있도록 돕는다.

---

# Unit 9. Input / Instructions / Context

AI 요청은 단순 문자열 하나보다 여러 요소로 이해하는 것이 좋다.

```text
Instruction
+
User Input
+
Context
+
Tool Definition
↓
Model
```

예:

```text
Instruction
→ 회사 문서에서 확인된 내용만 답한다.

User Input
→ 출장비 한도는?

Context
→ RAG에서 검색된 출장 규정

Tool
→ 필요 시 사내 시스템 조회
```

이 모든 정보가 Model Context를 사용한다.

---

# Unit 10. Structured Output

텍스트 응답만 필요한 것이 아니다.

예:

```json
{
  "category": "billing",
  "confidence": 0.91,
  "summary": "중복 결제 문의"
}
```

애플리케이션이 이런 구조를 기대한다면:

```text
자연어 Prompt
↓
JSON처럼 답해주세요
```

보다:

```text
Schema 기반 Structured Output
```

이 더 안정적일 수 있다.

하지만 중요한 경계:

```text
Schema가 맞음
≠
내용이 사실
```

이다.

따라서:

```text
Model Schema Validation
+
Business Validation
```

이 모두 필요하다.

---

# Unit 11. Tool Calling

Tool Calling은:

```text
Model이 Python 함수를 직접 실행
```

하는 것이 아니다.

기본 흐름:

```text
Application
↓
Tool Definition 제공
↓
Model
↓
Tool Call 요청
↓
Application
↓
실제 Tool 실행
↓
Tool Result
↓
Model
↓
Final Response
```

Tool Definition 예:

```python
tool = {
    "type": "function",
    "name": "get_order_status",
    "description": "주문 ID로 주문 상태를 조회한다.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string"
            }
        },
        "required": ["order_id"],
        "additionalProperties": False,
    },
    "strict": True,
}
```

중요:

```text
Model
→ Tool 사용 요청

Application
→ 실제 실행 권한 보유
```

이다.

---

# Unit 12. Tool 실행 전 검증

모델이 다음을 요청했다고 하자.

```json
{
  "tool": "refund_order",
  "order_id": "ORD-100"
}
```

바로 실행하지 않는다.

```text
Tool Call
↓
Schema Validation
↓
사용자 권한
↓
업무 상태 확인
↓
금액 확인
↓
Human Approval 필요 여부
↓
실제 실행
```

특히 Side Effect가 있는 Tool은 더 엄격하다.

```text
메일 발송
결제
환불
삭제
권한 변경
외부 전송
```

---

# Unit 13. Streaming

일반 Response:

```text
Request
↓
전체 생성 완료
↓
한 번에 Response
```

Streaming:

```text
Request
↓
Delta
↓
Delta
↓
Delta
↓
완료
```

사용자 경험:

```text
전체 답을 기다림
vs
생성되는 즉시 화면 표시
```

FastAPI에서는 SSE나 StreamingResponse 등을 사용할 수 있다.

중요:

```text
Streaming 시작
↓
중간 오류 발생
```

하면 이미 HTTP Header가 전송됐을 수 있다.

따라서 Streaming Error Contract를 별도로 설계해야 한다.

---

# Unit 14. Conversation State

대화를 이어가는 방법은 여러 가지다.

```text
Application DB에 History 저장
Provider의 Conversation 기능 활용
이전 Response 연결
필요한 Message만 재구성
```

교육 과정에서는 기본적으로:

```text
Conversation 소유권
→ Application
```

을 중심으로 설계한다.

이유:

```text
Provider 교체
권한 확인
삭제 정책
감사
Context 관리
```

가 쉬워진다.

---

# Unit 15. Timeout / Retry / Rate Limit

AI Provider 호출은 실패할 수 있다.

대표 원인:

```text
Network
Timeout
429
5xx
Provider 장애
잘못된 Request
인증 오류
```

모든 오류를 Retry하면 안 된다.

예:

```text
401
→ Credential 문제
→ Retry해도 해결되지 않음

400
→ Request 문제
→ Retry해도 해결되지 않음

429
→ Backoff 후 Retry 검토

일시적 5xx
→ 제한적 Retry 검토
```

## 15-1. Retry는 유한해야 한다

```text
Retry 1
↓
대기
↓
Retry 2
↓
대기
↓
실패 반환
```

무한 Retry는:

```text
Latency 증가
비용 증가
Worker 점유
장애 증폭
```

으로 이어질 수 있다.

---

# Part 3. 안전한 AI Service Architecture

---

# Unit 16. OpenAIProvider Adapter

```python
from openai import AsyncOpenAI


class OpenAIProvider:
    def __init__(self, client: AsyncOpenAI, model: str):
        self._client = client
        self._model = model

    async def generate(self, request: AIRequest) -> AIResult:
        response = await self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in request.messages
            ],
        )

        usage = response.usage

        return AIResult(
            text=response.output_text,
            usage=AIUsage(
                input_tokens=usage.input_tokens if usage else 0,
                output_tokens=usage.output_tokens if usage else 0,
            ),
        )
```

Provider SDK 변화는 Adapter 내부에 가두는 것이 목표다.

---

# Unit 17. AI Service

```python
class AIService:
    def __init__(self, provider: AIProvider):
        self._provider = provider

    async def ask(self, question: str) -> AIResult:
        question = question.strip()

        if not question:
            raise ValueError("question is empty")

        request = AIRequest(
            messages=(
                AIMessage(
                    role="system",
                    content="정확하고 간결한 한국어로 답하세요.",
                ),
                AIMessage(
                    role="user",
                    content=question,
                ),
            )
        )

        return await self._provider.generate(request)
```

Service가 하는 일:

```text
입력 정규화
정책
Prompt
Provider 사용
결과 검증
```

---

# Unit 18. FastAPI Endpoint

Request/Response DTO:

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
```

Router:

```python
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    service: AIService = Depends(get_ai_service),
) -> ChatResponse:
    result = await service.ask(body.message)

    return ChatResponse(
        answer=result.text,
    )
```

핵심:

```text
Router
→ 얇게 유지

Service
→ 업무 규칙

Provider
→ SDK
```

---

# Unit 19. Dependency Injection

Application 조립은 한 곳에서 한다.

```text
Settings
↓
Client
↓
Provider
↓
Service
↓
Router
```

예:

```python
def get_ai_service() -> AIService:
    provider = OpenAIProvider(
        client=openai_client,
        model=settings.openai_model,
    )

    return AIService(provider)
```

실무에서는 매 요청마다 Client를 새로 만드는 방식보다 Application Lifetime에 맞게 공유·관리하는 방식을 검토한다.

---

# Unit 20. Test — 실제 AI를 항상 호출하지 않는다

잘못된 Unit Test:

```text
Test
↓
실제 OpenAI
↓
비용
Network
비결정성
```

더 좋은 구조:

```text
Test
↓
FakeProvider
↓
결정적인 응답
```

예:

```python
class FakeProvider:
    async def generate(self, request: AIRequest) -> AIResult:
        return AIResult(
            text="테스트 응답",
            usage=AIUsage(
                input_tokens=10,
                output_tokens=5,
            ),
        )
```

Service Test:

```python
async def test_ai_service():
    service = AIService(FakeProvider())

    result = await service.ask("테스트")

    assert result.text == "테스트 응답"
```

---

# Unit 21. Observability

AI Service는 다음을 관찰해야 한다.

```text
Request Count
Error Rate
Latency
Provider
Model
Input Token
Output Token
Tool Call
Retry Count
RAG Hit
Guardrail Result
```

하지만 다음을 Log에 그대로 남기면 안 될 수 있다.

```text
Password
API Key
주민등록번호
기밀 문서 전문
민감한 Prompt
```

따라서:

```text
Observability
+
Data Minimization
```

이 함께 필요하다.

---

# Unit 22. Evaluation

서비스가 동작한다고 품질이 보장되는 것은 아니다.

```text
Code Test
≠
AI Quality Test
```

따라서:

```text
Unit Test
Integration Test
Golden Dataset
Regression Test
Online Monitoring
```

을 조합한다.

예:

```text
Prompt 변경
↓
Golden Dataset 실행
↓
기존 Version과 비교
↓
Quality Gate
↓
배포
```

---

# Part 4. LangChain Integration

---

# Unit 23. LangChain은 무엇인가?

LangChain은 AI Application을 구성할 때:

```text
Model
Prompt
Tool
Agent
Middleware
State
```

등을 하나의 공통 Framework로 다룰 수 있도록 도와주는 도구다.

하지만 다음처럼 이해하면 안 된다.

```text
AI Application
=
반드시 LangChain
```

아니다.

## 23-1. 언제 직접 SDK가 더 단순한가?

다음과 같은 경우:

```text
OpenAI 한 번 호출
단순 Structured Output
Tool 1~2개
간단한 RAG
```

는 직접 SDK가 더 명확할 수 있다.

## 23-2. 언제 LangChain이 유용한가?

```text
여러 Provider
Tool
Agent Loop
Middleware
공통 Model Interface
Tracing
복잡한 Orchestration
```

을 빠르게 조립할 때 유용할 수 있다.

---

# Unit 24. 현재 LangChain의 핵심 관점

현재 LangChain Python 문서는 Agent를:

```text
Agent
=
Model
+
Harness
```

로 설명한다.

Harness에는:

```text
Prompt
Tool
Middleware
State
Guardrail
```

등이 포함된다.

즉 LangChain은 Model 자체가 아니라:

> Model 주변의 실행 구조를 구성하는 Framework

로 이해하는 것이 좋다.

---

# Unit 25. create_agent

현재 기본 Agent 생성 예:

```python
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """도시의 날씨 정보를 반환한다."""
    return f"{city}: 맑음"


agent = create_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    system_prompt="간결한 한국어로 답하세요.",
)
```

호출:

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "서울 날씨를 확인해줘",
            }
        ]
    }
)
```

> Model ID는 LangChain 공식 문서 예시일 뿐 수업용 Model은 실습 전에 다시 고정한다.

---

# Unit 26. LangChain Tool

Python Function을 Tool로 등록할 수 있다.

```python
from langchain.tools import tool


@tool
def search_document(query: str) -> str:
    """사내 문서에서 query와 관련된 내용을 검색한다."""
    return "검색 결과"
```

중요:

```text
Decorator
→ Tool Metadata 생성

Model
→ Tool 설명과 Schema를 봄

Python 함수 내부 Source
→ Model이 자동으로 읽는 것이 아님
```

---

# Unit 27. LangChain과 Agent Runtime

Agent Loop:

```text
User
↓
Model
↓
Tool 필요?
├─ No → Final
└─ Yes
   ↓
Tool Call
↓
Tool Result
↓
Model
↓
반복
```

LangChain의 Agent는 이 Loop를 실행하는 Harness를 제공한다.

하지만 중요한 업무에서는:

```text
Tool Permission
Human Approval
Write Protection
Timeout
Stop Condition
```

을 별도로 설계해야 한다.

---

# Unit 28. LangChain과 LangGraph의 관계

현재 LangChain Agent는 LangGraph 위에서 동작한다.

개념적으로:

```text
LangChain
→ 높은 수준의 Agent API

LangGraph
→ 더 낮은 수준의 Workflow / State Orchestration
```

따라서:

```text
간단 Agent
→ LangChain create_agent

복잡한 상태 전이
→ LangGraph 검토
```

처럼 볼 수 있다.

그러나 이번 과목의 핵심은 LangGraph 사용법이 아니라:

> Framework를 사용해도 Application 책임은 사라지지 않는다.

는 점이다.

---

# Unit 29. OpenAI 직접 Tool Calling vs LangChain Agent

### OpenAI Responses 직접

```text
Application
↓
Responses API
↓
Tool Call
↓
Application Tool 실행
↓
Response 계속
```

장점:

```text
Provider 기능 직접 사용
구조가 명확
추상화가 적음
```

### LangChain Agent

```text
Application
↓
LangChain Harness
↓
Model
↓
Tool Loop
```

장점:

```text
Provider 교체
Agent Middleware
Tool 통합
공통 Interface
```

어느 하나가 항상 더 좋은 것은 아니다.

---

# Unit 30. OpenAI Managed Agent Runtime과 LangChain

현재 OpenAI는 Agent Loop 자체를 관리하는 Agents API도 제공한다.

개념적으로 세 가지 선택지를 구분한다.

```text
1. Responses API 직접
→ Application이 Loop를 직접 제어

2. OpenAI Agents API
→ OpenAI Managed Harness 사용

3. LangChain Agent
→ LangChain Harness 사용
```

선택 기준:

```text
Provider 종속성
Control 수준
Tool 생태계
State
Observability
운영 요구
팀 숙련도
```

---

# Part 5. Ollama Local LLM Integration

---

# Unit 31. Ollama의 역할

Ollama는 Local 또는 자체 관리 환경에서 Model을 실행할 수 있게 해주는 Runtime / Serving 도구다.

구분해야 한다.

```text
Gemma / Qwen / Llama
→ Model

Ollama
→ Model Runtime / Server

FastAPI
→ Application Backend

LangChain
→ Application Framework
```

---

# Unit 32. Ollama 기본 구조

```text
Application
↓
Ollama Client / REST
↓
Ollama Server
↓
Local Model
```

기본 Local 주소 예:

```text
http://localhost:11434
```

---

# Unit 33. Ollama Chat API

대표 REST Endpoint:

```text
POST /api/chat
```

예:

```python
import httpx


async def chat_with_ollama(
    model: str,
    question: str,
) -> str:
    async with httpx.AsyncClient(
        base_url="http://localhost:11434",
        timeout=60.0,
    ) as client:
        response = await client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                "stream": False,
            },
        )

        response.raise_for_status()
        data = response.json()

    return data["message"]["content"]
```

---

# Unit 34. Ollama Streaming

Streaming에서는 응답이 여러 조각으로 전달된다.

```text
Chunk
Chunk
Chunk
...
done
```

REST Stream을 직접 처리하는 경우 NDJSON 구조를 이해해야 한다.

```python
import json
import httpx


async def stream_ollama(model: str, question: str):
    async with httpx.AsyncClient(
        base_url="http://localhost:11434",
        timeout=60.0,
    ) as client:
        async with client.stream(
            "POST",
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                "stream": True,
            },
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line:
                    continue

                item = json.loads(line)

                if "error" in item:
                    raise RuntimeError(item["error"])

                content = item.get(
                    "message",
                    {},
                ).get("content", "")

                if content:
                    yield content

                if item.get("done") is True:
                    return
```

---

# Unit 35. Ollama Python Client

Python Client를 사용할 수도 있다.

```python
from ollama import AsyncClient


client = AsyncClient(
    host="http://localhost:11434"
)

response = await client.chat(
    model="YOUR_MODEL_NAME",
    messages=[
        {
            "role": "user",
            "content": "안녕하세요",
        }
    ],
    stream=False,
)

print(response.message.content)
```

SDK와 REST 중 하나가 무조건 정답은 아니다.

```text
SDK
→ 편리한 Typed Interface

REST
→ Transport를 직접 제어
```

---

# Unit 36. Ollama OpenAI Compatibility

Ollama는 일부 OpenAI 호환 Endpoint도 제공한다.

이 기능은 기존 OpenAI Client 기반 Application을 Local Runtime으로 연결할 때 편리할 수 있다.

하지만:

```text
OpenAI Compatibility
=
OpenAI API 모든 기능 100% 동일
```

은 아니다.

지원 기능과 차이는 공식 문서에서 확인한다.

따라서:

```text
Provider Adapter
```

를 유지하는 것이 안전하다.

---

# Unit 37. OllamaProvider

```python
from ollama import AsyncClient


class OllamaProvider:
    def __init__(
        self,
        client: AsyncClient,
        model: str,
    ):
        self._client = client
        self._model = model

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResult:
        response = await self._client.chat(
            model=self._model,
            messages=[
                {
                    "role": m.role,
                    "content": m.content,
                }
                for m in request.messages
            ],
            stream=False,
        )

        return AIResult(
            text=response.message.content,
            usage=AIUsage(
                input_tokens=response.prompt_eval_count or 0,
                output_tokens=response.eval_count or 0,
            ),
        )
```

---

# Unit 38. Local Model의 운영 특성

Cloud API와 Local Model은 비용 구조가 다르다.

Cloud:

```text
API Usage Cost
+
Network
```

Local:

```text
Hardware
Power
Memory
GPU
Model Loading
Concurrency
Maintenance
```

따라서:

```text
Local = 무료
```

이라고 단순화하면 안 된다.

---

# Unit 39. Local Model Readiness

Local AI Service는 단순 HTTP Health Check만으로 충분하지 않을 수 있다.

```text
Liveness
→ Process 살아 있음?

Readiness
→ 실제 요청 처리 가능?
```

Readiness 예:

```text
Ollama Server 연결 가능
Model 설치됨
Model Load 가능
필요 Memory 확보
```

---

# Part 6. Multi-provider Architecture

---

# Unit 40. Provider Factory

Application에서 Provider를 선택할 수 있다.

```python
def create_provider(settings):
    if settings.ai_provider == "openai":
        return OpenAIProvider(
            client=create_openai_client(settings),
            model=settings.openai_model,
        )

    if settings.ai_provider == "ollama":
        return OllamaProvider(
            client=AsyncClient(
                host=settings.ollama_base_url,
            ),
            model=settings.ollama_model,
        )

    raise ValueError("Unsupported provider")
```

핵심:

```text
Router
→ Provider 이름을 알 필요 없음
```

이다.

---

# Unit 41. Capability Matrix

Provider별 지원 기능이 다르기 때문에 Capability를 기록할 수 있다.

예:

| Capability | OpenAI | Ollama |
|---|---:|---:|
| Text Generation | O | O |
| Streaming | O | O |
| Function Tool | Model/환경에 따라 | Model에 따라 |
| Hosted Web Search | O | X 또는 별도 구현 |
| File Search | O | 별도 RAG 필요 |
| Local Execution | X | O |

이 표는 고정 정답이 아니다.

Model과 Runtime Version에 따라 달라지므로 실제 운영 환경에서 다시 검증한다.

---

# Unit 42. Provider Fallback

예:

```text
OpenAI 실패
↓
Ollama로 자동 전환
```

이 단순해 보이지만 위험할 수 있다.

왜냐하면:

```text
Model 성능 차이
Tool 지원 차이
Context 차이
정책 차이
Data Boundary 차이
```

가 있기 때문이다.

따라서 Fallback은:

```text
기능 등가성 확인
Data 정책 확인
Quality Gate
사용자 고지 필요 여부
```

를 검토해야 한다.

---

# Unit 43. Provider Routing

모든 요청을 같은 Model로 처리할 필요는 없다.

예:

```text
단순 분류
→ 작은 Model

복잡한 분석
→ 큰 Model

민감 문서
→ Local Model

최신 Web 정보
→ Tool 지원 Cloud Model
```

그러나 Routing 자체도 평가해야 한다.

```text
Routing Accuracy
Cost
Latency
Fallback
```

---

# Unit 44. Security Boundary

AI Integration에서 다음 경계를 분리한다.

```text
Untrusted User Input
↓
Application

Untrusted Document
↓
Application

Model Output
↓
Untrusted until validated

Tool Call
↓
Request, not authority
```

즉:

```text
Model이 말했다
=
실행 권한
```

이 아니다.

---

# Unit 45. Prompt Injection 대응

Prompt Injection은 다음 위치에서 들어올 수 있다.

```text
User Prompt
Retrieved Document
Web Page
OCR Text
Tool Result
```

기본 방어:

```text
Instruction / Data 분리
Tool Permission
Allowed Tool 제한
Output Validation
Sensitive Data 최소화
Human Approval
```

---

# Unit 46. Cost와 Latency Budget

하나의 요청에 여러 단계를 쓰면:

```text
RAG
+
Reranker
+
Model
+
Tool
+
Model
```

Latency와 Cost가 누적된다.

따라서 요청 하나의 예산을 설계한다.

예:

```text
Retrieval     300 ms
Reranking     200 ms
Model       2,000 ms
Tool          500 ms
Final Model 1,500 ms
--------------------
Budget      4,500 ms
```

실제 값은 측정한다.

---

# Unit 47. Context Budget

Model Context는 제한된 자원이다.

```text
System
User
History
RAG
Tool Result
Output Reserve
```

가 같은 예산을 사용한다.

따라서:

```text
History 전체
+
검색 문서 전체
+
Tool 결과 전체
```

를 무조건 넣는 방식은 좋지 않다.

---

# Unit 48. Error Contract

Provider 오류를 그대로 사용자에게 노출하지 않는다.

내부 Error:

```text
ProviderTimeout
ProviderRateLimited
ProviderUnavailable
InvalidProviderResponse
ToolExecutionError
```

HTTP Response 예:

```json
{
  "code": "AI_TEMPORARILY_UNAVAILABLE",
  "message": "AI 응답을 생성하지 못했습니다. 잠시 후 다시 시도해주세요."
}
```

Stack Trace, API Key, 내부 URL은 숨긴다.

---

# Part 7. 종합 프로젝트

---

# Unit 49. 프로젝트 목표

최종 프로젝트:

> **Multi-provider 안전한 AI Chat Platform**

기능:

```text
React Client
FastAPI Backend
OpenAI Provider
Ollama Provider
Provider 선택
Streaming
Conversation
Tool
Logging
Test
```

---

# Unit 50. 전체 Architecture

```text
[React]

Chat UI
Provider 선택
Streaming 표시

        ↓ HTTPS

[FastAPI]

Authentication
↓
Router
↓
AI Service
↓
Policy
↓
Provider Interface
├─ OpenAIProvider
└─ OllamaProvider
↓
Model

        +

Conversation Repository
Tool Gateway
RAG
Observability
```

---

# Unit 51. Directory 구조

```text
app/
├── main.py
├── core/
│   └── config.py
├── api/
│   ├── chat.py
│   └── schemas.py
├── ai/
│   ├── models.py
│   ├── provider.py
│   ├── openai_provider.py
│   ├── ollama_provider.py
│   └── service.py
├── tools/
│   └── registry.py
├── repositories/
│   └── conversation.py
└── observability/
    └── logging.py
```

---

# Unit 52. Request Trace

하나의 요청을 끝까지 추적한다.

```text
1. User
2. React
3. POST /chat
4. Authentication
5. Request Validation
6. AIService
7. Prompt / Context
8. Provider 선택
9. Model
10. Tool 필요 여부
11. Tool Permission
12. Tool 실행
13. Model Final
14. Output Validation
15. Usage 기록
16. Conversation 저장
17. HTTP Response
18. React Rendering
```

---

# Unit 53. Streaming Trace

```text
User
↓
POST /chat/stream
↓
FastAPI
↓
AI Service
↓
Provider Stream
↓
Delta
↓
SSE / Stream
↓
React
↓
화면 갱신
```

취소도 고려한다.

```text
사용자가 화면 이동
↓
Client Cancel
↓
Server가 Provider Stream 종료 시도
```

---

# Unit 54. Tool Gateway

Tool 실행을 한 곳에 모은다.

```text
Model Tool Call
↓
Tool Gateway
↓
Schema
↓
Permission
↓
Approval
↓
Execution
↓
Audit
```

Model이 Tool 함수를 직접 소유하도록 만들지 않는다.

---

# Unit 55. Health Check

```text
GET /health/live
→ Process 살아 있음

GET /health/ready
→ Provider 사용 가능
```

Readiness는 Provider별로 다를 수 있다.

```text
OpenAI
→ Credential / Network

Ollama
→ Server / Model
```

---

# Unit 56. Test 전략

```text
Unit Test
→ Service + Fake Provider

Contract Test
→ Provider Adapter

Integration Test
→ FastAPI + Fake Provider

Optional Live Test
→ 실제 OpenAI / Ollama

E2E
→ React → FastAPI → Provider
```

실제 Provider를 호출하는 Test는 별도 환경에서 실행한다.

---

# Unit 57. Observability Dashboard

관찰할 항목:

```text
Request Count
Success Rate
Error Rate
P50 / P95 Latency
Provider
Model
Token
Cost
Retry
Tool Count
Streaming Error
RAG Hit
```

---

# Unit 58. 실습 1 — Architecture 책임 분류

다음 기능을 어디에 둘지 분류한다.

```text
API Key
Prompt Template
HTTP Status Code
OpenAI SDK
Ollama URL
Tool Permission
Conversation Ownership
Response Schema
```

선택:

```text
Frontend
Router
Service
Provider
Repository
Runtime
```

---

# Unit 59. 실습 2 — OpenAI 직접 연동

목표:

```text
FastAPI
↓
OpenAI Responses API
↓
JSON Response
```

확인:

```text
Credential
Async
Timeout
Response 변환
```

---

# Unit 60. 실습 3 — FakeProvider

목표:

```text
실제 API 없이
Service Test
```

검증:

```text
Network 없음
API Key 없음
항상 같은 결과
```

---

# Unit 61. 실습 4 — LangChain Agent

Tool:

```text
get_project_status
```

Model이 Tool을 호출하는 Trace를 확인한다.

검증:

```text
Tool Description
Argument
Tool Result
Final Answer
```

---

# Unit 62. 실습 5 — Ollama Provider

목표:

```text
AIProvider
↓
OllamaProvider
↓
Local Model
```

같은 Service가 Provider 교체 후에도 동작하는지 확인한다.

---

# Unit 63. 실습 6 — Provider Contract Test

같은 Test를 다음에 적용한다.

```text
FakeProvider
OpenAIProvider
OllamaProvider
```

확인:

```text
AIResult 반환
Text 존재
Usage 음수 아님
Exception Mapping
```

---

# Unit 64. 실습 7 — Streaming

확인:

```text
첫 Token / Delta
중간 Delta
완료
중간 Error
Client Cancel
```

---

# Unit 65. 실습 8 — 장애 분석

다음 상황을 분류한다.

```text
401
429
500
Timeout
Ollama Server Down
Model Missing
Tool Failure
Schema Validation Failure
```

각각:

```text
Retry?
User Message?
Log?
Alert?
```

를 정한다.

---

# Unit 66. 실습 9 — Provider Routing

다음 요구사항에 Provider를 선택한다.

```text
민감 문서 요약
일반 Chat
Tool이 필요한 업무
Offline 환경
비용 최소화
```

그리고 선택 이유를 적는다.

---

# Unit 67. 실습 10 — 종합 Trace

한 요청에 대해 다음을 기록한다.

```text
request_id
user_id
provider
model
prompt_version
input_tokens
output_tokens
retrieval_used
tool_calls
latency_ms
status
error_code
```

단 민감 원문은 불필요하게 기록하지 않는다.

---

# Unit 68. Best Practice

## 68-1. Provider SDK를 Router에 넣지 않는다

```text
Router
→ Service
→ Provider
```

구조를 유지한다.

## 68-2. Provider 교체를 과도하게 추상화하지 않는다

공통 기능만 Interface로 만든다.

## 68-3. Model ID를 코드에 흩뿌리지 않는다

```text
Settings
```

에서 관리한다.

## 68-4. Prompt도 Version 관리한다

```text
Prompt v1
Prompt v2
```

변경 후 Regression Test를 수행한다.

## 68-5. AI Output은 신뢰하지 않는다

```text
Schema
Business Rule
Permission
Grounding
```

을 검증한다.

## 68-6. Tool Call은 실행 권한이 아니다

```text
Tool Call
→ Request

Runtime
→ Authority
```

이다.

## 68-7. Retry를 제한한다

무한 Retry 금지.

## 68-8. Framework는 문제를 해결할 때만 사용한다

LangChain을 사용하는 이유를 설명할 수 있어야 한다.

## 68-9. Local Model도 운영 비용이 있다

Hardware, Memory, Concurrency, Maintenance를 고려한다.

## 68-10. Test와 Evaluation을 분리하지 않는다

```text
Software Correctness
+
AI Quality
```

를 모두 본다.

---

# Unit 69. 자주 하는 오해

## 오해 1

```text
OpenAI API를 호출하면
AI Application이 완성된다.
```

아니다.

## 오해 2

```text
LangChain을 쓰면
Architecture 설계를 안 해도 된다.
```

아니다.

## 오해 3

```text
Ollama를 쓰면 비용이 없다.
```

아니다.

## 오해 4

```text
Provider Interface를 만들면
모든 Provider 기능이 같아진다.
```

아니다.

## 오해 5

```text
Tool Calling
=
Model이 함수를 직접 실행
```

아니다.

## 오해 6

```text
Streaming
=
속도가 빨라짐
```

항상 그렇지 않다.

첫 출력까지의 체감은 좋아질 수 있지만 전체 생성 시간이 반드시 줄어드는 것은 아니다.

## 오해 7

```text
async
=
Model 추론 속도 향상
```

아니다.

---

# Unit 70. 최종 Mental Model

```text
User
↓
Client
↓
Backend
↓
Authentication / Authorization
↓
Validation
↓
AI Service
↓
Context / Prompt / RAG
↓
Provider Interface
├─ OpenAI
├─ Ollama
└─ LangChain Harness
↓
Model
↓
Tool Call?
↓
Runtime Validation
↓
Tool
↓
Model
↓
Output Validation
↓
Logging / Evaluation
↓
Response
```

가장 중요한 문장:

> **AI Integration의 핵심은 Model을 호출하는 코드가 아니라, Model을 안전하고 교체 가능하며 평가 가능한 Application 구성요소로 만드는 것이다.**

---

# Unit 71. 자기 점검

1. AI Integration과 Fine-tuning은 무엇이 다른가?
2. Browser에서 Provider를 직접 호출하면 왜 위험한가?
3. Router / Service / Provider Adapter를 구분할 수 있는가?
4. Provider Interface를 왜 만드는가?
5. OpenAI Responses API는 어느 Layer에 위치하는가?
6. Structured Output과 Business Validation의 차이는 무엇인가?
7. Tool Call과 실제 Tool 실행은 무엇이 다른가?
8. Streaming에서 중간 오류를 별도로 고려해야 하는 이유는 무엇인가?
9. Conversation History를 Application이 소유하면 어떤 장점이 있는가?
10. 어떤 오류를 Retry하면 안 되는가?
11. FakeProvider가 왜 필요한가?
12. LangChain을 반드시 사용하지 않아도 되는 이유는 무엇인가?
13. `create_agent`의 Model / Tool / System Prompt 역할을 설명할 수 있는가?
14. LangChain과 LangGraph의 차이를 높은 수준에서 설명할 수 있는가?
15. OpenAI 직접 Tool Calling과 LangChain Agent의 차이는 무엇인가?
16. Ollama는 Model인가 Runtime인가?
17. Ollama `/api/chat`은 무엇을 하는가?
18. OpenAI Compatibility를 100% 동일 API라고 보면 안 되는 이유는 무엇인가?
19. Provider Fallback이 위험할 수 있는 이유는 무엇인가?
20. AI Integration에서 어떤 Metric을 Monitoring해야 하는가?

---

# Unit 72. 참고자료

## OpenAI

- OpenAI API Documentation
  - https://developers.openai.com/api/docs
- Responses API
  - https://developers.openai.com/api/reference/resources/responses
- Function Calling
  - https://developers.openai.com/api/docs/guides/function-calling
- Tools
  - https://developers.openai.com/api/docs/guides/tools
- Agents API
  - https://developers.openai.com/api/docs/guides/agents-api

## LangChain

- LangChain Overview
  - https://docs.langchain.com/oss/python/langchain/overview
- LangChain Agents
  - https://docs.langchain.com/oss/python/langchain/agents
- LangGraph
  - https://docs.langchain.com/oss/python/langgraph/overview

## Ollama

- Ollama API
  - https://docs.ollama.com/api
- Ollama Chat API
  - https://docs.ollama.com/api/chat
- OpenAI Compatibility
  - https://docs.ollama.com/api/openai-compatibility

> Provider API, Model ID, Framework API는 변경 속도가 빠르므로 실제 수업 직전에 공식 문서를 다시 확인한다.

---

# Unit 73. 관련 Wiki Link

```text
[[AI Application Architecture]]
[[FastAPI]]
[[OpenAI API]]
[[Responses API]]
[[Tool Calling]]
[[Structured Output]]
[[LangChain]]
[[LangGraph]]
[[Ollama]]
[[Provider Pattern]]
[[Dependency Injection]]
[[Streaming]]
[[Observability]]
[[Evaluation]]
[[AI Agent]]
[[RAG]]
```

---

# Unit 74. Knowledge 저장 위치 제안

```text
Knowledge/
└── Phase2/
    └── AI_Integration/
        ├── AI Integration.md
        ├── Provider Adapter.md
        ├── OpenAI Responses API.md
        ├── Tool Calling.md
        ├── LangChain.md
        ├── LangChain Agent.md
        ├── Ollama Integration.md
        ├── Multi-provider Architecture.md
        ├── AI Service Testing.md
        └── AI Observability.md
```

---

# Unit 75. 다음 과목과 연결

이번 과목에서 우리는:

```text
Model
+
Backend
+
Provider
+
Tool
+
State
+
Evaluation
```

을 서비스로 연결했다.

다음 **Document AI**에서는 이 Architecture 위에 실제 문서 처리 Pipeline을 올린다.

```text
Upload
↓
Parsing / OCR
↓
Document Structure
↓
Chunk
↓
Embedding
↓
Vector DB
↓
RAG
↓
LLM
↓
Citation
↓
Agent / Workflow
↓
Document Output
```

즉 다음 과목은 지금까지 배운 전체 내용을 **문서 자동화 플랫폼 하나로 통합하는 마지막 응용 단계**다.
