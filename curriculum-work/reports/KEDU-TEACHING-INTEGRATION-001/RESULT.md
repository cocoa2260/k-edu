# 전체 수강 흐름과 실습 연결 점검

**강의·준비·실습·제출·해설의 문서 연결을 점검하고 수강 안내를 추가했다. 실제 실행·과제 품질·독립 수업 검증은 완료하지 않았다.** 기준은 `cfc5a4adba62c4b7a7c0637567cbfdcbe15ab405`의 자료다. 70개 단원의 기존 설명 수정·동일 작성자 검수 이력은 유지한다. 이번 결과도 같은 작성자의 문서 검토다.

교육생은 [수강 안내](../../STUDY_GUIDE.md), 강사는 아래 연결표와 후속 검증 순서를 사용한다. 강사용 표의 단원/실습 식별자는 관리 매핑이며 학생에게 외우게 할 내용이 아니다.

## 발견한 문제와 수정

| 문제 | 이번 수정 | 해석의 한계 |
|---|---|---|
| 전체 순서·활동·제출 안내가 과목마다 흩어져 있음 | 수강 안내에 15개 과목의 순서, 기준 앱 준비, 활동/제출·전환을 연결 | 새 강의 설명을 요약본으로 대체하지 않음. 실제 수업 시간은 측정하지 않음 |
| 누적 실습 표에 마지막 단계가 없고 예전 Provider/UI/평가 미완료 안내가 누적됨 | 마지막 통합 단계를 포함하고 현재 확인 범위와 남은 검증으로 표를 재작성 | 과거 보고서는 당시 기록으로 보존 |
| ‘같은 Backend 확장’이 모든 기능의 API/UI 통합처럼 읽힐 수 있음 | 기존 API·RAG/Agent CLI·별도 SSE 서버/React 경로를 명시 | 실제 통합 구현을 새로 한 것은 아님 |
| 첫 HF 방문부터 앱 실행까지 준비 환경이 다르고, 사례도 바뀜 | Tokenizer/Backend/모델/문서/브라우저 준비를 나누고 출장비→회의실→환불 사례 전환을 설명 | 모든 환경을 합친 설치나 다른 OS 호환을 보장하지 않음 |
| 현재 현황에 ‘70개는 작성 수, 설명 수정이 남음’이라는 초기 검사 문장이 남음 | 초기 감사 이력과 이후 70개 설명 수정/자체 검수, 이번 연결 점검을 구분 | 독립 품질·수업 합격으로 상태를 올리지 않음 |
| 화면 실행 전에 과거 보고서를 필수로 읽게 하는 안내 | 강의→실행 안내→연결 활동으로 수정 | 과거 실행 보고서는 재현 담당자의 근거로 계속 연결 |

원본 64개 파일의 탐색·선수 조건·활동/제출·강사 해설 관련 부분과 상대 링크를 대조했다. 70단원 전 문장·실행 코드·모든 명령을 다시 감사한 작업은 아니다. 단원별 설명은 앞선 수정 이력을 이어 사용한다. 원본 파일 목록과 해시는 [검증 기록](validation.json)에 남긴다.

## 과목별 연결 검토

