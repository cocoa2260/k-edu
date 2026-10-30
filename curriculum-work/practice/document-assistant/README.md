# 문서 답변 누적 실습 — L0 기준 앱

먼저 [L0 강의 본문](../../lessons/baseline/lesson.md)을 읽고 [Backend 실행 안내](backend/README.md)에 따라 실행한다. 현재는 문서 검색 전의 문자열 대화 계약만 구현했다. L1~L9는 같은 Backend에 기능을 이어 붙인다.

| 위치 | 역할 |
|---|---|
| backend | Day3 코드에서 이어받은 실제 Python 앱·테스트·실행 도구 |
| baseline-source-map.json | 원문 파일/행·해시와 코드 이동·보완 근거 |
| milestones/L0.json | 이번 기준 환경·입출력·검증 범위와 미확인 Gate |

현재 계약 테스트와 로컬 HTTP 계약 데모는 검증했고 실제 모델 생성·React 화면·교육장 실행은 미검증이다. 데모의 고정 응답을 생성 모델 결과로 기록하지 않는다.
