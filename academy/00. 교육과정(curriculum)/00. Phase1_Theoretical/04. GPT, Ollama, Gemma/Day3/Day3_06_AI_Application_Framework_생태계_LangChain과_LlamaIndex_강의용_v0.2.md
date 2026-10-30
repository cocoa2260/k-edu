# Day 3 - 6교시. AI Application Framework 생태계 — LangChain과 LlamaIndex (강의용 v0.2)

> **교시의 역할:** 직접 AI API를 호출할 수 있게 된 학습자가, 복잡한 AI Application에서 Framework가 **어느 책임을 덜어 주고 어떤 책임은 남기는지** 판단하는 이론·설계 수업이다.  
> **교육내용 기준:** `00. 교육과정(curriculum).zip` 계열의 Day3 6교시 원문과 해당 과정의 보충 Q&A.  
> **시연 범위:** 동작하는 LangChain·LlamaIndex 프로그램을 만드는 실습이 아니라, 구성 요소·데이터 흐름·도입 판단을 검토한다. 실제 API 이름·설치·버전 호환성은 별도 실행 검증이 필요하다.

## 개요 — 이제 질문은 ‘모델 호출 방법’이 아니라 ‘여러 기능을 어떻게 연결할까?’

Day1~Day2에서 학습자는 FastAPI가 OpenAI SDK나 Ollama API에 요청을 전달하고 응답을 받는 프로그램을 만들었습니다. Day3 5교시까지는 어떤 Model을 사용할지도 근거를 들어 판단했습니다. 이번 시간에는 그 결과를 출발점으로 삼습니다. HTTP 요청 형식, 모델 실행 방식, Model Card, Parameter 크기를 처음부터 다시 가르치지는 않습니다.

**하나의 Model 호출**은 전체 AI Application 중 작은 부분일 수 있습니다. 예를 들어 사용자가 회사 내부 규정에 관해 질문했다고 생각해 봅시다. 단순히 질문을 Model에 전송하는 것 외에 ‘규정 문서를 찾아야 하는가’, ‘직원의 권한으로 볼 수 있는 자료인가’, ‘검색 근거가 부족한가’, ‘추가 조회가 필요한가’를 결정해야 할 수도 있습니다.

```text
사용자 질문
   │
   ▼
Application의 작업 판단
   ├── 필요한 사내 규정 검색
   ├── 권한을 확인한 업무 데이터 조회
   ├── Model에 전달할 Context 구성
   └── 결과 검증 및 응답
            │
            ▼
         사용자
```

처음에는 이러한 연결 코드를 직접 작성할 수 있습니다. 다만 자료 출처와 Provider가 늘고 반복적으로 재사용해야 하는 기능이 생기면, 공통 구성 요소와 흐름을 제공하는 Framework가 유리해질 수 있습니다. **LangChain과 LlamaIndex는 그 문제를 해결하기 위해 사용되는 AI Application Framework 생태계의 사례**입니다.

이번 교시의 핵심 질문은 세 가지입니다.

1. **어떤 복잡성이 생겼을 때** Framework를 검토해야 하는가?
2. LangChain·LlamaIndex는 **무엇을 제공하고, 무엇은 대신하지 않는가?**
3. 고정된 실행 순서, Retrieval, Tool, Agent 중 **어떤 접근이 요구사항에 맞는가?**

---

# 1. 학습 목표와 완료 기준

강의를 마치면 학생은 다음을 할 수 있어야 합니다.

1. 단일 Model 호출과 여러 구성 요소를 묶은 AI Application을 구분한다.
2. AI Application Framework를 도입할 때 줄어드는 코드와 추가되는 관리 부담을 각각 설명한다.
3. Model·Runtime·Web API Framework·AI Application Framework의 **책임 경계**를 그린다.
4. LangChain의 Model Interface·Tool·Agent·Retrieval 관련 역할을 설명한다.
5. LangGraph와 LangSmith가 LangChain과 **서로 다른 문제를 다룬다**는 점을 구분한다.
6. LlamaIndex의 데이터 연결·Indexing·Retrieval 중심 구성을 설명한다.
7. LangChain과 LlamaIndex의 기능이 겹치며, 목적에 따라 선택·조합할 수 있음을 설명한다.
8. Tool 호출을 **제안하는 Model**과 Tool을 **실제로 실행하는 프로그램**의 역할을 구분한다.
9. 고정 Workflow와 Agent가 각각 적절한 요구사항을 찾아낸다.
10. 간단한 도입 판단표를 작성하고 ‘Framework를 쓰지 않는 결정’도 근거를 들어 설명한다.

**이번 교시의 산출물:** `① Application 책임도 ② Framework 도입 판단표 ③ 선택 근거 3문장`입니다. 패키지 설치나 Agent 구현 결과를 제출하는 수업이 아닙니다.

---

# 2. 이번 수업의 경계 — 앞에서 가져오고 뒤에 남길 것

| 범위 | 이미 학습했거나 이후에 배울 내용 | 이번 시간의 활용 방법 |
|---|---|---|
| Day1~Day2 | OpenAI SDK·Ollama API·FastAPI 호출 | Model을 호출하는 **기존 기능**으로 간주 |
| Day2 6~8교시 | Runtime·Model Serving·Local API 통합 | 실행 위치 설명을 되풀이하지 않고 Framework가 놓일 위치만 지정 |
| Day3 1~5교시 | Model 유형·자원·선정 및 평가 | 후보 Model이 이미 결정되었다고 가정 |
| **Day3 6교시** | **Framework의 구성 요소, 역할, 도입 판단** | **이번 시간에 새롭게 학습** |
| Day3 7교시 | 직접 Provider Interface·Factory·FastAPI를 구현 | 코드 작성·전환 실습은 다음 시간으로 미룸 |
| Day3 8교시 | React에서 AI Provider까지의 전체 통합 | UI 및 최종 네트워크 실습은 미룸 |
| Phase2 AI | Embedding·Vector DB·RAG·Agent의 내부 원리 및 구현 | 오늘은 **구성 요소가 어디에 필요한지만** 살펴봄 |

> **강사 유의:** ‘학생 이해를 돕기 위해’ 같은 FastAPI 호출 코드와 Ollama 구조도를 다시 길게 보여주지 않습니다. 이 교시는 **같은 기존 Application에 새 요구사항이 붙으면 무엇이 추가되는가**를 보여주어야 합니다.

---

# 3. 한 가지 사례를 놓고 복잡해지는 지점을 찾기

이번 시간에는 여러 분야의 유사한 예시를 반복하는 대신, **회사 내부 규정 질의 Application**을 계속 사용합니다. 개념을 익히기 위한 가상의 업무 요구사항이며, 실제 데이터·연결 시스템이 준비된 것은 아닙니다.

첫 번째 요구사항은 간단합니다.

> 사용자가 질문하면, 이미 연결한 Model로 응답을 생성한다.

그러나 회사 규정에 대한 질문이 추가되면 Model만 호출해서는 문제가 남습니다. 해당 회사의 규정은 Model이 미리 알고 있다고 보장할 수 없기 때문입니다. 프로그램은 질문과 관련된 자료를 찾아 Model에 전달할 필요가 있습니다.

