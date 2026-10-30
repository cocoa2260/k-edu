# 첫 강의 제작 결과 — Hugging Face 입문

2026-10-30 · KEDU-PRODUCTION-001 · **자료 검토 가능 / 실제 Tokenizer 실행 검증 대기**

**[강의 본문 한 개](../../lessons/huggingface/README.md)**에서 먼저 읽으면 된다. 이번에 완성한 것은 PRE-HF / K2-03.U05~07의 첫 강의 자료, 실행 파일, 답안·평가 기준이며 전체 5단계의 완료가 아니다.

| 만든 것 | 내용 | 검증 상태 |
|---|---|---|
| 학생용 본문 | Hub 탐색 → Model Card/파일/실행 경로 → Tokenizer·Template | 같은 세션의 내용·링크·활동 검토 |
| 실제 화면 | 이전 구성안의 Docs·모델 페이지 캡처 2장 재사용 | 기준 커밋의 실제 JPEG 참조. 새 화면을 캡처했다고 표시하지 않음 |
| 짧은 핵심 코드 | encode/decode·Padding·Template 세 부분 | 구문 확인. 실제 Tokenizer 실행 미검증 |
| 관찰 실행 도구 | 고정 Revision·파일 제한·실제 Tokenizer·읽는 결과/JSON 기록 | 오류/중단/기록 보호 테스트 통과. 실제 Tokenizer 미실행 |
| 입력·모델 설정 | 문장 3개·대화 목록·모델 2개의 고정 리비전 | 원본 API 메타데이터·입력 구조 확인 |
| 학생 답안·강사용 기준 | 선택 근거·미확인 조건·실제 관찰 해석 | 같은 세션에서 학습목표와 연결 확인 |
| 재개 기록 | 70개 단원 목록·이번 3개·첫 미완료 Gate | 자료 작성과 실행 검증을 별도 상태로 관리 |

## 실제 수행한 검사와 한계

입력·준비 미완료·결과 덮어쓰기 방지 계약 테스트 **13개를 실행해 통과**했다. Python 구문과 자료 연결도 검사했다. 이 검사는 실제 Tokenizer나 생성 모델의 성공을 입증하지 않는다.

preflight를 실제로 실행했고 Transformers·Tokenizers·huggingface-hub가 설치되지 않은 상태를 확인했다. 관찰 명령도 실행했지만 의존성 준비 필요로 종료 코드 2를 반환했으며, 관찰 결과 파일을 생성하지 않았다. 가짜 결과·Token IDs·모델 답변으로 대체하지 않았다.

이 작업 환경의 Python은 3.12.14다. 실습의 직접 버전 후보는 Transformers 4.57.1 / Tokenizers 0.22.1 / huggingface-hub 0.36.0이다. 패키지 설치와 실제 두 모델 Tokenizer 파일 로드는 아직 수행하지 않아 호환성을 확정하지 않았다. 교육장 Windows/Mac·네트워크·전체 의존성·학생 수업 시간도 미검증이다.

이번 세션의 실행 호스트는 외부 접속 대상이 제한돼 있고 필요한 의존성과 캐시가 없다. 허용되지 않은 목적지로의 우회 다운로드를 시도하지 않았다. 원본 웹 문서·모델 리비전 조회와 실행 호스트의 패키지/파일 다운로드를 구분한다.

## 다음 검증

1. 격리된 Python 3.12 환경에 의존성을 설치하고 해결된 전체 버전을 기록한다.
2. models.json에 고정한 Qwen/Smol 리비전에서 Tokenizer 관련 파일만 확보한다.
3. Qwen 실제 관찰과 캐시 재실행의 안정적인 관찰값을 비교한다. 시간·출력 경로는 비교 대상에서 제외한다.
4. 길이 16 변경과 Smol 비교를 수행하고 Token 수·Template·특수 Token 동작을 검토한다.
5. 실제 결과·파일 해시·환경 기록으로 현재 미완료 Gate를 갱신한다. 검사 실패가 있으면 해당 부분만 수정하고 다시 검증한다.

이 Gate는 GPU가 없어 남은 항목이 아니라, 실제 Tokenizer 실행에 필요한 Python 의존성·파일 검증 항목이다. 추론 API 호출로 대체할 필요도 없다.

<details>
<summary>실행 담당자용 기록</summary>

- [validation.json](validation.json): 검사 범위·결과와 미수행 항목
- [contract-tests.json](contract-tests.json): 실제 계약 테스트 명령·표준 출력/오류·종료 코드
- [preflight.json](preflight.json): 실제 준비 상태 검사 결과
- [actual-run-attempt.json](actual-run-attempt.json): 관찰 경로가 준비 미완료로 종료한 기록
- [run.json](run.json): 기준·범위·게시·사용량 미공개 상태

위 JSON은 실제 작업 기록이며 강의 예시 코드가 아니다. 학생은 강의 본문과 직접 생성한 observations.md를 우선 읽는다. 독립 자동 Runner·독립 평가자·추론 강도 자동 전환을 구현했다고 표시하지 않는다.

</details>
