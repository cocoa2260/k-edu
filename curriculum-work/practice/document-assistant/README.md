# 문서 답변 누적 실습 — L0에서 L9 문서 등록까지

같은 Backend를 단계별로 확장한다. 강의 설명과 실행 코드는 파일을 나눠 두었다.

| 단계 | 읽을 파일 | 현재 검증 범위 |
|---|---|---|
| L0 | [기준 앱 강의](../../lessons/baseline/lesson.md) | Provider/API 계약·로컬 HTTP 고정 응답 |
| L1 | [공통 실습](L1.md) · [Prompt](../../lessons/prompt/lesson.md) · [Context](../../lessons/context/lesson.md) | 가상 자료·입력 준비·기준 Tokenizer 관찰 |
| L2 | [실습 안내](L2.md) · [Harness 강의](../../lessons/harness/lesson.md) | 고정 응답 호출·검사·재시도·보완·상한·회귀 |
| L3 | [실습 안내](L3.md) · [Embedding](../../lessons/embedding/lesson.md) · [Index](../../lessons/vector-index/lesson.md) | 실제 CPU Embedding·검색·Filter·갱신/삭제·설정 재구축 |
| L4 | [실습](L4.md) · [RAG 강의](../../lessons/rag/lesson.md) | 실제 검색·Qwen 생성·출력 보완/종료, 품질 보류 |
| L5 | [실습](L5.md) · [Single-Agent](../../lessons/single-agent/lesson.md) | 실제 모델 Tool 요청·Runtime·종료, 과제 품질 보류 |
| L6 | [실습](L6.md) · [Multi-Agent](../../lessons/multi-agent/lesson.md) | 실제 역할·전달/공통 예산, 최종 답변 품질 보류 |
| L7 | [실습](L7.md) · [훈련 강의](../../lessons/fine-tuning/training.md) | 전체 Train 포함 제한 Step 학습·18개 Agent 회귀, 품질 보류 |
| L8 | [실습](L8.md) · [문서 입력 강의](../../lessons/document-parsing/lesson.md) | 실제 한글 PDF/OCR·표·물리 원문 연결, Vision 미실행 |

[Backend 실행 안내](backend/README.md)에서 실행한다. L4 CLI에서 실제 로컬 생성을 실행했다. 답변 품질은 채택 보류이고 React 화면·교육장 수업은 미검증이다. 고정 응답을 모델 결과로 기록하지 않는다.

baseline-source-map.json은 L0 원문 이동 당시의 해시 기록이다. 이후 누적 기능의 변경 기록은 milestones와 각 제작 보고서에서 읽는다. 현재 소스 전체가 L0 당시와 같다는 뜻이 아니다. L7 데이터 준비를 확인했다. LoRA 소규모 훈련·저장/재로드를 확인했고 전체 훈련·품질·QLoRA는 남아 있다.

[실제 LoRA 소규모 훈련 결과](../../reports/KEDU-PRODUCTION-010/RESULT.md)를 함께 본다.

[전체 Train 포함 학습·18개 Agent 회귀 결과](../../reports/KEDU-PRODUCTION-011/RESULT.md): 모든 예제를 학습에 포함했으며 품질 채택은 미완료다.

[L8 PDF/OCR 실제 결과](../../reports/KEDU-PRODUCTION-012/RESULT.md): 합성 문서 네 개와 변경 범위 검사만 실행했다. 일반 문서 품질·LLM/Vision·실제 업로드 UI는 미검증이다.

[L9 첫 묶음](L9.md): PDF/TXT 공통 구조와 등록·상태·권한·삭제를 실행했다. [결과](../../reports/KEDU-PRODUCTION-013/RESULT.md)를 본다. L9 보고서/UI/최종 평가는 미완료다.

[L9 보고서 확장](../../lessons/document-ai/report.md): Claim별 근거·검토 해시를 DOCX/PDF에 연결했다. [실제 결과](../../reports/KEDU-PRODUCTION-014/RESULT.md)를 본다. Provider/UI/최종 평가는 남아 있다.

[L9 Provider 제어](../../lessons/document-ai/provider.md): 로컬 HTTP 고정 응답으로 기능·준비 상태·공유 예산·Fallback·Trace를 검사했다. [실제 결과](../../reports/KEDU-PRODUCTION-015/RESULT.md)를 본다. 실제 모델/웹/Streaming 연결은 미완료다.

[L9 React·Streaming](../../lessons/document-ai/streaming.md): 실행 가능한 React 화면과 별도 Python SSE 서버를 추가했다. [실제 결과](../../reports/KEDU-PRODUCTION-016/RESULT.md)와 [화면 실행 안내](stream-ui/README.md)를 본다. 기존 API 전환·실제 모델 Streaming·최종 수업 평가는 남아 있다.

[L9 다중 형식·평가](../../lessons/document-ai/evaluation.md): PDF/TXT에 좁은 DOCX 문단/표 입력을 연결했다. [실제 결과](../../reports/KEDU-PRODUCTION-017/RESULT.md)를 본다. K2-14 여섯 단원 자료는 작성했으나 L9 독립 품질·운영 채택은 보류다.
