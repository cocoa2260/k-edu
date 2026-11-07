# EDU-05 — Phase2_AI 단원별 이론·실습 연결 및 누적 개발 단계 상세 설계

- **상태:** 사용자 승인 완료 (2026-11-07) / 학생용 표기 가독성 원칙 반영
- **작성일:** 2026-11-07
- **프로젝트:** `cocoa2260/k-edu`
- **대상 브랜치:** `work/curriculum-production-001`
- **확인한 브랜치 HEAD:** `54ff445765925c6a9e5cc8fefe580e51b494eea3`
- **승인된 상위 기준:** EDU-03(최종 누적 실습 프로젝트), EDU-04(11개 단원 구성·학습 순서)
- **범위:** 기존 Phase2 교안과 `document-assistant` 구현을 참고하여 **학생이 실제로 코드 작성할 단원별 연결 설계**를 정한다. **학생용 완성 코드와 새 폴더의 실제 생성은 아직 하지 않는다.**
- **GitHub 반영:** 사용자 승인 후 설계 문서로 등록. 실제 학생용 코드·교안은 후속 작업.

> **학생용 표기 원칙(사용자 승인 조건):** 학생에게 제공하는 교안·목차·실습 안내·검사표에는 내부 작업 단계 코드나 검사 일련번호를 사용하지 않는다. 각 항목은 실제 기능명, 학생이 수행할 작업, 눈으로 확인할 결과로 표현한다. 프로그램이 실제 사용하는 파일명·API 필드·문서 식별자는 구현 호환성을 위해 필요한 경우에만 남기고 학생에게 의미를 풀어 설명하거나 읽기 쉬운 문서 제목을 함께 제공한다.

> **우선순위:** 학생이 Obsidian 교안을 보면서 **자신의 단일 프로젝트에 코드를 복사·붙여넣고 수정한 다음, 그 자리에서 실행 결과를 볼 수 있어야 한다.** 전 단원에서 처음부터 다시 만들게 하거나, 미리 완성된 코드를 받아 결과만 분석하는 수업은 본과정의 목표와 맞지 않는다.

## 0. 이번 설계에서 확정하고, 뒤로 남기는 것

### 이번에 확정 후보로 제시하는 것

1. **01~11단원 각각**의 새 학습 개념, 학생이 바꿀 파일, 구현 순서, 실습 출력, 테스트, 다음 단원 전달물.
2. 단일 학생용 애플리케이션에서 기능을 **기존 파일을 유지한 채 확장**하는 순서.
3. 구간별 임시 확인 API와 **최종 통합 API의 형태(설계 제안)** 및 공통 응답 구조.
4. 구분해야 할 검증 상태: **파일/코드 존재 ≠ 실행 성공 ≠ 모델 응답의 사실적 정확성 ≠ 수업 채택 완료**.
5. 기존 원문 자료의 재사용과 본과정/심화 분리 및 **실습 작성 시 중복 방지 규칙**.

### 이 문서에서 완료라고 주장하지 않는 것

- 학생에게 제공할 실제 시작본·완성본, 각 단원의 완전한 붙여넣기 코드, 최종 명령 및 출력의 검증.
- 학생 PC의 패키지 설치·CPU 모델 로드·브라우저 실행, 전체 E2E 또는 수업 시연.
- EDU-06의 최종 Obsidian 디렉터리명, 배포 파일명, 각 교시별 시수.
- GitHub의 현재 `document-assistant` 전체 소스가 **이미** 하나의 React/FastAPI Multi-Agent 서비스라는 판정.

---

## 1. 공통 실습 구조 — 모든 단원에서 유지

### 1.1 학생이 하나만 갖는 프로젝트

아래 경로는 **논리적 설계명**이다. 실제 GitHub/Obsidian 폴더 위치는 EDU-06에서 확정한다. `backend/`와 `frontend/`는 01단원부터 유지하고, 뒤 단원에서 프로젝트 전체를 교체하지 않는다.

```text
<학생용-단일-프로젝트>/
├── README.md                         # 최초 실행과 지금까지 구현한 기능
├── backend/
│   ├── requirements.txt              # 필수 시작 의존성; 후속 단원에 최소 확장
│   ├── .env.example                  # 실습 설정 예시, 실제 비밀값은 Git 반영 금지
│   ├── app/
│   │   ├── main.py                   # 기준 대화 앱: FastAPI 생성, 기존 /ai/chat 보존
│   │   ├── schemas.py                # 기준 대화 앱: 기본 계약; 이후 공통 결과 확장
│   │   ├── service.py                # 기준 대화 앱: Provider 연결; 계속 재사용
│   │   ├── providers/                # 기준 대화 앱: 기존 Provider 인터페이스/선택 경계
│   │   ├── assistant_service.py      # Prompt·Context: 요청 조정; 뒤 단계에 모드 추가
│   │   ├── prompting.py              # Prompt·Context: Prompt/Context 구성
│   │   ├── harness.py                # 실행 관리: 검증·재시도·실행 종료
│   │   ├── documents.py              # 문서 처리: 로컬 문서 적재·전처리·Chunking
│   │   ├── rag.py                    # RAG: 검색→Context→생성→출처
│   │   ├── tools_registry.py         # Tool Calling: 안전한 검색/원문읽기 Tool
│   │   ├── agent.py                  # Single-Agent: Single-Agent 실행 반복
│   │   └── multi_agent.py            # Multi-Agent: 순차 역할 및 공유 예산
│   ├── retrieval/
│   │   ├── encoder.py                # Embedding: 질의/청크 Embedding
│   │   └── index.py                  # 벡터 검색: SQLite Exact 검색·Metadata
│   ├── data/
│   │   ├── fixtures/                 # 기준 대화 앱: Prompt·Context와 실행 관리 입력 실험용 고정 가상 문서·질문
│   │   ├── sources/                  # 문서 처리: 같은 가상 규정의 TXT·MD 원문
│   │   ├── catalog.json              # 문서 처리: 문서 버전·상태·접근범위
│   │   └── cases.json                # 공통 질문과 학습/검증 사례
│   ├── local_data/                   # 문서 처리 Chunk Snapshot, Embedding·검색 Index 등(.gitignore)
│   ├── tools/                        # 단원별 실행/관찰 CLI; 앱 본 코드 재사용
│   └── tests/                        # 매 단원 새 테스트를 누적
└── frontend/
    ├── package.json                  # 기준 대화 앱부터 존재
    ├── index.html
    └── src/
        ├── App.jsx                   # 기준 대화 앱부터 같은 질문·결과 화면을 계속 확장
        ├── api.js                    # 기준 대화 앱부터 HTTP 호출 창구 하나 유지
        └── style.css
```

**중요:** 여기 표시한 `assistant_service.py`, `documents.py`, `tools_registry.py`, URL 일부는 **새 학생용 설계 후보**이지 GitHub에 같은 이름으로 이미 있는 파일이 아니다. 반대로 기존 GitHub의 `app/rag.py`, `app/agent.py`, `app/multi_agent.py`는 **참조 구현이 실제 존재**한다. 어떤 파일을 가져오고 어떤 부분을 학생이 처음부터 작성할지는 EDU-07/08에서 파일별 Diff로 고정한다.

### 1.2 직접 작성과 사전 제공의 경계

| 분류 | 학생에게 보이는 시점 | 허용 범위 |
|---|---|---|
| **시작본** | 01단원 시작 | 최소 React/FastAPI 대화 화면, 기존 Chat Provider 연결 및 실행에 필요한 설정/종속성. 미래 RAG/Agent 모듈을 시작본에 포함하지 않는다. |
| **학생용 교안 코드** | 해당 단원에 도달했을 때 | 새 파일의 붙여넣을 **완전한 코드** 및 기존 파일의 **정확한 교체·삽입 위치**를 안내. 생략한 필수 함수나 암묵적 선수 파일이 없어야 한다. |
| **교사용 기준 완성본** | 수업 자료 관리 영역 | 단계별 정답·테스트·오류 대응. 학생 시작본과 구분. |
| **기존 GitHub 완성 소스** | 집필·검증 담당자가 참조 | 기존 `document-assistant` 구현을 그대로 학생에게 선행 배포하지 않는다. 특히 RAG/Agent/ Multi-Agent가 미리 설치되었다고 학생 실습 완료로 판정하지 않는다. |
| **단계별 테스트/검증 자료** | 기능 작성과 동시에 | 학생이 실행 가능한 확인 명령과 정상/실패 케이스. 저장된 과거 모델 출력은 현재 실행 결과와 구분. |

