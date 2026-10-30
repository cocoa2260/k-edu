# Tokenizer CPU 관찰 실습

학생은 먼저 [강의 본문](../../lessons/huggingface/README.md)을 읽는다. 이 폴더는 실제 Python 실행 파일과 입력·설정·답안이다. 모델 생성/훈련 앱과 별도인 작은 도구이며, 이후 누적 프로젝트를 새 앱으로 복제한 것이 아니다.

## 준비 상태

Python 3.12, 인터넷으로 준비한 Python 의존성, 선택한 리비전의 Tokenizer 파일이 필요하다. GPU·PyTorch·생성 모델 가중치는 이 실습의 필요 조건이 아니다. Linux x86_64 / Python 3.12.14에서 직접 의존성 설치와 실제 Qwen·Smol Tokenizer 실행을 검증했다. requirements-tested.txt에는 전체 설치 버전을 기록했다. 다른 운영체제와 교육장 호환성은 별도 확인이 필요하다. 실제 확인 결과는 [제작 기록](../../reports/KEDU-PRODUCTION-001/RESULT.md)을 확인한다.

## 실행 순서

터미널에서 이 폴더로 이동한다. 저장소 루트에서 명령을 실행하려면 inputs·requirements 상대경로가 달라지므로, 처음에는 이 폴더에서 실행한다.

| 단계 | macOS/Linux 명령 | Windows PowerShell 명령 |
|---|---|---|
| 환경 만들기 | `python3.12 -m venv .venv` | `py -3.12 -m venv .venv` |
| 설치 | `.venv/bin/python -m pip install -r requirements.txt` | `.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| 준비 상태 | `.venv/bin/python inspect_tokenizer.py --preflight` | `.venv\Scripts\python.exe inspect_tokenizer.py --preflight` |
| 실제 관찰·처음 파일 확보 | `.venv/bin/python inspect_tokenizer.py --profile qwen --allow-download --output runs/qwen-01` | `.venv\Scripts\python.exe inspect_tokenizer.py --profile qwen --allow-download --output runs/qwen-01` |
| 캐시로 반복 | `.venv/bin/python inspect_tokenizer.py --profile qwen --output runs/qwen-offline-01` | `.venv\Scripts\python.exe inspect_tokenizer.py --profile qwen --output runs/qwen-offline-01` |

위 명령은 입력할 명령이며 실행 로그가 아니다. 종료 코드 0은 해당 명령의 검사를 통과했다는 뜻이다. preflight의 0은 의존성 버전 메타데이터만 일치한다는 뜻으로 캐시·실제 Tokenizer 실행 성공과 다르다. 종료 코드 2는 준비/입력/출력 경로 문제, 1은 실제 관찰의 내부 정합성 오류다.

다운로드 허용이 없으면 snapshot_download의 local_files_only 경로를 사용한다. 설치·파일 확보는 온라인 준비 작업이며, 캐시 재실행은 네트워크 다운로드가 필요 없는 경로다. 다운로드 허용 옵션을 빼고 재실행했다는 사실과 OS 수준에서 네트워크를 차단해 검증했다는 사실은 구분한다.

## 파일 역할

| 파일 | 역할 |
|---|---|
| inspect_tokenizer.py | 실제 Tokenizer 로드·인코딩·길이/Padding·Template 관찰 |
| tokenizer_steps.py | 학생이 읽을 짧은 실제 API 호출 코드. 위 명령으로 캐시를 준비한 뒤 같은 Python으로 실행 |
| models.json | 모델 ID·고정 리비전·Template 옵션. 실제 설정 |
| inputs.json | 수업에서 사용할 실제 입력 세 개와 메시지 목록 |
| requirements.txt | 이번 도구의 직접 의존성 버전 |
| WORKSHEET.md | 학생이 작성할 답안 양식 |
| tests/test_contracts.py | 입력·중단·기록 보호 검사. 실제 Tokenizer 검증을 대신하지 않음 |
| runs/실행명/observations.md | 성공한 실제 실행이 만드는 사람이 읽는 관찰 결과 |
| runs/실행명/observations.json | 같은 실행의 파일 해시·리비전·설정·수치 기록 |

runs는 실행할 때 생성한다. 이 폴더에 정상 결과 예시를 미리 넣어 실제 실행처럼 보이게 하지 않았다.

## 문제가 생기면

| 증상 | 먼저 확인할 것 | 기록할 상태 |
|---|---|---|
| Python 3.12 명령을 못 찾음 | 설치한 Python·실행기와 PATH | 환경 준비 필요 |
| preflight가 setup_required | 표시된 실제 버전과 requirements 비교 | 의존성 준비 필요 |
| Tokenizer files unavailable | 인터넷·파일 접근 조건·선택 리비전·캐시 | 파일 확보 필요. 성공 결과를 만들지 않음 |
| output folder 오류 | 이전 결과가 있는지 확인하고 새 실행명 사용 | 기존 결과 유지 |
| Template/로더 불일치 | 프로필과 리비전·설치 버전·파일 누락 확인 | 실제 실행 검증 필요 |
| 관찰 검사가 1로 종료 | observations.md의 확인할 오류를 보고 원인 조사 | 실행됨·검사 실패 |

설정이 안 맞으면 출력 값을 만들어서 채우지 않는다. 설치 오류를 해결한다고 모델 가중치·CUDA·대규모 학습 도구를 무조건 추가하지 않는다.

<details>
<summary>개발자용 계약 검사</summary>

저장소 루트에서 `python -m unittest discover -s curriculum-work/practice/huggingface-tokenizer/tests -v`를 실행한다. 이 검사는 고정 리비전 요구·입력 오류·의존성 미준비·기존 결과 덮어쓰기 방지를 확인한다. 기록된 실제 관찰을 읽는 회귀 검사는 보고서의 runtime 폴더가 있으면 함께 실행한다. 실제 Tokenizer의 새 실행 증거는 위의 관찰 명령으로 별도 확보한다.

</details>