| 범위 | 교육생 자료와 선행 연결 | 제출/후속 연결 | 강사용 해설 |
|---|---|---|---|
| 시작 안내 · 3단원 | [업무·목표·책임](../../lessons/orientation/lesson.md). 기술 경험 없이 시작 | 활동지의 문제/실패/책임/미확인 조건 → 데이터 과제 정의 | [해설](../../lessons/orientation/teacher-guide.md) |
| 데이터·평가 · 4단원 | [강의](../../lessons/data-evaluation/lesson.md). 입력 시점과 목표부터 고정 | 활동지·Dataset Card 요약·계보/분리·지표 → 모델/훈련 평가 기준 | [해설](../../lessons/data-evaluation/teacher-guide.md) |
| Transformer · 5단원 | [강의](../../lessons/transformer-basics/lesson.md). 표와 작은 계산 | A~E 계산·Shape/Mask/Cache → LLM 입력·생성 원리 | [해설](../../lessons/transformer-basics/teacher-guide.md) |
| LLM·Hugging Face · 7단원 | [LLM](../../lessons/llm-basics/lesson.md) → [HF](../../lessons/huggingface/README.md). 화면/손계산 뒤 Python 준비 | LLM A~D, HF 후보 비교·실제 Tokenizer/캐시관찰 → Prompt/Context. HF는 별도 과목 추가가 아니라 같은 과목의 뒤 3단원 | [LLM](../../lessons/llm-basics/teacher-guide.md) · [HF](../../lessons/huggingface/INSTRUCTOR.md) |
| 기준 앱 준비 · 별도 안내 | [기준 앱](../../lessons/baseline/lesson.md). Phase1 Python/HTTP/JSON/FastAPI 준비 | 입력/응답/오류·Provider 구분 기록 → 공통 Backend. 70단원에 추가 산입하지 않음 | 본문의 실행 경계와 기준 기록, [Backend](../../practice/document-assistant/backend/README.md) |
| Prompt · 4단원 / L1 | [강의](../../lessons/prompt/lesson.md) → [실습](../../practice/document-assistant/L1.md) | 지시/예시 변경·질문/자료 유지·회귀 기준 → 같은 지시의 Context 비교 | [해설](../../lessons/prompt/teacher-guide.md) |
| Context · 4단원 / L1 | [강의](../../lessons/context/lesson.md) → [별도 활동](../../practice/document-assistant/CONTEXT.md) | 자료 선택·순서·기존 Token 관찰 산술·현재 전달 자료 → 호출/검사 | [해설](../../lessons/context/teacher-guide.md) |
| Harness · 5단원 / L2 | [강의](../../lessons/harness/lesson.md) → [실습](../../practice/document-assistant/L2.md) | 고정 응답의 재시도/보완·예산/종료·형식/내용 판정 → 검색/생성 실행기 재사용 | [해설](../../lessons/harness/teacher-guide.md) |
| Embedding · 4단원 / L3 | [강의](../../lessons/embedding/lesson.md) → [공통 검색 실습](../../practice/document-assistant/L3.md)의 앞 활동 | 표현/벡터 계산·검색 누락·기록 해석 → Index 저장/탐색 | [해설](../../lessons/embedding/teacher-guide.md) |
| Index · 4단원 / L3 | [강의](../../lessons/vector-index/lesson.md) → 같은 실습의 Index 활동 | 원문·버전·상태·필터/변경/삭제·탐색 비교 → RAG 근거 | [해설](../../lessons/vector-index/teacher-guide.md) |
| RAG · 4단원 / L4 | [강의](../../lessons/rag/lesson.md) → [실습](../../practice/document-assistant/L4.md) | 실제 기록의 입력/원응답·보완·주장/인용·한 조건 비교 → 도구 실행. 새 실행은 별도 모델 환경 | [해설](../../lessons/rag/teacher-guide.md) |
| Single-Agent · 4단원 / L5 | [강의](../../lessons/single-agent/lesson.md) → [실습](../../practice/document-assistant/L5.md) | 요청/함수 진입·승인/출처·상태/종료 → 역할 전달. Framework/MCP 구현과 구분 | [해설](../../lessons/single-agent/teacher-guide.md) |
| Multi-Agent · 4단원 / L6 | [강의](../../lessons/multi-agent/lesson.md) → [실습](../../practice/document-assistant/L6.md) | 전달 근거/수신 범위·공통 예산/보완·최종/부분 초안 → 실패 원인과 학습 가설 | [해설](../../lessons/multi-agent/teacher-guide.md) |
| Fine-tuning · 8단원 / L7 | [데이터](../../lessons/fine-tuning/lesson.md) → [훈련](../../lessons/fine-tuning/training.md) → [실습](../../practice/document-assistant/L7.md) | 목표·분리/증강·정답 범위, LoRA 계산·QLoRA 자원·실제 응답/회귀·재현. 새 훈련/재로드는별도 증거 | [데이터](../../lessons/fine-tuning/teacher-guide.md) · [훈련](../../lessons/fine-tuning/training-teacher-guide.md) |
| PDF/OCR · 4단원 / L8 | [강의](../../lessons/document-parsing/lesson.md) → [실습](../../practice/document-assistant/L8.md) | 페이지 경로·표 관계·OCR 오류 영향·현재 권한/원문 위치 → 문서 등록/출력 | [해설](../../lessons/document-parsing/teacher-guide.md) |
| Document AI · 6단원 / L9 | [등록](../../lessons/document-ai/intake.md) → [보고서](../../lessons/document-ai/report.md) → [Provider](../../lessons/document-ai/provider.md) → [Streaming](../../lessons/document-ai/streaming.md) → [평가](../../lessons/document-ai/evaluation.md) · [실습](../../practice/document-assistant/L9.md) | 형식별위치·버전/권한/삭제·주장 검토/출력·예산·부분/확정·최종 채택/보류이유 | [앞 3단원](../../lessons/document-ai/teacher-guide.md) · [뒤 3단원](../../lessons/document-ai/delivery-teacher-guide.md) |