### 1.3 수업마다 학생에게 보여줄 화면의 축

**01단원부터 똑같은 React 화면을 열고, 아래 영역이 순서대로 등장한다.** 실습 중 CLI 출력도 사용하되 웹 화면을 최종 단원까지 미루지 않는다.

```text
AI 문서 도우미
 ├─ 질문 입력 / 실행 모드 [Chat → RAG → Single-Agent → Multi-Agent]
 ├─ 답변 / 근거 부족 / 오류 / 중단 상태
 ├─ 학습 관찰 패널
 │   ├─ Prompt·Context  실제 전달 입력 미리보기
 │   ├─ 실행 관리  호출 횟수·형식 검사·종료 이유
 │   ├─ 문서 처리  문서·Chunk/원문 위치
 │   ├─ Embedding·검색  Vector 차원·유사도·검색 결과
 │   ├─ RAG  RAG 근거와 답변 비교
 │   ├─ 도구 호출·Agent  Tool 요청/실행/선택 단계
 │   └─ Multi-Agent  역할별 전달·검토 결과
 └─ 현재 단계에서 아직 배우지 않은 기능은 비활성화
```

관찰 패널이 **상용 제품의 필수 UI**라는 뜻은 아니다. 학습 중 학생이 자신의 코드가 어떤 데이터를 만들었는지 확인하도록 제공하는 교육용 표시다. 실제 Provider의 비밀키나 숨겨야 할 시스템 운영 정보는 UI에 노출하지 않는다.

### 1.4 누적 코드의 변경 원칙

1. 기준 대화 앱의 `/ai/chat`과 `/health`는 변경 없이 보존한다.
2. 뒤 단원은 **새 기능만 추가**하고, 기존 파일을 수정할 때는 **이전 내용 + 변경 대상 + 수정 후 확인**을 명시한다.
3. **Prompt·Context와 실행 관리에 필요한 문서 내용은 기준 대화 앱에 포함된 작은 고정 Fixture에서 읽는다.** 문서 처리에서 *같은 가상 규정*을 TXT/MD 원문과 Catalog로 변환하면서 자료 공급원을 실습이 만든 Chunk로 교체한다. Prompt·Context에서 문서 적재 기능을 미리 구현하거나, 문서 처리에서 무관한 새 데이터로 바꾸지 않는다.
4. 새 명령·API는 미래 단계의 함수를 미리 Import하게 만들지 않는다. 미구현 모드를 누르면 `아직 학습하지 않은 기능`으로 안내한다.
5. 학생은 **같은 프로젝트 디렉터리**를 사용한다. `L1용 앱`, `L3용 앱`, `L6용 앱` 등 별도의 실행 프로젝트로 갈아타지 않는다.
6. 이전 단원의 정상 동작 확인을 회귀 검사로 남긴다. 설치와 환경 구축을 매 단원 반복 작성하지 않는다.
7. **각 단원의 새 개념 설명은 충분히**, 앞 단원·Phase1의 유사 설명·비유·코드는 되풀이하지 않는다.

---

## 2. 전체 누적 개발 작업 맵

| 단원 | 이번에 구현할 기능 | 이번에 **직접 작성·수정**할 주요 파일 | UI/CLI에서 확인할 것 | 남겨야 할 누적 결과 |
|---|---|---|---|---|
| 01. LLM 심화·출발 | **기존 대화 앱 실행·확인** | 제공 시작본 실행; `App.jsx`, `main.py`, Provider 코드 위치 찾기 | Chat 답변/오류와 실제 네트워크 요청 | 기본 React·FastAPI·Provider 실행 상태 |
| 02. Prompt·Context | **모델 입력 구성 및 비교** | `app/prompting.py` 신규, `assistant_service.py` 신규, `main.py`·`App.jsx` 확장 | 입력 지시/자료/질문이 실제 요청에 들어가는 과정 | 공통 입력 조립 함수 |
| 03. Harness | **응답 검사·재시도·종료 처리** | `app/harness.py` 신규, `assistant_service.py`의 호출 경로 교체 | 정상/오류/재시도/종료 이유 | 한도 있는 실행기와 이력 |
| 04. Document·Chunk | **원문 정리와 단락 분할** | `app/documents.py` 신규, `data/sources/*`·`catalog.json` 준비, 문서 관찰 UI 추가 | TXT·MD → Chunk ID/순서/원문 위치 | 정규화된 문서·Chunk 데이터 |
| 05. Embedding | **실제 벡터 생성·비교** | `retrieval/encoder.py` 신규, 관찰 endpoint/UI 추가 | 실제 벡터의 차원·길이·유사도 | 문서/질문 Embedding 호출 함수 |
| 06. Vector DB·검색 | **벡터 저장과 유사도 검색** | `retrieval/index.py` 신규, 검색 API/UI 추가 | SQLite 저장, Top-k 검색, Metadata, 갱신 반영 | 검색 가능한 Index와 `search()` |
| 07. RAG | **문서 근거를 사용하는 답변 생성** | `app/rag.py` 신규, `assistant_service.py`에 RAG 모드 연결 | 근거가 첨부된 답변, 근거 없는 질문 처리 | Chat/RAG 2개 모드 |
| 08. Tool Calling | **도구 요청·검사·실행** | `app/tools_registry.py` 신규, 요청 Schema/Dispatcher와 관찰 UI 추가 | 도구 요청 vs 실제 실행, 잘못된 인자 거부 | 안전한 검색/읽기 도구 |
| 09. Single-Agent | **도구를 선택하는 반복 실행** | `app/agent.py` 신규, 공통 실행경로에 Single 모드 연결 | 모델의 도구 선택→실행→다음 행동→종료 | 제한된 Single-Agent |
| 10. Multi-Agent | **검색·작성·검토 역할 분담** | `app/multi_agent.py` 신규, 공통 실행경로에 Multi 모드 연결 | 검색/작성/검토 Handoff, 전체 한도 | 제한된 순차 Multi-Agent |
| 11. 통합·평가 | **전체 기능 실행·비교·검증** | `App.jsx`·`api.js` 정리, 공통 응답·테스트·README 최종화 | 동일 질문의 4개 모드·회귀·실제 모델 결과 | 최종 학생용 애플리케이션 |

**학습 흐름:** Embedding과 벡터 검색은 연속된 두 단원에서 구현한다. Tool Calling을 구현한 다음 Single-Agent 기능으로 확장한다. 어느 단원에서도 별도의 새 앱을 시작하지 않는다.

---

## 3. 단원별 상세 연결 설계

이하 표에서 **`[기존]`은 현재 GitHub 참조 구현에서 확인한 개념/소스**, **`[신규]`는 앞으로 학생용 프로젝트에 작성할 파일·기능**, **`[제안]`은 EDU-05 승인 후 상세 구현 시 확정할 계약**을 뜻한다.

### 01단원. LLM 심화와 AI 프로젝트 출발

**새 이론:** 생성 결과와 검증된 사실의 차이, 현재 문서가 모델에 없는 경우, Chat·RAG·Agent·Multi-Agent의 최종 기능 대비, 실행 성공·답변 정확성·업무 허용 기준의 차이. **Phase1의 AI 역사·React/HTTP/JSON·Ollama 설치 기본을 다시 강의하지 않는다.**

