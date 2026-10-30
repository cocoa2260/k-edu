# 문서 답변 누적 실습 — L0 Backend

현재는 문서 검색을 추가하기 전의 문자열 대화 앱이다. Day3 7~8교시의 코드와 CORS를 실제 파일로 옮겼으며, 이후 L1~L9가 같은 앱을 확장한다. 학생은 [L0 본문](../../../lessons/baseline/lesson.md)에서 시작한다.

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
