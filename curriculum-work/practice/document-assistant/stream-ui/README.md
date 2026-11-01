# React와 SSE 실행 실습

[강의](../../../lessons/document-ai/streaming.md) → [결과](../../../reports/KEDU-PRODUCTION-016/RESULT.md)를 읽는다. 이 폴더는 새 React 실행 프로젝트이며 academy의 강의 원문을 변경하지 않았다.

| 순서 | 실행 담당자의 작업 |
|---|---|
| 1 | Node와 npm을 준비하고 이 폴더에서 npm ci로 package-lock.json의 의존성을 설치 |
| 2 | npm test로 공통 Parser/상태/수신 검사를 실행하고 npm run build로 dist 생성 |
| 3 | Backend 폴더에서 tools.stream_lab 모듈에 ui 인자로 ../stream-ui/dist, port 인자로 8765 지정 |
| 4 | 브라우저에서 http://127.0.0.1:8765 열고 여섯 상황을 차례로 실행 |
| 5 | 부분 문장·최종 판정·취소 접수·재실행 결과를 비교 |

정확한 서버 CLI는 [stream_lab.py](../backend/tools/stream_lab.py) 첫 설명에 있다. 서버는 127.0.0.1에만 바인딩하고 같은 Origin에서 제공하는 UI를 사용한다. 별도 CORS 배포나 기존 FastAPI API 통합은 아니다. 실행 화면의 URI는 로컬 서버가 실행 중일 때만 열린다.

시험한 앱 빌드 버전은 React/React DOM 19.2.0, esbuild 0.25.10이다. 최신 버전 추천이나 다른 장비 전체의 호환성을 뜻하지 않는다. dist/node_modules는 저장소에 넣지 않고 lock 파일과 소스를 보존한다. 런타임에 CDN React를 불러오지 않는다.

| 파일 | 역할 |
|---|---|
| src/stream.mjs | UTF-8/SSE 프레이밍·실행 ID/번호·상태·소비 함수. Node와 브라우저 공통 |
| src/App.jsx·style.css | React 화면·실행 세대·취소·부분/확정 답변 표시 |
| tests/stream.test.mjs | 공통 처리 34개 검사 |
| tests/browser-check.mjs | 실제 Chromium UI/상태 경합·모바일 크기 검사 |
| ../backend/tools/stream_lab.py | 별도 로컬 HTTP/SSE 고정 응답 서버·U04 Router 연결 |
| ../backend/stream_tests | Python HTTP 계약·취소 등 11개 검사 |

브라우저 자동 확인은 추가로 Playwright가 필요하다. 이번 환경의 Playwright는 1.62.1, 실제 실행한 Chrome Headless Shell은 156.0.8078.80이었다. 브라우저 실행 파일은 Git에 넣지 않는다. 환경의 번들 브라우저 다운로드가 잘린 ZIP으로 실패해 공식 Chrome for Testing 배포의 실행 파일을 사용했다.

재현 담당자는 PLAYWRIGHT_MODULE에 설치한 Playwright 모듈 경로를, 필요하면 BROWSER_EXECUTABLE에 실행 파일 경로를 지정한다. Backend의 [stream_browser_lab.py](../backend/tools/stream_browser_lab.py)에 ui 폴더와 새 output 폴더를 지정하면 서버와 브라우저 검사를 같은 실행 트리에서 시작하고 종료한다. 테스트의 두 사례는 의도적으로 취소 접수 응답을 지연하거나 HTML처럼 생긴 문자열을 가로채서 보낸다. 실제 모델/API 결과가 아니다.

Backend의 stream_tests/router_tests/registry_tests/report_tests는 표준 unittest discover로 각각 실행한다. Python HTTP 서버/Router 자체는 새 패키지가 필요 없지만 기존 Registry/보고서 회귀에는 이전 PDF/DOCX 의존성이 필요하다. 브라우저 검사는 빌드를 먼저 완료한 뒤 시작한다.

서버는 완성된 고정 답변을 나눠 보낸다. 모델 Token Streaming·모델 강제 중단·인증·자동 재시도/재개·실제 운영 배포는 미검증이다. 기본 검증에는 네트워크 모델 호출이나 유료 API가 필요하지 않다.