| 구분 | 내용 |
|---|---|
| 시작 상태 | **제공된 최소 시작본**: Backend Provider/Service, `/health`, `/ai/chat`; React 질문/답변/오류 화면 |
| 학생 작업 | ① 파일 역할을 화면과 대응 ② 환경 변수 입력 ③ Backend·Frontend 실행 ④ 질문·공백/연결 오류 확인 ⑤ `기준 대화 앱` 기준 기록 작성 |
| 직접 수정 | 새로운 AI 기능 코딩은 없음. 설치·실행을 위해 학생이 설정을 수정하고 **실제로 실행한 기준점**을 확보 |
| 관찰 결과 | 사용자 질문 → React HTTP 요청 → FastAPI Service → Provider → 응답/오류 |
| 완료 검사 | `/health`, `/ai/chat`, 실제 React 질문, 입력 오류, Provider 연결 실패 중 정상·실패를 학생이 구분. 최소 하나의 정상 모델 경로가 준비되지 않으면 **환경 차단** 상태로 기록 |
| 다음 단원 입력 | 동일 `frontend/`, `backend/`, 실행 설정, 모델 호출 경로, 최초 질문/응답 기록 |
| 기존 자료 | `12. AI Integration/강의용.md`, `01. AI 최신 동향 및 전체 지도`, `04. 대규모 언어 모델(LLM)`의 실제 한계·평가 부분; `document-assistant/backend/app/main.py` 기준선 |

**교안 집필 요구:** Prompt·Context와 실행 관리의 Prompt 비교에 사용할 **작은 고정 가상 문서/질문 Fixture만 기준 대화 앱에 함께 제공**한다(미리 구현한 검색기는 포함하지 않음). 학생이 다운로드·복사할 시작본 목록, `cd` 위치, OS별 실행 명령, 새 브라우저 주소, 모델/키가 없을 때의 상태를 정확하게 적는다. 학생에게 미리 RAG·Agent 전체 구현을 복사하도록 하지 않는다.

### 02단원. Prompt & Context Engineering

**새 이론:** 동일 질문/문서를 유지한 채 지시·제약·출력 형식을 조정하는 방법, 신뢰할 수 없는 문서와 개발자 지시의 경계, 이번 호출에 포함되는 Context의 수명·선택·순서·Token 예산. Phase1의 Tokenizer·Context Window 정의는 다시 길게 반복하지 않는다.

| 구분 | 내용 |
|---|---|
| 선행 | 기준 대화 앱의 실제 Chat 요청이 정상 동작 |
| `[신규]` | `app/prompting.py`: `build_messages(question, documents, policy)` 또는 단일 Provider 입력 생성(하나의 함수가 **미리보기와 실제 호출에 공통 사용**) |
| `[신규]` | `app/assistant_service.py`: Chat 요청의 입력 조립과 기존 Provider 호출 조정. 이 파일을 03·07·09·10단원에서 확장 |
| 수정 | `app/main.py`: 입력 미리보기용 API 추가; `App.jsx`/`api.js`: **실제로 전송되는 입력**을 보여주는 패널 추가 |
| 학생 구현 순서 | ① 기준 대화 앱 고정 Fixture를 읽고 지시·자료·질문 구획 나누기 ② 예시가 포함될 때의 변화를 구성 ③ 불필요한/사용 금지 문서 제외 ④ 길이/Token 측정값의 실측·미측정 구분 ⑤ 같은 조립 함수로 실제 모델 호출 |
| 화면 관찰 | 동일 질문에서 지시 변경/문서 선택 시 실제 전송 입력이 어떻게 달라지는지 확인. 생성 답의 품질 향상은 자동으로 주장하지 않음 |
| 필수 예외 | 입력 공백, 자료 없음, 길이 초과, 문서에 들어 있는 ‘이전 지시 무시’ 같은 지시형 문자열을 **자료로만 처리** |
| 다음 단원 입력 | `build_messages(...)`와 Provider 요청 연결, 입력 미리보기 화면 |
| 기존 자료 | Prompt/Context 강의용, `L1.md`, `CONTEXT.md`, `backend/app/experiments.py`, `/ai/prepare`의 입력 구성 참고 |

**주의:** 현재 GitHub의 `/ai/prepare`는 `case_id`와 `variant`로 고정 자료를 조립하는 **기존 실험**이다. 학생이 브라우저에서 임의 질문을 보내는 새 입력 미리보기는 이를 그대로 학생의 실제 Chat 연동이라고 부르지 않는다. 별도 통합을 구현해야 한다.

### 03단원. AI 실행 관리(Harness)

**새 이론:** 통신 실패·응답 형식 실패·근거 실패의 차이, 재시도와 수정 요청(Repair)의 차이, 총 호출 예산과 시간 한도, 종료 기록. 고정 응답 테스트와 실제 모델 생성의 차이.

| 구분 | 내용 |
|---|---|
| 선행 | Prompt·Context `build_messages`가 정상적으로 실행/표시 |
| `[신규]` | `app/harness.py`: `run_with_limits(...)`, 응답 검증 함수, 시도 횟수/종료 사유 Trace |
| 수정 | `assistant_service.py`가 모델을 직접 호출하던 곳을 **Harness 호출**로 교체; 공통 응답 및 React 상태/시도 로그 패널 확장 |
| 학생 구현 순서 | ① 응답 Schema 정의 ② 첫 호출 ③ 잘못된 형식 판정 ④ 유형별 제한된 재시도·보완 ⑤ 횟수/취소/시간 한도 ⑥ 종료 기록 |
| 화면 관찰 | 정상 응답, 최초 실패 후 회복, 반복 실패 시 중단; 모델의 답이 의미상 틀려도 **형식 검사 통과할 수 있음**을 확인 |
| 필수 예외 | 잘못된 JSON, 통신 Timeout, 반복 실패, 취소 후 지연 응답, 허용되지 않은 재시도 |
| 다음 단원 입력 | 모든 이후 모드가 재사용할 `run_with_limits`, 공통 Trace 표시 |
| 기존 자료 | `05.../Harness/강의용.md`, `L2.md`, 기존 `app/harness.py` 및 `tests/test_harness.py` |

**주의:** 처음부터 복잡한 비동기 감독/하드 Cancel 보장을 구현한다고 주장하지 않는다. 취소한 응답은 UI에서 버리더라도 외부 모델 작업 중단이 보장되는지 별도로 확인해야 한다.

### 04단원. 문서 수집·전처리·Chunking

**새 이론:** 문서 원본과 검색용 텍스트의 차이, TXT/Markdown의 제목·단락·표 구조, 정규화와 원문 손실의 위험, **Chunk 단위 결정(단락/제목/길이/의미)**, Chunk ID·순서·출처 위치/버전·Metadata, 변경 시 재인덱싱의 필요.

| 구분 | 내용 |
|---|---|
| 선행 | 기준 대화 앱 Backend에 문서를 읽을 수 있는 Python 실행 환경. Prompt·Context/2는 뒤 RAG 연결에 활용 |
| `[신규]` | `data/sources/*.md`/`*.txt`: 기존 가상 규정을 **텍스트 원문으로 옮긴 교육용 샘플**. `data/catalog.json`에 ID/버전/상태/접근 범위를 따로 보존 |
| `[신규]` | `app/documents.py`: `load_documents()`, `normalize_text()`, `split_into_chunks()`, `locate_source()`, `rebuild_chunks()` |
| 수정 | `main.py`에 지정된 교육용 원본만 다시 읽는 API와 Chunk 조회 API, `App.jsx`에 문서/청크 목록 표시 |
| 학생 구현 순서 | ① **Prompt·Context 고정 Fixture와 동일한 가상 규정**의 TXT/MD 열기 ② 정규화 전후 비교 ③ 제목/빈 줄을 반영한 단락 분할 ④ 각 Chunk에 문서·버전·순번·원문 위치 ⑤ `local_data/chunks.json`(안)에 Snapshot 저장·재로드 ⑥ 원문 복귀와 분할 기준/문서 수정 시 변화를 확인 |
| 화면 관찰 | 원문 본문 → Chunk N개 → Chunk ID/번호/위치 → 원본 구간. 길이나 순서 변경 시 결과 차이 |
| 필수 예외 | 빈 문서, 너무 긴 단락, 제목만 있는 문서, 원문 줄 번호 손실, 폐기 버전/비허용 문서가 후속 검색에 섞이지 않도록 **Metadata 보존** |
| 다음 단원 입력 | 확정된 `Chunk` 목록, `source_id`, `source_position`, `document_version`, `content_hash` |
| 기존 자료 | `13. Document AI/01. 문서 등록.md` 일부, `11. OCR`의 원문 위치 개념 일부, `data/documents-v1.json`, `retrieval/index.py`의 Line/Metadata 구조 |

