# Harness·Loop / L2 제작·검증 결과

**Harness 5개 단원과 L2 실습을 작성했다. 기존 검사 포함 136개 테스트 통과, 고정 응답 10개 실험과 동일 12개 사례의 구조 회귀 비교를 실제 실행했다. 실제 모델 생성·답변 품질은 미검증이다.**

[강의](../../lessons/harness/lesson.md) → [실습 안내](../../practice/document-assistant/L2.md) 순서로 읽으면 된다. 누적 작성 자료는 70개 중 16개이며 수업 검증 완료 수가 아니다.

## 무엇을 만들었나

기존 Provider와 L1 입력 준비를 재사용하는 Harness를 추가했다. 통신 재시도와 형식/ID 보완을 구분하고 실행 전체가 같은 호출 예산을 공유한다. 오류/검사 실패·보완·종료를 순번과 해시로 기록한다. 기존 /ai/chat와 /ai/prepare는 변경하지 않았다.

출력의 필드·형식·빈 답변·중복/미제공 인용 ID를 검사한다. 사실·조건·예외·인용 문장의 타당성은 검사하지 않는다. 실제로 틀린 999999원과 올바른 DOC-A ID를 조합한 고정 응답이 구조 검사를 통과했다. 결과 상태는 항상 사람 검토가 필요한 초안이며 미승인이다. Tool 실행 기능은 없다.

## 실제 관찰

아래는 예상 예시가 아니라 [observed-demo.json](observed-demo.json)에 저장한 고정 응답 실행 관찰이다. calls는 Provider 메서드 시도 수이며 실제 모델 추론 수가 아니다.

| 고정 응답 실험 | 시도 | 재시도 | 보완 | 종료 이유 |
|---|---|---|---|---|
| valid_shape | 1 | 0 | 0 | structure_passed_review_required |
| timeout_then_success | 2 | 1 | 0 | structure_passed_review_required |
| repair_then_success | 2 | 0 | 1 | structure_passed_review_required |
| repeated_invalid | 2 | 0 | 1 | repair_limit |
| global_three_calls | 3 | 1 | 1 | structure_passed_review_required |
| retry_exhausted | 2 | 1 | 0 | retry_limit |
| upstream_terminal | 1 | 0 | 0 | provider_error |
| restricted_citation | 2 | 0 | 1 | repair_limit |
| forged_approval | 2 | 0 | 1 | repair_limit |
| wrong_fact_shape_passes | 1 | 0 | 0 | structure_passed_review_required |

정상 구조·보완 성공은 draft_needs_review이고 실패 종료는 초안을 반환하지 않았다. 재시도는 입력 해시가 같고 보완은 실패 ID를 추가해 해시가 달라졌다. 원격 상태/Provider 해석 오류는 즉시 종료하도록 정했다. 오류 전문과 잘못된 응답 전문은 Trace·보완 입력에 복사하지 않는다.

같은 12개 사례의 고정 출력 A/B에서는 구조 통과가 9건에서 10건으로 늘었지만 C07 회귀가 생겼다. C01/C02는 개선, C07은 악화, C10 공백 입력은 양쪽 모두 호출 전 거부였다. B의 채택은 보류했다. 이는 비교 도구의 실험이며 Prompt 개선·모델 정답률이 아니다. 사람의 사실/행동 채점은 모든 칸이 미실행이다.

기존 L0/L1 93개와 L2 43개를 합쳐 136개 테스트를 통과했다. 연결·시간 초과 재시도, 원격/해석 오류 종료, 보완 후 재검사, 공통 상한, 승인 추가 필드 거부, 제한/미제공 ID 거부, 빈 입력·최종 2000문자 계약, 취소·늦은 결과 폐기, 기존 API 회귀를 확인했다. L1의 60개 조합은 출력 계약을 붙인 뒤에도 55개 호출 준비와 공백 질문 5개 사전 거부로 확인했다. 이 수치는 모델 성공률이 아니다.

## 환경과 재현

2026-10-31 기준 기존 격리 Linux Python 3.12.14 환경을 사용했다. 의존성 추가·업그레이드는 없고 기존 requirements-tested.txt를 유지한다. 자동 테스트는 기존 fixture에서 실제 외부 httpx 전송을 금지하며 데모는 scripted-fixture/no-model-executed를 주입한다. 실제 모델·유료 API 호출은 0회다.

backend 폴더에서 입력할 명령은 `python -m pytest -q`와 `python -m tools.harness_demo --output 새파일.json`이다. 두 번째 명령은 기존 파일을 덮어쓰지 않는다. 재현한 검사 명령·표준 출력·관찰 시각은 [tests.json](tests.json), 세부 범위는 [validation.json](validation.json)에 있다.

이번 온라인 문서 검색은 두 검색 시스템 모두 오류로 내용을 얻지 못했다. 새 SDK 연결이나 버전 변경은 하지 않았고 설치된 Pydantic의 엄격한 형식·추가 필드 거부를 실제 실행으로 검사했다. 새 API의 최신성 조사 완료로 기록하지 않는다.

## 해석 한계와 다음 단계

90초는 호출 전후에 확인하는 경과시간 상한이며 진행 중 호출을 끊지 않는다. 가짜 시계·취소 신호 테스트는 제어 흐름 증거이며 실제 장애 서버의 벽시계 측정이 아니다. 입력 문자와 응답 수신 후 크기 제한은 Token·비용 강제 상한이 아니다. Provider 계약에 사용량 반환이 없어 사용량·비용은 미확인으로 남긴다.

승인 필드 거부는 실제 인증·승인 저장소·부작용 실행의 검증이 아니다. 제공 ID 검사도 인용 내용·현행성·Prompt Injection 저항성의 증거가 아니다. 현재 선택은 수동이며 검색·Index·삭제 전파를 구현하지 않았다.

같은 Work 세션의 검토이며 독립 검토·교육장 실습·React UI 검증은 미실행이다. L0/L1/L2 실제 모델 정상·보완·안전 종료와 사람의 사례별 채점은 별도 Gate로 남긴다. 다음 제작 묶음은 K2-07/K2-08/L3 검색용 표현·Index이며 추천 추론 강도는 High다. 아직 작성하지 않은 기초 단원도 전체 완료 전에 제작한다.
