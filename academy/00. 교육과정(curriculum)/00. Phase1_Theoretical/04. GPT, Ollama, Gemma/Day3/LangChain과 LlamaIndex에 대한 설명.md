둘 다 **LLM을 이용해서 실제 AI 애플리케이션을 만들기 위한 Python 프레임워크**라고 생각하면 됩니다.

다만 출발점이 조금 다릅니다.

> **LangChain = LLM을 여러 기능과 연결해서 AI 애플리케이션의 흐름을 만드는 데 강함**  
> **LlamaIndex = 내 문서/데이터를 LLM이 잘 찾아서 사용할 수 있게 만드는 데 강함**

---

# 1. 왜 이런 프레임워크가 필요한가?

OpenAI나 로컬 LLM을 직접 호출하는 것 자체는 어렵지 않습니다.

예를 들어:

```python
response = model.invoke("안녕하세요")
```

정도로 끝날 수도 있습니다.

하지만 실제 서비스를 만들려면 금방 복잡해집니다.

```text
사용자 질문
   ↓
질문 분석
   ↓
Vector DB 검색
   ↓
관련 문서 추출
   ↓
Prompt 생성
   ↓
LLM 호출
   ↓
결과 검증
   ↓
답변
```

그리고 여기에:

```text
PDF
DB
API
검색엔진
Memory
Tool
Agent
Vector DB
Embedding Model
```

같은 것들이 계속 붙습니다.

이걸 매번 직접 구현하기보다 쉽게 연결할 수 있도록 만든 프레임워크가 LangChain과 LlamaIndex입니다.

---

# 2. LangChain