**Chunk 분할 기준(초안):** 제목/단락 경계를 우선 존중하고, 한 단락이 지나치게 길면 문장 경계에서 나눈다. 처음부터 기계적인 고정 길이 중첩(Overlap)을 강제하지 않는다. 각 Chunk는 `chunk_id`, `document_id`, `document_version`, `chunk_index`, `text`, `source_path`, `source_position`, `content_hash`, `access`, `current`를 보유하도록 설계한다. 나눈 텍스트를 이어 붙여 원문을 복원할 수 있는지(정규화로 제거한 공백의 차이는 별도 기록) 확인한다. 정확한 크기 상한과 정규화 규칙은 실제 교육 샘플·모델 제한을 확인한 뒤 EDU-07/08에서 고정한다.

**범위:** 이번 필수 교안은 **TXT/Markdown**만 처리한다. PDF·OCR·표 레이아웃 재구성은 심화. 기존 `retrieval/index.py`는 줄 단위로 청크를 만드는 구현이므로, 이번에 요구하는 단락/제목 기준을 **그대로 만족하는 코드라고 가정하지 않는다.** EDU-07에서 의도적으로 수정할 범위를 구분해야 한다.

### 05단원. Embedding

**새 이론:** Token ID와 검색용 Embedding의 차이, 생성 LLM vs 임베딩 Encoder, Passage/Query 입력 역할, 벡터·차원·정규화·Cosine Similarity, 의미 유사도와 사실/정책 적합성의 차이. Pooling은 **Embedding 생성에 필요한 원리**로만 다루고 Transformer 전체 수식은 반복하지 않는다.

| 구분 | 내용 |
|---|---|
| 선행 | 문서 처리 `Chunk` 목록에 본문과 출처가 존재 |
| `[신규]` | `retrieval/encoder.py`: `encode_passages(chunks)`, `encode_query(question)` 또는 공통 `encode(texts, kind)`; 출력값·모델 ID·Revision·차원을 기록 |
| 수정 | `main.py`에 관찰용 Embedding API; `App.jsx`에 **벡터 길이, 일부 숫자 값, 차원, 유사도** 표시 |
| 학생 구현 순서 | ① 기존 2개 Chunk를 Encoder에 전달 ② Passage Vector 생성 ③ 질문 Query Vector 생성 ④ 차원/Norm 확인 ⑤ Cosine Similarity 계산·정렬 ⑥ 단어가 다르지만 의미가 관련된 질문 비교 |
| 실행 필수 | **실제 임베딩 모델 1건 이상 로드·추론**. 실행 부담이 있으면 CPU용 모델/사전 다운로드 경로를 안내하되, 가짜 벡터만으로 단원 완료하지 않는다 |
| 화면 관찰 | `문서/질문 → 벡터 차원 → 일부 성분 → 코사인 유사도`가 실제 숫자로 표시. 임의의 점수는 가상 예제라고 분리 |
| 필수 예외 | 입력 누락, 모델 파일 없음, 차원 불일치, 길이 상한/잘림, 동일 모델·Revision이 아닌 벡터 혼합 금지 |
| 다음 단원 입력 | 재사용 가능한 Encoder와 `Chunk → Vector` 연결, Embedding 모델 프로필 |
| 기존 자료 | `06. 임베딩(Embedding)/강의용.md`, `backend/retrieval/encoder.py`, `L3.md` 중 Embedding 부분 |

**실제 기존 코드 근거:** `retrieval/encoder.py`에는 `intfloat/multilingual-e5-small` 및 특정 Revision, `query:`/`passage:` prefix, CPU 기반 `E5Encoder.encode(texts, kind)`가 존재한다. **이번 설계에서 실습 모델의 확정 설치 조건/교육장 재현 성공까지 검증한 것은 아니다.**

### 06단원. Vector DB & Retrieval

**새 이론:** 벡터 생성(Encoder)과 검색 Index(저장/조회)의 분리, 본문·Vector·Metadata 저장, SQLite 기반 Exact Search와 전용 Vector DB의 차이, Top-k/거리/정렬·필터, 갱신·삭제·재색인, ANN·Hybrid는 비교 개요.

| 구분 | 내용 |
|---|---|
| 선행 | Embedding에서 생성한 실제 문서/질문 Embedding |
| `[신규]` | `retrieval/index.py`: `build_index(chunks, encoder)`, `search(question, top_k)`, `read_chunk(source_id)`, `invalidate_on_change()`; SQLite 이용 |
| 수정 | `main.py`에 검색 요청 API, `App.jsx`에 `검색어/순위/점수/원문/문서상태` 표시 |
| 학생 구현 순서 | ① 기존 Chunk·Vector를 SQLite에 저장 ② 질문 임베딩 ③ 대상 문서 필터 ④ Exact Cosine Similarity 정렬 ⑤ 상위 Chunk 표시 ⑥ 문서 버전 변경/삭제 후 오래된 검색 결과 차단 |
| 화면 관찰 | 유사도 상위 자료, 허용 문서의 위치·버전; 오래된 규정이 현행 규정처럼 나오지 않는지 |
| 필수 예외 | 제한 자료/폐기 문서 제외, 빈 검색, 모델 프로필이 바뀐 상태, 이전 Index 결과 재사용, 원문 수정 후 Stale 선택 |
| 다음 단원 입력 | 단일 `search`/`read_chunk` 인터페이스 + 검색 결과·원문 위치 |
| 기존 자료 | `07. 벡터 데이터베이스(VectorDB)/강의용.md`, `retrieval/index.py`, `L3.md` Index 부분 |

**주의:** SQLite + Python의 전체 Vector Exact 비교는 **교육용 검색 Index**이지 SQLite 자체를 전용 벡터 DB와 완전히 동일하게 구현했다는 뜻이 아니다. ANN/HNSW/FAISS 설치·재현은 **선택 심화**로 둔다.

### 07단원. RAG 구축

**새 이론:** 문서 인덱싱과 질문시 Retrieval 분리, 검색된 Chunk를 Context에 넣는 방식, 검색 결과와 답변의 차이, Claim/Quote/Source 확인, 근거 부족 시 보류·되묻기, **인용 존재 ≠ 주장 사실성**.

| 구분 | 내용 |
|---|---|
| 선행 | Prompt·Context Prompt Builder + 실행 관리 Harness + 문서 처리 Chunk + 벡터 검색 Retrieval |
| `[신규]` | `app/rag.py`: `answer_with_retrieval(question, index, provider)`; 검색→필터→Context→생성→출처 연결 |
| 수정 | `assistant_service.py`에 `mode='rag'` 연결, `App.jsx`의 모드 선택에 `RAG` 추가, 근거/상태 표시 |
| 학생 구현 순서 | ① 질문 받아 검색 ② 현재·허용된 근거만 선택 ③ Context 구성 ④ 구조화 답변 생성 ⑤ 출처 ID/인용 일치 확인 ⑥ 근거가 없을 때 보류 ⑦ 기존 Chat과 같은 질문 비교 |
| 화면 관찰 | 같은 질문의 Chat/RAG 차이, 답변과 관련된 Chunk/원문 링크, 찾지 못한 경우의 상태 |
| 필수 예외 | 환각/틀린 주장, 인용문만 일치하는 잘못된 답, 관련 문서 없음, 도중 문서 변경, Provider 실패 |
| 다음 단원 입력 | Chat + RAG 두 모드, 재사용 가능한 Search/Read/Context/검사 함수 |
| 기존 자료 | `08. 검색 증강 생성(RAG)/강의용.md`, `L4.md`, `app/rag.py`, `tests/test_rag.py` |