서로 다른 사례의 문서를 하나의 최신 업무 규정처럼 합치지 않는다. Prompt에서 임시 수정한 지시가 후속 고정 조건이나 API에 자동 반영되지 않는 점, 새 RAG/Agent 출력과 과거 합본 기록의 형식이 다른 점도 해당 안내의 경계를 따른다. 같은 파일을 공유하는 과목은 표에 적은 활동 순서를 사용한다.

## 남은 검증 순서

우선순위는 실행 의존성과 학생이 처음 막힐 지점을 기준으로 정했다. 문서 확장/화면 점검은 준비된 범위에서 본편 모델 평가와 병행할 수 있다. QLoRA·Vision·Framework/MCP는 별도 준비가 필요한 경로이며 본편의 성공 증거로 대신하지 않는다. 각 담당 역할은 필요한 검토 주체를 뜻하며 실제 담당자를 배정하거나 연락한 것은 아니다.

| 우선순위 | 할 일과 준비 | 남겨야 할 구체적인 근거 | 판정 주체/제한 |
|---|---|---|---|
| 1 · 바로 다음 | 격리 Python 3.12에 Tokenizer 고정 의존성·정확한 revision 파일 준비. Qwen/Smol의 기존 입력/길이 옵션과 캐시 반복 | 버전/preflight, 입력·revision·옵션/출력 해시, 실제 IDs/Mask/Template, 캐시 반복 대조. 현재 deps 부재를 과거 실행으로 덮지 않음 | 제작자가 실행 재현. 다른 OS/교육장·모델 생성은 별도. **다음 추천 Medium** |
| 2 · 본편 실행 기반 | Backend 고정 요구/Pydantic 환경을 맞추고 기존 API/Provider 계약 확인 후 선택한 실제 Provider 웹 생성 | 사용 환경/모델/설정, HTTP 요청/원응답, 실패 경로와 준비 상태. 고정 demo와 실제 생성 구분 | 제작자 실행, 강사 결과 해석. 모델 없는 성공만으로 생성 완료 불가 |
| 3 · 입력/생성 비교 | 위 모델 준비 뒤 Prompt 다섯 조건과 Context 조건, LLM 생성 설정을 통제해 실행 | 원본 질문/자료·Template·Token/생성 설정·원응답·시간/자원, 사례별 의미/경계 채점. 한 번에 한 원인 가설 | 제작자 실험 + 독립 강사/업무 검토. 같은 Test를 보고 조정했다면 새 평가 범위 필요 |
| 4 · RAG→Agent 과제 | 검색 환경/원문 현재성/고정 모델을 맞춘 뒤 RAG, Single, Multi를 같은 과제/예산으로 비교 | 검색 누락과 생성 오류 구분, 주장별 원문, 조건/예외, 도구/전달/종료, 실패/보완/최종 초안. 기존 실패도 포함 | 독립 내용 검토 필요. 형식 통과·호출 감소만으로 품질 채택 금지 |
| 5 · 학습 실험 | 데이터/분리/Tokenizer/정답 Mask를 재현한 뒤 LoRA·선택 기법/QLoRA 자원별 계획 확정 | Base/seed/augmented 동일 평가, Loss/행동/사실/Agent 과제, Adapter 새 프로세스 재현, 실제 자원/실패기록 | 제작자 실행 + 독립 품질 검토. 전체 행 포함은 수렴/품질 합격 아님. QLoRA·IA3/DoRA 비교 등은 미실행으로 유지 |
| 6 · 문서/출력 | PDF/OCR/글꼴을 준비하고 대표 일반 문서·복잡한 표·지원 밖 구조를 평가. 현재 보고서 출력도 새로 렌더링 | 원본/추출/표 관계/Locator, 핵심 필드 오류, 현재 v2 보고서내용과 화면. 과거 v1출력과 구분 | 문서/업무 검토자. 합성 네 문서와 단순 DOCX 성공을 일반 품질로 확대하지 않음 |
| 7 · 연결/운영 경계 | 실제 모델을 별도 SSE/기존 API에 연결할 범위 결정 후 구현/검증. Framework/MCP·인증/지속 승인·취소/강제 중단도 별도실험 | 실제 Token 수신시각, 최종/부분/취소 경합, 접근거부, 업로드/삭제/원문·예산·장애 기록. 고정 화면과 구분 | 구현자/운영 검토자. 기존 Chromium 9상황은 고정 전송 UI 증거이며 운영 배포 승인이 아님 |
| 8 · 수업 채택 | 실험에서 사용 가능 범위를 정하고 독립 강사/교육생의 대표 수업 시행. 강사 해설과 장비/시간 준비 | 막힌 용어/단계, 설명/도움 횟수, 작성 시간·제출물·판정 불일치, 다른 OS/동시 실행·복구 기록 | 독립 강사/교육생. 현재 실제 수강 시간·처리량은 미측정이며 사용자가 70개 문제를 대신 찾는 방식으로 전가하지 않음 |

