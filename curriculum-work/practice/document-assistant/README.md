# 문서 답변 누적 실습 — L0에서 L3까지

같은 Backend를 단계별로 확장한다. 강의 설명과 실행 코드는 파일을 나눠 두었다.

| 단계 | 읽을 파일 | 현재 검증 범위 |
|---|---|---|
| L0 | [기준 앱 강의](../../lessons/baseline/lesson.md) | Provider/API 계약·로컬 HTTP 고정 응답 |
| L1 | [공통 실습](L1.md) · [Prompt](../../lessons/prompt/lesson.md) · [Context](../../lessons/context/lesson.md) | 가상 자료·입력 준비·기준 Tokenizer 관찰 |
| L2 | [실습 안내](L2.md) · [Harness 강의](../../lessons/harness/lesson.md) | 고정 응답 호출·검사·재시도·보완·상한·회귀 |
| L3 | [실습 안내](L3.md) · [Embedding](../../lessons/embedding/lesson.md) · [Index](../../lessons/vector-index/lesson.md) | 실제 CPU Embedding·검색·Filter·갱신/삭제·설정 재구축 |
| L3 | [실습 안내](L3.md) · [Embedding](../../lessons/embedding/lesson.md) · [Index](../../lessons/vector-index/lesson.md) | 실제 CPU Embedding·검색·Filter·갱신/삭제·설정 재구축 |

[Backend 실행 안내](backend/README.md)에서 실행한다. 실제 모델 생성·답변 품질·React 화면·교육장 수업은 미검증이다. 고정 응답을 모델 결과로 기록하지 않는다.

baseline-source-map.json은 L0 원문 이동 당시의 해시 기록이다. 이후 누적 기능의 변경 기록은 milestones와 각 제작 보고서에서 읽는다. 현재 소스 전체가 L0 당시와 같다는 뜻이 아니다. 다음 L4에서 검색·Context·실제 생성·근거 평가를 연결한다.