**중요:** 자료를 인용해도 모델이 잘못된 금액을 말할 수 있다. 교육용 응답 구조에서 **구조 검사 통과**와 **사실성 검토 필요**를 분리하여 학생 화면에도 표현한다.

### 08단원. Tool Calling

**새 이론:** Tool 이름/설명/입력 Schema, 모델이 요청하는 작업과 Backend가 허용·실행하는 작업의 분리, 도구 Registry/Dispatcher, 인자 검증, 권한·실패·결과 메시지. Tool Calling이 곧 Agent 전체를 의미하지 않음.

| 구분 | 내용 |
|---|---|
| 선행 | RAG의 검색·원문 읽기 함수 |
| `[신규]` | `app/tools_registry.py`: `search_documents(query, k)`·`read_evidence(source_id)`만 허용, `dispatch_tool(name, arguments)` 및 Schema |
| 수정 | 관찰 API/React에 요청 이름·인자·허용 여부·실제 실행값 표시 |
| 학생 구현 순서 | ① Tool Schema 선언 ② Registry 작성 ③ 허용 목록 검사 ④ 인자 Validation ⑤ 기존 검색/읽기 함수 연결 ⑥ 실행 결과를 모델/화면에 돌려주기 |
| 화면 관찰 | 도구 **요청**, 실제 **실행**, 조회 결과를 서로 다른 이벤트로 확인. 잘못된 Tool명·인자 거부 |
| 필수 예외 | 없는 도구, 과도한 k, 제한/폐기 문서 조회, 임의 파일 읽기, 모델 문장에 들어 있는 ‘승인됐다’ 지시 |
| 다음 단원 입력 | 안전한 Tool Registry, 결과 메시지, 공통 Trace 이벤트 |
| 기존 자료 | `09. Agent/01. Single-Agent`의 Tool 부분, `L5.md`, `app/agent.py`의 `Registry`, 관련 Tests |

**기술 구분:** 기존 참조 구현에는 모델의 **구조화된 JSON 행동 요청 → Python 검증·Dispatch** 경로가 있다. 이는 도구 사용의 요청/실행 원리를 학습하는 방법이지만, 모든 Provider SDK의 네이티브 Tool Calling API를 이미 구현했다는 뜻은 아니다. **네이티브 Tool Call ID/메시지 프로토콜은 Provider 선택 이후 별도 구현 여부를 표시**한다. 실제 학생 결과에는 *요청이 모델로부터 왔는지 또는 고정 응답 Fixture인지*를 구분한다.

### 09단원. Single-Agent 구축

**새 이론:** 고정 RAG Workflow와 동적 행동 선택의 차이, 관찰→다음 행동→도구→새 관찰을 반복하는 Agent Loop, 상태/이력, 종료 조건, 예산·Timeout, 허용되지 않은 행동을 거절하는 Runtime.

| 구분 | 내용 |
|---|---|
| 선행 | Tool Calling Tool Registry + 실행 관리 실행 제어 |
| `[신규]` | `app/agent.py`: `run_agent(question, tools, provider, limits)` 및 모델 응답 구조 파서·Trace |
| 수정 | `assistant_service.py`에 `mode='single'` 연결, `App.jsx`에 단계별 Tool 호출/결정 표시 |
| 학생 구현 순서 | ① 질문/현재 상태 생성 ② 모델이 다음 행동 선택 ③ 허용 Tool 실행 ④ 관찰값을 다음 입력에 추가 ⑤ 최종답/되묻기/보류/정지 판정 ⑥ 반복 한도 초과 시 중단 |
| 화면 관찰 | 실제 검색 요청→근거 읽기→최종 응답 또는 조건 추가 질문·중단. 선택하지 않은 Tool은 실행하지 않아야 함 |
| 필수 예외 | 같은 행동 무한 반복, 미허용 Tool, 출처 없는 최종답, Tool 오류, 예산 초과/취소 |
| 다음 단원 입력 | 재사용 가능한 Agent 실행/Trace, `search`/`read` 결과와 종료 정책 |
| 기존 자료 | `09. Agent/01. Single-Agent`, `L5.md`, `app/agent.py`, `tests/test_agent.py` |

**주의:** 단순히 `search→read→answer`를 **항상 하드코딩**하면 Single-Agent 기능을 설명하기에 부족하다. 최소 한 단계는 **실제 모델이 허용된 후보 중 다음 행동을 요청**하고 Runtime이 그 행동을 검증·실행하도록 한다. 결정 경로와 재현용 Fixture 테스트는 별도로 남긴다.

### 10단원. Multi-Agent 구축

**새 이론:** Agent 간 목표/책임 분리, 검색자·작성자·검토자의 데이터 전달, 역할별 입력 범위, 공통 예산, 실패 전파, 전체 종료 책임, 모델 검토와 실제 승인 분리.

| 구분 | 내용 |
|---|---|
| 선행 | Single-Agent Agent Loop, RAG Grounding, Tool Calling Tool Registry |
| `[신규]` | `app/multi_agent.py`: 검색→작성→검토 **순차 역할** 실행, `handoff`, shared `budget`, `finish` 처리 |
| 수정 | `assistant_service.py`에 `mode='multi'` 연결, `App.jsx`에 역할 카드/전달된 출처/최종 평가 표시 |
| 학생 구현 순서 | ① 역할별 입출력 Schema ② 검색 역할에 Tool 허용 ③ 근거와 Chunk ID를 작성 역할에 전달 ④ 검토 역할에 Claim/Quote 전달 ⑤ 근거 누락·오류 반환 ⑥ 공통 모델/Tool/재시도 예산에서 종료 |
| 화면 관찰 | 역할별 요청/응답/전달 자료의 흐름, 어느 역할에서 중단되었는지, 결과 검토 상태 |
| 필수 예외 | 허용되지 않은 Handoff, 없는 출처·변경된 Chunk ID, 반복 검토, 공통 예산 초과, 모델 검토의 ‘승인’ 오인 |
| 다음 단원 입력 | Chat/RAG/Single/Multi 4모드와 실행 Trace/출처 |
| 기존 자료 | `09. Agent/02. Multi-Agent`, `L6.md`, `app/multi_agent.py`, `tests/test_multi_agent.py` |

**주의:** 기존 구현은 **한 Provider를 역할별로 순차 호출**할 수 있는 구조다. 여러 GPU/서버나 독립된 모델 세 개를 요구하지 않는다. Orchestrator가 허용된 역할 순서를 정하고 모델은 역할 범위 안에서 행동한다. 이것을 완전 자율 분산 Agent라고 설명하지 않는다.

### 11단원. 통합 서비스 및 최종 검증

**새 이론:** 공통 API/응답·출처·Trace 계약, 로딩/오류/취소와 오래된 결과 차단, 동일 질문으로 다른 모드 비교, 고정 응답 테스트/실제 모델 실행/답변 정확성 평가의 차이. Phase1의 React/FastAPI 문법 재강의 금지.

| 구분 | 내용 |
|---|---|
| 선행 | 01~10단원 누적 코드: 4가지 모드 + Chunk/Index/Embedding/Tool/Trace |
| 수정 | 기존 `App.jsx`/`api.js`에서 이미 연결한 영역을 **정돈**. `schemas.py`, `assistant_service.py`, `main.py`의 통합 계약·예외 일관성 점검 |
| 학생 구현 순서 | ① 실행 모드 네 개 비교 ② Chunk/Embedding/검색 상태 확인 ③ 근거/Trace 표시 ④ 실패·취소·중복 요청 화면 관리 ⑤ 문서 변경/회귀 테스트 ⑥ 결과 기록 |
| 화면 관찰 | 같은 가상 문서/질문으로 Chat·RAG·Single·Multi를 실행하고 **답변/근거/실행 단계/오류** 비교 |
| 필수 예외 | 오래된 요청의 늦은 응답이 새 결과 덮어쓰기, 근거 없는 결론, API 계약 불일치, 로컬 모델 불가/시간 초과 |
| 다음 전달물 | 학생용 최종 프로젝트 소스·실행 README·테스트/관찰 보고, 강사용 기준 구현 및 재현 절차 |
| 기존 자료 | `12. AI Integration` 기준 앱, `13. Document AI`의 검증·화면 범위 중 필요한 부분, 기존 React·API 계약 테스트 |

