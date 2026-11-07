# EDU-07 — Phase2_AI 기존 실습 코드 활용 및 재구성 범위 설계

- **문서 버전:** v0.1
- **작성일:** 2026-11-07
- **상태:** 사용자 승인 완료 (2026-11-07) / GitHub 설계 문서 반영
- **대상 저장소:** `cocoa2260/k-edu`
- **작업 브랜치:** `work/curriculum-production-001`
- **확인한 기준 HEAD:** `dcc389bf74d45eeac9432605a5856f66bd3848a3`
- **원본 참조 경로:** `academy/00. 교육과정(curriculum)/02. 실습/document-assistant/`
- **새 학생용 경로:** `academy/00. 교육과정(curriculum)/03. Phase2_AI_수업용/실습앱/`
- **상위 승인 기준:** EDU-03 최종 프로젝트, EDU-04 11개 단원, EDU-05 누적 구현 설계, EDU-06 Obsidian 학생용 폴더 구조

> **결정의 중심:** 학생은 처음부터 완성된 문서 도우미를 내려받아 실행하는 것이 아니다. 첫날에는 **React와 FastAPI가 연결된 최소 Chat 앱**만 받는다. 이후 같은 앱의 파일을 학생이 직접 추가·수정해서 문서 분할 → Embedding → 벡터 검색 → RAG → Tool Calling → Single-Agent → Multi-Agent까지 완성한다. 기존 GitHub 코드는 **참고·검증 원본**으로 활용한다.
>
> **표기 규칙:** 학생용 교안·목차·실습 체크리스트에는 내부 단계/검사 식별자를 적지 않는다. 이 문서의 `EDU-07`은 설계 이력의 작업명이고, `L3.md` 같은 표기는 **원본에 실제 존재하는 파일명**을 추적하는 강사용 표기에 한정한다. 학생용 문서에는 ‘Embedding 실습’, ‘RAG 구축’처럼 자연어로 적는다.

---

## 1. 확인한 사실과 아직 확인하지 못한 사실

### 1.1 확인한 자료 범위

GitHub 브랜치의 트리와 주요 Python·React·테스트·데이터·기존 실습 안내를 확인했다.

- 기존 `document-assistant` 하위 **174개 파일**을 Git 트리에서 식별했다. 이 중 **Python 88개**, **Markdown 18개**, **JSON 29개**, **웹 소스(JSX/CSS/MJS/HTML) 7개**, **PDF·이미지·DOCX 12개**를 확인했다. 확장자 분류에서 빠진 설정·잠금·요구사항 파일도 존재한다.
- 주요 코드 파일을 직접 읽었다: `app/main.py`, `service.py`, `schemas.py`, `config.py`, `providers/`, `experiments.py`, `harness.py`, `retrieval/encoder.py`, `retrieval/index.py`, `rag.py`, `agent.py`, `multi_agent.py`, 주요 CLI·검증 테스트 및 `stream-ui/src/App.jsx`.
- 기존 가상 문서 6개, 기본 질문 12개 및 Agent/역할 전달용 별도 사례, `milestones/`의 과거 검증 범위를 확인했다.
- **174개 모든 파일을 각각 실행·내용 전수 감사한 것은 아니다.** 파일 식별은 Git 트리 기준이며, 주요 기능/의존성 판단은 실제 소스 열람 기준이다.

### 1.2 현재 코드가 해주는 일과 하지 않는 일

| 기존 구현 | 확인한 현재 기능 | EDU-07 판단 |
|---|---|---|
| `backend/app/main.py` | `GET /health`, `POST /ai/chat`, `POST /ai/prepare` | Chat 시작본의 핵심. 준비 API는 고정 사례용이며 RAG 화면 호출이 아님 |
| `backend/app/providers/` | Ollama/OpenAI 선택과 공통 `generate(message)` 인터페이스 | 기본 시작본 재사용. 환경 변수·실제 모델 연결 확인 필요 |
| `backend/app/experiments.py` | 고정 질문·자료로 Prompt 조립, 생성 미실행 | 기존 `/ai/prepare`의 호환성을 위해 별도 유지. 학생이 새로 만드는 자유 질문 Builder와 혼동 금지 |
| `backend/app/harness.py` | 구조 검사, 호출 제한·재시도·종료 기록 | 실행 관리 단원의 참고 구현. 현재 `app.experiments` 의존성 존재 |
| `backend/retrieval/encoder.py` | `intfloat/multilingual-e5-small` 실제 CPU Embedding 클래스 | Embedding 수업 참고. 학생 시작본에는 포함하지 않음 |
| `backend/retrieval/index.py` | SQLite 기반 벡터 Exact 검색·메타데이터·갱신 및 검증 | 벡터 검색 참고. 현재 **비어 있지 않은 문서 각 줄을 Chunk로 취급**하므로 승인된 단락 분할 설계와 맞춰 변경 필요 |
| `backend/app/rag.py` | 검색, Context 구성, 모델 생성, 인용/형식 검사 | RAG 수업 참고. 웹 API에 이미 결합된 것은 아님 |
| `backend/app/agent.py` | 검증된 도구 요청·실행과 제한된 Single-Agent 반복 | Tool Calling 및 Single-Agent 수업에서 나누어 재구성 |
| `backend/app/multi_agent.py` | 검색·작성·검토 역할의 순차 실행, 전달·공유 한도 | Multi-Agent 수업 참고. 독립된 여러 모델을 필수로 실행하는 구조는 아님 |
| `backend/tools/*_lab.py` | 기능별 독립 CLI 실행, 실제 모델 또는 고정 응답 실험 | 교사용 재현·검사 참고. 실행만 시켜서 학생 구현으로 간주하지 않음 |
| `stream-ui/src/App.jsx` | `/lab/stream` 고정 시나리오에 연결된 Streaming UI | **최종 문서 도우미의 Chat/RAG/Agent 화면이 아님**. 학생 시작 화면으로 그대로 복사하지 않음 |

