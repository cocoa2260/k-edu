# 문서 답변 누적 실습 — Backend L0~L6

Day3 7~8교시의 코드와 CORS에서 출발해 L1 입력 준비, L2 Harness, L3 실제 Embedding·검색·Index를 같은 프로젝트에 추가했다. 기존 대화 API는 유지하고 L4 CLI에서 실제 검색·로컬 생성·출력 검사를 연결했다. 답변 품질은 채택 보류다. 처음 시작하는 학생은 [L0 본문](../../../lessons/baseline/lesson.md)을 읽는다.

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

## L4 확장

[L4 안내](../L4.md)는 같은 L3 CPU 환경에서 Qwen3-0.6B 가중치를 추가해 실제 RAG를 실행한다. 기존 웹 API Factory는 자동 전환하지 않으며 HFCpuProvider는 CLI에서 명시적으로 주입한다. 공통 Harness에 입력 준비·출력 계약·검사기를 주입하는 선택 인자를 추가했고 기존 L2 동작은 유지한다.

구조·Source ID·부분 인용 검사는 의미적 근거 검증이 아니다. 실제 두 지시 버전 모두 서비스 채택을 보류했다. 사례별 결과는 [읽기용 검토본](../../../reports/KEDU-PRODUCTION-006/REVIEW.md)에 있다.

## L5 확장

[L5 안내](../L5.md)에서 별도 CPU 환경·LangChain Core 1.7.3과 같은 모델 캐시를 사용한다. 실제 모델 행동과 Registry의 이름/인수/권한·발견한 출처·종료 상한을 연결했다. StructuredTool 연결은 도구 API만 확인했으며 Framework Agent/MCP 실행은 아니다.

HFCpuProvider의 신규 출력 상한을 선택 인자로 추가했다. 기본 512 Token은 유지하고 L5만 192 Token으로 실행한다. requirements-agent-tested.txt는 이 환경의 전체 스냅샷이며 기존 L3/L4 환경 파일은 보존한다. 실제 모델 과제 완료·답변 품질은 미통과다.

현재 L5 모델 입력은 app/agent.py의 planner_prompt 함수가 구성한다. 같은 파일의 INSTRUCTIONS 상수는 준비 실행에서 사용한 과거 지시이며 현재 경로에서 사용하지 않는다.

## L6 확장

[L6 안내](../L6.md)에서 L5 CPU 환경/캐시를 재사용한다. multi_agent.py는 세 역할의 계약과 현재 원문·수신 범위 Handoff를 검사하며 전역 모델 8회·도구 6회·보완/일시 재시도 각 1회·240초 전후 검사 한도를 유지한다. 역할별 4/2/3회는 전체 8회 안에 포함한다.

tools.multi_lab는 같은 18개를 체크포인트로 저장한다. role-probes 옵션은 Runtime이 실제 E5로 근거를 준비한 별도 역할 호출이며 통합 성공이 아니다. tools.multi_fixture_lab의 Control/M01~M04는 고정 응답 검사다. 기존 웹 API를 새 Runtime에 연결하지 않았고 새 의존성도 추가하지 않았다. 의미적 품질은 미통과다.

응답 전체의 단일 JSON 코드 블록만 transport 포장으로 제거한다. Markdown 안의 Python을 실행하거나 앞뒤 문장에서 JSON을 추출하지 않는다. 모델 원응답은 observed.json의 생성 관찰에 보존한다.