요구사항이 더 늘어난 상황을 살펴봅시다.

| 추가 요구 | Application에서 새로 필요한 책임 | Model 호출만으로 충분한가? |
|---|---|---|
| 사내 규정에서 근거 찾기 | 문서 읽기·검색 및 근거 전달 | 부족할 수 있음 |
| 규정 문서가 바뀌어도 반영하기 | 자료를 최신 상태로 연결·관리 | 부족할 수 있음 |
| 직원별 열람 가능 자료 제한 | 인증 결과에 따른 접근 권한 확인 | 부족함 |
| 인사 시스템에서 현재 상태 조회 | 내부 API 또는 DB 연결 | 부족함 |
| 승인 시 알림 전송 | 외부 작업 실행과 오류 처리 | 부족함 |

여기서 중요한 것은 Model이 더 큰 Model로 바뀐다고 **다섯 가지 Application 책임이 자동으로 사라지는 것은 아니라는 점**입니다. 복잡성의 원천은 모델의 Parameter가 아니라 **업무 기능과 연결 관계가 늘어난 것**입니다.

학생 질문: ‘AI가 회사 규정을 답할 수 있으면 굳이 검색을 붙일 이유가 없지 않나요?’  
강사 설명: 일반적인 답변 능력과 회사 내부의 최신·정확한 규정에 근거한 응답은 다른 요구사항입니다. 자료가 바뀌거나 접근 제한이 있으면 Application이 다뤄야 할 문제가 남습니다.

---

# 4. Framework는 ‘AI를 만드는 것’이 아니라 ‘연결을 조직하는 것’이다

AI Application Framework는 Model 생성·학습에 쓰는 모든 기술을 통칭하는 말이 아닙니다. 이번 수업의 LangChain과 LlamaIndex는 **Model과 Application의 외부 기능을 연결하고 조합하도록 돕는 소프트웨어 계층**을 말합니다.

```text
기존 Application
   └── Model 호출

요구사항 증가
   ├── Model과 Provider 연결
   ├── 문서·데이터 연결
   ├── 여러 작업의 흐름 제어
   ├── Tool 실행과 결과 전달
   └── 실행 기록·오류 분석

Framework가 돕는 영역
   └── 공통 인터페이스·컴포넌트·연결 방식 제공
```

Framework가 없더라도 이 기능들은 개발자가 직접 구현할 수 있습니다. Framework는 불가능한 일을 가능하게 하는 ‘마법의 도구’가 아니라, 자주 등장하는 구성을 **재사용 가능한 추상화**로 제공해 직접 작성할 코드를 줄여 주는 선택지입니다.

반대로 Framework를 설치했다고 실제 검색 대상 문서가 만들어지거나 적절한 접근 권한이 자동으로 정해지지 않습니다. 사용자는 어떤 자료를 검색할지, 언제 어떤 기능을 호출할지, 결과를 어떻게 검증할지 계속 결정해야 합니다.

이번 교시에서는 **기능의 존재**와 **요구사항이 실제로 충족되었다는 사실**을 구분해 배웁니다.

---

# 5. Model·Runtime·Web Framework·AI Application Framework의 책임 경계

이제 헷갈리기 쉬운 이름을 **책임 기준**으로 비교해 보겠습니다. 각 도구의 사전적 정의를 다시 암기하는 활동은 아닙니다.

| 구성 요소 | 이번 사례에서 맡을 수 있는 책임 | 맡지 않는다고 봐야 하는 책임 |
|---|---|---|
| Model | 입력 Context를 바탕으로 답변 생성 | 시스템의 실제 DB 권한을 스스로 보장 |
| Ollama 같은 Runtime | Local Model 로딩·Inference 실행 | 회사 규정 접근 정책을 직접 설계 |
| FastAPI | 웹 요청 수신·입력 검증·서비스 경계 제공 | Model 자체의 학습된 지식 보장 |
| LangChain | Model·Tool·Retrieval·Agent 구성 요소 연결 | Model Weight나 회사 원문을 스스로 생산 |
| LlamaIndex | Application Data의 연결·Indexing·Retrieval·Query 구성 지원 | 검색된 근거의 적법성·정확성 자동 보장 |

하나의 서비스를 여러 구성 요소로 만들면 각 구성 요소가 자기 역할을 수행합니다. 따라서 ‘LangChain을 쓴다’는 말은 ‘FastAPI나 Ollama를 제거한다’는 뜻이 아닙니다. 특정 Application에서는 이 도구들이 함께 있을 수 있습니다.

**새로운 이해:** 도구의 이름이 아니라 **실제 문제를 해결하는 계층의 경계**를 그리면, 장애 발생 시 어느 부분을 확인해야 할지도 명확해집니다.

---

# 6. Framework가 도와주는 첫 번째 문제 — 구성 요소를 공통 방식으로 연결하기

Application 코드 안에 서로 다른 Model 서비스, 검색 기능, 문서 변환 기능을 직접 연결하면 각 구성 요소의 입출력과 호출 방법을 알아야 합니다. 서로 다른 기능이 늘어날수록 연결 코드를 수정해야 하는 위치도 늘어날 수 있습니다.

예를 들어 질문을 처리할 때 필요한 기능을 `Model`, `Retriever`, `Tool`이라는 역할로 분리해 보면, Application은 **어느 역할이 먼저 동작해야 하는지**를 더 명확하게 표현할 수 있습니다.

```text
Application의 목표
   │
   ├── Model Integration : Model 요청·응답을 다룸
   ├── Retriever         : 필요한 자료를 찾아옴
   ├── Tool              : 외부 Function/API 작업 수행
   └── Workflow / Agent  : 실행 순서와 선택을 다룸
```

Framework가 제공하는 것은 ‘이 역할들은 어떻게 연결될 수 있는가’에 대한 공통 구성 방법입니다. 각 구성 요소가 어떤 데이터를 사용하고 어떤 실패를 낼 수 있는지는 Application 개발자가 여전히 이해해야 합니다.

### 연결과 책임을 구분하기 위한 질문

- Framework를 빼면 어떤 연결 코드를 직접 작성해야 할까요?
- Framework를 추가해도 그대로 남는 비즈니스 규칙은 무엇일까요?
- 문제가 생겼을 때 Framework 탓인지, Model·데이터·외부 API 탓인지 어떤 근거로 구분할까요?

---

# 7. LangChain은 어떤 문제를 중심으로 살펴볼까?

LangChain은 Model과 다른 서비스·도구를 연결하는 Integration, Model을 공통 방식으로 다루는 Interface, Tool 및 Agent를 활용한 Application 구성을 지원하는 Framework 생태계입니다. 원본 강의자료에서는 **Model·Tool·Agent Integration**을 대표적인 특징으로 소개합니다.