### 1.3 과거 검증 기록의 의미

- 기본 Chat 계약 검사가 과거 기록에 존재하지만 **현재 학생용 React 앱 실행과 실제 모델 생성까지 입증한 기록은 아니다**.
- 실제 E5 Embedding·검색 실행 기록이 존재한다. 다만 EDU-08의 새 학생용 환경에서 재현했다고 볼 수 없다.
- 기존 RAG는 실제 생성 기록이 있으나 **답변의 의미적 품질 채택이 보류**되었다.
- 기존 Single-Agent와 Multi-Agent는 실제 모델 호출/제어 경로 기록이 있지만 **과제 수행 품질 채택이 보류**되었다.
- 기존 Streaming 화면 기록은 별도 로컬 고정 응답 실험이며 실제 모델 Streaming·최종 통합 앱 검증을 대신하지 않는다.

따라서 **원본 코드 존재 / 과거 실행 / 현재 환경 재현 / 학생 완주 / 답변 사실성**을 각각 다르게 표시한다.

---

## 2. EDU-07에서 정하는 세 가지 구분

| 구분 | 뜻 | 새 수업 패키지에서의 취급 |
|---|---|---|
| **처음 제공할 시작본** | 학생이 첫 단원에서 바로 실행할 수 있어야 하는 최소 코드 | 기본 Provider·Chat Backend와 새 React Chat 화면, 샘플 자료, 설정·검사만 포함 |
| **학생이 직접 구현할 기능** | 이번 단원에서 새 개념을 배우고 코드를 작성해야 하는 부분 | 해당 단원이 시작되기 전에는 학생용 폴더에 **완성된 파일·함수를 넣지 않음** |
| **교사용 참고·검증 구현** | 원본 코드, 고정 시나리오, 과거 검증 기록, 심화 구현 | 기존 원본 경로에 보존하고 교사에게만 작업/검수 기준으로 사용. 학생 실습앱에 통째로 복사하지 않음 |

**단원마다 새로운 앱이나 독립된 실행 환경을 만들지 않는다.** 같은 `backend/`, `frontend/`, `data/`, `tests/`에서 이전 기능이 계속 작동하도록 누적한다.

---

## 3. 첫 수업 시작본 — 파일별 채택 결정

> 아래 **채택**은 '지금 배포 완료'라는 뜻이 아니다. EDU-08에서 새 학생용 위치에 복사·재작성하고 실행 확인을 해야 한다.

### 3.1 Backend — 유지하거나 최소 수정하여 제공

새 위치는 모두 `실습앱/backend/` 아래다.

| 새 시작본 파일 | 기존 참조 | 처리 방식과 이유 |
|---|---|---|
| `app/__init__.py` | `backend/app/__init__.py` | 패키지 파일 복사 가능 |
| `app/config.py` | `backend/app/config.py` | 환경 설정 로딩 함수 유지. 새 경로에서 `.env`를 읽는지 확인 |
| `app/schemas.py` | `backend/app/schemas.py` | 기본 `ChatRequest`와 `ChatResponse` 유지. 입력 1~2000자, 공백 거부를 변경하지 않음 |
| `app/service.py` | `backend/app/service.py` | `AIService`와 `ChatResult` 유지. 후속 모드가 생겨도 Chat 동작 보존 |
| `app/main.py` | `backend/app/main.py` | `create_app()`, CORS, `/health`, `/ai/chat` 유지. 기존 `/ai/prepare`도 호환성을 위해 유지하되 고정 실험임을 명시. 미래 RAG/Agent 라우트는 제공하지 않음 |
| `app/providers/__init__.py` | 동일 파일명 | 패키지 파일 유지 |
| `app/providers/base.py` | 동일 파일명 | `AIProvider` 공통 인터페이스 유지 |
| `app/providers/errors.py` | 동일 파일명 | 연결·시간 초과·상위 서비스·응답 오류 유형 유지 |
| `app/providers/factory.py` | 동일 파일명 | 기본 Ollama, 선택 OpenAI 분기 유지. 다른 Provider를 임의로 추가하지 않음 |
| `app/providers/ollama_provider.py` | 동일 파일명 | Ollama API 연결 기능 유지. 실제 로컬 모델 이름과 연결 확인 필수 |
| `app/providers/openai_provider.py` | 동일 파일명 | 대체 Provider로 보존하되 실제 키를 포함하지 않음. 외부 API 비용 발생 가능성 안내 |
| `app/experiments.py` | `backend/app/experiments.py` | **기존 `/ai/prepare` 호환성만을 위해 유지**. 데이터 위치를 새 `backend/data/fixtures/`에 맞춰 수정해야 함. 실제 모델 호출·자유 질문 Prompt Builder로 오인하지 않음 |
| `.env.example` | `backend/.env.example` | 환경 변수 이름 유지. 실제 키·모델 설치 경로·로컬 실행 조건은 교육생 환경에 맞게 안내 |
| `requirements.txt` | `backend/requirements.txt` | 기본 FastAPI/Pydantic/HTTP/Provider 의존성을 출발점으로 사용. 버전·OS 호환성은 EDU-08에서 재검증 후 핀 고정 |
| `.gitignore` | `backend/.gitignore` | `.env`, `.venv`, 캐시, `local_data`, 이후 Node 산출물까지 새 패키지 구조에 맞춰 보완 |

