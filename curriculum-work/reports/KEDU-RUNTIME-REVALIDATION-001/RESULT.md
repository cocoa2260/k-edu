# Tokenizer 실제 실행과 캐시 재현 결과

2026-11-04 · Linux x86_64 / Python 3.12.14

**격리 환경에서 Qwen·Smol Tokenizer를 실제 실행했고, 캐시 반복과 과거 관찰 대조를 통과했다.** 앞선 설명 정비 당시의 의존성 미설치 상태를 이번 실행으로 해소했다. 모델 답변 생성·훈련·교육생 장비/독립 수업 검증은 수행하지 않았다.

## 교육생과 강사가 확인할 결과

입력·모델 revision·옵션을 기존 실습과 같게 유지했다. 아래 Token 수는 기대값을 적어 둔 표가 아니라 이번 실제 실행 결과다. 각 링크에서 입력·IDs·복원·Padding·대화 형식을 볼 수 있다.

| 조건 | KO / EN / SHORT Token 수 | 잘림 뒤 Token 수 | 대화 입력 Token 수 | 결과 |
|---|---|---|---|---|
| [Qwen 길이 8](runtime/qwen-8/observations.md) | 16 / 13 / 2 | 8 / 8 / 2 | 25 | 통과 |
| [Qwen 길이 8 캐시 반복](runtime/qwen-8-cache/observations.md) | 16 / 13 / 2 | 8 / 8 / 2 | 25 | 통과 |
| [Qwen 길이 16](runtime/qwen-16/observations.md) | 16 / 13 / 2 | 16 / 13 / 2 | 25 | 통과 |
| [Qwen 길이 16 캐시 반복](runtime/qwen-16-cache/observations.md) | 16 / 13 / 2 | 16 / 13 / 2 | 25 | 통과 |
| [Smol 길이 8](runtime/smol-8/observations.md) | 64 / 13 / 2 | 8 / 8 / 2 | 22 | 통과 |
| [Smol 길이 8 캐시 반복](runtime/smol-8-cache/observations.md) | 64 / 13 / 2 | 8 / 8 / 2 | 22 | 통과 |

한국어 원문은 30문자다. Qwen의 첫 세 ID는 126246·144370·91145이며 전체 decode는 원문과 같다. Qwen 배치 폭은 16이고 짧은 입력은 내용 2자리·패딩 14자리다. 길이 16 조건에서 잘림이 없다는 것은 정상이다. Smol 배치 폭은 64다. 이 예문 몇 개의 Token 수로 한국어 능력이나 모델 품질 순위를 매기지 않는다.

학생이 읽는 [짧은 실행 파일](../../practice/huggingface-tokenizer/tokenizer_steps.py)도 실제 캐시로 실행했다. 그 파일의 별도 문장은 **21문자·12 Token**이며 decode가 일치했다. 위 표의 30문자·16 Token과 다른 입력이다. `Hi!`는 내용 2자리·패딩 10자리였고 대화 문자열은 생성할 입력으로만 렌더링했다. [실제 출력](student-steps.json)을 남겼다.

## 무엇을 대조했는가

- 세 조건 각각 최초 실행과 캐시 반복을 대조했다. 또 Qwen 길이 8/16·Smol 길이 8을 [과거 실제 실행](../KEDU-PRODUCTION-001/RESULT.md)의 동일 조건과 비교했다. **6개 비교 모두 안정적인 관찰 필드 전체가 같았다.**
- 비교에는 입력/파일 해시·revision·옵션·각 ID와 조각·복원문·잘림·특수 Token·Padding/Mask·Template 문자열/IDs·내부 검사 결과가 포함된다. 생성 시각·다운로드 허용 여부·의존성 메타데이터만 동일성 판정에서 제외하고 별도로 기록했다.
- 네 번의 캐시 실행에는 다운로드 미허용, HF/Transformers offline 환경과 Python `requests` 및 socket 연결 차단을 적용했다. 각 실행의 요청/연결 시도는 0회였다. OS 전체 방화벽으로 차단한 실험은 아니다.
- 별도 빈 캐시로 같은 차단 실행을 시도하자 **종료 코드 2 / setup_required**, 관찰 출력 폴더 미생성, 요청/연결 시도 0회였다. 과거 결과나 가짜 Tokenizer로 대체하지 않았다.

비교 필드·파일 해시·차단 계수는 [comparison.json](comparison.json), 차단 실행 코드는 [offline_probe.py](offline_probe.py)에 있다. 차단 코드는 이번 재현용 진단 도구이며 교육생 필수 독해 대상이 아니다.

## 설치와 검사