LangChain의 이름 때문에 반드시 여러 프롬프트를 직렬로 연결해야만 사용할 수 있다고 생각할 필요는 없습니다. Model 하나의 호출을 공통 Interface로 다루는 것도 가능합니다. Tool이나 Retrieval 없이도 일부 기능을 사용할 수 있습니다.

**예를 들어 사내 규정 질의 Application의 요구가 단순 Model 호출에서 ‘문서 검색 후 답변’으로 증가했다면**, 개발자가 외부 검색 기능을 이미 가지고 있을 때 그 결과를 Model에 전달하는 연결을 구성할 수 있습니다. 더 나아가 필요 시 다른 Tool을 사용하도록 구성하는 방식도 검토할 수 있습니다.

그러나 Framework가 무엇을 추상화하든 **실제 Model은 어떤 Provider 또는 Runtime에서 실행**됩니다. LangChain이 자체적인 언어 모델 Weight를 제공한다고 오해하면 안 됩니다.

---

# 8. Standard Model Interface — 공통 인터페이스의 진짜 이점

원본에서는 LangChain이 여러 Provider의 Model Interaction을 일관되게 다룰 수 있는 Interface를 제공한다고 설명합니다. 이 이점은 다음 상황에서 나타납니다.

> Application은 ‘응답을 생성하는 Model’을 사용하고 싶지만, Provider마다 연결 방법과 데이터 표현이 다를 수 있습니다.

Model Interface를 두면 Application 측 코드를 Provider 고유 호출에 지나치게 결합하지 않고 구성할 가능성이 높아집니다.

```text
Application의 공통 모델 사용 지점
                   │
                   ▼
            Model Interface
               /       \
         Provider A   Provider B
              │          │
          각 Provider의 실제 API/Runtime
```

하지만 **공통 Interface가 모든 기능을 동등하게 보장하지는 않습니다.** 예를 들어 어떤 Model은 특정 Tool Calling이나 Structured Output 기능을 지원하지만 다른 Model은 지원하지 않을 수 있습니다. 공통 호출이 가능하더라도 실제 출력 품질·기능 지원은 다를 수 있습니다.

이를 구별하기 위한 핵심 문장:

> **호출 모양을 비슷하게 만든다는 것과, Model 능력이나 동작 결과가 같다는 것은 전혀 다른 일입니다.**

**교시 경계:** 여기서 여러 Provider의 Class·Factory·Dependency Injection을 실제로 구현하지 않습니다. 공통 Interface의 필요성을 이해했다면 Day3 7교시의 직접 구현을 위한 준비가 된 것입니다.

---

# 9. LangChain의 Model Interface는 Agent와 별개로도 쓸 수 있다

학생들이 흔히 “LangChain을 쓰려면 Agent부터 만들어야 한다”고 생각합니다. 그러나 원본은 Model 단독 호출이 가능하다고 명확히 설명합니다.

고정된 절차에 Model 호출을 추가할 때는 반드시 Agent가 필요하지 않습니다. 예를 들어 요청 내용을 검사한 다음 **정해진 하나의 Model을 호출해 결과를 돌려주는 기능**이라면, 고정 로직으로 처리할 수 있습니다.

| 요구사항 | 필요한 판단 |
|---|---|
| Model을 공통 API로 한 번 호출 | Model Interface만 검토 가능 |
| 검색된 규정 내용을 Model에 제공 | Retrieval와 Model 연결을 검토 |
| 상황에 따라 다른 내부 기능 선택 | 고정 분기 또는 Agent의 필요성을 검토 |

**Framework의 일부 기능만 도입할 수 있다는 사실**을 먼저 이해해야 합니다. 구성 요소를 모두 사용해야 한다는 부담 때문에 간단한 Application에 불필요한 복잡성을 추가하지 않도록 합니다.

---

# 10. Tool은 Model의 ‘지식’이 아니라 Application이 연결한 외부 기능이다

이번 과정의 원본에서는 `search_document`, `get_customer_info`, `save_summary`, `send_notification`처럼 별도의 프로그램 기능을 Tool 후보로 소개합니다. Tool은 정의된 입력을 받아 실제 데이터 조회나 작업을 수행하는 **호출 가능한 기능**입니다.

```text
Tool 후보: search_document
입력: 검색어
출력: 찾아낸 문서의 일부 또는 검색 결과
실행 주체: Application/연결된 도구 코드

Tool 후보: send_notification
입력: 받는 대상, 내용
출력: 처리 결과
실행 주체: Application/연결된 도구 코드
```

두 Tool은 둘 다 함수처럼 호출될 수 있지만 영향은 다릅니다. `search_document`는 정보를 조회하는 작업인 반면, `send_notification`은 외부 대상에게 알림을 보내는 **Side Effect**가 있습니다. 따라서 두 Tool을 무조건 동일한 수준의 자동 실행 권한으로 취급해서는 안 됩니다.

여기서 처음으로 Tool의 **입력·출력뿐 아니라 실제 영향과 권한**을 함께 살펴봅니다. 이는 Framework API를 외우는 것보다 중요한 Application 설계 기준입니다.

---

# 11. Tool Calling에서 ‘요청’과 ‘실행’을 분리하기

Framework가 Tool Calling을 연결하더라도 외부 코드는 누군가 실제로 실행해야 합니다. 이를 학생이 역할별로 나누어 보도록 합니다.

```text
① 사용자: “규정 문서에 이 내용이 있나요?”
             │
             ▼
② Model: 문서 검색 Tool이 필요하다고 판단·요청할 수 있음
             │
             ▼
③ Application / Agent Runtime: Tool 이름과 입력 검사
             │
             ▼
④ 실제 Tool 코드: 허용된 문서를 검색
             │
             ▼
⑤ Tool Result: 검색한 자료를 Application에 반환
             │
             ▼
⑥ Model: Tool Result를 참고하여 답변 작성
```

이는 **개념적 흐름**이며 특정 LangChain API의 실행 예시가 아닙니다. 호출 여부, 입력 검증, 권한 승인 및 오류 대응은 구성 방식에 따라 다르게 구현됩니다.

학생 확인 질문: “Model이 `send_notification`을 호출하자고 제안하면 알림이 이미 전송된 것인가요?”  
아닙니다. 요청 또는 선택과 실제 작업 성공은 다른 단계입니다. 프로그램이 허용 여부를 확인하고 실행해야 하며 결과도 확인해야 합니다.

---

# 12. 고정 Workflow와 Agent를 구분하는 기준

원본에서 강조하는 중요한 판단 기준은 **“Agent가 더 발전했으므로 무조건 사용한다”가 아닙니다.** 누가 실행 순서를 결정해야 하는가를 살펴야 합니다.

고정 Workflow는 미리 정해진 조건과 순서를 프로그램이 수행합니다.

```text
질문 수신 → 규정 검색 → 검색 결과를 Model에 제공 → 결과 반환
```

Agent 방식에서는 Model이 필요한 Tool이나 일부 다음 행동을 선택하도록 구성할 수 있습니다.

```text
질문 수신
   │
   ▼
Model이 다음 행동을 판단
   ├─ 문서 검색 Tool
   ├─ 업무 데이터 조회 Tool
   └─ 추가 정보 요청
   │
Tool 결과를 보고 다음 행동 또는 종료 판단
```