**중요한 경로 수정:** 기존 `app/experiments.py`는 `Path(__file__).resolve().parents[2] / "data"`를 사용해 원본의 `document-assistant/data/`를 찾는다. 승인된 새 구조는 `실습앱/backend/data/fixtures/`이다. **그대로 복사하면 데이터 검색 위치가 달라져 실패한다.** EDU-08에서 `backend` 기준의 명시적 설정 경로로 변경하고 `/ai/prepare` 호환성 검사를 해야 한다.

**API 보존:** `POST /ai/chat`의 요청 `message`와 응답 `provider`, `model`, `answer`, 422/502/503/504 오류 흐름을 유지한다. `/ai/prepare`는 기존 `case_id`·`variant` 입력으로 **생성하지 않은 Prompt 준비 결과만 반환**한다. 새 수업에서 학생이 작성할 `assistant/preview`와 역할이 다르다.

### 3.2 첫날 반드시 추가 제작할 React 화면

현재 기존 `stream-ui`는 별도 Streaming 데모다. **승인된 기능을 만족하는 최소 React Chat 시작 화면이 기존 `document-assistant` 안에 완성되어 있지 않으므로 EDU-08에서 새로 작성**한다.

| 새 파일 | 첫 수업에서 해야 하는 일 | 하지 않아야 하는 일 |
|---|---|---|
| `frontend/package.json` 및 잠금 파일 | React 개발/빌드 도구와 실행 스크립트 고정 | 사용하지 않을 Streaming 데모 의존성을 그대로 복사 |
| `frontend/index.html` | React 시작점 제공 | 별도 독립 실습 페이지 추가 |
| `frontend/src/App.jsx` | 질문 입력, Chat 전송, 답변과 Provider 오류 표시. 후속 패널을 추가할 기본 레이아웃 | RAG·Agent·Multi-Agent 완성 기능을 첫날 활성화 |
| `frontend/src/api.js` | FastAPI 호출을 한 곳에 모으고 422/502/503/504 처리 | 단원마다 다른 HTTP 유틸리티 신설 |
| `frontend/src/style.css` | 수업에서 읽기 쉬운 최소 화면 스타일 | 고급 Streaming UI 전체 이식 |
| 개발 서버 설정(필요 시) | FastAPI 8000번과 React 개발 서버의 CORS/Proxy 조건 확정 | 기존 데모의 `/lab/stream` 주소 사용 |

React 빌드 도구 및 Node 버전은 **기존 `stream-ui`의 `esbuild` 설정을 학생용 최종 도구로 자동 확정하지 않는다.** EDU-08에서 실제 교육 장비에서 실행되는 조합을 확인해 하나로 고정한다.

### 3.3 데이터와 시작 안내

| 새 시작본 파일·범위 | 기존 참조 | 처리 |
|---|---|---|
| `backend/data/fixtures/documents-v1.json` | 원본 `data/documents-v1.json` | **가상 규정 6개**를 학습 입력으로 보존. 버전·접근 범위·현행 상태 속성 유지 |
| `backend/data/fixtures/core-v1.json` | 원본 `data/core-v1.json` | **기본 질문 12개** 중 유효/오류 사례 유지. 학생은 불투명한 사례 번호 대신 질문 문장으로 보고 학습 |
| `backend/data/fixtures/shots-v1.json` | 원본 `data/shots-v1.json` | 별도 주제의 예시 2개. Prompt 실습 준비 자료로 유지 |
| `backend/tests/test_provider.py` 등 | 원본 Chat 계약 테스트 | 구조·파일 경로에 맞춰 이식. Mock 성공만으로 실제 모델 실행 완료 처리하지 않음 |
| `실습앱/README.md` | 신규 | 정확한 작업 폴더·설정·설치·Backend/Frontend 실행·첫 질문·확인 방법 설명 |

