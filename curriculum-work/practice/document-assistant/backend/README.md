# 문서 답변 누적 실습 — Backend L0~L3

Day3 7~8교시의 코드와 CORS에서 출발해 L1 입력 준비, L2 Harness, L3 실제 Embedding·검색·Index를 같은 프로젝트에 추가했다. 대화 API와 검색 실험 도구는 현재 별도로 실행하며, L4에서 검색과 생성을 연결한다. 처음 시작하는 학생은 [L0 본문](../../../lessons/baseline/lesson.md)을 읽는다.

## 시작하기

이 폴더를 터미널에서 열고 Python 3.12 가상환경을 만든다. 아래 python은 그 가상환경의 실행기를 뜻한다. Windows/macOS별 전체 명령은 강의 본문에 있다.

| 목적 | 입력할 명령 |
|---|---|
| 수업·검증 패키지 설치 | `python -m pip install -r requirements-dev.txt` |
| 모델 없이 계약 검사 | `python -m pytest -q` |
| 계약 데모 서버 | `python -m uvicorn tools.contract_demo:create_contract_app --factory --host 127.0.0.1 --port 8000` |
| 설정한 실제 Provider 서버 | `python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000` |
| 로컬 Ollama 준비 상태 읽기 | `python -m tools.check_readiness` |

실제 Provider 서버는 .env.example을 로컬 .env로 복사해 선택한 Provider 값만 채운 뒤 실행한다. Key나 모델 설정이 빠진 실제 경로는 실패하며, 계약 데모로 자동 전환하지 않는다.

계약 데모는 provider=contract-demo / model=no-model-executed를 반환하는 고정 규칙 응답이다. Provider 준비 도구는 http://localhost:11434/api/tags만 읽으며 생성·모델 다운로드·OpenAI API 호출을 하지 않는다. 도구가 정상 종료해도 출력의 Gate가 G_MODEL_PENDING이면 실제 모델 검증은 미완료다.

## 고정한 계약

POST /ai/chat: message 문자열을 받고 provider·model·answer 문자열을 돌려준다. 입력은 1~2000문자이며 공백 입력은 422로 거부한다. 수락한 메시지의 앞뒤 공백은 제거한다. 추가 요청 필드는 원문의 기본 동작에 따라 무시하며 Provider 선택을 바꾸지 않는다.

연결 실패는 503, 시간 초과는 504, 원격/응답 형식 오류는 502다. GET /health는 설정 확인으로 실제 모델을 호출하지 않는다. Streaming·대화 기록·Tool·인증은 이 버전의 기능이 아니다.

## 환경과 검사 범위

requirements.txt는 이번 격리 Linux Python 3.12 환경에서 설치·계약 검사한 직접 버전이다. requirements-tested.txt는 설치된 전체 버전 스냅샷이며 다른 운영체제까지 보장하는 해시 Lock은 아니다. 기존 FastAPI 강의 전체의 버전 설명을 일괄 변경한 것은 아니다.

설정된 SOCKS 프록시를 사용하는 환경에서도 HTTP 클라이언트가 동작하도록 httpx의 socks 옵션을 포함한다. 프록시를 끄거나 TLS 검증을 끄는 해결법은 사용하지 않는다.

검증 결과와 실제 Provider·UI의 미확인은 [L0 결과](../../../reports/KEDU-PRODUCTION-002/RESULT.md)에 있다. 학생의 실제 생성·성능·화면 증거는 별도로 기록해야 한다.

## L1 확장

POST /ai/prepare는 사례 ID와 조건으로 입력만 준비한다. 실제 생성은 하지 않는다. [L1 안내](../L1.md)에서 비교 조건·공통 자료·명령·채점을 확인한다. /ai/chat 계약은 유지한다.

## L2 확장

[L2 안내](../L2.md)의 고정 응답 실험은 같은 Provider 인터페이스에 Harness를 붙인다. 실제 모델 선택 옵션이나 새 API는 추가하지 않았다. 입력 준비·출력 구조/인용 ID 검사·공통 호출 상한·Trace·회귀 비교를 실행한다. 입력할 명령은 `python -m tools.harness_demo --output l2-observed.json`이며 기존 파일은 덮어쓰지 않는다.

총 Provider 시도 3회·재시도 1회·보완 1회는 실행 전체의 상한이다. 90초는 호출 전후 검사이며 요청을 진행 중에 끊지 않는다. 구조 통과는 사실성·승인·Token 예산 검증이 아니다. 실제 모델 Gate는 여전히 미완료다.

## L3 확장

[L3 안내](../L3.md)에서 별도 Linux CPU 환경 설치와 고정 모델 다운로드·캐시 실행을 따라간다. retrieval 패키지는 실제 E5 Embedding과 SQLite Exact 검색을 수행한다. BM25/Dense/Hybrid와 권한·현행 필터, 실제 임시 갱신/삭제·오래된 선택 거부를 검사했다. 선택 FAISS 비교는 별도 합성 벡터다.

실제 답변 생성이나 새 웹 API는 추가하지 않았다. requirements-retrieval-tested.txt는 이번 ML 추가 환경 전체 스냅샷이며 플랫폼 공통 Lock이 아니다. 기존 L0의 requirements-tested.txt와 과거 보고서는 보존한다. 모델 파일·SQLite 실행 파일은 Git에 넣지 않으며 새 출력 폴더로 재현한다.