[LangChain 공식 사이트](https://www.langchain.com/?utm_source=chatgpt.com)은 이름 그대로 처음에는 **LLM 작업들을 Chain처럼 연결하는 것**에서 출발했습니다.

예를 들어:

```text
사용자 질문
   ↓
Prompt
   ↓
LLM
   ↓
Output Parser
   ↓
결과
```

여기에 검색을 붙이면:

```text
사용자 질문
   ↓
Retriever
   ↓
Vector DB
   ↓
관련 문서
   ↓
Prompt
   ↓
LLM
   ↓
Answer
```

이런 구조를 만들 수 있습니다.

---

# 3. LangChain을 "레고"라고 생각하면 쉬움

LangChain은 여러 부품을 제공합니다.

```text
LangChain
│
├── Model
│     ├── OpenAI
│     ├── Anthropic
│     └── Ollama
│
├── Prompt
│
├── Document Loader
│
├── Text Splitter
│
├── Embedding
│
├── Vector Store
│
├── Retriever
│
├── Tool
│
└── Agent
```

개발자는 이걸 조립합니다.

예를 들어:

```text
PDF Loader
   ↓
Text Splitter
   ↓
Embedding
   ↓
Vector DB
```

그리고 질문이 들어오면:

```text
Question
   ↓
Retriever
   ↓
Vector DB
   ↓
Context
   ↓
LLM
   ↓
Answer
```

즉 **AI 애플리케이션을 구성하는 여러 부품을 연결하기 위한 프레임워크**라고 이해하면 됩니다.

---

# 4. LlamaIndex는?

[LlamaIndex 공식 사이트](https://www.llamaindex.ai/?utm_source=chatgpt.com)도 LLM 애플리케이션 프레임워크입니다.

그런데 이름에 `Index`가 들어가 있죠.

처음부터 특히 중요하게 다뤘던 문제가:

> **"내가 가지고 있는 데이터를 어떻게 LLM에게 잘 제공할 것인가?"**

였습니다.

예를 들어 회사에 이런 데이터가 있다고 해봅시다.

```text
회사 데이터

├── PDF
├── Word
├── Excel
├── Database
├── Notion
└── Web
```

LLM은 기본적으로 이 자료의 내용을 모릅니다.

그래서:

```text
내 데이터
   ↓
읽기
   ↓
구조화
   ↓
Chunk
   ↓
Embedding
   ↓
Index
   ↓
검색
   ↓
LLM
```

과정을 만들어야 합니다.

LlamaIndex가 특히 이 부분에 강점을 두고 발전했습니다.

---

# 5. 도서관으로 비유해보자

두 프레임워크의 차이를 이해하기 좋은 비유입니다.

엄청 큰 도서관이 있다고 해봅시다.

```text
도서관

📕 법률.pdf
📗 인사규정.pdf
📘 업무매뉴얼.pdf
📙 회의록.pdf
...
```

사용자가 묻습니다.

> "우리 회사 육아휴직 규정 알려줘."

### LlamaIndex의 관심사는

```text
어떤 책을 찾아야 하지?
        ↓
그 책의 어느 부분이지?
        ↓
관련 내용 가져오기
        ↓
LLM에게 전달
```

즉 **자료를 정리하고 검색하여 LLM에게 적절한 Context를 제공하는 것**이 핵심 관심사입니다.

### LangChain의 관심사는 좀 더 넓습니다.

```text
질문 받음
   ↓
질문 종류 판단
   ↓
문서 검색할까?
DB 조회할까?
API 호출할까?
   ↓
필요한 Tool 실행
   ↓
LLM 호출
   ↓
결과 검증
   ↓
답변
```

즉 **전체 AI 애플리케이션 Workflow**에 더 초점을 맞춘다고 생각하면 됩니다.

---

# 6. 그래서 RAG를 기준으로 보면

우리가 RAG를 직접 만든다고 해봅시다.

```text
PDF
 ↓
Text 추출
 ↓
Chunk
 ↓
Embedding
 ↓
Vector DB
```

사용자가 질문하면:

```text
Question
 ↓
Embedding
 ↓
Vector Search
 ↓
관련 Chunk
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

이 전체를 **둘 다 구현할 수 있습니다.**

여기서 중요한 점입니다.

> ❌ LangChain은 RAG, LlamaIndex는 RAG가 아니다.  
> ❌ LangChain은 Agent만 만들고 LlamaIndex만 RAG를 만든다.

이건 아닙니다.

**둘 다 RAG를 만들 수 있습니다.**

차이는 어느 부분을 중심으로 설계되어 발전했느냐에 가깝습니다.

---

# 7. 간단한 비교

||LangChain|LlamaIndex|
|---|---|---|
|핵심|LLM Application 구성|Data + LLM 연결|
|강점|Workflow, Tool, Agent, Integration|RAG, Indexing, Retrieval|
|RAG|가능|가능|
|Vector DB|지원|지원|
|Document 처리|지원|특히 강점|
|Agent|강함|지원|
|Tool 호출|강함|지원|
|복잡한 흐름|강함|가능|
|대표 이미지|AI 앱 조립도구|LLM용 데이터 검색/연결 계층|

다만 현재는 두 프로젝트 모두 기능 범위가 많이 넓어져서 **"LangChain은 이것만, LlamaIndex는 저것만"이라고 명확하게 나눌 수는 없습니다.**

---

# 8. LangGraph까지 나오면 관계가 더 명확해짐

여기서 이전에 공부했던 [LangGraph](https://www.langchain.com/langgraph?utm_source=chatgpt.com)가 등장합니다.

LangChain 생태계를 이렇게 보면 이해하기 쉽습니다.

```text
LangChain
   │
   ├── Model
   ├── Prompt
   ├── Retriever
   ├── Tool
   └── 기타 Component
             │
             ▼
         LangGraph
             │
             ▼
복잡한 Workflow / Agent 제어
```

LangGraph는 복잡한 AI 실행 흐름을 **Graph 형태로 정의하고 제어**하는 데 초점을 둡니다.

예를 들어 우리가 전에 이야기했던:

```text
Router
  │
  ├──→ RAG Node
  │
  ├──→ CAG Node
  │
  └──→ SQL/TAG Node
            ↓
        Evaluator
            ↓
         Answer
```

이런 구조가 LangGraph가 잘하는 영역입니다.

---

# 9. 그러면 LangChain과 LangGraph는 다른 건가?

네. 관련은 있지만 역할을 구분하는 게 좋습니다.

```text
LangChain
    ↓
LLM Application을 만들기 위한
Component / Integration

LangGraph
    ↓
그 Component들을 이용한
복잡하고 상태가 있는 실행 흐름 제어
```

비유하면:

```text
LangChain
= 레고 블록

LangGraph
= 레고 블록을 어떤 순서와 조건으로
  움직이게 할지 만드는 설계
```

정도로 생각할 수 있습니다.

---

# 10. LlamaIndex도 LangChain과 같이 사용할 수 있음

둘 중 하나만 선택해야 하는 것도 아닙니다.

예를 들어 상당히 자연스러운 구조가:

```text
               LangGraph
                   │
              전체 Workflow
                   │
          ┌────────┴────────┐
          │                 │
       RAG Node          SQL Node
          │
      LlamaIndex
          │
    Document Index
          │
      Vector DB
          │
       Retriever
          │
          └────────┐
                   ↓
                  LLM
```

입니다.

즉:

**LlamaIndex**

```text
문서
 ↓
Indexing
 ↓
Retrieval
 ↓
Context
```

를 담당시키고,

**LangGraph**

```text
질문
 ↓
Router
 ↓
어떤 기능 실행?
 ↓
RAG / SQL / Web / Tool
 ↓
Evaluation
 ↓
Answer
```

처럼 전체 흐름을 담당시킬 수도 있습니다.

---

# 11. 코드로 보면 감이 더 잘 옴

LangChain을 사용한다고 하면 개념적으로:

```python
loader = PDFLoader("manual.pdf")

documents = loader.load()

chunks = text_splitter.split_documents(documents)

vectorstore = VectorStore.from_documents(
    chunks,
    embedding_model
)

retriever = vectorstore.as_retriever()

context = retriever.invoke(question)

answer = llm.invoke(
    prompt.format(
        context=context,
        question=question
    )
)
```

입니다.

핵심은:

```text
Loader
 ↓
Splitter
 ↓
Embedding
 ↓
Vector Store
 ↓
Retriever
 ↓
Prompt
 ↓
LLM
```

여러 Component를 연결했다는 것입니다.

LlamaIndex는 같은 문제를 좀 더 **데이터 → Index → Query** 중심으로 추상화합니다.

개념적으로:

```python
documents = load_documents()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

response = query_engine.query(
    "육아휴직 규정이 어떻게 돼?"
)
```

처럼 사용할 수 있습니다.

내부적으로는 물론 이것보다 훨씬 많은 작업이 이루어집니다.

---

# 12. 그런데 왜 굳이 Framework를 사용하지?

사실 직접 구현해도 됩니다.

```python
PDF 읽기

→ 직접 Chunk

→ Embedding API 호출

→ pgvector 저장

→ SQL로 similarity search

→ Prompt 작성

→ LLM API 호출
```

충분히 가능합니다.

하지만 시스템이 커지면:

```text
OpenAI → Ollama 변경
Embedding Model 변경
Vector DB 변경
Retriever 변경
Reranker 추가
Tool 추가
Agent 추가
Memory 추가
Evaluation 추가
```

같은 요구사항이 계속 생깁니다.

Framework는 이런 구성요소들을 일정한 인터페이스로 묶어서 **교체하고 조합하기 쉽게 만들어주는 것**에 가치가 있습니다.

---

# 13. 지금 단계에서는 이렇게 기억하면 충분함

```text
LLM
= 실제 언어를 이해하고 생성하는 Model

        ↑

LangChain
= LLM + Tool + Prompt + Retriever 등을
  연결해서 AI Application을 만드는 Framework

        ↑

LangGraph
= 복잡한 실행 순서/조건/상태를
  Graph로 관리하는 Framework
```

그리고 다른 축에서:

```text
내 문서 / DB / 데이터
        ↓
    LlamaIndex
        ↓
Indexing / Retrieval
        ↓
      Context
        ↓
       LLM
```

입니다.

그래서 한 줄씩 외우면:

> **LangChain = LLM 애플리케이션을 조립하는 프레임워크**

> **LangGraph = 그 애플리케이션의 복잡한 실행 흐름을 제어하는 프레임워크**

> **LlamaIndex = 내 데이터를 LLM이 검색하고 활용하기 쉽게 연결하는 데 강점을 가진 프레임워크**

라고 정리하면 됩니다.

그리고 이 세 개를 이해하고 나면 **RAG 자체는 LangChain이나 LlamaIndex가 만들어주는 "기술 이름"이 아니라, `Retrieval → Context → Generation`이라는 아키텍처 패턴이고 이 프레임워크들이 그 구현을 편하게 해준다는 것**까지 구분해서 이해하는 게 중요합니다.