# 첫 강의 제작·실제 Tokenizer 검증 결과

2026-10-31 · KEDU-PRODUCTION-001 · **Linux CPU 실제 실행·캐시 재현 검증 완료**

**[강의 본문](../../lessons/huggingface/README.md)**은 PRE-HF / K2-03.U05~07의 첫 제작본이다. 설명·화면·실습 파일에 이어 실제 Tokenizer 검증까지 수행했다. 전체 70개 단원 중 작성한 자료는 여전히 3개이며, 생성 모델·훈련·교육장 수업 검증까지 완료한 것은 아니다.

## 실제 실행한 관찰

모델 ID·전체 리비전과 입력을 고정했다. 아래 네 조건의 실제 결과를 보존했다.

| 실행 조건 | KO / EN / SHORT Token 수 | 길이 제한 뒤 Token 수 | 검사 |
|---|---|---|---|
| [Qwen 기본, 길이 8](runtime/qwen-01/observations.md) | 16 / 13 / 2 | 8 / 8 / 2 | 통과 |
| [Qwen 캐시 재실행, HTTP 차단](runtime/qwen-offline-guarded/observations.md) | 16 / 13 / 2 | 8 / 8 / 2 | 통과·요청 시도 0회 |
| [Qwen 길이 16](runtime/qwen-length16-fixed/observations.md) | 16 / 13 / 2 | 16 / 13 / 2 | 통과 |
| [Smol 기본, 길이 8](runtime/smol-01/observations.md) | 64 / 13 / 2 | 8 / 8 / 2 | 통과 |

문자 수는 같은 입력에서 KO 30 / EN 61 / SHORT 3이다. 이 작은 예문 묶음의 Token 수로 언어 능력·답변 품질의 순위를 정하지 않는다. Chat Template은 입력 형식 변환이며 답변 생성이 아니다.

Qwen의 처음 관찰과 HTTP 차단 캐시 재실행에서 모델 리비전·원문/Token IDs·Padding·Chat Template·Tokenizer 파일 해시·입력 해시 등 안정적인 관찰 필드가 모두 일치했다. 생성 시각과 실행 경로는 일치 판정에서 제외했다.

오프라인 재실행은 HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE 설정과 Python requests의 요청 차단을 함께 적용했고 요청 시도가 0회였다. OS 전체의 네트워크를 차단해 검증했다고 주장하지 않는다.

## 실행 중 발견해 수정한 것

| 문제 | 실제 발생한 일 | 수정과 재검증 |
|---|---|---|
| Jinja2 누락 | Tokenizer 파일을 받은 뒤 apply_chat_template이 ImportError로 중단 | jinja2 3.1.6을 requirements·준비 검사에 추가. 두 모델 Template 실행 통과 |
| 잘림 판정 오류 | Qwen 길이 16에서 모든 입력이 제한 안에 들어가자 ‘잘림이 없다’는 이유로 검사 실패 | 입력 길이와 제한으로 기대 길이·잘림 여부를 검사하도록 수정. 길이 8/16 통과, 잘못된 잘림 표시를 주입한 회귀 검사는 오류 검출 |

조건을 완화해 무조건 성공 처리한 것이 아니다. 길이 제한 안의 정상 입력을 허용하면서, 제한을 넘는 잘림과 표시 오류를 계속 검사한다. 실패했던 실행 로그도 runtime의 기록과 validation.json의 보완 이력에 남겼다.

## 확인한 실행 환경과 범위

- Linux x86_64 · Python 3.12.14 · 격리 가상환경에서 실행했다.
- Transformers 4.57.1 / Tokenizers 0.22.1 / huggingface-hub 0.36.0 / Jinja2 3.1.6을 설치했다.
- 의존성 검사에 충돌이 없었고 계약·실제 관찰 회귀 테스트 **17개 통과, 실패 0, 생략 0**을 확인했다.
- [전체 설치 버전 스냅샷](../../practice/huggingface-tokenizer/requirements-tested.txt)을 남겼다. 다른 운영체제까지 보장하는 해시 Lock은 아니다.
- Qwen은 Tokenizer 관련 파일 5개, Smol은 6개를 사용하고 각 파일 SHA256을 실제 관찰 기록에 남겼다.
- 모델 가중치를 요청/로드하지 않았고 GPU·PyTorch·생성 API·훈련은 사용하지 않았다.

이전에는 패키지·파일 준비를 시도하지 않은 상태를 미완료로 남겼다. 이번에는 정상 설치/다운로드 경로를 실제 시도해 성공했다. 앞선 환경 제한 설명만으로 다운로드가 불가능하다고 단정하지 않고, 실제 시도 결과를 기준으로 상태를 갱신했다.

## 남은 항목과 다음 작업

이 묶음에서 남은 것은 교육장 Windows/Mac·학생 PC, 학생의 따라하기·수업 시간 검증이다. 이번 Linux CPU의 Tokenizer 성공을 실제 생성 모델·RAG·Agent·Fine-tuning 성공으로 확대하지 않는다.

**다음 제작 작업은 L0-BASELINE이며 추천 추론 강도는 High다.** 기존 Phase1 Day3 앱의 환경·Provider·입출력 계약을 고정한 뒤 K2-04~06 / L1~L2로 이어간다. [재개 기록](../../PROGRESS.md)을 읽으면 된다.

<details>
<summary>실행 담당자용 증거</summary>

- [validation.json](validation.json): 실제 네 관찰 조건·파일 해시·재현 비교·수정·범위
- [contract-tests.json](contract-tests.json): 실제 17개 검사 명령·종료 코드·출력
- [preflight.json](preflight.json), [dependency-check.json](dependency-check.json): 설치 버전·의존성 확인
- [runtime/offline-guarded.json](runtime/offline-guarded.json): HTTP 시도 0회 검증
- [runtime/qwen-length16.json](runtime/qwen-length16.json): 수정 전 잘림 검사 실패 로그
- [actual-run-attempt.json](actual-run-attempt.json): 최초 제작 때 의존성 미설치로 중단했던 과거 기록
- [run.json](run.json): 현재 상태·후속 Gate·게시 기록. 모델 내부 토큰/총 Tool 호출은 미공개이므로 null 유지

각 관찰 폴더의 observations.md는 사람이 읽는 실제 결과이고 observations.json은 같은 실행의 수치·설정·파일 해시다. 기대값을 만들어 넣은 예시 출력이 아니다. 의미 검토는 같은 작업 세션이며 독립 평가자나 자동 Runner를 구현했다고 주장하지 않는다.

</details>