**가상 문서 6개의 역할:** 현행 출장 규정, 교육비 규정, 폐기된 출장 규정, 제한 자료, 악의적 지시가 삽입된 첨부 메모, 표 형태의 텍스트. 이것들을 무심코 삭제하면 뒤 단원의 *문서 현행성·접근 범위·Prompt Injection·표의 원문* 검증이 무너진다. 제한 자료는 교육생 디스크에 존재하는 가짜 자료이므로 `staff/restricted` 표시는 **실제 인증·비밀 보호가 아님**을 교안에 설명한다.

기존 기본 질문의 테스트용 식별자는 코드 내부 데이터 매칭에만 사용하고, 학생용 교안에서는 `국내 당일 출장 식비 상한 질문`, `규정에 없는 해외 출장 질문`처럼 **읽기 쉬운 제목과 질문 문장**을 제시한다.

---

## 4. 11개 단원에서 학생이 작성할 코드 — 파일 단위 순서

아래 파일들은 **첫 수업 시작본에는 들어가지 않는다**. 각 단원의 강의와 실습 하나 안에서 학생이 작성한다. `main.py`, `App.jsx`, `api.js`, `tests/`는 **모든 단원에서 동일 파일을 수정·확장**한다.

| 단원 | 이번에 직접 작성할 새 파일 | 기존 파일 수정 | 기존 참조 구현 / 이번에 확인할 새 결과 |
|---|---|---|---|
| **01. LLM 심화와 AI 프로젝트 출발** | 없음. 시작본 구성 후 실행 | `README.md`에 본인 환경 설정 | 기본 Chat 실제 응답·오류 확인. 원본 `main.py`/Provider 참조 |
| **02. Prompt & Context Engineering** | `app/prompting.py`, `app/assistant_service.py` | `main.py`, `App.jsx`, `api.js` | 원본 `experiments.py`, Prompt/Context 강의와 CLI 참고. **실제 모델에 전달되는 입력 구성** 비교 |
| **03. AI 실행 관리(Harness)** | `app/harness.py` | `assistant_service.py`, 화면의 상태/실행 기록 | 원본 `harness.py` 참조. 형식 검사·실패·재시도·종료 상한 확인 |
| **04. 문서 수집·전처리·Chunking** | `app/documents.py`, `data/sources/*.md`·`*.txt`, `data/catalog.json` | `main.py`, 화면에 문서/단락 목록 | 동일 규정의 원문·단락 나누기·순서·원문 위치·버전 표시 |
| **05. Embedding** | `retrieval/__init__.py`, `retrieval/encoder.py` | `main.py`, Embedding 결과 패널, 의존성 | 원본 `retrieval/encoder.py` 참조. **실제 모델이 만든 벡터** 차원·정규화·질문/문서 차이 확인 |
| **06. Vector DB & Retrieval** | `retrieval/index.py` | `main.py`, 검색 패널, `tests/` | 원본 SQLite Index 참고. 저장→유사도 검색→Top-k→문서 변경 반영 |
| **07. RAG 구축** | `app/rag.py` | `assistant_service.py`, `main.py`, RAG 모드·근거 표시 | 원본 `rag.py` 참고. 검색된 출처로 답변 생성·근거 부족 처리 |
| **08. Tool Calling** | `app/tools_registry.py` | `schemas.py`, `assistant_service.py`, 화면 실행 이력 | 원본 `agent.py`의 Registry/입력 검증 부분 분리. **도구 요청과 실제 허용 실행의 차이** 확인 |
| **09. Single-Agent 구축** | `app/agent.py` | `assistant_service.py`, `main.py`, Agent 모드·도구 이력 | 원본 `agent.py`의 제한된 반복 참고. 실제 모델의 다음 행동 선택 확인 |
| **10. Multi-Agent 구축** | `app/multi_agent.py` | `assistant_service.py`, `main.py`, 역할 전달 패널 | 원본 `multi_agent.py` 참고. 검색·작성·검토 간 **명시적 전달과 공유 종료 한도** 확인 |
| **11. 서비스 통합 및 최종 검증** | 새 독립 앱 없음 | 기존 `App.jsx`, `api.js`, `schemas.py`, `assistant_service.py`, 테스트/README 정리 | 동일 질문을 Chat/RAG/Single-Agent/Multi-Agent 네 방식으로 비교 |

**교안에 반드시 쓸 방식:** 새 파일은 처음부터 끝까지 실제로 저장 가능한 전체 코드, 기존 파일은 **수정 전 식별 위치와 정확히 바꿀 코드**를 제공한다. 숨겨진 선행 함수·생략 기호·설명 없는 Import가 있으면 수업용으로 승인하지 않는다.

**수업용 화면 설명:** 개발 중에는 문서 조각·Embedding 일부 숫자·검색 점수·도구 선택·역할 전달 정보를 단계별로 추가한다. 이는 학습용 관찰 기능이며 모델 내부 사고과정, 비밀키, 무제한 로그 전체를 노출하는 기능이 아니다.

