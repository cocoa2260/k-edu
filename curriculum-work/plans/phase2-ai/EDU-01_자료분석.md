# EDU-01 — 기존 Phase1·Phase2 강의자료 및 실습자료 분석 (1차)

- **분석일:** 2026-11-06
- **저장소:** `cocoa2260/k-edu`
- **브랜치:** `work/curriculum-production-001`
- **기준 커밋:** `39f85fc9570ed15f68d27850c9cd05e2a45eb7ec`
- **상태:** `진행 중 — 실제 구조·주요 교안·실습 구현의 1차 분석 완료, 전체 정밀 분석 및 실행 검증 미완료`
- **목적:** 기존 자료를 폐기하지 않고 재사용할 수 있도록, Phase1 선수학습과 Phase2 교안/실습의 현행 구성·역할·연결·위험을 파악한다. 새 폴더 구조 및 최종 단원 배치는 후속 EDU-03~06에서 결정한다.
- **변경:** GitHub 파일 수정·이동·삭제·커밋·푸시 없음.

## 1. 출처와 확인 구분

이번 분석에서 실질적인 교육내용의 기준은 사용자 지정 GitHub 브랜치다. 이전 `PROJECT_CONTEXT.md`, `CURRICULUM_ANALYSIS.md`, `WORK_PROGRESS.md`에는 과거 ZIP-only 기준이 남아 있으나, 이 세 문서는 현재 사용자가 명시적으로 지정한 GitHub 기준을 대체하지 않는다.

- **확인:** GitHub 트리·Markdown 본문·주요 소스 코드·실습 안내·단계 상태 JSON을 직접 조회하여 확인한 내용.
- **분석상 판단:** 현재 자료만으로 예상되는 수업 운영상의 문제 또는 재구성 기회. 실제 교육생 실습으로 입증한 것은 아님.
- **미검증:** 실제 설치/실행, 강의 전체 문장별 교차 비교, 교육생 직접 구현 과정, Obsidian 링크 및 첨부파일 전체 검증.

## 2. 파일 Inventory

| 범위 | 파일 | Markdown | Python | 기타 |
|---|---:|---:|---:|---:|
| `academy/00. 교육과정(curriculum)/00. Phase1_Theoretical/` | 158 | 64 | 84 | 10 |
| `academy/00. 교육과정(curriculum)/01. Phase2_AI/` | 47 | 45 | 0 | 2(JPG) |
| `academy/00. 교육과정(curriculum)/02. 실습/` | 190 | 20 | 94 | 76 |
| **합계** | **395** | **129** | **178** | **88** |

숨김 `.DS_Store`와 통합본, 질문 보충, 데이터 및 코드도 위 집계에 포함되므로 '파일 개수'와 '수업 단위 개수'는 같지 않다. 저장소에는 별도의 `curriculum-work/reports`, `curriculum-work/loop` 등 제작·검증용 경로가 존재한다. 이들은 학생용 강의와 구분할 필요가 있다.

### Phase1 분포

| 폴더 | 전체 파일 | MD | Python | 주요 성격 |
|---|---:|---:|---:|---|
| AI 애플리케이션 아키텍처 | 2 | 1 | 0 | 시스템 전체 구조/HTTP/JSON/Client/Server/상태 |
| React | 3 | 2 | 0 | UI 상태·컴포넌트·API 통신 교안 |
| Python_FastAPI | 91 | 4 | 84 | Python·Backend 강의와 별도 예제 코드 |
| GPT, Ollama, Gemma | 61 | 57 | 0 | Day1~Day3 24교시, 질문/보충, 통합 교안 |

### Phase2 분포 및 역할

