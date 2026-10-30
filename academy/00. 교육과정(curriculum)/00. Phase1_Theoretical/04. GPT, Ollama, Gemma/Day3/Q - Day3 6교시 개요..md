이 개요의 핵심은 **“LangChain이나 LlamaIndex를 배우기 전에, 얘들이 기존 구조에서 정확히 어디에 끼어드는지를 이해하자”**는 겁니다.

지금까지 만든 구조는 다음과 같습니다.

```text
React
↓
FastAPI
↓
AI Service
↓
OpenAI SDK 또는 httpx
↓
Cloud API / Ollama
↓
Model
```

여기서 각 계층의 역할은 비교적 명확합니다.

- `React`는 사용자 화면을 담당합니다.
    
- `FastAPI`는 HTTP 요청을 받고 응답하는 Backend입니다.
    
- `AI Service`는 “어떤 모델을 어떻게 호출할 것인가” 같은 AI 관련 비즈니스 로직을 담당합니다.
    
- `OpenAI SDK`나 `httpx`는 실제 외부 API에 요청을 보내는 수단입니다.
    
- `OpenAI API`, `Ollama` 같은 Provider/Runtime을 통해 실제 Model이 실행됩니다.
    

즉 지금까지는 **AI Framework 없이 우리가 필요한 연결을 직접 만든 것**입니다.

---

그런데 여기서 LangChain을 처음부터 사용했다고 생각해보면 문제가 하나 생깁니다.

예를 들어 코드가 이렇게 아주 간단해질 수도 있습니다.

```python
model = ChatOpenAI(...)
response = model.invoke("안녕하세요")
```

학생 입장에서는 “오, AI 호출이 이렇게 쉬운 거구나”라고 생각할 수 있습니다.

그런데 내부 구조를 배우지 않은 상태라면 바로 이런 질문이 생깁니다. 강의안에서도 이 부분을 강조하고 있습니다.

```text
Framework가 정확히 무엇을 대신하고 있는가?

Model은 어디에서 실행되는가?

HTTP Request는 누가 보내는가?

Provider가 바뀌면 무엇이 달라지는가?

Tool은 누가 실행하는가?

RAG의 Retrieval은 어디에서 일어나는가?
```

이 질문들이 중요한 이유는 **Framework가 실제 기능을 마법처럼 새로 만들어내는 것이 아니라, 우리가 직접 작성했어야 할 여러 연결 코드를 추상화해서 대신 제공하기 때문**입니다.

예를 들어 기존 구조가:

```text
FastAPI
↓
AI Service
↓
OpenAI SDK
↓
OpenAI API
```

였다면 LangChain을 도입했을 때는 개념적으로:

```text
FastAPI
↓
AI Service
↓
LangChain
↓
OpenAI Integration
↓
OpenAI API
```

처럼 중간에 하나의 계층이 들어오는 겁니다.

그러니까 LangChain이 OpenAI를 대체하는 것도 아니고, Model을 대체하는 것도 아닙니다.

**“Application과 AI 관련 여러 구성 요소 사이의 연결을 대신 정리해 주는 계층”**에 가깝습니다.

강의안에서도 AI Application Framework를 다음과 같이 설명하고 있습니다.

> Model을 Application의 다른 구성 요소와 연결하고 조합하는 개발을 돕는 Software Framework입니다.

---

## 그러면 Framework가 왜 필요한가?

단순한 프로그램에서는 사실 필요 없습니다.

예를 들어:

```text
사용자 입력
↓
OpenAI 호출
↓
응답
```

이 정도라면 그냥 OpenAI SDK를 직접 사용하는 게 더 간단합니다.

```python
client.responses.create(...)
```

한 번 호출하면 끝이니까요.

강의안에서도 **AI Application이라고 해서 반드시 LangChain이 필요한 것은 아니다**라고 명확히 설명합니다.

그런데 프로젝트가 커지기 시작하면 문제가 달라집니다.

예를 들어 요구사항이 이렇게 증가할 수 있습니다.

```text
OpenAI도 사용
Ollama도 사용
Gemini도 사용

PDF 검색
Vector DB 검색

Database 조회

Weather API 호출

Structured Output

Conversation 상태 관리

Tool Calling

Agent

Tracing

Evaluation
```

이걸 Framework 없이 전부 직접 구현할 수도 있습니다.

하지만 그러면 점점 이런 코드가 늘어나게 됩니다.

```python
if provider == "openai":
    ...

elif provider == "ollama":
    ...

elif provider == "google":
    ...
```

거기에 RAG까지 들어가면:

```text
PDF Loader
↓
Text Splitter
↓
Embedding
↓
Vector DB
↓
Retriever
↓
Prompt 생성
↓
Model 호출
```

까지 직접 연결해야 합니다.

Agent까지 들어가면:

```text
Model 판단
↓
Tool 선택
↓
Tool 실행
↓
결과 전달
↓
Model 재호출
```

같은 반복 구조도 직접 만들어야 합니다.