---

## 5. 재사용할 핵심 파일의 **의존성 절단 및 재구성 지점**

이 절은 EDU-08에서 단순 복사 때문에 막히지 않도록 마련한 **선행 조치 명세**다.

### 5.1 첫 시작본: 기존 Prompt 준비 API의 데이터 경로

- `main.py`가 현재 `app.experiments.prepare`를 가져오므로 기본 Chat만 무턱대고 복사하면 `/ai/prepare`와 Import 문제가 생긴다.
- 위 3.3의 데이터 파일을 함께 제공하고 `app/experiments.py`의 기준 경로를 새 `backend/data/fixtures/`로 **명시적으로 수정**한다.
- 기존 Prompt 준비 API는 **원래의 고정 자료 실험**으로 남기고, 새 Prompt·Context 단원에서 자유 질문에 쓰일 `prompting.py` Builder를 별도로 학생이 작성한다. 결과를 혼용하지 않는다.

### 5.2 Harness: 고정 사례 전용 의존성 분리

- 기존 `harness.py`는 `app.experiments.prepare`를 가져오고 고정 질문 사례에 결합돼 있다.
- 학생용에서는 생성 호출·응답 검사·재시도·시간/횟수 상한을 **범용 실행 함수**로 분리한다. 고정 사례 준비는 별도 시험 입력으로만 사용한다.
- 기존 응답의 JSON 구조 검사는 성공한 모델 답변의 **사실적 정확성 판정이 아니다**. 이 구분을 출력 상태에 유지한다.

### 5.3 Chunking과 기존 Index 형식 불일치

- 기존 `LocalIndex.upsert()`는 문서의 비어 있지 않은 **줄 단위**를 Chunk로 만들고, `doc_id@version:L1` 형태의 근거 ID를 사용한다.
- 승인된 새 단원은 **제목/단락 경계 우선, 필요 시 긴 단락을 문장 단위로 재분할**하는 방식을 요구한다.
- EDU-08 이후 **`documents.py`가 만든 Chunk의 명시적 스키마**와 `index.py`의 입력 계약을 연결해야 한다. 줄 번호를 무심코 Chunk 번호로 치환하면 기존 근거 ID·위치·인용 검사와 불일치가 발생한다.
- 원문 위치, Chunk 순서, 내용 해시, 문서 버전·현행 여부·접근 범위, Index 갱신/삭제 후 이전 근거 무효화 기능을 **동시에 보존**한다. 새 Chunk 포맷은 EDU-08의 기능 계약 테스트에서 고정한다.

### 5.4 실제 Embedding 환경

- 기존 인코더: `intfloat/multilingual-e5-small`, **384차원**, Query/Passage 구분과 정규화. 소스에는 모델·Revision을 고정한 코드가 있다.
- 현재 인코더 기본값은 **오프라인 모델 로드**다. 미리 가중치를 내려받지 않은 교육생 PC에서는 실패할 수 있다.
- 기존 `requirements-retrieval.txt`는 **Linux x86_64 CPU Torch Wheel**을 전제로 한 설치 안내를 담고 있다. Mac/Windows나 다른 Python 환경에서 그대로 설치 가능하다고 보장하지 않는다.
- EDU-08에서 수업 장비별 설치 경로, 캐시/사전 다운로드, 모델 메모리와 실제 1건 추론을 검증한다. 단순 2차원 가상 벡터나 과거 저장 결과만으로 Embedding 단원 완료 처리하지 않는다.

### 5.5 RAG의 Index·검사 연결

- 기존 `rag.py`는 `app.harness`, `retrieval.index`, 공통 Chat Schema에 의존한다.
- 새 문서 Chunk/Index를 사용하는 Context 생성 함수와 근거 식별자 형식을 먼저 고정하고 RAG 코드를 적용한다.
- 실제 모델 답변에 문서 인용이 있다고 해서 **답변이 사실과 일치한다고 단정하지 않는다**. 출처 존재·인용 문자열 존재·주장 의미의 정확성을 각각 표시한다.

### 5.6 Tool Calling과 Single-Agent를 둘로 나누기

- 기존 `agent.py`에는 `SearchArgs`·`ReadArgs`·`Registry`·검증/Dispatch와 `run_agent()` 반복이 **한 파일에 함께 있다**.
- 08단원은 **도구 스키마·허용 목록·인자 검증·실행기**를 `tools_registry.py`로 먼저 학생이 작성한다. 09단원에 가서 그 함수를 재사용하는 `agent.py` 반복을 구현한다.
- 기존 구현의 구조화된 **JSON 행동 요청**은 기술적으로 모든 Provider SDK가 제공하는 네이티브 Tool Calling 프로토콜과 **동일하지 않다**. 실제 수업에서 어떤 경로를 실행했는지 구분한다. 모델이 낸 요청도 Runtime 검증 없이 실행하지 않는다.

### 5.7 Multi-Agent의 실제 성격