**중요:** 11단원에서 새 프런트엔드 앱을 만드는 것이 아니다. **01단원부터 같은 `frontend/src/App.jsx`가 존재**하고 02~10에서 기능을 누적했음을 Diff로 보여준다.

---

## 4. 학생용 API 계약 초안 — EDU-05 승인 후 EDU-07/08에서 구현

> 아래는 **새 학생 앱의 목표 설계**다. 현재 GitHub API가 모두 이 형태라는 뜻이 아니다. 기존 `/ai/chat`와 `/ai/prepare`의 동작은 **보존**하고, 학생용 누적 기능은 별도 경로에 연결한다. 이름·세부 스키마는 이 문서의 승인 후 교안/코드에 동일하게 적용한다.

### 4.1 기존 유지 API (GitHub에서 확인)

| API | 확인된 실제 동작 | 주의 |
|---|---|---|
| `GET /health` | 설정된 Provider/Model 등 Backend 준비 상태 | 실제 모델 생성 성공 판정 아님 |
| `POST /ai/chat` | `{ "message": "..." }` → `{ "provider": ..., "model": ..., "answer": ... }` | 기존 Chat 계약 유지 |
| `POST /ai/prepare` | `{ "case_id": "C01", "variant": "baseline" }` 등 고정 사례 준비 | `generation_executed: false`인 입력 실험. 브라우저 자유 질문/API와 동일하지 않음 |

### 4.2 새 누적 학습 API 후보

| 도입 단원 | API (설계 후보) | 역할/요청 | UI에서 보이는 결과 |
|---|---|---|---|
| 02 | `POST /api/v1/assistant/preview` | `question`, 선택한 문서 ID/지시 변경 조건 → **실제 호출과 동일한 Builder**가 조립한 입력 | 입력 섹션·선택 문서·측정/미측정 길이 |
| 02 (이후 확장) | `POST /api/v1/assistant/run` | `question`, `mode=chat\|rag\|single\|multi` → 공통 응답. **처음에는 chat만 활성화** | 답·상태·Trace·근거(기능별 점진적 추가) |
| 04 | `POST /api/v1/documents/rebuild` | 사전에 제공한 **교육용 sources/catalog만** 다시 읽어 Chunk 구성 | 문서·Chunk 수, 원문 위치 |
| 04 | `GET /api/v1/documents/chunks` | Chunk 목록 조회 (민감한 원문은 제외하는 **교육용 Fixture** 전용) | Chunk ID/본문/순서/원문 위치 |
| 05 | `POST /api/v1/retrieval/embedding-preview` | `question` 및 샘플 Chunk ID → 벡터 차원·일부 성분·유사도 | 실제 Embedding 관찰 |
| 06 | `POST /api/v1/retrieval/search` | `question`, `top_k` → 적격 Chunk·점수·출처 | 검색 결과 확인 |
| 07 | 기존 `assistant/run` 확장 | `mode=rag` 활성화 | RAG 답/근거 |
| 08 | Tool 관찰 (동일 Trace) | 모의 행동/모델 요청의 `tool_call` 결과 표시. 별도 공개 API는 필요할 때만 | 요청/검증/실행 결과 구분 |
| 09 | 기존 `assistant/run` 확장 | `mode=single` 활성화 | Agent Trace |
| 10 | 기존 `assistant/run` 확장 | `mode=multi` 활성화 | 역할별 Handoff·검토 |
| 11 | 변경 없이 정리 | 네 모드·오류/취소/근거 계약 검증 | 같은 앱에서 전체 비교 |

**Prompt·Context와 문서 수집 연계:** Prompt·Context와 실행 관리는 `data/fixtures`의 고정 자료를 사용하며, 문서 처리에서 그와 **동일한 문서 ID/규정 내용**을 TXT/MD와 `catalog.json`으로 가져온다. 문서 처리의 재구축이 끝나면 후속 Embedding·검색부터 Multi-Agent까지은 `local_data/chunks.json`/Index를 기준으로 동작한다.

**교육용 안전 범위:** 문서 추가 API는 외부 임의 파일 경로나 절대경로를 받지 않는다. 문서는 미리 제공한 `data/sources`에서만 읽는다. 지금 사용하는 `access: staff`는 가상 시나리오 표시이며 **로그인/실제 인증·인가 기능이 아니다**.

### 4.3 공통 응답 최소 형태 (제안)

```json
{
  "mode": "rag",
  "status": "completed",
  "outcome": "answer",
  "answer": "[모델이 실제 생성한 문장 또는 Fixture 결과]",
  "sources": [
    {
      "source_id": "DOC-A@v1:C001",
      "document_id": "DOC-A",
      "version": "v1",
      "locator": "교육용 샘플의 실제 위치",
      "quote": "[검사 대상 원문 인용]"
    }
  ],
  "trace": [
    {"seq": 1, "stage": "retrieval", "event": "searched"},
    {"seq": 2, "stage": "generation", "event": "generated"}
  ],
  "evidence_kind": "actual_model_or_fixture",
  "review_status": "not_independently_verified"
}
```

**이 JSON은 실제 실행 결과가 아닌 `설계 스키마 예시`다.** 값의 어구/ID는 교육용 설명을 위한 가상 예시다. 최종 구현은 `status`(기술 실행 종료/오류/차단), `outcome`(answer/abstain/clarify/deny 등), `review_status`(사실성 별도 검토)를 분리한다. `trace`에는 실제 사용한 Tool과 역할 단계만 기록하고 모델 내부 사고과정이나 비밀정보는 넣지 않는다. Fixture 결과의 `evidence_kind`를 실제 모델 결과와 혼동하지 않는다.

### 4.4 계약 호환성 검사

- **절대 변경 금지:** `/ai/chat`의 `message` 요청 및 `provider/model/answer` 응답 구조를 새 API 때문에 바꾸지 않는다.
- **한 경로 재사용:** React와 테스트는 `frontend/src/api.js`의 한 HTTP 유틸리티를 통해 통신한다. API URL·필드는 단원마다 임의로 바뀌지 않는다.
- **비활성 모드:** 수업에서 아직 구현하지 않은 모드는 UI에서 비활성화. Backend도 유효하지 않은 `mode`를 명시적으로 거부한다.
- **답변 판단:** `sources`가 비어 있거나 `review_status` 미검증인데도 무조건 정확한 답이라고 표기하지 않는다.
- **변경 시 재검사:** Source/Index가 바뀐 뒤에는 이전 결과의 Chunk ID/버전/해시를 재확인하고 오래된 근거를 사용하지 않는다.
- **오류:** HTTP 검증 오류와 모델/검색/도구 실패를 구분. 기존 422/502/503/504 계약과 충돌하지 않게 EDU-07/08에서 명시적 테스트로 고정.

---

## 5. 공통 가상 문서·질문 세트 (재사용 대상)

**현재 GitHub에 확인된 실습 자료:** `02. 실습/document-assistant/data/documents-v1.json` 및 `core-v1.json`. 이 두 파일은 TXT/MD 원문·청크 실습을 만들 때 **교육용 사실과 테스트 조건을 보존하는 기준**으로 사용할 수 있다.