두 구조는 겉으로는 비슷한 기능을 제공할 수 있습니다. 차이는 **선택 규칙을 개발자가 고정하는지**, 아니면 **Model이 일부 실행 경로를 결정하도록 허용하는지**입니다.

예를 들어 회사가 “질문을 받으면 반드시 권한 확인을 거친 후 규정 검색만 수행한다”고 명시했다면, 우선은 일반적인 고정 Workflow가 더 직접적입니다. 상황별로 Tool을 선택해야 하더라도 규칙이 명확하면 일반 코드의 조건문으로 처리할 수 있습니다.

**Agent는 선택지 중 하나이며 기본값이 아닙니다.**

---

# 13. Agent의 실행 반복에는 종료 조건과 책임이 필요하다

Agent는 Model의 판단, Tool 실행, 결과 확인을 반복할 수 있습니다. 그렇다고 “필요할 때까지 무한 반복”시키는 것이 안전하거나 유용하다는 뜻은 아닙니다.

원본은 Agent가 가져올 수 있는 추가 비용으로 `Latency`, `Cost`, `Non-determinism`, `Tool Error`, `Observability`, `Security`를 제시합니다. 이번 교시에서는 **그 부담이 왜 발생하는지**를 구조적으로만 살펴봅니다.

- 여러 Tool을 연속 호출하면 실행 시간과 외부 서비스 호출량이 늘 수 있습니다.
- Model의 선택 결과에 따라 실행 경로가 달라져 동일 요청도 결과가 달라질 수 있습니다.
- Tool 오류가 발생했을 때 재시도할지, 중단할지, 사용자에게 설명할지 기준이 필요합니다.
- 조회와 달리 데이터 변경·알림 전송 등은 권한과 실행 기록이 더욱 중요합니다.

Agent를 도입한다면 프로그램이 최소한 **허용된 Tool, 실행 횟수나 종료 기준, 오류 처리 원칙, 사용자 권한과 Side Effect 제어**를 정해야 한다는 판단을 내릴 수 있어야 합니다.

여기서는 Agent Loop의 구현 코드나 LangGraph State 정의에 들어가지 않습니다. 그 구현을 모르더라도 **Agent를 설계할 때 빠뜨리면 안 될 질문**을 이해하는 것이 목표입니다.

---

# 14. LangGraph는 LangChain과 어떤 관계일까?

원본 강의자료에서는 LangGraph를 **상태가 있는 Agent/Workflow의 실행 흐름을 더 낮은 수준에서 다루는 Framework/Runtime**으로 소개합니다. LangChain은 상대적으로 높은 수준의 Model·Tool Integration과 Agent 활용에 초점을 둔다고 구분합니다.

| 이름 | 원본에 근거한 핵심 관심사 | 오늘 이해할 깊이 |
|---|---|---|
| LangChain | Model·Tool·Agent 등을 구성하고 연결 | 구성 요소와 Application 책임 구분 |
| LangGraph | 실행 단계·분기·상태가 있는 복잡한 Workflow의 제어 | “왜 실행 흐름 제어가 별도 문제인가”까지 |
| LangSmith | Tracing·Debugging·Evaluation·Observability | “어디서 무엇이 일어났는지 확인해야 한다”까지 |

LangChain의 Agent와 LangGraph의 구현 관계는 자료에 설명되어 있으나, **이 수업에서 실제 패키지·API 버전을 고정하거나 런타임 동작을 검증하지 않았습니다.** 교육장용 구현에서는 실제 환경 기준 확인이 필요합니다.

“LangChain을 쓰면 반드시 LangGraph 코드를 직접 작성해야 하나요?”라는 질문에는, 직접 LangGraph Workflow를 작성하는 것과 상위 Agent 구성 요소를 사용하는 일을 구분하여 답하도록 합니다. 상위 추상화를 선택했다고 모든 내부 기능을 수동으로 구현해야 하는 것은 아닙니다.

---

# 15. LangSmith는 ‘실행 기능’보다 ‘실행 관찰’을 위한 구분이다

복잡한 Application에서는 마지막 답변만 살펴봐서는 실패 원인을 알기 어려울 수 있습니다. 예를 들어 잘못된 규정 답변이 나왔을 때 다음 원인이 모두 가능합니다.

| 실패 지점 | 확인해야 할 사실 |
|---|---|
| Retrieval | 적절한 문서를 찾았는가? |
| Tool | 올바른 인수로 실행했는가? |
| Model Input | 찾아온 문서가 실제 Prompt Context에 들어갔는가? |
| Model Output | 전달된 근거를 잘못 해석했는가? |
| Application | 중간 결과를 잘못 변환했는가? |

이런 단계별 동작을 추적하고 분석하는 활동이 중요합니다. 원본에서는 LangSmith를 Tracing·Debugging·Evaluation·Observability를 돕는 Platform으로 설명합니다.

**핵심은 특정 제품의 기능 화면을 배우는 것이 아니라**, 단순 Model 응답 외에 여러 연결 단계가 생기면 **단계별 입력·출력과 실패 지점이 보이는 구조가 필요해진다**는 점입니다.

로그·추적 정보에 내부 규정이나 개인정보가 포함될 수 있다면 별도의 접근·보관 정책이 필요합니다. Framework를 사용한다는 이유만으로 민감한 데이터를 어디에 저장해도 되는 것은 아닙니다.

---

# 16. Retrieval와 RAG — 이번 시간에는 ‘구성 요소의 자리’만 배운다

회사 문서를 답변의 근거로 사용한다면, Application은 질문과 관련된 자료를 **어디선가 가져와야** 합니다. 그 과정이 Retrieval입니다. 원본에서는 외부 자료를 찾아 Model Context에 전달한 뒤 답변을 만드는 RAG 구조로 연결합니다.

```text
사내 문서들  ─── [검색할 수 있게 준비된 자료]
                          │
질문 ──► Retriever ──► 관련 자료 ──► Model Context ──► 답변
```

이 그림의 학습 목적은 ‘Model이 외부 문서를 자동으로 학습한다’는 오해를 피하는 것입니다. Model의 Weight를 수정하지 않아도 현재 요청에 필요한 문서 내용을 **Input Context로 제공**할 수 있습니다.

다만 Retrieval이 어떤 검색 방법을 쓰는지, Embedding을 어떻게 계산하는지, 검색 점수를 어떻게 평가하는지, Vector Database를 어떻게 구성하는지는 여기서 구현하지 않습니다. 그것은 후속 심화 과정에서 다루어야 할 **별도의 설계·기술 주제**입니다.

> **Retrieval은 데이터를 가져오는 단계이고, Framework는 이 단계를 연결하는 구성 요소를 제공하는 도구입니다. RAG는 이런 단계를 묶어 사용하는 Application 방식입니다.**

---

# 17. LangChain의 Retrieval 구성 요소를 역할로만 읽기