- 기존 `multi_agent.py`는 `agent.py`의 검증 계약·Registry와 RAG 근거 검사에 의존한다.
- 여러 역할을 하나의 모델이 순서대로 수행할 수 있다. 각 역할이 독립 모델·GPU·서버여야 Multi-Agent라는 설명을 하지 않는다.
- 역할 사이 자료 전달은 명시적으로 제한하고, 조회 가능한 출처·공유 예산·종료 사유는 Runtime이 관리한다. **검토자 모델의 의견을 시스템 승인·인증·권한 제어로 표시하지 않는다**.

### 5.8 React 데모의 잘못된 재사용 방지

- `stream-ui/src/App.jsx`는 `fetch('/lab/stream')`과 `stream.mjs`를 사용한다. 일반 Chat 또는 RAG/Agent 요청 UI가 아니다.
- 시작본은 `POST /ai/chat`을 보내는 React 화면을 새로 작성한다. 기존 Streaming 이벤트 코드와 `build.mjs`를 그대로 시작본에 복사하지 않는다.
- **01단원부터 같은 `App.jsx`를 사용**하며 11단원에 새 UI를 교체 생성하지 않는다.

---

## 6. 본과정에서 분리해 원본 보존할 코드·자료

다음은 **없애라는 뜻이 아니라 본과정 시작본에 넣지 않는다**는 결정이다. 모든 원본은 기존 경로에 그대로 남긴다.

| 기존 파일·범위 | 용도 | 새 패키지 처리 |
|---|---|---|
| `backend/app/document_ingest.py`, `docx_ingest.py`, `document_registry.py` | PDF/OCR·DOCX·문서 등록/버전 확장 | 문서 분할 수업의 필수 구현으로 통째로 이식하지 않음. 관련 개념·일부 원리만 참고하고 심화 과정 보존 |
| `backend/app/report_spec.py`, `provider_router.py` | 보고서/Provider 라우팅 확장 | 최종 4모드 본과정의 필수 코드에서 제외 |
| `backend/app/training_data.py`, `data/finetuning-v1/` | 학습 데이터·Fine-tuning | 심화/LoRA 자료로 보존 |
| `backend/app/agent_bridge.py` | 선택적 LangChain `StructuredTool` 브리지 | 직접 Tool Calling 이해를 우선하고 프레임워크 브리지는 심화 참고 |
| `backend/app/providers/hf_cpu_provider.py` | CPU Qwen 생성 실험 어댑터 | 모델 선택/장비 검증 후 참고. 기본 웹 Provider Factory에는 직접 연결돼 있지 않음 |
| `backend/tools/`의 기존 41개 파일 | 별도 CLI·예제·과거 기록 읽기·재현 | 학생 시작본에 일괄 포함 금지. 필요하면 **학생이 작성한 새 앱의 함수만 호출하는 보조 검사 도구**로 최소화 |
| `backend/tests/` 및 독립 `*_tests/` | 기존 계약·경계/심화 테스트 | 기본 Chat 테스트부터 시작해 해당 기능을 가르치는 시점에 테스트 단계적으로 이식·수정 |
| `backend/data/document-v1/`, `multiformat-v1/`, `report-v1/` | OCR/PDF/DOCX/보고서용 자료·산출물 | 본과정 필수 파일에서 제외. 원본·라이선스 문서 보존 |
| `stream-ui/` 전체 | 별도 고정 Streaming 실험 | 시작본에 이식하지 않음. CSS/상태관리 아이디어만 필요 시 검토 |
| `milestones/` 전체 | 과거 개발 검증·수락 상태 기록 | 강사용 이력 참고. **학생의 신규 실행 성공으로 표시 금지** |
| `baseline-source-map.json`, 기존 `L1.md`~`L9.md`, `CONTEXT.md`, `MODEL_CARD.md` | 이전 자료 출처·실습·모델 기록 | 새 학생용 11개 교안에 통째로 복사 금지. 내용/실습 연결만 참고하고 한 단원에 한 교안으로 재작성 |
| `requirements-ann.txt`, `requirements-lora*.txt`, `requirements-document.txt`, `requirements-report.txt` 등 | ANN/LoRA/다중 문서 형식 별도 의존성 | 모든 패키지를 첫날 설치하지 않음. 해당 심화/선택 수업에서만 안내 |

**강사 전용 위치:** EDU-06에서 승인된 `curriculum-work/teacher/phase2-ai/`를 계획상 사용한다. 다만 저장소가 공개되어 있다면 같은 저장소 내부의 강사용 폴더는 기술적으로 비밀이 아니다. 정답 접근을 실제로 제한해야 한다면 강사용 완성본은 별도 비공개 공간에 두어야 하며, 학생 배포 폴더에 포함하지 않는다.

---

## 7. 기존 검증 코드를 수업용 검사에 활용할 기준