| 현재 폴더 | 파일 수 | 현재 실제 교안의 주제·주요 역할 |
|---|---:|---|
| 01. AI 최신 동향 및 전체 지도 | 3 | AI 서비스의 목표·실패·책임·기술 구분 |
| 02. AI 머신러닝 딥러닝 개요 | 4 | 데이터 설계·분리·누수·모델 평가 (단순 AI 역사 소개 아님) |
| 03. 트랜스포머(Transformer) | 3 | Attention, Transformer Block, Mask, KV Cache 계산 |
| 04. 대규모 언어 모델(LLM) | 7 | 학습·생성·Context·평가 + Hugging Face/Tokenizer 별도 교안, JPG 2개 |
| 05. 프롬프트 엔지니어링 | 6 | Prompt, Context Engineering, Harness의 서로 다른 학습 활동 |
| 06. 임베딩(Embedding) | 2 | 검색용 숫자 표현·유사도·어휘 검색 비교 |
| 07. 벡터 데이터베이스(VectorDB) | 2 | 본문·출처·버전·상태가 있는 Index와 검색·갱신 |
| 08. 검색 증강 생성(RAG) | 2 | 검색-생성 연결과 근거 검증·실패 구분 |
| 09. AI 에이전트(Agent) | 4 | Single-Agent, Multi-Agent 분리, 역할 전달·실행 제한 |
| 10. 미세조정(Fine-tuning) | 4 | 데이터/정답 범위와 LoRA 실습 |
| 11. OCR_Multimodal | 2 | PDF 추출·표·OCR 오류·출처 복원 |
| 12. AI Integration | 1 | **기준 대화 앱 및 누적 실습 출발점 안내** |
| 13. Document AI | 7 | 문서 등록·근거 보고서·Provider·Streaming·평가 |

> **구조상의 1차 사실:** 12번 폴더가 실제로는 앞 단계의 공통 실습 출발점이다. 따라서 폴더 순서 그대로 수업하면 선수 실습 안내가 뒤에 나오는 문제가 발생한다.

## 3. Phase1에서 이미 학습한 것 (주요 교안 확인)

| 기존 과목 | 학습 내용 | Phase2 설계 시 의미 |
|---|---|---|
| AI 애플리케이션 아키텍처 | Model/Application, Frontend, Backend, HTTP/JSON, State | 용어·비유를 처음부터 장황하게 반복하지 않아도 되는 기반 |
| GPT/Ollama/Gemma Day1 1~6 | AI/ML/DL, Foundation Model, Transformer의 등장 배경, 주요 라이브러리 | Phase2에서 기초 소개보다 원리·실제 구현 중심 발전 필요 |
| Day1 7~8 | OpenAI SDK와 FastAPI, Structured Output | API 호출 자체 재교육보다 확장/검증 필요 |
| Day2 1~5 | Tokenizer, Tensor, Parameter, Training, HF Model Card, 모델 직접 실행 | Phase2 LLM/HF에서 설명의 신규성을 구분해야 함 |
| Day2 6~8 | Runtime vs Serving, Ollama, Python/FastAPI 로컬 API | 동일 설치·호출 재현을 줄이고 RAG 프로젝트에 활용 |
| Day3 1~5 | Gemma 모델 계열·양자화·장비·평가/선택 | 프로젝트용 모델 선정과 평가 기준으로 재사용 가능 |
| Day3 6~8 | LangChain/LlamaIndex 개요, Tool/Agent 생태계 소개, Provider 추상화, React·FastAPI·Model 통합 | **Phase2 기준 앱을 이어받는 출발점**으로 적합 |
| React | State, Fetch, Loading/Error/Cancel, AI Chat 관련 화면 | 최종 UI 통합 단계에서 선수학습 활용 |
| Python/FastAPI | Python 함수/객체/타입, 라우팅·검증·Service·Provider·Streaming | 백엔드 기초 재교육보다 모듈별 기능 개발로 연결 |

**중복 판정 유의:** 개념이 등장한다는 이유만으로 불필요한 중복이라고 판단하지 않았다. 동일·유사 문장/비유/코드 수준의 대조는 EDU-02에서 수행한다.

## 4. 현재 실습 경로의 실제 역할

기준: `academy/00. 교육과정(curriculum)/02. 실습/document-assistant/`

