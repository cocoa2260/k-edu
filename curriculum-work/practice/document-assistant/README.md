# 문서 답변 누적 실습 — L0에서 L7 준비까지

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
| L7 준비 | [실습](L7.md) · [Fine-tuning 준비](../../lessons/fine-tuning/lesson.md) | 실제 Dataset/Token/label·저장/재로드, 모델 훈련 미실행 |

[Backend 실행 안내](backend/README.md)에서 실행한다. L4 CLI에서 실제 로컬 생성을 실행했다. 답변 품질은 채택 보류이고 React 화면·교육장 수업은 미검증이다. 고정 응답을 모델 결과로 기록하지 않는다.

baseline-source-map.json은 L0 원문 이동 당시의 해시 기록이다. 이후 누적 기능의 변경 기록은 milestones와 각 제작 보고서에서 읽는다. 현재 소스 전체가 L0 당시와 같다는 뜻이 아니다. L7 데이터 준비를 확인했다. 다음은 실제 훈련·Adapter 저장/새 프로세스 Reload다.
