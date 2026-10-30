# L0 기준 앱·환경·입출력 계약 검증 결과

2026-10-31 · KEDU-PRODUCTION-002 · **기준 Backend·계약 검증 완료 / 실제 모델·UI 미검증**

학생이 읽을 자료는 **[L0 강의 본문](../../lessons/baseline/lesson.md)**이다. 실행 파일은 [문서 답변 누적 실습](../../practice/document-assistant/README.md)에 있다. 이후 Prompt·Context·Harness 실습은 이 앱을 이어서 확장한다.

## 확인한 원본과 이번에 만든 것

Day3 7~8교시의 앱은 완성된 실행 폴더가 아니라 Markdown의 파일별 코드와 추가 수정 지시로 존재했다. 두 원문에서 11개 실행 코드 블록을 꺼내 실제 Backend 폴더로 만들었다. 원문 파일은 수정하지 않았다.

| 항목 | 처리 |
|---|---|
| Provider·Service·Schema·Route | Day3 7교시 원문 코드 추출 |
| CORS | Day3 8교시 추가 블록을 같은 앱에 적용 |
| 앱 시작 | Import 때 Provider를 만들던 방식을 Uvicorn --factory 명시 실행으로 변경 |
| 테스트 설정 | 수집 단계에서 환경 변수를 바꾸는 코드를 제거하고 테스트마다 격리 |
| 오류·입력 경계 | 정상·무효 입력·선택 설정·응답 형식·CORS·비공개 오류·Import 경계 검사 추가 |
| 환경 프록시 | HTTP 클라이언트에 SOCKS 지원 추가. 기존 프록시·TLS 검증 유지 |

파일별 원문 행·원문 Blob SHA·추출/현재 코드 해시는 [연결표](../../practice/document-assistant/baseline-source-map.json)에 있다. 기준은 기존 원본 커밋 bc58756866cd6bdee20c102fb54340f21e65ad56이다.

## 고정한 HTTP 계약

| 구분 | 기준 |
|---|---|
| Endpoint | POST /ai/chat |
| Request | message 문자열, 1~2000문자. 공백 거부·수락 값 앞뒤 공백 제거 |
| Response | provider·model·answer 문자열 |
| 잘못된 입력 | 422, Provider 호출 전 중단 |
| 연결·시간 초과 | 각각 503·504 |
| 원격/응답 형식 오류 | 502 |
| Provider 선택 | 서버 설정·앱 생성 때 선택. 자동 대체 없음 |
| 추가 요청 필드 | 원문의 Pydantic 기본 동작으로 무시. Client가 Provider를 변경할 수 없음 |
| health | 설정 확인이며 생성 호출 아님 |

Streaming·대화 기록·Tool·인증은 아직 없다. CORS는 인증 기능이 아니며, 허용하지 않은 Origin의 실제 POST도 서버에서 처리될 수 있음을 검사했다. 후속 인증을 구현했다고 주장하지 않는다.

## 실제 검증 결과

- **계약 테스트 30개 통과.** 원문 기반 10개와 경계 검사 20개를 실행했다. Pytest 중 실제 외부 HTTP 전송은 차단했다.
- **실제 로컬 HTTP 서버 왕복 통과.** Uvicorn으로 계약 데모를 켜서 health, 정상 POST 200, 공백 POST 422, CORS Preflight 200, 실제 OpenAPI 응답을 확인했다.
- 위 HTTP 데모는 provider=contract-demo / model=no-model-executed의 고정 규칙 응답이다. 생성 모델·RAG·Agent 실행 성공이 아니다.
- 의존성 검사에 충돌이 없었고 Linux x86_64 / Python 3.12.14의 전체 설치 버전을 저장했다.
- 로컬 Ollama의 /api/tags를 실제 점검했으나 연결 실패였고 모델 설정도 없었다. OpenAI Key도 미설정이며 유료 API를 호출하지 않았다. 따라서 **G-MODEL은 미완료**다.
- React 화면은 생성/실행/브라우저 검증하지 않았다. CORS/API 검사를 UI 검증으로 대신하지 않는다. L0에서 CLI 경로를 사용할 수 있도록 G-UI는 진단 상태로 유지한다.

## 고정한 검증 환경

FastAPI 0.162.0 / Pydantic 2.14.2 / HTTPX 0.28.1(SOCKS 지원 포함) / Uvicorn 0.54.0 / OpenAI SDK 3.41.0 / python-dotenv 1.2.4 / pytest 9.2.0을 설치해 검사했다. [직접 버전](../../practice/document-assistant/backend/requirements.txt)과 [전체 버전 스냅샷](../../practice/document-assistant/backend/requirements-tested.txt)을 구분해 보관했다.

이번 앱의 격리 검증 환경이며 기존 FastAPI 강의 전체의 버전 설명을 일괄 수정하거나 교육장 호환성을 확정한 것은 아니다. OpenAI/Ollama/FastAPI 공식 웹 문서 조회는 이번 세션에서 도구 오류로 실패했다. 원문의 호출 형식을 유지했고 설치된 SDK의 Responses.create가 model/input 인자를 제공하는 점과 대체 클라이언트 계약을 확인했다. 실제 API 이용 가능성·모델 지원·실제 응답은 검증하지 않았다.

## 다음 작업

**다음은 K2-04/K2-05와 L1의 Prompt·Context 학습자료·공통 규정/질문·평가 기준 제작이다. 추천 추론 강도: High.** 같은 앱과 /ai/chat 기준 계약을 재사용하고, 실습용 대조 실험은 별도 계약으로 추가한다. 그다음 K2-06/L2에서 Harness·상한·실패 검증을 연결한다.

현재 새 70개 학습 단위 중 작성한 강의는 기존 Hugging Face 3개다. 이번 L0 연결 안내와 원문 코드의 실행 폴더화를 새 단원으로 중복 집계하지 않았다. 학습자 선수지식·교육장 실습·시수 검증은 남아 있다.

<details>
<summary>실행 담당자용 증거</summary>

- [validation.json](validation.json): 기준·검사·실제 Provider 미확인
- [tests.json](tests.json): 실제 Pytest 30개 결과
- [http-smoke.json](http-smoke.json): 로컬 서버 실제 HTTP 요청·결과
- [openapi.json](openapi.json): 해당 서버가 실제 반환한 API 문서
- [provider-readiness.json](provider-readiness.json): 모델 목록 점검 결과. 생성 요청은 하지 않음
- [dependency-check.json](dependency-check.json): 실제 의존성 충돌 검사
- [run.json](run.json): 기준 커밋·범위·게시·미공개 사용량

모델 내부 토큰·총 Tool 호출 수는 미공개이므로 임의 숫자로 채우지 않는다. 의미 검토는 같은 작업 세션이며 독립 평가자·자동 Runner·추론 강도 자동 변경을 구현했다고 표시하지 않는다.

</details>