| 단계 | 현재 실습 자료 | 주요 학생 활동 | 단계별 누적 개발 관점 |
|---|---|---|---|
| L0 | `12. AI Integration/강의용.md` + Backend | `/ai/chat` 계약·Provider 구조·CORS 확인 | 기반 코드 존재, Phase1 원본과 연결됨 |
| L1 | `L1.md` | Prompt/예시 입력 생성·비교 | 직접 기능 작성보다 제공 도구 실행 중심 |
| Context | `CONTEXT.md` | 입력에 포함할 자료·순서·예산 선택 | 독립 활동지 존재 |
| L2 | `L2.md` | Harness 재시도·보완·중단 사례 실험 | `app/harness.py`가 이미 구현됨 |
| L3 | `L3.md` | Embedding, 검색·Index 상태·갱신 분석 | `retrieval/encoder.py`, `index.py`가 이미 구현됨 |
| L4 | `L4.md` | 저장된 RAG 결과, 인용·답변 오류 검토 | `app/rag.py`가 이미 구현됨 |
| L5 | `L5.md` | Single-Agent 도구 실행·상태·한도 관찰 | `app/agent.py`가 이미 구현됨 |
| L6 | `L6.md` | 역할 전달, 실패 전파·중단 기록 관찰 | `app/multi_agent.py`가 이미 구현됨 |
| L7 | `L7.md` | 데이터/정답 준비, LoRA 계산 및 선택적 훈련 | 주된 Multi-Agent 완성 경로 밖의 확장 후보 |
| L8 | `L8.md` | PDF/OCR 처리와 원문 위치 확인 | 문서 입력 심화 후보 |
| L9 | `L9.md` | 문서 등록·근거 보고서·Provider·Streaming·평가 | 최종 서비스 확장 후보 |

독립 보조 실습은 `data-evaluation`, `huggingface-tokenizer`, `llm-basics`, `transformer-basics`에 존재하며, `document-assistant`와 다른 목적을 가진 작은 학습/확인 도구다.

### 기존 Backend의 실제 확인된 실행 구조

- `backend/app/main.py`: FastAPI `/health`, `/ai/chat`, `/ai/prepare` 노출.
- `backend/app/service.py`: 기본 `AIService.chat()`가 Provider에 문자열 요청.
- `backend/app/harness.py`: 제한된 호출·검사·재시도 구조.
- `backend/retrieval/encoder.py` 및 `retrieval/index.py`: E5 임베딩과 SQLite Index.
- `backend/app/rag.py`: 검색과 답변 생성을 연결하는 워크플로.
- `backend/app/agent.py`: 제한된 Single-Agent 실행기.
- `backend/app/multi_agent.py`: 순차 역할 실행과 공유 예산/전달 관리.
- `backend/tools/rag_lab.py`, `agent_lab.py`, `multi_lab.py`: 각각 별도 CLI 실행 진입점.
- `stream-ui/src/App.jsx`: `/lab/stream` 등 별도 스트리밍 실습 서버와 상호작용하는 React 화면.

**판단:** 공통 Backend에 단계별 소스가 존재한다는 것과, 학생이 직접 한 파일씩 작성·확장할 수 있는 수업 패키지가 존재한다는 것은 다르다. 현재 L1~L6 활동 대부분은 제공 코드 실행/결과 해석 성격이 강하다. 단계별 학생 시작본·작성 지시·단계별 정답본을 별도로 정리할 필요가 있다.

## 5. 추가로 확인된 구조·연결 문제

1. **출발점 위치:** `12. AI Integration` 교안이 실제 누적 실습의 L0이지만 Phase2 폴더 순서상 뒤쪽에 있다.
2. **완성 프로젝트의 정의:** `/ai/chat` 기본 API와 RAG/Agent 별도 CLI, Streaming 별도 데모 UI가 서로 다른 경로다. 하나의 React/FastAPI Multi-Agent 완성 애플리케이션으로 연결되었다고 판정할 수 없다.
3. **실습의 주체:** 학생이 단계적으로 코드를 복사·붙여넣어 기능을 구현한다는 원래 의도와, 지금 제공된 구현을 실행·관찰하는 주요 활동 사이에 차이가 있다.
4. **교육용 경로 이슈 확인:** `document-assistant/backend`에서 실행하도록 안내된 L3~L6의 일부 `../../../reports/KEDU-PRODUCTION-00x/...` 경로는 현재 트리에서 `academy/00. 교육과정(curriculum)/reports/...`로 해석되어 존재하지 않는다. 실제 증거는 `curriculum-work/reports/`에 있어 상대경로가 달라졌다. 수정·검증은 후속 작업에서 수행.
5. **강의 제목 대 본문:** 기존 `02. AI 머신러닝 딥러닝 개요`의 실질 주제는 데이터/평가이며, `12. AI Integration`의 실제 기능은 기준 대화 앱 안내다. 현재 폴더명만으로 수업 내용과 진행 순서를 정확히 알기 어렵다.
6. **상태 기록의 해석:** `milestones/L4.json`은 `semantic_quality_accepted=false`, `L5.json`은 `model_task_quality_accepted=false`, `L6.json`은 `actual_task_quality_accepted=false`로 기록한다. 이는 **기존 기록의 자기보고 상태**이며, 이번 분석에서 모델을 새로 실행해 확인한 결과가 아니다. 품질 통과나 교육과정 완료로 간주하지 않는다.
7. **활동 자료의 위치:** 강의용/강사용/활동지가 일부 과목 내부에 있고, 실습 안내는 별도 폴더에 있으며, 과거 실행 근거는 `curriculum-work/reports`에 있어 수강생 관점의 이동 경로가 복잡하다.

