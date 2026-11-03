# Backend 환경·API/Provider 계약 재검증

2026-11-04 · **계약/입력 준비 70개와 실제 loopback HTTP 8개 통과. 실제 모델 생성은 미실행.**

새 Linux Python 3.12.14 가상환경에 기존 requirements-dev.txt를 설치했다. FastAPI 0.162.0, Pydantic 2.14.2, HTTPX 0.28.1, Uvicorn 0.54.0, OpenAI 3.41.0, python-dotenv 1.2.4, pytest 9.2.0을 사용했다. pip check는 충돌 없이 통과했다. 전체 설치 버전은 [versions.json](versions.json)에 보존하며 다른 OS용 Lock으로 간주하지 않는다.

## 확인한 동작

- [기존 검사 70개](contracts-complete-source.json): Provider 인터페이스, 입력 검증, 오류의 HTTP 매핑, Factory 선택, Ollama/OpenAI 어댑터의 고정 응답 계약, CORS, 입력 준비와 기존 대화 Schema 보존. 실제 외부 모델 HTTP는 검사 fixture에서 차단했다.
- [실제 HTTP 8개](http-loopback.json): Uvicorn 고정 데모 서버를 loopback에 띄워 health, 앞뒤 공백 제거, 공백 거부, 2000문자 수락/2001문자 거부, 추가 요청 필드로 Provider 변경 불가, 허용/미허용 Origin preflight를 확인했다. 종료 후 서버를 정리했다. CORS는 인증 검증이 아니다.
- [실제 준비 상태](readiness.json): localhost:11434 연결 실패, Ollama 모델 설정 없음, OpenAI 키 설정 없음. 확인 도구의 종료 코드 0은 준비 상태 기록 성공이며 실제 생성 성공이 아니다. G_MODEL_PENDING을 유지한다. 키 값이나 비밀 파일은 읽거나 게시하지 않았다.

처음 검사에서는 69개 통과/1개 실패였다. 로컬 부분 체크아웃에 과거 OpenAPI 증거 파일이 없어 발생했다. GitHub 기준 커밋의 해당 파일을 해시 확인 후 복원하자 70개가 통과했다. [최초 실패](contracts.json)도 보존한다. 코드 결함으로 보고 테스트를 삭제하거나 기대값을 바꾸지 않았다. 별도로 초기에 가상환경 실행기의 상대 경로를 다른 작업 폴더에서 사용해 명령이 시작되지 않은 시도가 있었으며, 이후 절대 경로로 위 기록을 확보했다.

## 보존과 한계

기존 앱·Provider·실습 데이터·요구 버전·검사·과거 증거는 수정하지 않았다. 70개 단원과 milestones/기존 품질 게이트도 유지했다. 이번 검사는 tests/test_provider.py와 tests/test_l1.py 범위이며 전체 Backend·RAG/Agent/훈련 검사 전부를 실행한 것은 아니다. 어댑터의 고정 응답 성공을 실제 Ollama/OpenAI 생성으로 해석하지 않는다. 교육생 장비·독립 수업·운영 배포도 미검증이다.

## 다음 작업

**실제 생성 Provider를 로컬 CPU로 준비할 실행 경로를 확인하고, 기준 질문의 실제 생성부터 검증한다. 추천 추론 강도 High.** 현재 기준 API의 Ollama/OpenAI 경로와 기존 Hugging Face CPU 실험은 별개이므로, 유료 API 없이 사용할 경로의 설치·모델 파일·자원·API 연결을 대조해야 한다. 사용자의 PC에 이미 설치된 Ollama가 이 실행 환경에도 존재한다고 가정하지 않는다. 고정 응답으로 생성 성공을 대체하지 않는다. 준비 실패 시 구체적 원인과 가능한 실행 범위를 기록한다.

[검증 기록](validation.json) · [전체 검증 순서](../KEDU-TEACHING-INTEGRATION-001/RESULT.md)