| 가르친 기능 | 우선 활용할 기존 테스트 | 학생용에서 새로 확인할 것 |
|---|---|---|
| 기본 Chat/Provider | `test_provider.py`, `test_boundaries.py`, `test_frontend_contract.py` | Mock 계약 + 실제 Ollama 또는 선택 Provider 호출 + React 브라우저 요청 |
| Prompt·Context | `test_l1.py`, `experiments.py` 관련 검증 | 실제 입력 Builder와 미리보기 입력이 **같은 문자열**을 사용하는지 |
| Harness | `test_harness.py` | 유한한 재시도·복구·종료/시간 한도, 실제 생성과 고정 출력 구분 |
| Embedding/Index | `test_retrieval.py`, `embedding_tests/test_manifest_snapshot.py` | 실제 벡터 1건 + 새 단락 Chunk 인터페이스 + Index 갱신/보안 경계 |
| RAG | `test_rag.py` | 실제 자료에서 인용, 근거 없음, 잘못된 인용·잘못된 주장 구분 |
| Tool/Single-Agent | `test_agent.py` | 허용되지 않은 도구/인자 실행 차단, 모델의 다음 행동 선택, 반복 종료 |
| Multi-Agent | `test_multi_agent.py` | 역할별 전달/권한 경계, 공유 호출 한도, 검토 결과·실제 모델 구분 |
| 최종 React 앱 | 기존 `stream-ui/tests/*`의 일부 상태 관리 원리 | 학생 앱의 네 모드 API 연결, 브라우저 오류·출처·이력, 이전 기능 회귀 |

테스트의 **Mock 성공**은 구조·경계 검증이다. **실제 모델 호출 성공** 및 **답변 내용의 정확성**은 별도 항목으로 확인한다. 학생이 완주할 수 있는 설치·실습 절차도 별도로 검증한다.

---

## 8. 공통 API와 데이터 호환성 — EDU-08 전달 조건

EDU-05에서 승인한 기존/신규 API 구분을 유지한다.

| API | 현재/목표 | 적용 기준 |
|---|---|---|
| `GET /health` | 기존 유지 | Provider 설정/서버 준비 상태. 모델 생성 확인 아님 |
| `POST /ai/chat` | 기존 유지 | 기본 Chat 계약 절대 변경하지 않음 |
| `POST /ai/prepare` | 기존 고정 사례 API 유지 | 고정 자료의 Prompt 준비 결과만 반환, `generation_executed: false` |
| `POST /api/v1/assistant/preview` | Prompt 단원에서 **새로 구현** | 새 자유 질문 Builder가 실제 요청에 사용할 입력을 그대로 미리보기 |
| `POST /api/v1/assistant/run` | Prompt 단원부터 Chat 경로 신설, 이후 모드 확장 | 처음에는 Chat만 활성화; RAG/Single/Multi를 각각 해당 단원에 구현 |
| `POST /api/v1/documents/rebuild`, `GET /api/v1/documents/chunks` | 문서 수집·분할 단원부터 | 오직 제공된 가상 자료만 적재. 단락·원문 위치·버전 확인 |
| `POST /api/v1/retrieval/embedding-preview` | Embedding 단원부터 | **실제 모델**로 만든 벡터·유사도 관찰 |
| `POST /api/v1/retrieval/search` | 벡터 검색 단원부터 | 적격 Chunk의 점수·순위·출처 반환 |

- 예전 `main.py`를 유지하면서도 후속 모드별 라우트를 **학생이 작성한 기존 서비스에 연결**한다. 별도 CLI에서만 실행되는 기능을 학생용 앱의 구현 완료로 보지 않는다.
- 실제 API의 필드 이름·스키마·에러 코드·문서 출처 규칙을 EDU-08에서 테스트와 함께 고정한다. 이 문서는 코드 구현 전 명세다.
- 응답 상태(기술적 성공/실패), 답변 종류(답변/보류/되묻기/거부), 근거, 사실 검토 상태, 실제 모델인지 고정 응답인지 여부를 **혼합하지 않는 구조**로 설계한다.
- 에러 로그에 모델 비밀키와 민감한 운영 정보를 기록하지 않는다. 실습의 가상 문서에는 실제 개인정보나 업무 비밀을 넣지 않는다.

---

## 9. EDU-08에서 바로 실행할 제작 순서