## 6. EDU-01에서 얻은 재활용 판단 (초안)

| 대상 | 1차 재활용 방향 | 후속 결정 작업 |
|---|---|---|
| Phase1 아키텍처·AI 기초·React·FastAPI | 기존 선수학습으로 보존. Phase2에서 동일 설명 반복 금지 | EDU-02, EDU-04 |
| Phase2 01~05 이론 | 새 과정의 목적·필수 개념·실습 위치에 따라 재배치/개편 | EDU-04, EDU-05 |
| Embedding/VectorDB/RAG | 핵심 본과정 교안으로 활용, 문서 적재·Chunking 연결 보완 | EDU-04~05, EDU-12~15 |
| Single/Multi-Agent | 핵심 종착점으로 활용, 설명보다 구현 절차/실행 통합 강화 | EDU-17~19 |
| Fine-tuning/LoRA | 유지하되 별도 확장/심화 후보 | EDU-20 |
| OCR/Document AI | 일부 문서 입력 요소는 핵심 과정으로 연결, 나머지는 확장 후보 | EDU-12, EDU-20 |
| Backend 소스·테스트 | 가능한 한 재사용하고 단계별 학생 구현 가이드를 새로 구성 | EDU-07~08, EDU-22~24 |
| 고정 응답·과거 모델 기록·평가 결과 | 학생 기능 작성 뒤 검증/오류 분석에 재사용 | EDU-22~25 |

## 7. EDU-01 남은 분석 및 완료 조건

- [x] 지정 GitHub 브랜치의 HEAD와 전체 파일 트리 식별
- [x] Phase1·Phase2·공통 실습의 실제 파일 수 및 분포 집계
- [x] Phase1 24교시 주요 학습영역과 대표 React/Python/FastAPI 교안 확인
- [x] Phase2 주요 학생용 강의의 실제 제목·목차·도입 및 관련 실습 연결 확인
- [x] `document-assistant` L0~L9 실습 역할과 핵심 Backend/Frontend 소스 구조 확인
- [x] 1차 구조 불일치 및 경로 오류 후보 발견
- [ ] Phase1 전체 보충 질문·Q&A 및 84개 Python 예제의 단위별 상세 매핑
- [ ] Phase2 전체 교안(강사용·활동지 포함)의 문장·예제·개념별 상세 대조
- [ ] 전체 수업용 링크·첨부파일 및 코드 실행 지시의 정합성 전수검사
- [ ] 실제 환경 설치·단계별 시작본/완성본 재현 및 학생 관점 누적 개발 검증

**EDU-01 상태:** `진행 중 / 구조·자산·역할 1차 분석 완료`. 상세 중복 판정은 EDU-02, 최종 결과물 정의는 EDU-03, 실습 코드 재구성 판단은 EDU-07에 걸쳐 순차적으로 심화한다. 현재 분석만으로 강의·실습 전체 품질을 검증했다고 표현하지 않는다.

---

## GitHub 빠른 참조

- [작업 브랜치](https://github.com/cocoa2260/k-edu/tree/work/curriculum-production-001)
- [Phase1](https://github.com/cocoa2260/k-edu/tree/work/curriculum-production-001/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical)
- [Phase2_AI](https://github.com/cocoa2260/k-edu/tree/work/curriculum-production-001/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI)
- [공통 실습](https://github.com/cocoa2260/k-edu/tree/work/curriculum-production-001/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/02.%20%EC%8B%A4%EC%8A%B5)