그래서 이런 **반복되는 연결 구조와 공통 문제들을 대신 처리해 주는 Framework가 등장한 것**입니다. 강의안에서도 Application이 복잡해질수록 Provider, Tool, Retrieval, Agent, Workflow 등의 연결 코드가 증가한다고 설명합니다.

---

## LangChain은 무엇을 해주는가?

아주 단순하게 표현하면:

```text
Model
+
Tool
+
RAG
+
Agent
+
여러 Provider
```

를 Application에서 **공통된 방식으로 연결하기 쉽게 해주는 Framework**입니다.

예를 들어 직접 작성하면:

```python
if provider == "openai":
    openai_call()

elif provider == "ollama":
    ollama_call()
```

이런 구조가 될 수 있는데,

LangChain에서는 개념적으로:

```python
model.invoke(...)
```

라는 비슷한 인터페이스를 유지하면서 실제 Provider Integration을 바꿀 수 있게 도와줍니다.

그래서 강의안에서 `Standard Model Interface`를 중요하게 설명하는 겁니다.

중요한 것은 이것이:

```text
OpenAI
Gemini
Anthropic
Ollama
```

를 같은 Model로 만들어준다는 뜻은 아닙니다.

단지 **Application이 이 모델들을 호출하는 방식을 어느 정도 통일해 주는 것**입니다.

각 Model이 제공하는 Context, Tool Calling, Structured Output, Multimodal 기능까지 똑같아지는 것은 아닙니다.

---

## LlamaIndex는 왜 같이 배우는가?

LlamaIndex 역시 AI Application Framework인데, 특히 다음 흐름을 이해할 때 많이 등장합니다.

```text
우리 회사 PDF
↓
Load
↓
Index
↓
Retrieve
↓
LLM Context
↓
Answer
```

즉 **“내 데이터를 어떻게 LLM과 연결할 것인가?”**라는 문제에 강하게 초점이 맞춰져 있습니다.

강의안에서는 이를 다음처럼 설명합니다.

```text
Load
↓
Index
↓
Retrieve
↓
LLM Context
```

그래서 입문 단계에서는 이렇게 이해하면 충분합니다.

```text
LangChain
→ Model / Tool / Agent / Retrieval 등을 폭넓게 연결

LlamaIndex
→ Data / Retrieval / RAG 중심의 연결에 강점
```

다만 현재 두 Framework 모두 기능이 많이 확장되어서 **“LangChain은 Agent만, LlamaIndex는 RAG만”**처럼 완전히 분리해서 이해하면 안 됩니다. 강의안에서도 두 Framework의 기능 범위가 겹친다는 점을 명시하고 있습니다.

---

## 이 강의에서 가장 중요한 부분

학생들에게는 저는 이렇게 설명하는 게 가장 이해가 잘 될 것 같습니다.

```text
Framework를 배우는 이유는
새로운 AI 기술을 배우기 위해서가 아니다.

우리가 이미 직접 만든 구조를
더 쉽게 연결하고 관리하기 위해서다.
```

예를 들어 이미 학생들이 이해한 구조가:

```text
FastAPI
↓
AI Service
↓
OpenAI SDK
↓
OpenAI API
```

라면 Framework를 배우고 나서는:

```text
FastAPI
↓
AI Service
↓
LangChain
↓
OpenAI Integration
↓
OpenAI API
```

로 볼 수 있습니다.

그리고 RAG를 붙이면:

```text
FastAPI
↓
AI Service
↓
LangChain / LlamaIndex
├── Document Loader
├── Text Splitter
├── Embedding
├── Vector Store
└── Retriever
↓
Model
```

Agent를 붙이면:

```text
FastAPI
↓
AI Service
↓
LangChain Agent
├── Model
├── Search Tool
├── DB Tool
└── File Tool
```

처럼 점점 Framework의 역할이 커지는 겁니다.

---

따라서 이 교시의 목표는 **“LangChain 코드 사용법을 많이 외우는 것”이 아닙니다.**

오히려 학생이 다음 질문에 답할 수 있으면 성공입니다.

```text
LangChain은 Model인가?
→ 아니다.

Ollama를 대체하는가?
→ 아니다.

FastAPI를 대체하는가?
→ 아니다.

OpenAI SDK를 무조건 대체해야 하는가?
→ 아니다.

그럼 왜 사용하는가?
→ Model, Tool, Retrieval, Agent,
   여러 Provider 등을 Application에서
   연결하고 조합하는 복잡성을 줄이기 위해 사용한다.
```

이게 바로 문서에서 말하는 **“Framework가 어떤 계층을 추상화하고 조합하는지 이해한다”**의 의미입니다.

한 문장으로 정리하면:

> **LangChain과 LlamaIndex는 AI 자체를 만들어주는 도구가 아니라, 이미 존재하는 Model·API·Data·Tool 등을 AI Application 안에서 더 쉽게 연결하도록 도와주는 Framework입니다.**

그리고 이걸 먼저 `SDK → HTTP → Provider → Model` 구조를 직접 배운 뒤에 배우는 이유는, 그래야 **“Framework가 무엇을 해주는지”가 보이기 때문**입니다.