1. **새 학생용 프로젝트 뼈대 생성:** 승인된 `03. Phase2_AI_수업용/` 안에 `교안/`, `실습앱/backend/`, `실습앱/frontend/` 구성. 기존 원본 파일 이동·삭제 금지.
2. **시작본 파일 구축:** 3.1의 Python Chat 경계 채택, 3.2의 최소 React 새 작성, 3.3의 가상 자료 및 설정 정리. `main.py`/`experiments.py` 경로 호환성과 `/ai/prepare` 기능 유지.
3. **환경 고정:** 교육생 OS·Python·Node, Ollama 모델 설치·접속 가능 여부 확인. React↔FastAPI 개발 서버 CORS/Proxy를 실제 구성. OpenAI 키 없이도 기본 실습 경로 마련.
4. **기능 연결 시험:** Backend `/health`와 실제 `/ai/chat`, React 실제 질문 전송, 유효하지 않은 질문 422, Provider 오류 502/503/504를 각각 확인. 실제 모델이 없으면 ‘환경 차단’으로 표시하고 Mock만으로 완료 처리하지 않음.
5. **시작본의 기능 누출 검사:** `rag.py`, `agent.py`, `multi_agent.py`, `encoder.py`, `index.py`, `tools_registry.py` 등이 **첫 학생 배포물에 없어야 함**. `App.jsx`는 Chat만 실행할 수 있어야 하고 미래 모드 기능은 존재하더라도 비활성/미구현 표시.
6. **학생이 따라 하기 쉬운 기준 확보:** 실행 명령의 **현재 작업 폴더**, 파일의 정확한 저장 위치, `.env` 설정, 브라우저 주소, 예상 결과와 실제 실행 기록 분리.
7. **후속 교안·소스의 누적 변경 규칙 작성:** 02~11단원에서 어떤 파일을 새로 만들고 기존 파일의 어느 부분을 변경하는지 학생용 교안에 순차적으로 안내. 이전 Chat 계약 회귀 검사를 매번 포함.
8. **강사용 정답/참고 구현 별도 유지:** 교육생 배포 폴더에는 미구현 미래 기능·정답 전체 소스·과거 로그를 넣지 않는다. 학생용 패키지 한 폴더로 수업 가능한지 확인.

### EDU-08 첫 실행본 완료 조건

- [ ] 학생용 시작본의 모든 파일이 준비되고, 새 경로 기준 Import/상대경로가 정상이다.
- [ ] 실제 장비 기준 Python/Node 및 의존성 설치 명령이 재현된다.
- [ ] FastAPI의 `/health`, `/ai/chat`, `/ai/prepare` 계약을 확인한다.
- [ ] React에서 **실제 모델로 Chat 질문/응답**을 확인한다.
- [ ] 422/502/503/504 오류가 화면에서 적절히 구분된다.
- [ ] 이후 단원용 완성 모듈이 처음 배포물에 포함되지 않았다.
- [ ] `README.md`를 따라 처음부터 같은 결과를 재현할 수 있다.
- [ ] 모의 응답/실제 모델 생성/사실 검증 상태를 혼동하지 않는다.

---

## 10. 위험·미확정 사항 및 처리

| 항목 | 현재 확인된 사실 또는 위험 | 다음 조치 |
|---|---|---|
| React 통합 시작본 부재 | 기존 `stream-ui`는 고정 Streaming 데모 | EDU-08에서 Chat 화면을 새로 작성·실행 |
| 기존 `/ai/prepare` 데이터 상대경로 | 원본의 상위 폴더를 기준으로 데이터 참조 | 새 `backend/data/fixtures/`에 맞춰 Import/경로·계약 검사 |
| Chunk Schema 불일치 | 기존 Index는 줄 기반, EDU-05는 단락 우선 | 자료 원문/Chunk Schema와 Index 입력을 함께 설계·검증 |
| 모델 다운로드 및 OS | E5 오프라인 로딩 기본값, Linux CPU 전용 패키지 안내 | 학습 PC별 설치·다운로드·실측 재현 검증 |
| 실제 Agent 품질 | 기존 과거 기록에서도 의미 품질 미채택 | 단계별 실제 모델 테스트와 사람이 확인하는 품질 체크 분리 |
| 단원별 코드의 부분 이식 | 원본 모듈이 다른 모듈 Import에 결합 | 후속 단원 기능 누출·누락 Import 검사 |
| 학생용 정답 분리 | 같은 공개 저장소의 강사용 폴더는 비공개가 아님 | 별도 배포 패키지와 접근 제한이 필요한 자료의 보관 위치 검토 |
| 이전 자료의 깨진 참조 링크 | 기존 독립 CLI·보고서 상대경로 일부는 이동 전 위치를 참조 | 새로운 학생 교안에서 원본 링크를 그대로 이식하지 않고 실제 경로 재검사 |

---

## 11. EDU-07 자체 완료 판단

- [x] 기존 `document-assistant` 파일 트리, 주요 소스/테스트, 과거 기록의 범위를 파악했다.
- [x] 학생 시작본, 학생 직접 구현 코드, 강사용 참고 코드의 경계를 **파일 단위**로 구분했다.
- [x] 승인된 11개 단원별 추가/수정 파일과 관찰 결과의 연결을 유지했다.
- [x] `main.py`·`experiments.py` 데이터 경로, Chunk/Index 계약, Harness·Agent 의존성 등 **재구성 위험 지점**을 명시했다.
- [x] EDU-08에서 제작할 실제 Chat 시작본의 완료 검사 기준을 제시했다.
- [x] 사용자 EDU-07 설계 승인 (2026-11-07).
- [x] GitHub 설계 문서 반영 (승인 후).
- [ ] 실제 학생용 코드 생성 및 환경·브라우저 실행 검증 (EDU-08 이후).

**현재 판정: EDU-07 설계 승인 완료 / GitHub 반영.** 이 문서가 작성되었다고 학생 시작본이나 완성된 교육용 앱이 생성·검증된 것은 아니다.