순위 7은 단순 재실행을 넘어 추가 구현이 필요한 항목을 포함한다. 그 범위는 후속 작업에서 구체화하고 구현하지 않은 기능을 현재 교안의 동작으로 설명하지 않는다. 각 품질 실험은 실패 원인에 따라 보완 후 같은 기준으로 다시 판단하며, 모든 기능을 추가해야 기존 개념 활동을 시작할 수 있다는 뜻은 아니다.

## 검증과 보존

상대 파일/폴더 링크 524개와 문서 내 이동 지점 13개, 70단원의 자료 경로/강사 매핑·단원 수·현재 미완료 상태를 정적으로 확인했다. 변경은 수강/실습 탐색 안내·기준 앱의 제목/선수 표기·현재 상태/후속 작업 기록이다. 실행 코드·요구 패키지·모델/데이터·과거 보고서·기존 70단원 기록·milestones·first_unfinished_gate를 보존했다. 새 모델/훈련/브라우저/OCR/렌더링/독립 수업을 실행하지 않았으며 외부 링크의 현재 접속/화면 전체를 다시 검사하지 않았다.

문서 연결 판정은 **동일 작성자 검토 통과**다. 전체 교육과정 완료·수업/운영 채택은 계속 미완료로 둔다. 세부 검사 수와 게시 확인은 [validation.json](validation.json)에 기록한다.
