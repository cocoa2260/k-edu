# 문서 답변 누적 실습 — Backend L0~L7 준비

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

학생은 안내의 `python -m tools.prompt_inputs`로 지시·예시 수·자료 수·문자 수를 먼저 읽을 수 있다. `--variant instruction` 등으로 실제 전체 입력도 표시한다. 기존 준비 함수를 재사용하는 읽기 도구이며 모델·API·Token 계산을 실행하지 않는다. 지시에 한 문장을 추가하고 자료·질문 유지 여부를 확인하는 활동은 같은 안내에 있다. 전체 준비 도구와 기존 API/자료는 유지한다.

[Context 활동](../CONTEXT.md)은 `python -m tools.context_steps`로 자료 선택을 읽는다. `--part order`, `--part budget`, `--part handoff`로 각각 순서·기존 관찰 예산 계산·일회성 현재 전달 자료를 확인한다. 기존 입력/자료/API는 보존하며 실제 검색·지속 Memory·새 Tokenizer 실행이나 모델 생성을 구현한 도구가 아니다.

## L2 확장

[L2 안내](../L2.md)의 고정 응답 실험은 같은 Provider 인터페이스에 Harness를 붙인다. 실제 모델 선택 옵션이나 새 API는 추가하지 않았다. 입력 준비·출력 구조/인용 ID 검사·공통 호출 상한·Trace·회귀 비교를 실행한다. 입력할 명령은 `python -m tools.harness_demo --output l2-observed.json`이며 기존 파일은 덮어쓰지 않는다.

`python -m tools.harness_steps`는 작성한 식비 답안을 고정 반환해 요청 하나의 전체 흐름을 보여준다. 기존 기록을 읽을 때는 `--input l2-observed.json --scenario repair_then_success`, 전체 고정 출력 비교는 `--input l2-observed.json --compare`를 사용한다. `--boundaries`는 별도로 가짜 시계·취소 신호를 주입한다. 원래 Harness/데모/데이터/API는 보존하며 실제 모델·인증·강제 중단을 구현한 도구가 아니다.

총 Provider 시도 3회·재시도 1회·보완 1회는 실행 전체의 상한이다. 90초는 호출 전후 검사이며 요청을 진행 중에 끊지 않는다. 구조 통과는 사실성·승인·Token 예산 검증이 아니다. 실제 모델 Gate는 여전히 미완료다.

## L3 확장

[L3 안내](../L3.md)에서 별도 Linux CPU 환경 설치와 고정 모델 다운로드·캐시 실행을 따라간다. retrieval 패키지는 실제 E5 Embedding과 SQLite Exact 검색을 수행한다. BM25/Dense/Hybrid와 권한·현행 필터, 실제 임시 갱신/삭제·오래된 선택 거부를 검사했다. 선택 FAISS 비교는 별도 합성 벡터다.

실제 답변 생성이나 새 웹 API는 추가하지 않았다. requirements-retrieval-tested.txt는 이번 ML 추가 환경 전체 스냅샷이며 플랫폼 공통 Lock이 아니다. 기존 L0의 requirements-tested.txt와 과거 보고서는 보존한다. 모델 파일·SQLite 실행 파일은 Git에 넣지 않으며 새 출력 폴더로 재현한다.