가상환경 `.venv-tokenizer-r1`을 새로 만들고 기존 requirements.txt를 그대로 설치했다. 직접 의존성 Transformers 4.57.1 / Tokenizers 0.22.1 / huggingface-hub 0.36.0 / Jinja2 3.1.6이 모두 맞았다. `pip check`와 preflight는 종료 코드 0이다. preflight만으로 파일 준비나 실제 실행이 성공했다고 판정하지 않고 위 실제 관찰을 별도로 확인했다.

전체 간접 의존성 중 **filelock만 과거 4.2.4 → 현재 4.2.7**로 달랐다. 기존 requirements-tested.txt를 덮어쓰지 않고 이번 [설치 버전 스냅샷](requirements-observed.txt)을 따로 보존했다. 동일 환경 전체를 완전히 복제했다고 주장하지 않는다. 이 차이가 있는 상태에서도 이번에 비교한 Tokenizer 관찰은 모두 같았다.

기존 계약/저장 관찰 검사 17개를 통과했다. 실제 실행 후에는 `KEDU_OBSERVATIONS`를 이번 Qwen 관찰에 연결해 같은 17개를 다시 통과했고 실패·생략은 0개였다. 같은 검사 집합을 두 자료 경로로 실행한 것이며 34종의 서로 다른 검사로 집계하지 않는다. 입력 오류·기존 출력 보호·잘못된 잘림 표시 거부와 새 관찰의 정합성을 확인한다. [신규 관찰을 사용한 검사 출력](fresh-observation-tests.json)을 남겼다.

새 캐시에는 고정 revision의 Qwen 관련 파일 5개, Smol 6개가 있다. 실행 도구의 허용 목록은 Tokenizer/Config 파일로 제한돼 있고 캐시 스냅샷에 모델 Weight·원격 Python 코드는 없다. PyTorch·생성 모델 로딩·유료 API·훈련은 사용하지 않았다. Weight 없이 Tokenizer만 사용한다는 라이브러리 경고는 이 실습의 예상 범위다.

## 재현할 때

교육생은 [기존 실행 안내](../../practice/huggingface-tokenizer/README.md)의 명령을 사용한다. 최초 준비는 다운로드 허용 실행, 반복은 그 옵션을 뺀 새 출력 폴더로 진행한다. 이번 추가 차단 실험은 다음과 같이 준비된 캐시를 명시해 재현할 수 있다. 아래는 저장소 루트 기준 **명령 형태**이며 캐시와 Python 경로는 실제 준비한 위치로 바꾼다.

```bash
HF_HOME=/path/to/prepared-cache /path/to/venv/bin/python curriculum-work/reports/KEDU-RUNTIME-REVALIDATION-001/offline_probe.py --lab curriculum-work/practice/huggingface-tokenizer/inspect_tokenizer.py --profile qwen --max-length 8 --output /path/to/new-observation --guard-report /path/to/new-guard.json
```

이 명령은 macOS/Linux 셸 형식이다. 이번 실제 실행은 Linux에서만 했다. 스크립트가 두 offline 환경 변수를 설정하며 기존 캐시를 요구한다. 진단 기록의 절대 실행 경로는 이번 환경의 위치이며 다른 장비에 그대로 존재한다고 가정하지 않는다. 과거 관찰 폴더와 현재 출력 폴더를 덮어쓰지 않는다.

## 남은 작업과 다음 순서

현재 해소한 것은 이 Linux 환경의 **실제 Tokenizer 실행·캐시 재현**이다. Mac/Windows·교육생 장비·동시 수업·수업 시간, 실제 생성/검색/Agent/훈련 품질과 전체 교육과정 채택은 남아 있다. 기존 70개 단원·단계별 실행 이력·품질 게이트는 보존했다. 기존 설명/입력/Tokenizer 구현을 수정할 오류는 이번 실행에서 발견하지 않았다.

**다음 작업은 Backend 고정 환경·API/Provider 계약 재검증과 실제 Provider 준비 상태 확인이다. 추천 추론 강도는 Medium.** 기존 명세와 실행 경로가 정해져 있어 환경·관찰 대조가 중심이다. 실제 Provider가 준비되지 않았다면 계약 데모 성공을 실제 생성 성공으로 바꾸지 않고 원인과 후속 조건을 기록한다. 전체 순서는 [통합 점검의 검증 계획](../KEDU-TEACHING-INTEGRATION-001/RESULT.md)을 이어 따른다.

상세 실행 명령·종료 코드·환경·보존/게시 확인은 [validation.json](validation.json)에 있다. 외부 모델 페이지/UI를 이번에 다시 검수한 작업은 아니다.