원본에서는 다음 Building Block을 소개합니다. 새 용어가 많으므로 **하나의 문서가 답변에 쓰이기까지 맡는 역할만** 확인합니다.

| 구성 요소 | 담당 역할 | 이번 교시에서 다루지 않을 것 |
|---|---|---|
| Document Loader | 외부 문서 내용을 읽어 오는 연결 | 문서 형식별 Parser 코드 |
| Text Splitter | 큰 문서를 나누는 처리 | Chunk Size 최적화 |
| Embedding Model | 검색에 사용할 수치적 표현 생성 | 벡터 수학 및 학습 원리 |
| Vector Store | 검색을 위해 표현과 자료를 저장·조회하는 계층 | DB 설치와 Index 설정 |
| Retriever | 질문과 관련된 자료를 가져오는 Interface | 검색 점수·Top-k 튜닝 |
| Model Integration | 가져온 Context를 사용해 답변 생성 연결 | Prompt 최적화 및 모델 품질 평가 |

서로 다른 역할을 목록으로 외우기보다 **문서 준비 구간과 질문 처리 구간**이 다르다는 점을 확인하도록 합니다.

```text
[자료 준비] 문서 → 읽기/분할 → 검색할 수 있도록 저장

[질문 처리] 질문 → 관련 자료 찾기 → Model에 전달 → 답변
```

이 두 구간을 나누면 문서 업데이트 때문에 생긴 문제와 질문 처리 때문에 생긴 문제를 구분하기 쉽습니다. 여기서도 전체 RAG 구현 코드를 제공하지 않습니다.

---

# 18. LlamaIndex의 출발점 — 우리 데이터를 LLM과 연결하기

LlamaIndex는 특히 **Application이 보유한 문서와 데이터를 LLM이 사용할 수 있게 연결하는 문제**를 중심으로 이해할 수 있습니다. 원본에는 `Load → Index → Retrieve → LLM Context` 흐름이 대표적인 형태로 제시됩니다.

예를 들어 사내 규정 문서가 여러 종류라면 ‘질문할 때 문서를 처음부터 끝까지 매번 전송’하는 대신, 필요한 부분을 찾을 수 있도록 자료를 준비하고 검색하는 구조를 만들 수 있습니다. LlamaIndex는 이런 Data·Index·Query/ Retrieval 연결을 위한 추상화를 제공합니다.

```text
내가 가진 데이터
   │
   ▼
Load / Index 준비
   │
   ▼
Query 또는 Retrieval
   │
   ▼
관련 Context를 Model에 전달
   │
   ▼
Model 응답
```

여기서 **Index는 사람이 읽는 문서 제목 목록만을 뜻하지 않습니다.** 자료를 나중에 검색하거나 조회할 수 있도록 구성한 데이터 구조·접근 계층과 관련됩니다. 다만 어떤 Index 유형을 사용하고 어떻게 저장하는지는 이 교시에서 구현하지 않습니다.

LlamaIndex를 쓰더라도 어떤 문서가 최신인지, 누가 읽을 수 있는지, 검색 결과가 사실인지 확인하는 책임은 별도로 남습니다.

---

# 19. LangChain과 LlamaIndex를 비교할 때 함정 피하기

원본 강의와 보충 Q&A는 LangChain과 LlamaIndex를 **서로 배타적인 Framework가 아니라 중첩되는 기능을 가진 생태계**로 봐야 한다고 강조합니다.

| 관찰 기준 | LangChain | LlamaIndex |
|---|---|---|
| 출발점·주요 설명 관점 | Model·Tool·Agent·Integration | Data를 LLM에 연결하는 Index·Retrieval·Query |
| RAG 구성 | 가능 | 가능 |
| Tool / Agent 활용 | 가능 | 가능 |
| Model 호출 | 가능 | 가능 |
| 외부 Data 연결 | 지원 | 중요한 초점 |
| 주의할 표현 | “Agent만 하는 Framework”가 아님 | “문서 검색만 하는 Framework”가 아님 |

따라서 단순히 “문서가 있으면 무조건 LlamaIndex”, “Agent를 쓰면 무조건 LangChain”이라고 판단하면 안 됩니다. **현재 요구사항에서 중요한 작업이 무엇인지, 이미 갖고 있는 코드와 잘 연결되는지, 실제로 필요한 기능을 제공하는지**를 확인해야 합니다.

교사가 물어볼 질문:

> “우리 사내 규정 질의 Application에는 문서 검색과 Tool 선택이 모두 필요합니다. 어느 Framework만 사용해야 하나요?”

**가능한 대답:** 둘 중 하나의 적합한 구성 요소만 사용하거나, 책임을 분리해 조합할 수도 있습니다. 다만 두 Framework를 모두 쓰는 것 자체가 목표가 되어서는 안 됩니다. 중복된 추상화와 의존성을 감당할 이유가 있어야 합니다.

---

# 20. 함께 사용할 수도 있다 — 다만 중복된 계층은 이유가 있어야 한다

원본 보충 자료에는 LlamaIndex가 문서 준비·검색을 담당하고 LangGraph가 더 큰 Workflow를 제어하는 구성이 소개되어 있습니다. 이는 **가능한 결합의 한 예**이지 교육생이 반드시 따라야 하는 표준 구성이 아닙니다.

```text
Application
   │
   ▼
Workflow의 실행 판단
   ├─ 문서 검색이 필요 ─► Data/Retrieval Component
   ├─ 업무 조회가 필요 ─► Tool/API Component
   └─ 확인 질문이 필요 ─► 사용자 입력 요청
   │
   ▼
Model이 결과 정리
```

역할을 명확히 정하지 않고 여러 Framework를 겹겹이 도입하면 디버깅 경로와 패키지 의존성만 복잡해질 수 있습니다. 반대로 이미 검증된 Retrieval 구성 요소가 있고 고급 Workflow가 실제로 필요하다면 두 영역을 분리해 사용하도록 설계할 수 있습니다.

학생은 Framework 조합을 이야기할 때 다음을 반드시 적습니다.

- 어느 Component가 문서를 읽고 검색하는가?
- 어느 Component가 실행 경로를 결정하는가?
- 실패하면 어느 Component에서 근거를 확인하는가?

원본 보충 자료의 상세한 LangGraph Node·Router·SQL 결합 예제를 이번 수업에서 구현하지 않는 이유는, 해당 구현 자체가 **별도 학습 목표를 가진 심화 과정**이기 때문입니다.

---

# 21. Framework가 자동으로 해결하지 못하는 문제

LangChain·LlamaIndex는 유용한 Integration을 제공하지만 **업무에 맞는 결과를 자동 보장하는 시스템**은 아닙니다. 다음 문제를 Framework 선택만으로 해결했다고 말해서는 안 됩니다.

