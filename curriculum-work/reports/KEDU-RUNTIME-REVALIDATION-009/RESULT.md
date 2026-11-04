# K-Edu 009 · 실제 모델 스트리밍과 중단·승인 경계

2026년 11월 4일 · `KEDU-RUNTIME-REVALIDATION-009`

**별도 로컬 경로에서 실제 Qwen의 생성 중 SSE 전송과 두 가지 중단 방식을 확인했다.** 기존 React 화면의 실제 모델 연결과 서비스 인증·권한은 미완료다.

## 실제 모델 응답과 중단

앞선 L9 실습은 고정 문장을 먼저 완성한 뒤 조각으로 나누어 전송한다. 이번에는 고정 리비전 Qwen3-0.6B를 Linux CPU의 전용 자식 프로세스에서 실행했다. 생성 중 디코딩한 텍스트 조각을 SSE로 전송하고, 클라이언트가 첫 조각을 받은 시각을 모델의 생성 종료 시각과 같은 단조 시계로 대조했다. SSE 조각 개수와 생성 토큰 개수는 별도로 기록했다.

| 시험 | 실제 결과 | 최종 상태 |
|---|---|---|
| 정상 스트리밍 | 모델이 생성을 마치기 전에 클라이언트가 첫 조각을 받았다. 수신 조각을 합친 문자열과 모델 최종 디코딩이 일치했다. | 완료 · 최종 답변 있음 |
| 사용자 취소 | 첫 조각을 받은 직후 별도 HTTP 연결로 취소했다. 모델이 토큰 경계에서 중단 신호를 확인했고 자식 프로세스는 종료 코드 0으로 끝났다. | 취소 · 최종 답변 없음 |
| 강제 중단 | 첫 조각을 받은 직후 실행 중인 전용 프로세스에 SIGKILL을 보냈다. 종료 코드 -9를 확인하고 부모 프로세스가 회수했다. | 실패 · 최종 답변 없음 |

정상 실행은 38토큰을 생성했고 클라이언트는 텍스트 조각 12개를 받았다. 모델 로딩을 포함해 요청 후 10.09초에 첫 조각이 도착했고, 그 뒤 6.40초 후에 생성이 끝났다. 취소 요청에서 생성 종료까지 177ms, 강제 중단 요청에서 자식 프로세스 회수까지 77ms였다. 각 수치는 이 환경의 한 번 측정값이다.

중단 요청 뒤 새로 생성된 조각이 클라이언트로 전달되지 않았고, 최종 응답 뒤 다시 보낸 중단 요청은 승인되지 않았다. 강제 중단의 증거는 **이번 Linux 전용 워커 한 개**에 적용된다. 다른 런타임, 외부 모델 서버 또는 자손 프로세스 트리 전체의 종료는 별도 검증 대상이다.

## 기존 React·API와의 연결 범위

기존 화면의 JavaScript 수신기는 고정 응답 시작 이벤트(`fixture=true`)를 처리하고 실제 모델을 표시하는 이벤트(`fixture=false`)는 `invalid_start`로 거부했다. 실제 모델의 HTTP 검증은 별도 실험 경로에서 했으며 기존 React 화면, FastAPI `/ai/chat`, Provider Router를 연결하거나 수정하지 않았다. 숫자 생성은 전송과 중단을 확인하기 위한 입력이다.

## 인증과 승인

| 경계 | 실행한 검사와 확인 결과 |
|---|---|
| 로컬 HTTP 실습 | 다른 Origin으로 취소하면 403이었다. Origin과 인증 정보가 없는 별도 HTTP 연결은 실행 목록을 조회하고 다른 연결이 시작한 실행을 취소할 수 있었다. 실행 ID에 접근할 수 있는 주체를 서버가 구분하는 검사는 구현되지 않았다. |
| Agent의 메모 저장 승인 | 모델이 `approved=true`를 넘기면 인자 검사에서 거절됐다. 승인 없는 호출, 인자나 실행 ID가 다른 호출, 같은 Registry 내 두 번째 사용은 거절됐다. 같은 승인 정보와 실행 ID를 새 Registry 인스턴스에 다시 주면 재사용이 가능했다. 소비 기록의 범위는 기존 인스턴스 메모리였다. |
| 보고서 검토 승인 | 미승인 상태는 거절했다. 승인 기록은 SQLite를 닫고 다시 열어도 남았다. 승인 후 주장을 바꾸거나 원본을 제한 상태로 만들면 거절했다. 로컬 호출자가 넣은 검토자 문자열을 저장하는 시연 경로였다. |

다중 사용자 환경의 실행 조회·취소에는 실행별 권한 검사가 필요하다. [OWASP API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/)

## 검사와 재현

기존 Python 자동 검사 118개와 하위 검사 35개, Node 검사 34개 및 React 빌드가 통과했다. 별도 실제 모델 시험 3건, 기존 HTTP·Agent·보고서 경계는 [실행 기록](observations-summary.json)에 정리했다.

기준 커밋은 `c79eac7f39c925d40da822e50d4db89362f85690`이다. Linux CPU에서 기존 [Qwen 모델 파일 명세](../KEDU-RUNTIME-REVALIDATION-003/model-files.json)의 해시가 일치하는 로컬 스냅샷을 사용했다. 모델은 PyTorch 2.15.0+cpu 및 Transformers 4.57.1로 실행했다. 아래 명령은 `curriculum-work/practice/document-assistant/backend`에서 실행한다.

```sh
report=../../../reports/KEDU-RUNTIME-REVALIDATION-009
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONPATH="$PWD" python "$report/stream_probe.py" \
  --snapshot "$run/model" --manifest "$report/../KEDU-RUNTIME-REVALIDATION-003/model-files.json" --output "$run/stream.json"
PYTHONPATH="$PWD" python "$report/boundary_probe.py" --ui ../stream-ui/dist --output "$run/boundaries.json"
python -m pytest -q -rs stream_tests router_tests registry_tests report_tests tests/test_agent.py
(cd ../stream-ui && npm ci && npm test && npm run build)
```

## 다음 작업

**010 · 권장 추론 강도 High.** 지금까지의 실습별 실행 증거와 미해결 품질·운영 항목을 묶어 수업에서 사용할 범위를 구분하고, 독립 강사와 교육생의 대표 검증에 필요한 교안·장비·판정 기준을 정리한다. 서비스 배포와 수업 채택은 보류다.