| 자료·사례 | 기존 확인된 내용 | 누적 사용 단계 | 확인할 핵심 |
|---|---|---|---|
| `DOC-A` | 현행 가상 출장 규정, 식비 상한·사전 승인·영수증·식사 제공 예외 | Prompt·Context~최종 통합 | 정답 근거·출처 |
| `DOC-B` | 가상 교육비 규정, 사전 승인·상한·증빙·제외 조건 | 문서 처리부터 최종 통합까지 | 유사/비유사 문서 구분 |
| `DOC-A-OLD` | 폐기된 과거 출장 규정 | 문서 처리부터 최종 통합까지 | 오래된 문서 제외·버전 변경 |
| `DOC-R` | 접근 제한용 가상 자료 | 문서 처리부터 최종 통합까지 | 검색/입력/답변에서 제외. 실제 인증 구현으로 오인 금지 |
| `DOC-I` | 문서 안에 들어 있는 명령형 공격 샘플 | Prompt·Context, 문서 처리부터 최종 통합까지 | 자료 내용은 Model/시스템 지시가 아님 |
| `DOC-T` | 텍스트 표 형식의 시작 자료 | 문서 처리부터 Tool Calling까지 | 표/원문 위치 관련 주의. OCR 결과로 제시하지 않음 |
| `C01` | 국내 당일 출장 식비 조건과 자료 질문 | 전 단계 동일 질문 비교 | 정답 근거와 조건/예외 |
| `C03` | 해외 출장 숙박비 상한 질문 | RAG부터 최종 통합까지 | 문서에 없는 조건을 만들어 답하지 않음 |
| `C04` | 조건이 빠진 식비 질문 | RAG부터 최종 통합까지 | 조건부 답/되묻기 |
| `C05` | 이전 문서와 현행 문서의 금액 충돌 | 벡터 검색부터 최종 통합까지 | 현행 버전 기준 확인 |
| `C06` | 제한 문서 표식 요청 | 벡터 검색부터 최종 통합까지 | 가상 접근 경계·정보 노출 방지 |
| `C07` | 첨부 메모의 잘못된 지시 요구 | Prompt·Context, RAG부터 최종 통합까지 | 명령처럼 보이는 자료를 그대로 따르지 않음 |

**데이터 사용 원칙:** 기존 수치와 규정은 전부 **가상 교육 데이터**다. 학생용 TXT/MD로 옮길 때 문서 버전·접근 범위·현행 여부를 임의로 제거하지 않는다. `DOC-R`과 `DOC-I`처럼 수업의 실패 조건을 검증하는 자료도 누락하지 않는다. 같은 질문/자료를 재사용하는 것은 기능이 발전하는 변화를 보기 위한 것이지, 같은 개념을 비슷한 예시로 길게 재강의하기 위한 것이 아니다.

---

## 6. 수업·구현 검증 매트릭스

### 6.1 단원별 최소 검사 (모두 **실행 전 설계 예정 항목**)

| 단원 | 구조·기능 검사 | 학생이 남길 화면/터미널 증거 |
|---|---|---|
| 01 | Chat 성공, 빈 질문 422, Provider 연결 오류와 UI 표시 | 기준 Chat 요청/응답·오류 |
| 02 | 미리보기/실제 호출 입력 일치, 부적격 자료 제외, 자료 안 지시를 데이터로 처리 | Prompt 변화 화면 |
| 03 | 정상·형식 오류·재시도 상한, 중단 Trace | 시도 횟수·종료 이유 |
| 04 | TXT/MD Chunk 원문 복귀, 순서·위치, 빈/변경 문서 | Chunk 목록·원문 위치 |
| 05 | **실제 Embedding 추론** 1건, 차원/Norm, Query/Passage 역할 구분 | 벡터 차원·유사도 |
| 06 | Top-k, 제한/폐기 문서 제외, 문서 변경 후 재인덱싱·Stale 방지 | 검색 표·버전 |
| 07 | RAG 근거 표시, 근거 없는 질문, 잘못된 인용/주장 구분 | RAG 답/출처·보류 |
| 08 | 허용 Tool만 호출, 인자 오류 거부, 요청/실행 구분 | Tool Trace |
| 09 | 모델 행동 요청, 한도 내 실행, 반복/오류 종료 | Agent 단계·종료 |
| 10 | 역할 전달, 공유 한도, 실제 모델 역할 호출 구분 | 역할 전달 Trace |
| 11 | 최종 일곱 가지 시나리오 전체 회귀/E2E | 4모드 비교 화면·실행 로그 |

**수행 원칙:** 학생은 각 단원에서 **새 기능 검사 + 이전 기능의 최소 회귀 검사**를 한다. 예를 들어 07단원 RAG를 구현한 뒤에도 01단원 Chat 모드가 정상 작동해야 한다.

### 6.2 최종 일곱 가지 필수 검증 시나리오

| 검증 내용 | 대응 단원 | 필수 증거 |
|---|---|---|
| 기준 앱 대화 | 01, 11 | 실제 Backend/Frontend Chat 왕복 |
| Chunk/Index 조회 | 04~06, 11 | Chunk·Embedding·Index 저장 및 조회 |
| 근거 있는 RAG 질문 | 07, 11 | 검색→생성→답/출처 |
| 근거 없는 질문 | 07~11 | 보류/되묻기 또는 명확한 실패 안내 |
| Single 도구 호출 | 08~09, 11 | 모델/Fixture 출처 표시, 요청·Dispatch·종료 |
| Multi 역할 협업 | 10, 11 | 역할별 Handoff/공통 예산/결론 |
| 문서 변경·오류 | 06~11 | 이전 Index/근거 무효화, 오류 처리와 회귀 유지 |

### 6.3 같은 테스트라도 결과를 따로 기록

1. **정적 검사:** 코드·타입·링크·파일 경로가 올바른가.
2. **Fixture 기능 검사:** 정해진 응답을 통해 루프/도구/경계가 동작하는가.
3. **실제 모델·Embedding 실행:** 진짜 모델/Provider를 호출했는가, 어떤 장비/버전/명령이었는가.
4. **결과 내용 검토:** 답이 규정과 일치하는가, 근거가 주장을 지지하는가.
5. **학생 수업 재현:** 깨끗한 환경과 Obsidian 절차로 초보자가 실제 완주할 수 있는가.

Fixture가 성공했다고 실제 모델이 안정적으로 정확히 답한다는 뜻은 아니다. 현재 GitHub 과거 `milestones/L4~L6`도 기능/실행 이력과 **답변·과제 품질 미채택**을 분리하고 있다.

---

## 7. 기존 자료 재사용·작성 충돌 방지표

| 자료 | 새 단원으로 가져갈 **고유한 내용** | 이번 교안에서 다시 만들면 안 되는 것 |
|---|---|---|
| `01. AI 최신 동향 및 전체 지도` | 업무 문제, 막아야 할 실패, 실행 단계와 책임 | Phase1 AI 역사·모델/앱 비유 전체 재진술 |
| `02. AI 머신러닝 딥러닝 개요` | 평가·데이터 누수·실험 조건 등 새 프로젝트와 관련된 부분 | ML/DL 기초를 다시 한 교시로 전부 반복 |
| `03. Transformer` | 05단원에 필요한 벡터/Pooling 원리 연결 | Q/K/V 손계산 전체를 본과정 필수로 반복 |
| `04. LLM` + Hugging Face | 출력 근거·Token/Context 한계 중 **이번 프로젝트 판단에 필요한 대목** | Phase1 Tokenizer 설치/모델 실행/Model Card 첫 설명 반복 |
| `05. Prompt/Context/Harness` | 입력 구성, 실행 제어, 경계검사 | 관찰 실습 결과만 다시 읽고 코드 작성 없이 종료 |
| `06. Embedding` | 실제 문서/질의 Embedding·유사도 | 말로만 개념 설명하고 모델 추론은 하지 않기 |
| `07. Vector DB` | SQLite Index/검색/갱신 | 외부 Vector DB 설치를 필수로 강요 |
| `08. RAG` | 검색→Context→생성·근거 검토 | 인용이 존재하면 사실성이 검증됐다고 가르치기 |
| `09. Agent` | Tool 계약→Single 반복→Multi 전달 | Single/Multi 완성코드를 시작본에 넣기 |
| `12. AI Integration` | 기존 Chat API/Provider 기준선 | 같은 앱을 01단원에서 다시 처음부터 전부 작성 |
| `13. Document AI` | 04 원문/버전, 07 근거, 11 전송 상태 중 필요한 것 | OCR/보고서·고급 Streaming을 본과정 핵심 경로에 끼워 넣기 |
| `L1~L6`, `CONTEXT.md` | 비교·오류/경계·평가 사례와 현재 구현 참고 | 저장된 과거 결과를 지금 학생의 실행 성공으로 표시 |