| 문제 | Framework가 제공할 수 있는 도움 | 별도로 검토할 사항 |
|---|---|---|
| 자료 검색 | Loader·Retriever 연결 | 자료 최신성·검색 품질 |
| Model 출력 | Model Interface와 결과 처리 | 정확도·형식 준수·Hallucination |
| 외부 기능 | Tool 등록·호출 흐름 | 입력 검증·권한·Side Effect |
| 복합 작업 | Agent/Workflow 구성 | 종료 조건·실패 대응·예측 가능성 |
| 운영 관찰 | 실행 추적과 평가 도구 연계 | 보관 정책·민감 정보·유지보수 |
| Provider 변경 | 공통 Model Interface | 지원 기능·호환성·실측 성능 차이 |

특히 **Framework 적용 = Retrieval 품질 향상**, **Agent 도입 = 정확성 향상**, **공통 Interface = 동일한 Model 기능**이라는 식의 설명은 근거가 부족합니다.

이 표는 나중에 Model 평가나 보안·운영을 할 때 살펴볼 체크포인트입니다. 이번 교시에서 그 기술적 구현이나 정량 평가 절차까지 선행하지 않습니다.

---

# 22. 우리 Application에서는 Framework를 어디에 배치할까?

앞 교시까지 만든 Web API의 경계는 유지한다고 가정합니다. 새로운 AI Application Framework가 들어와도 Frontend와 FastAPI를 반드시 교체하는 것은 아닙니다.

```text
사용자 / UI
     │
     ▼
FastAPI (요청을 받아 Application Service에 전달)
     │
     ▼
AI Service
     │
     ├── 직접 SDK / HTTP 사용
     │
     └── [필요할 때] AI Application Framework
                 ├── Model Integration
                 ├── Retrieval
                 ├── Tool
                 └── Agent / Workflow
                           │
                           ▼
                    Provider / Runtime / Data Source
```

위 그림에서 Framework는 **선택적인 Application 구성 계층**입니다. 하나의 모델만 호출하면 하단의 직접 SDK/HTTP 방식으로 충분할 수 있습니다. 더 많은 기능을 연결해야 할 때만 Framework를 검토합니다.

Framework를 넣었다고 전체 요청 경로가 자동으로 바뀌는 것은 아닙니다. 각 요청에 대해 어떤 기능이 실제로 사용되는지, 어떤 데이터를 어디에 보내는지 확인해야 합니다.

---

# 23. ‘직접 구현’이 더 나은 경우

Framework는 별도의 패키지와 사용 방법을 배워야 하고, 버전 변경·의존성·오류 진단 부담이 생길 수 있습니다. 다음과 같은 요구사항에서는 기존 SDK·HTTP 통신 방식이 더 단순할 수 있습니다.

**사례:** 정해진 Prompt 하나를 보내고 짧은 텍스트를 받아 반환하는 내부 기능. Provider는 하나이며, 문서 검색이나 외부 Tool은 없습니다.

- 호출 흐름이 한눈에 보입니다.
- 실제 Provider가 지원하는 고유 기능을 별도 추상화 없이 사용할 수 있습니다.
- 오류가 발생하면 확인해야 할 연결 계층이 상대적으로 적습니다.
- 새 Framework의 버전·설치·내부 동작을 관리할 필요가 없습니다.

이러한 경우 “LangChain을 사용하지 않았으므로 기술 수준이 낮다”는 판단은 잘못입니다. **요구사항을 만족하는 가장 단순하고 유지 가능한 구성이 충분히 좋은 설계**일 수 있습니다.

원본에서 강조하는 ‘Framework가 반드시 필요한 것은 아니다’라는 메시지는 바로 이 선택을 말합니다.

---

# 24. Framework 도입이 유리해질 수 있는 경우

이번에는 반대 상황을 생각해 봅니다. 외부 문서 종류가 여러 개이고, 여러 데이터 소스에 연결하며, 특정 Tool을 선택해야 하고, 이 연결을 여러 업무 기능에서 반복 사용한다고 가정합니다.

그 경우 Framework를 이용하면 다음 부분에서 이점을 얻을 수 있습니다.

- 여러 Model/Provider와의 **일관된 연결 방식**을 검토할 수 있습니다.
- Document Loader·Retriever 같은 **재사용 가능한 구성 요소**를 활용할 수 있습니다.
- Tool 호출과 Agent 흐름을 **이미 제공되는 추상화**로 구성할 가능성이 높아집니다.
- 업무별로 비슷한 연결 코드를 반복 작성하는 부담을 줄일 수 있습니다.

그러나 개발 속도가 빨라질지는 현재 팀의 숙련도·필요한 기능·Framework 버전과 지원 상태에 따라 달라집니다. 적절한 Framework를 도입한 뒤에도 **복잡한 디버깅이나 이해하기 어려운 실행 경로가 새 비용으로 생길 수 있습니다.**

따라서 ‘Framework가 도움을 줄 것 같다’에서 끝내지 않고, **무엇이 줄고 무엇이 늘어나는지** 비교해야 합니다.

---

# 25. LangChain과 LlamaIndex 중 무엇을 선택할지 판단하기

이번 시간의 비교는 실제 설치·성능 벤치마크가 아니라 **요구사항과 구성 요소의 적합성에 대한 1차 검토**입니다. 이를 구분해 기록합니다.

| 확인 질문 | 검토 방법 |
|---|---|
| 현재 필요한 기능은 무엇인가? | Model 호출 / Retrieval / Tool / Agent 중 실제 필요한 것에 표시 |
| 이미 작성한 코드와 연결되는가? | 기존 Service를 유지할 수 있는지 살펴봄 |
| 어떤 데이터에 접근하는가? | 문서·Database·외부 API와 권한 경계를 기록 |
| 고정 Workflow로 충분한가? | 정해진 분기 규칙으로 해결 가능한지 확인 |
| Framework가 줄여 줄 코드가 명확한가? | 직접 구현해야 할 연결과 Framework 구성 요소 비교 |
| 새로 생기는 부담은? | 의존성·디버깅·학습 비용·관찰 도구 검토 |
| 확인되지 않은 기술 사실은? | ‘실행 검증 전’으로 기록하고 확정하지 않음 |

**선택 결론은 세 가지 중 하나입니다.**

`직접 구현 유지` — 필요 기능이 간단하고 현재 코드로 충분하다.  
`Framework 도입 검토` — 재사용·연결 복잡성이 있어 얻는 이점이 크다.  
`정보 부족으로 보류` — 호환성이나 실제 필요 기능이 확인되지 않았다.

‘무조건 LangChain’, ‘무조건 LlamaIndex’처럼 이름만 적는 답은 이번 교시의 완료 기준을 충족하지 못합니다.

---

# 26. 학생 활동 A — Tool이 필요한 이유와 실행 주체 찾기

**상황:** 사용자가 “최신 사내 출장 규정에서 숙박비 상한을 찾아 줘”라고 질문했습니다. Model은 일반적인 출장 규정을 설명할 수 있지만 현재 회사 규정의 정확한 내용은 모를 수 있습니다.

학생은 다음 빈칸을 채웁니다.

| 질문 | 학생 작성 |
|---|---|
| 필요한 외부 정보는? | |
| 어떤 Tool/기능으로 가져올 수 있는가? | |
| Model과 Tool 중 누가 실제 자료를 검색하는가? | |
| 검색 결과가 없다면 어떻게 해야 하는가? | |
| Framework가 대신 결정하지 못하는 접근 권한은? | |

