# U05 React와 SSE 통합 검증 결과

**U05 자료와 실행 가능한 React 화면·공통 Parser·로컬 SSE 서버를 작성했다. 전체 자료 작성은 53/70개다.** 실제 모델 Token Streaming이나 L9 전체 완료를 뜻하지 않는다.

[강의](../../lessons/document-ai/streaming.md) 다음 이 결과를 읽으면 된다. 실행 담당자는 [React 화면 안내](../../practice/document-assistant/stream-ui/README.md)를 본다.

| 실제 실행 | 결과 | 해석 범위 |
|---|---|---|
| React 화면 → Python 서버 → U04 Router → SSE → 공통 Parser → 화면 | 고정 문장의 실제 HTTP 전송과 최종 판정 연결 | Router가 만든 완성된 고정 답변을 나눠 전송. 모델 Token 생성 스트림 아님 |
| 정상 전송 | 7일 문장을 누적한 뒤 전송 완료 | 의미/근거 승인 아님 |
| 오류·중간 끊김·기능 미지원·시간 한도 | 완료되지 않음·한국어 이유·부분 응답 경고 | 오류 뒤 자동 재호출 없음 |
| 취소 | 수신 중단·접수 안내·서버 전송 루프 cancelled 확인 | 실제 모델 계산 강제 중단 아님 |
| 취소 직후 새 실행 | 늦은 이전 취소 확인이 새 완료 상태를 덮어쓰지 않음 | 취소 확인 지연을 의도적으로 주입한 경합 검사 |
| HTML처럼 생긴 문자열 | React 텍스트로 표시, img 요소 생성 없음 | 브라우저 응답 가로채기 Fixture. 전체 XSS 감사 아님 |
| 데스크톱·모바일 크기 | 1120×900·390×844 화면 확인, 390px 가로 넘침 없음 | 실제 폰·다른 브라우저 검증 아님 |

자동 검사는 **Node 34개 + Python 88개 = 122개 통과**했다. Python은 새 HTTP/SSE 11개와 기존 Router/Registry/보고서 회귀 77개다. 별도로 **실제 Chromium 브라우저 시나리오 9개**를 통과했고 페이지 JavaScript 오류는 0개였다. 브라우저에서 실제 서버 실행은 9회였으며 HTML 문자열 사례는 브라우저 가로채기 응답이었다. 과거 FastAPI 웹·L8 OCR·ML 전체 검사는 재실행하지 않았다.

Parser는 모든 2분할 바이트 위치와 1바이트 조각으로 한글/이모지를 검사했다. 실제 HTTP 서버도 한글 바이트 중간에서 나누어 쓰지만 TCP가 다시 합칠 수 있으므로 실제 브라우저가 모든 분할 위치를 관측했다는 뜻은 아니다. EOF 전에 최종 판정이 없거나 마지막 프레임이 잘리면 완료로 처리하지 않는다. 첫 유효 final 뒤에는 수신을 닫고 늦은 데이터가 결과를 바꾸지 못하게 한다.

브라우저 준비 중 기본 Playwright 브라우저 다운로드가 잘린 ZIP으로 실패해 공식 Chrome for Testing 배포를 사용했다. 검사는 Playwright 1.62.1·Chrome Headless Shell 156.0.8078.80에서 수행했다. 첫 경합 검사 도구는 지연된 Route를 너무 일찍 해제해 실패했고, 해당 Handler 완료를 기다리도록 검사 코드를 수정한 뒤 전체 브라우저 검사를 통과했다. 최종 UI 문구를 한국어로 보완한 빌드도 다시 검사했다.

기존 FastAPI API·Factory·Provider·데이터는 변경하지 않았다. 실행용 React 프로젝트가 없어서 academy 원문을 보존하며 별도 stream-ui를 추가했다. 실제 모델 Streaming·인증/권한·모델 강제 중단·재연결/작업 재개·Proxy/운영 배포·부하·독립 수업·전체 접근성 검증은 미완료다. 기존 RAG/Agent/LoRA 의미 품질 및 QLoRA 게이트도 유지한다.

다음은 **U06 다중 형식 확장과 최종 평가**다. **추천 추론 강도 High**. 지원 형식별 원본·구조·실패·근거·출력·비용의 연결을 비교하고 남은 미통과 항목을 보존해야 한다. 이후 기초/안내 16개 단원과 품질·수업 검증이 남아 있다.

<details>
<summary>재현 담당자용 기록</summary>

- [node-tests.json](node-tests.json): 공통 Parser/상태/수신 34개 검사.
- [python-tests.json](python-tests.json): HTTP/SSE 11개와 기존 회귀 77개.
- [browser.json](browser.json): 브라우저 9개 사례·실제 서버 상태·버전·페이지 오류.
- [validation.json](validation.json): 환경·소스/빌드 해시·화면 확인과 미완료.
- [run.json](run.json): 기준 커밋·게시 상태.

</details>