**실행 전 재확인 이슈:** 기존 L3~L6 일부 문서는 과거 `curriculum-work/reports/...` 경로를 전제로 한다. 현재 `academy/02. 실습/...`에서 그대로 실행하면 상대 경로가 맞지 않을 수 있다. 새 학생용 교안에서는 **학생 프로젝트 루트를 기준으로 명령/파일 위치를 통일하고 정적 링크 검사 + 실제 실행을 수행**한다.

---

## 8. 단원별 실제 교안 제작 템플릿 (EDU-09~19 공통)

**반드시 모두 포함한다.** 세부 문체와 강의 분량은 집필 단계에서 조정하지만, 빠지면 ‘교안 작성 완료’로 처리하지 않는다.

```text
[단원 번호·단원 제목]
1. 오늘 만들 기능과 지난 단원 결과의 연결
2. 이번 단원에서 처음 배우는 개념
   - 왜 필요한가 / 쉬운 정의 / 실제 동작 / 코드 책임 / 흔한 오해
   - 이미 배운 Phase1·이전 Phase2 개념은 연결 문장으로만
3. 학생이 단원 시작 전에 갖고 있어야 할 폴더·파일·실행 상태
4. 이번 단원에서 추가·수정할 파일 목록과 해당 파일이 맡는 역할
5. 따라 하는 코드 작성 (반드시 단계 순서대로)
   - 새 파일: 복사해서 저장할 **전체 코드**
   - 기존 파일: 수정 전 위치와 수정 후 코드, 교체 범위 정확히 표시
   - 모든 Import·의존 파일을 함께 확인
6. 실행 명령 (작업 디렉터리, OS별 차이, 준비 조건 명시)
7. 눈으로 확인할 결과 (브라우저/터미널/API, 샘플과 실측 구분)
8. 실패했을 때 확인하는 순서 (입력/설정/코드/모델/검색/권한)
9. 이번 단원 새 기능 검사 + 이전 단원 회귀 검사
10. 다음 단원으로 가져갈 파일·데이터·함수·상태
11. 간단한 응용·확인 문제 (이번에 새롭게 배운 내용만)
[강사용 별도]
- 준비해야 할 모델·파일·환경, 시간 소모 구간, 정답/오답·오류 설명
- 단원 완료 증빙 및 학생 코드 비교를 위한 기준 구현
```

**완료 실패 예시:** 강사가 기존 코드를 실행한 화면만 보여 줌 / 학생이 어떤 파일을 수정해야 할지 모름 / 붙여넣는 코드가 뒤 단원 함수를 미리 Import함 / 단원별 새 앱을 생성함 / 수업 자료 링크가 열리지 않음 / Fixture만 실행하고 실제 모델로 구현 완료를 주장함.

---

## 9. 지금 확인된 사실·새 설계·미결정의 분리

| 항목 | 구분 | EDU-05의 처리 |
|---|---|---|
| 기존 `/ai/chat`, `/ai/prepare`가 있는 FastAPI 기준 구현 | **GitHub에서 확인** | 시작본 설계에 반영, 기존 API 보존 |
| 기존 RAG/Single/Multi Python 구현과 테스트가 있음 | **GitHub에서 확인** | 강사용 참조. 학생 시작본에는 선행 노출하지 않음 |
| 기존 `retrieval/index.py`는 SQLite/줄 단위 Chunk 구조 | **GitHub에서 확인** | 단락/제목 Chunking 요구와 차이를 기록 |
| 기존 E5 Encoder가 특정 모델/Revision을 사용 | **GitHub에서 확인** | 실제 CPU 모델 실습 후보로 연결. 현재 학생 장비 실행은 미검증 |
| `frontend/src/App.jsx`가 처음부터 동일 앱에서 확장 | **EDU-03/04 승인 설계** | 기준 대화 앱 시작본에 편성, 파일 전체를 바꾸지 않음 |
| 학생용 `prompting.py`, `documents.py`, `tools_registry.py` | **EDU-05 신규 설계** | EDU-07~08에서 직접 작성 코드로 구현 |
| `api/v1/assistant/...` 등의 신규 계약 | **EDU-05 설계 제안** | 승인 후 코드·교안·테스트 일치하도록 확정 |
| 학생 PC의 운영체제·실제 모델·패키지 버전 | **확정 전** | EDU-07~08에서 수업 환경/대체 실행 조건 고정 |
| 직접 붙여넣을 전체 코드와 단계별 Diff | **미작성** | EDU-09~19 및 EDU-07~08 |
| 실제 E2E/정답 정확성/학생 수업 재현 | **미검증** | EDU-24~25에서 직접 검증 |
| 오프라인 교육장 모델 설치의 시간·용량 | **미확정** | 배포 전 다운로드/캐시 계획 수립 |

---

## 10. EDU-05에서 다음 작업으로 넘기는 것

### EDU-06 — Obsidian 구조 설계

- 단원 01~11 폴더는 **실제 수업 순서**에 맞게 새로 만든다.
- 하나의 학생 실습 프로젝트와 단원별 **코드 작성 지시 문서**를 연결한다.
- 기존 원본 강의·전체 완성본·학생 시작본/단계별 코드·강사용 정답을 서로 구분한다.
- 본과정의 흐름을 깨지 않는 심화 자료(Transformer 계산·Fine-tuning·OCR·Document AI) 위치를 별도로 정한다.

### EDU-07~08 — 실제 학생용 시작본과 단계별 코드

- **기준 대화 앱 시작본만** 처음 배포한다. Provider 경로/학생 PC/버전을 1벌로 정하고 `App.jsx`가 실제 실행됨을 확인한다.
- Prompt·Context부터 Multi-Agent까지에서 새 파일/수정 파일별 **코드 블록과 Patch 순서**를 구현·검증한다.
- 위 신규 API 계약은 같은 Backend/Frontend에서 테스트로 일치시킨다.
- 참고 구현의 복잡한 경계를 모두 처음부터 노출하지 말고, 해당 단원에서 배운 기능만 직접 구현하게 한다.

### EDU-09~19 — 실제 교안 제작

- 각 단원에 충분한 이론 설명과 단계별 붙여넣을 코드·실행/검증 결과를 함께 작성한다.
- 매 단원 `지난 단원에서 남긴 코드 → 이번에 새로 만드는 코드 → UI/CLI 확인 → 다음 코드`를 한 문서 안에서 이어준다.
- Phase1은 전수 재분석 없이 **겹치는 해당 개념/예제만** 점검한다.
- 기존 실습 원본과 작성 교안 간 변경·이동 관계를 추적한다.

### EDU-24~26 — 검증/배포

- 단원마다 실제 설치·실행·브라우저 검증, 단원 간 회귀 테스트, 학생의 수업 가능성 검수.
- 승인된 설계는 GitHub에서 이력으로 관리하되, 실제 교안/코드가 생성·검증됐다는 주장과 구분한다.

## 11. EDU-05 종료 판정

- [x] EDU-03·04의 목표와 11개 단원을 기준 대화 앱 실행부터 최종 통합까지에 연결했다.
- [x] 단원별 **새 개념·학생 수정 파일·구현 순서·관찰·오류·다음 단원 입력**을 정의했다.
- [x] 하나의 React·FastAPI 앱을 유지하며 단계별 기능을 추가하는 설계를 명시했다.
- [x] Chunking·Embedding·검색·RAG·Tool/Single/Multi를 필수로 포함했다.
- [x] 기존 실제 GitHub 구현과 신규 설계 후보를 구분했다.
- [x] 테스트/실제 모델/사실성/학생 수업 가능성의 검증 기준을 분리했다.
- [x] 사용자 EDU-05 설계안 승인.
- [ ] 실제 학생용 소스·단원별 전체 붙여넣기 코드 작성/실행 검증 (후속 작업).
- [x] GitHub 설계안 반영 (승인 후).

**최종 현재 상태: `EDU-05 사용자 승인 완료 / 실제 교안·코드 작성은 후속 작업`.** 본 문서는 **교육자료 집필·코딩의 구현 명세 방향**이며 동작하는 학생 앱이나 완성된 교안은 아니다.