**강사 해설:** `search_document`와 같은 검색 기능을 연결할 수 있습니다. Model이 검색을 요청하더라도 자료 읽기는 실제 프로그램이 수행합니다. 근거를 찾지 못했다면 사실처럼 답을 확정하는 대신 **확인할 수 없음을 알리는 응답 정책**이 필요합니다. 자료 접근 권한은 Application의 책임입니다.

이 활동에서는 검색 함수나 Agent 코드를 작성하지 않습니다. **역할과 책임을 연결할 수 있는지**를 확인합니다.

---

# 27. 학생 활동 B — 고정 Workflow인가, Agent인가?

다음 세 가지 요구사항을 구분합니다. 정답은 ‘Agent가 더 복잡해 보이므로 사용’이 아닙니다.

| 요구사항 | 우선 검토할 방식 | 판단 근거 |
|---|---|---|
| ① 질문을 받으면 반드시 정해진 규정집을 검색하고 한 번 답변한다 | 학생 작성 | |
| ② 질문 종류별로 사전에 작성한 규칙에 따라 서로 다른 DB를 조회한다 | 학생 작성 | |
| ③ 사용자 목표를 수행하면서 조회 결과에 따라 추가 Tool을 선택해야 하고 경로를 사전에 전부 정하기 어렵다 | 학생 작성 | |

**강사 해설:**

①은 고정 Workflow가 단순합니다. ②도 규칙이 명확하므로 일반 코드의 조건 분기가 충분할 수 있습니다. ③은 Model이 일부 실행 경로를 선택하는 Agent를 검토할 수 있지만, **권한·실행 횟수·종료 조건을 먼저 정의해야 합니다.**

학생은 ③에 대해서도 “Agent가 반드시 정답”이라고 쓰지 말고 *어떤 조건에서 도입할 가치가 있는지*를 설명해야 합니다.

---

# 28. 학생 활동 C — Framework와 다른 구성 요소의 책임 구분하기

다음 장애 상황을 읽고 먼저 확인할 책임 계층을 적으세요.

| 상황 | 먼저 확인할 부분 | 이유 |
|---|---|---|
| Model이 정상 응답했지만 규정이 오래되었다 | | |
| 내부 직원에게 접근 권한이 없는 문서가 검색되었다 | | |
| Tool 호출을 요청했는데 외부 시스템은 아무 작업도 하지 않았다 | | |
| 같은 요청에 응답 시간이 갑자기 길어졌다 | | |
| Framework 호출 자체가 실행 오류를 낸다 | | |

**강사 해설 방향:** 자료 최신성은 데이터 준비·갱신 단계, 잘못된 문서 노출은 권한·검색 범위, Tool 미실행은 실행 주체·호출 결과, 긴 응답은 여러 단계의 시간 기록, Framework 오류는 사용 API·의존성·구성 오류를 각각 의심합니다. 한 번에 모든 오류를 ‘AI 품질 문제’라고 부르면 원인을 찾기 어렵습니다.

이 활동의 목적은 Framework 이름을 분류하는 것이 아니라 **문제가 생길 때 첫 조사 지점을 합리적으로 정하는 것**입니다.

---

# 29. 학생 활동 D — Framework 선택 메모 작성하기

앞서 사용한 사내 규정 질의 Application에 다음 요구를 추가합니다.

> 내부 규정집 여러 종류를 검색한다. 질문에 따라 사내 DB 조회도 필요하다. 대다수 요청은 정해진 흐름으로 처리하지만, 일부 요청에서는 추가 자료를 찾아야 할 수 있다. Model은 이미 결정되어 있다.

학생은 아래 양식을 작성해 제출합니다.

```text
[Framework 도입 검토 기록]

기존에 직접 구현한 기능:
신규로 필요한 구성 요소:
현재 가장 복잡한 연결 지점:
고정 Workflow로 충분한 구간:
Agent 도입을 검토할 구간:
LangChain에서 기대하는 기능:
LlamaIndex에서 기대하는 기능:
Framework 없이 유지할 기능:
예상되는 새 의존성·디버깅 부담:
권한/Side Effect 관리가 필요한 Tool:
미확인 사항:

결론: 직접 구현 유지 / Framework 검토 / 보류
선택 근거(3문장):
```

평가 기준은 ‘유명한 Framework 이름을 선택했는가’가 아닙니다. **요구사항 → 필요한 연결 기능 → 선택 이유와 남는 책임**이 논리적으로 이어지는지가 핵심입니다. 서로 다른 결론이어도 타당한 근거가 있다면 인정할 수 있습니다.

---

# 30. 강사 진행안 — 설명보다 판단을 많이 시키기

수업을 실제로 진행할 때는 다음 흐름이 자연스럽습니다. 분 단위 시간은 교육장 진행 속도에 따라 조정합니다.

| 순서 | 강사 진행 | 학생이 남겨야 할 결과 |
|---|---|---|
| 도입 | 기존 Model 호출에서 추가 요구사항이 생기는 순간을 제시 | Model 밖에 필요한 기능 찾기 |
| 구성 요소 | Framework·Retriever·Tool·Agent의 책임을 연결 | 역할도 완성 |
| Framework 비교 | LangChain·LlamaIndex의 출발점과 중복 영역 설명 | 차이와 공통점 2가지씩 기록 |
| 실행 판단 | 고정 Workflow·Agent 사례 판단 | 적용 방식과 그 이유 작성 |
| 실습·발표 | 도입 판단 메모 작성 및 상호 검토 | 결론·미확인 사항 제시 |

**강사용 개입 포인트:** 학생이 “Framework를 쓰면 다 해준다”고 말하면 해결되는 항목 하나와 여전히 남는 항목 하나를 반드시 구분하게 합니다. 반대로 “Framework가 없으면 RAG나 Agent를 못 만든다”고 말하면 직접 구현 가능한 기본 연결 흐름을 확인하게 합니다.

프레임워크 설치와 고급 API 사용은 **오늘의 완료 요건이 아닙니다.** 이 경계를 유지해야 다음 실습과 후속 심화 과정이 의미를 갖습니다.

---

# 31. 수업 확인 질문과 예상 답안

**Q1. AI Application Framework를 쓰는 이유는 무엇인가요?**  
Model과 Tool, 자료 검색, 복잡한 실행 흐름 등을 연결할 때 공통 구성 요소·추상화를 활용해 직접 작성할 연결 코드를 줄이기 위해서입니다. 단, 모든 Application에 필수인 것은 아닙니다.

**Q2. LangChain과 LlamaIndex 중 하나만 RAG를 만들 수 있나요?**  
아닙니다. 둘 다 Retrieval/RAG 관련 구성을 지원합니다. 출발점과 특히 강조하는 부분은 다르지만 기능이 겹칩니다.

**Q3. Model이 Tool을 사용한다고 하면 누가 실제 Tool 코드를 실행하나요?**  
Application 또는 Agent 실행 계층이 호출을 확인하고 Tool 코드를 실행합니다. Model의 요청이 실제 실행 성공을 뜻하지 않습니다.

