# U04 Provider 기능과 공유 예산 검증 결과

**U04 자료와 별도 Router·HF 계약 어댑터·로컬 HTTP 실습을 작성했다. 전체 자료 작성은 52/70개다.** 실제 모델 품질·독립 수업 검증과 L9 전체 완료를 뜻하지 않는다.

[강의](../../lessons/document-ai/provider.md) 다음 이 결과를 읽으면 된다. 실행 담당자는 [L9 안내](../../practice/document-assistant/L9.md)를 추가로 본다.

| 실제 로컬 HTTP 사례 | 최종 판정 | HTTP 요청 수 | 예약량 |
|---|---|---:|---:|
| primary 503 → backup 200 | completed | 2 | 42 |
| Vision 요청, 후보는 text만 지원 | all_unavailable | 0 | 0 |
| 호출 상한 1, primary 503 | budget_exhausted | 1 | 21 |
| 예약 상한 41, primary 503 | budget_exhausted | 1 | 21 |

전체 실제 loopback HTTP 요청은 4회다. 인식 데이터·모델·외부 유료 API 호출은 하지 않았다. 입력 ‘정책 확인’은 Unicode 코드 포인트 5개를 가짜 Token 수로 세고 최대 출력 16을 더해 시도당 21을 예약했다. **실제 Tokenizer·청구 사용량 실측이 아니다.** 실패한 호출도 사용량을 몰라 예약을 환급하지 않았다.

새 Router 검사 32개와 기존 Registry 25개·보고서 20개, 합계 **77개가 통과**했다. Capability·전송 범위·준비 상태/관찰 유효 기간·Context·공유 호출/예약 예산·일시/중대 오류·잘못된 응답·출력 길이 한도 도달·가상 시계의 늦은 응답·취소·Trace 노출 경계와 HF 어댑터의 프로필/사용량 계약을 포함한다. 이전 웹 API·L8 OCR·ML 전체 검사 재실행은 아니다.

기존 AIProvider 계약은 문자열 입력/출력뿐임을 확인했다. 기존 Ollama/OpenAI/HF 코드와 웹 Factory는 변경하지 않고, 별도 Endpoint 계약과 명시적인 HF 어댑터를 추가했다. HF의 Chat Template·입력 수·고정 출력 상한·사용량 관찰을 연결하는 코드는 가짜 Tokenizer/Provider로 검사했다. 실제 Qwen 가중치나 모델 답변은 이번에 재실행하지 않았다.

Readiness는 어댑터의 관찰을 믿는 계약이다. HTTP 시연은 직접 시작한 고정 서버, HF 경로는 전달받은 프로필 검사를 사용했다. 구성값만으로 모든 모델/기능의 현재 준비 상태를 검증했다고 부르지 않는다. 실제 모델/서비스 Probe와 장애 분류는 후속 통합 대상이다.

시간·취소는 동기 호출 전후 검사다. 늦은 결과는 버리고 대체 호출도 막지만 실행 중 계산을 강제로 중단하지 않는다. 가상 시계 검사로 경계를 확인했으며 실제 강제 종료를 실행한 결과가 아니다. 같은 후보 반복 재시도·회로 차단기·금액 예산·실제 외부 경로·Streaming·웹 Factory 연결·독립 의미/수업 검증은 미완료다. 기존 RAG/Agent/LoRA 품질·QLoRA 게이트도 유지한다.

다음은 **U05 React와 Streaming 통합**이다. **추천 추론 강도 High**. 분할 이벤트·오류·취소·최종 판정이 Backend와 화면에서 일치하는지 확인해야 한다. U06 다중 형식/최종 평가와 기초/안내 16개도 남아 있다.

<details>
<summary>재현 담당자용 기록</summary>

- [observed.json](observed.json): 네 실제 HTTP 사례의 상태·예약·시도별 Trace·요청 수.
- [tests.json](tests.json): 새 검사 32개와 기존 회귀 45개 결과.
- [validation.json](validation.json): 환경·코드 해시·실행과 미완료 구분.
- [run.json](run.json): 기준 커밋·게시 상태.

</details>