Embedding 수업의 계산·현재 분절·저장된 실제 검색 기록 읽기는 `python -m tools.embedding_steps --math`, `--lexical`, `--record <observed.json>`으로 진행한다. 이 도구는 모델을 실행하지 않는다. [학습 흐름과 실제 모델 재실행](../L3.md#embedding-활동)을 구분해 따른다. Manifest는 현재 설정의 독립 복사본을 반환한다. 과거 기록의 128/512 표시값·해시 불일치는 원본을 보존한 채 교안과 이번 보고서에 설명했다. 새 회귀 검사는 `python -m unittest discover -s embedding_tests -v`이며 기존 Pytest/모델 전체 검증을 대신하지 않는다.

Index 수업은 `python -m tools.index_steps --toy`로 좌표/단순 탐색을 계산하고, `--lifecycle`로 고정 비의미 벡터를 넣은 실제 임시 SQLite 동작을 관찰한다. `--ann-record <json>`과 `--stored-record <json>`은 저장된 FAISS/E5 결과를 읽으며 모델을 새로 실행하지 않는다. 기본 출력은 요약이고 `--output <new.json>`은 전체 관찰을 새 파일에만 저장한다. [Index 활동](../L3.md#index-활동)에서 원문 추적·갱신/삭제·원본 재구축 후 복귀와 실제 실행 준비를 구분한다. 기존 Index와 인코더는 이번 수업 수정에서 변경하지 않았다.

## L4 확장

[L4 안내](../L4.md)는 같은 L3 CPU 환경에서 Qwen3-0.6B 가중치를 추가해 실제 RAG를 실행한다. 기존 웹 API Factory는 자동 전환하지 않으며 HFCpuProvider는 CLI에서 명시적으로 주입한다. 공통 Harness에 입력 준비·출력 계약·검사기를 주입하는 선택 인자를 추가했고 기존 L2 동작은 유지한다.

구조·Source ID·부분 인용 검사는 의미적 근거 검증이 아니다. 실제 두 지시 버전 모두 서비스 채택을 보류했다. 사례별 결과는 [읽기용 검토본](../../../reports/KEDU-PRODUCTION-006/REVIEW.md)에 있다.

RAG 수업의 `python -m tools.rag_steps --record <합본 observed.json> --case C01`은 저장된 실제 E5/Qwen 사례를 읽는다. `--compare prompt`, `--compare rewrite`, `--compare neighbors`는 각각 저장된 비교를, `--input`은 해시가 일치하는 Template 전 호출 문자열 재구성을 보여 준다. `--counterexample`만 현재 Pydantic 검사기에 교사가 만든 틀린 주장을 넣으며 모델을 실행하지 않는다. [L4 활동](../L4.md)은 합본 읽기와 새 rag_lab의 개별 사례 파일/모델 실행을 구분한다. 기존 검색·생성·검사 구현은 이번 교안 수정에서 변경하지 않았다.

## L5 확장

[L5 안내](../L5.md)에서 별도 CPU 환경·LangChain Core 1.7.3과 같은 모델 캐시를 사용한다. 실제 모델 행동과 Registry의 이름/인수/권한·발견한 출처·종료 상한을 연결했다. StructuredTool 연결은 도구 API만 확인했으며 Framework Agent/MCP 실행은 아니다.

HFCpuProvider의 신규 출력 상한을 선택 인자로 추가했다. 기본 512 Token은 유지하고 L5만 192 Token으로 실행한다. requirements-agent-tested.txt는 이 환경의 전체 스냅샷이며 기존 L3/L4 환경 파일은 보존한다. 실제 모델 과제 완료·답변 품질은 미통과다.

현재 L5 모델 입력은 app/agent.py의 planner_prompt 함수가 구성한다. 같은 파일의 INSTRUCTIONS 상수는 준비 실행에서 사용한 과거 지시이며 현재 경로에서 사용하지 않는다.

## L6 확장

[L6 안내](../L6.md)에서 L5 CPU 환경/캐시를 재사용한다. multi_agent.py는 세 역할의 계약과 현재 원문·수신 범위 Handoff를 검사하며 전역 모델 8회·도구 6회·보완/일시 재시도 각 1회·240초 전후 검사 한도를 유지한다. 역할별 4/2/3회는 전체 8회 안에 포함한다.

tools.multi_lab는 같은 18개를 체크포인트로 저장한다. role-probes 옵션은 Runtime이 실제 E5로 근거를 준비한 별도 역할 호출이며 통합 성공이 아니다. tools.multi_fixture_lab의 Control/M01~M04는 고정 응답 검사다. 기존 웹 API를 새 Runtime에 연결하지 않았고 새 의존성도 추가하지 않았다. 의미적 품질은 미통과다.

응답 전체의 단일 JSON 코드 블록만 transport 포장으로 제거한다. Markdown 안의 Python을 실행하거나 앞뒤 문장에서 JSON을 추출하지 않는다. 모델 원응답은 observed.json의 생성 관찰에 보존한다.

## L7 준비

[L7 안내](../L7.md)에서 별도 환경에 requirements-training-data.txt를 설치한다. Datasets 4.4.1과 기존 고정 Tokenizer를 사용하며 모델 가중치·PEFT 훈련 API는 호출하지 않는다. requirements-training-data-tested.txt는 실제 설치 스냅샷이다.

app/training_data.py는 원문 가족·검수 해시·Train 부모의 고정 바꿔쓰기, 한 턴 Qwen Template/Token 경계와 assistant 정답~EOS label을 검사한다. tools.training_data_lab는 로컬 JSONL·Datasets Features/filter/map·Arrow 저장/재로드·실제 Padding·가짜 Logit Mask 검사를 실행한다. 의미적 정답과 실제 Optimizer Step의 검증은 별개다. 원본/검수 파일은 data/finetuning-v1의 Card에서 읽는다.

엄격한 캐시 실행에는 프로세스 시작 전 HF_HUB_OFFLINE/HF_DATASETS_OFFLINE/HF_HUB_DISABLE_TELEMETRY를 지정한다. 로컬 JSON 사용 통계용 HEAD 시도와 차단 후 동일성은 제작 보고서에 보존했다. 기존 웹 API는 바꾸지 않았다.

## L7 실제 LoRA 소규모 훈련

requirements-lora.txt와 tools.lora_lab를 사용한다. CPU 일반 정밀도 조건별 4 Step·고정 Test 생성·Adapter 저장/별도 프로세스 재로드를 확인했다. 전체 데이터 학습·18개 회귀·QLoRA는 미완료다. [실제 결과](../../../reports/KEDU-PRODUCTION-010/RESULT.md)를 본다.

## L7 전체 Train 포함 학습과 회귀

tools.lora_full_lab는 같은 초기 Adapter와 조건별 28 Step을 사용하고 원본 20개/증강 28개 전체를 학습에 포함한다. Validation 선택을 고정한 뒤 Test와 기존 L5 18개 회귀를 세 조건에서 실행한다. 완료 기록은 사례별로 저장하며 코드/자료/환경이 다르면 재개를 거부한다. tools.lora_full_reload로 별도 프로세스 재로드를 확인한다. [실제 결과](../../../reports/KEDU-PRODUCTION-011/RESULT.md)를 본다.

## L8 문서 입력

[L8 안내](../L8.md)는 requirements-document.txt의 별도 CPU 환경에서 tools.document_assets와 tools.document_lab를 사용한다. 기존 data/document-v1에 저장한 PDF와 새 output 폴더를 지정한다. document_tests만 실행해 기존 FastAPI/Torch 의존 환경과 분리한다. 실제 PDF/OCR·BM25/물리 출처 연결을 검사하며 Encoder는 비의미적 상수 Fixture다. 기존 Index 코드·문서/Agent/훈련 데이터·모델·웹 API는 변경하지 않았다. [이번 결과](../../../reports/KEDU-PRODUCTION-012/RESULT.md)를 본다.

## L9 첫 묶음

[L9 안내](../L9.md)는 tools.registry_lab와 registry_tests의 표준 unittest를 사용한다. app/document_registry.py는 PDF/TXT의 원본 사본·IR·현재 버전·요청 키·상태·무효화를 별도 SQLite에서 검사한다. 문자열 포함 검색이며 기존 LocalIndex나 웹 API의 대체 구현이 아니다. DOCX/HWPX/HWP·보고서·Provider/SSE/React 연결은 미완료다.

## L9 보고서 출력

requirements-report.txt와 tools.report_lab를 사용한다. [강의](../../../lessons/document-ai/report.md)와 [결과](../../../reports/KEDU-PRODUCTION-014/RESULT.md)를 본다. 실제 DOCX/PDF·내용·렌더링을 확인했다. 고정 검토자 시연이며 기존 Registry/Provider/웹 API를 바꾸지 않았다.

## L9 Provider 제어

[U04 강의](../../../lessons/document-ai/provider.md)와 [결과](../../../reports/KEDU-PRODUCTION-015/RESULT.md)를 본다. tools.provider_lab는 표준 라이브러리 loopback HTTP 고정 서버, router_tests는 unittest를 사용한다. 기존 Provider/Factory/API를 변경하지 않았다. 기능/범위/준비 상태/Context/공유 예산/Trace와 동기 전후 시간·취소를 검사하며 실제 모델 품질·강제 중단 검증은 아니다.

## L9 Streaming 화면

[U05 강의](../../../lessons/document-ai/streaming.md)와 [결과](../../../reports/KEDU-PRODUCTION-016/RESULT.md)를 본다. ../stream-ui를 빌드한 뒤 tools.stream_lab에서 ui 디렉터리를 지정한다. Python 표준 HTTP 서버이며 기존 FastAPI 앱은 보존했다. stream_tests는 HTTP/SSE 계약, tools.stream_browser_lab는 같은 실행 트리의 실제 Chromium UI를 검사한다. 모델 생성 스트리밍이 아닌 고정 답변의 분할 전송이다.

## L9 다중 형식

[U06 강의](../../../lessons/document-ai/evaluation.md)와 [결과](../../../reports/KEDU-PRODUCTION-017/RESULT.md)를 본다. app/docx_ingest.py의 좁은 DOCX 입력을 Registry에 연결했다. tools.multiformat_lab는 PDF/TXT/DOCX와 고정 검토·DOCX/PDF 출력을 실행한다. 보고서 템플릿 v2는 DOCX 구조적 위치를 설명한다. 이전 출력/보고서는 보존한다. multiformat_tests와 관련 회귀를 사용하며 HWP/HWPX·실제 모델/인증·독립 품질/수업은 미검증이다.

Single-Agent 기록 읽기는 `python -m tools.agent_steps --record ../../../reports/KEDU-PRODUCTION-007/observed.json --case A02`를 사용한다. fixture-observed.json을 선택하면 고정 응답 제어 기록이며 모델 품질 증거가 아니다. [L5 활동](../L5.md)은 직접 Runtime 코드와 별도 실제 모델/Framework 실행을 구분한다.

Multi-Agent 저장 기록은 `python -m tools.multi_steps --record ../../../reports/KEDU-PRODUCTION-008/observed.json --case A02`로 읽는다. fixture-observed.json의 control/M01/M02/M03/M04 하위 키는 고정 제어 실험이며 실제 모델 품질이 아니다. [L6 활동](../L6.md)에서 직접 경계 코드·과거 통합·별도 역할Probe·본인의 새 실행을 구분한다.