**Q4. 고정 Workflow와 Agent의 가장 중요한 차이는 무엇인가요?**  
고정 Workflow에서는 프로그램이 정한 실행 규칙을 따르며, Agent는 Model이 상황에 따라 일부 다음 행동이나 Tool 선택에 관여할 수 있습니다.

**Q5. LangGraph와 LangSmith는 둘 다 Model Runtime인가요?**  
아닙니다. 자료에서는 LangGraph를 상태 있는 실행 흐름의 제어에, LangSmith를 추적·디버깅·평가·관찰에 초점을 둔 도구로 구분합니다.

**Q6. Framework를 도입하면 회사 문서 접근 권한과 검색 정확도가 자동으로 해결되나요?**  
아닙니다. 접근 권한과 데이터 최신성, 검색 품질과 응답 검증은 Application이 별도로 정해야 합니다.

**Q7. 단순하게 Model 한 번 호출하는 서비스에도 반드시 LangChain을 적용해야 하나요?**  
아닙니다. 기존 SDK/HTTP 호출이 요구사항에 충분하고 유지보수에 유리하면 직접 구현을 유지하는 것도 합리적입니다.

**Q8. Provider별 호출 코드를 하나의 Interface로 묶는 구현을 오늘 하나요?**  
하지 않습니다. 오늘은 Framework가 이런 문제를 왜 다루는지 이해하고, 직접 Interface를 구현하는 실습은 Day3 7교시에 진행합니다.

---

# 32. 자주 발생하는 오해 — 중복 정의 대신 설계 판정으로 확인

| 주장 | 판정 | 구체적 이유 |
|---|---|---|
| “LangChain은 언어 모델 자체다.” | 부정확 | Model 실행·연결 계층과 Model Weight는 다른 것 |
| “LangChain을 쓰면 FastAPI도 Ollama도 항상 없앨 수 있다.” | 부정확 | Web Backend·Local Runtime은 각각 다른 책임을 가짐 |
| “LlamaIndex만 RAG를 만들 수 있다.” | 부정확 | 두 Framework 모두 관련 구성 지원 |
| “Framework가 문서를 읽으면 정답 품질까지 보장한다.” | 부정확 | 데이터·검색·Model·검증 문제는 별도로 남음 |
| “Tool 호출 요청이 나왔으면 실제 작업은 끝난 것이다.” | 부정확 | 실제 실행·권한 확인·결과 처리가 필요 |
| “모든 복잡한 업무는 Agent로 만들어야 한다.” | 부정확 | 규칙이 명확하면 고정 Workflow가 더 단순할 수 있음 |
| “Framework를 도입하지 않는 결정은 실패한 설계다.” | 부정확 | 요구사항과 관리 비용을 근거로 선택해야 함 |

학생이 오해를 발견했다면, 해당 문장에 **예외 조건을 붙이는 수준**에서 끝내지 말고 원래 어떤 구성 요소의 책임인지를 다시 설명하도록 합니다.

---

# 33. 이번 교시에서 반드시 남겨야 할 결론

AI Application Framework는 더 좋은 Model을 자동으로 만들어 주지 않습니다. Framework가 필요한 상황은 **Application이 연결해야 하는 기능이 늘어나고**, 그 연결의 재사용·일관성·흐름 관리가 중요한 상황입니다.

LangChain에서는 Model Interface, Tool, Agent, Retrieval 등 여러 기능을 연결하는 관점을 배웠습니다. LlamaIndex에서는 자료를 읽고 정리하여 필요한 Context를 찾아 Model에 연결하는 관점을 배웠습니다. 두 생태계는 일부 영역을 공유하기 때문에 절대적인 이분법으로 선택하지 않습니다.

또한 Agent를 선택한다는 것은 Model에게 일부 실행 판단을 맡기는 설계이므로, 고정 Workflow와 비교해 필요성을 먼저 확인해야 합니다. Framework가 무엇을 대신하는지뿐 아니라 **실제 데이터·권한·오류·평가의 책임이 어디에 남는지** 설명할 수 있어야 합니다.

> **이번 교시의 핵심 문장:** “Framework는 Model·Data·Tool·Workflow를 연결하는 데 도움을 주지만, Application 요구사항과 실행 책임을 대신 결정해 주지는 않는다.”

---

# 34. 다음 교시 연결 — 직접 Provider Interface를 구현한다

이번에는 ‘공통 Model Interface가 왜 필요한가’를 설계 관점에서 살펴봤습니다. 다음 시간에는 그 문제를 Framework 없이 직접 코드로 구현합니다.

**Day3 7교시 — AI Provider 추상화: OpenAI와 Ollama를 하나의 FastAPI 구조로 통합하기**

다음 시간의 고유 학습 내용은 다음과 같습니다.

- `AIProvider` 공통 Interface를 정의하고
- `OpenAIProvider`와 `OllamaProvider` 구현을 분리하고
- 설정에 따라 Provider를 선택하여
- 하나의 FastAPI API Contract를 유지하는 **실행 가능한 코드**를 작성합니다.

이번 문서에서는 그 Class·Factory·환경 변수·API 호출의 완성 코드를 미리 작성하지 않았습니다. 뒤의 Day3 8교시는 이를 React 화면까지 연결하는 최종 통합 실습입니다. RAG와 Agent의 구체적인 동작 원리·구현도 후속 과정에서 별도로 배웁니다.

---

# 참고자료와 검증 범위

- 원본 교육과정: Day3 6교시 「AI Application Framework 생태계 — LangChain과 LlamaIndex」
- 동일 교육과정의 보충 Q&A: 「LangChain과 LlamaIndex에 대한 설명」
- 원본에서 제시한 후속 참고자료: LangChain Overview·Models·Tools·Agents·Retrieval, LangGraph Overview, LlamaIndex RAG/Agent 관련 문서

**검증 주의:** 여기서 사용한 LangChain·LlamaIndex·LangGraph·LangSmith 역할 설명은 교육과정 원문을 기준으로 합니다. 수업 배포 시점의 최신 패키지 API·동작·지원 범위에 대해 외부 자료로 재확인한 결과는 아닙니다. 실행 코드 없이 설명한 자료이므로 **Framework 실행 검증 완료**로 표시해서도 안 됩니다.

# 관련 Wiki Link

- [[AI Application Framework]]
- [[LangChain]]
- [[LlamaIndex]]
- [[LangGraph]]
- [[LangSmith]]
- [[Model Provider]]
- [[Tool Calling]]
- [[Agent]]
- [[Retrieval]]
- [[RAG]]
- [[Embedding]]
- [[Vector Store]]
- [[Workflow]]
- [[FastAPI]]
- [[Ollama]]
- [[Provider Abstraction]]

# 저장 위치 제안

```text
Academy/
└── 00. 교육과정(curriculum)/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day3_06교시_AI_Application_Framework_생태계_LangChain과_LlamaIndex_강의용_v0.2.md
```
