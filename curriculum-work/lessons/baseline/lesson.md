# L0. 기존 대화 앱을 누적 실습의 출발점으로 고정하기

2026-10-31 · 연결 실습 L0 · 선수: Python 함수·예외·가상환경, HTTP·JSON·FastAPI 기초

**이번에는 기능을 늘리기 전에, 우리가 이어서 고칠 앱이 어디서 시작하고 어떤 데이터를 주고받는지 확인한다.** 이후 Prompt·Context·Harness 실습은 이 앱을 계속 확장한다. 단계마다 비슷한 새 앱을 다시 만드는 방식으로 진행하지 않는다.

기존 Day3 7~8교시에는 Provider·Service·FastAPI 코드와 React 연결 지시가 Markdown에 나뉘어 있었다. 이번 기준 앱은 그 Backend 코드를 실제 실행 파일로 옮기고 CORS를 합친 것이다. 기존 academy 원문은 수정하지 않았다. [파일별 원문 연결](../../practice/document-assistant/baseline-source-map.json)은 필요할 때 확인한다.

## 1. 질문 하나의 이동 경로

| 순서 | 담당 | 하는 일 |
|---|---|---|
| 1 | Client | message 문자열을 /ai/chat으로 전송 |
| 2 | FastAPI·Schema | JSON 형식·문자 길이·공백 입력 확인 |
| 3 | AIService | 공통 Provider 계약에 문자열 전달 |
| 4 | 선택한 Provider | Ollama HTTP 또는 OpenAI SDK 호출·응답 해석 |
| 5 | FastAPI | provider·model·answer를 Client에 반환 |

**확인 질문:** Provider를 바꿀 때 Client가 보내는 필드도 바꿔야 할까? 이 단계에서는 서버 설정으로 Provider를 선택하므로 요청에는 provider나 model을 넣지 않는다. 실제 선택은 Backend가 한다.

## 2. 이번에 고정할 약속

| 항목 | L0 기준 |
|---|---|
| 요청 주소 | POST /ai/chat |
| 요청 데이터 | message라는 필드의 문자열 |
| 입력 제한 | 1~2000문자. 공백만 있으면 거부하고, 수락한 메시지의 앞뒤 공백은 제거 |
| 성공 결과 | provider·model·answer 세 문자열 |
| 잘못된 입력 | 422, Provider 호출 전 거부 |
| Provider 연결 실패 | 503 |
| Provider 시간 초과 | 504 |
| 원격 오류·응답 형식 오류 | 502 |
| Provider 변경 | 서버 설정 후 재시작. 자동으로 다른 Provider로 넘어가지 않음 |
| Streaming·대화 기록·인증 | L0에서 구현하지 않음 |

2000은 **문자 수**이며 Token 예산이 아니다. Tokenizer 실습에서 확인한 Token 길이는 후속 Context 구성에서 따로 계산한다.

원문의 Schema는 추가 필드를 무시한다. 따라서 Client가 provider를 보내도 선택은 바뀌지 않지만, 그 필드 때문에 422가 나오는 것은 아니다. 입력 계약을 나중에 엄격하게 바꾸려면 별도 변경으로 기록하고 Client도 함께 점검한다.

GET /health는 앱이 선택한 설정을 보여준다. 실제 모델에 질문하지 않으므로 health 성공을 모델 생성 성공으로 해석하지 않는다.

## 3. 실제 파일에서 책임 찾기

실행 폴더는 **[practice/document-assistant/backend](../../practice/document-assistant/backend/README.md)**다.

| 파일 | 읽을 이유 |
|---|---|
| app/main.py | HTTP Route·공통 오류 응답·CORS |
| app/schemas.py | Client 입력/출력 구조 |
| app/service.py | Provider 종류와 독립적인 업무 흐름 |
| app/providers/base.py | generate(message), provider_name, model_name 계약 |
| app/providers/factory.py | 서버 설정으로 구현체 선택 |
| app/providers/ollama_provider.py | Ollama의 요청·응답 형식 |
| app/providers/openai_provider.py | 원문의 Responses SDK 경로를 유지한 선택 구현 |
| tools/contract_demo.py | 모델 없이 계약만 보는 명시적인 데모 |

**활동:** Route 안에 모델 종류별 호출 코드가 있는지, Service가 구체적인 SDK를 Import하는지 찾아본다. Provider 하나를 추가할 때 Client와 Service를 고칠 필요가 있는지도 설명한다.

## 4. 모델 없이 계약부터 확인하기

계약 데모는 **고정 규칙으로 반환하는 테스트용 응답**이다. 실제 모델을 실행하지 않는다. 응답의 provider는 contract-demo, model은 no-model-executed로 표시된다. 이 결과를 RAG·Agent·모델 품질의 성공으로 제출하지 않는다.

아래는 터미널에 **입력할 명령**이다. 실행 로그가 아니다. 먼저 위 Backend 폴더를 연다.

| 단계 | macOS/Linux | Windows PowerShell |
|---|---|---|
| 가상환경 생성 | `python3.12 -m venv .venv` | `py -3.12 -m venv .venv` |
| 설치 | `.venv/bin/python -m pip install -r requirements-dev.txt` | `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` |
| 계약 테스트 | `.venv/bin/python -m pytest -q` | `.venv\Scripts\python.exe -m pytest -q` |
| 계약 데모 서버 | `.venv/bin/python -m uvicorn tools.contract_demo:create_contract_app --factory --host 127.0.0.1 --port 8000` | `.venv\Scripts\python.exe -m uvicorn tools.contract_demo:create_contract_app --factory --host 127.0.0.1 --port 8000` |

서버를 켠 뒤 브라우저에서 http://127.0.0.1:8000/docs를 열고 POST /ai/chat을 선택한다. Try it out의 message 값으로 짧은 질문을 넣어 전송한다. 질문 앞뒤에 공백을 넣었을 때 반환 문자열을 관찰하고, 공백만 보냈을 때 422가 나오는지도 본다.

FastAPI 문서 화면을 사용하는 데 React 지식은 필요하지 않다. React 화면을 아직 검증하지 않아도 Backend 계약 활동은 진행할 수 있다. 자동 검증에서는 실제 로컬 HTTP 서버 왕복도 확인했지만, 이 계약 데모가 생성 모델을 호출한 것은 아니다.

## 5. 실제 Provider를 연결할 때 추가로 필요한 것

Ollama 경로는 실행 중인 Ollama 서버와 준비한 모델 이름이 필요하다. OpenAI 경로는 별도 API 이용 조건·자격 증명·모델 설정을 확인해야 한다. 이번 검증에서는 유료 API를 호출하지 않았다. OpenAI 경로를 선택하지 않으면 해당 Key를 준비할 필요가 없다.

Backend의 .env.example을 로컬 .env로 복사하고 선택한 Provider의 값만 채운다. 실제 비밀 값이 들어가는 .env는 공유하거나 Git에 올리지 않는다. .env.example은 실제 설정 양식이지 실행 결과가 아니다.

실제 설정 경로의 시작 명령은 `python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`이다. 여기의 python은 위 가상환경 실행기로 바꿔 쓴다. 설정이 빠졌다면 시작 단계에서 오류가 나야 하며, 조용히 계약 데모로 바뀌지 않는다.

원문은 파일을 Import할 때 바로 앱을 만들었다. 기준 앱은 앱 생성 함수를 명시적으로 실행하는 --factory를 사용한다. 따라서 테스트에서 Key·모델 설정 없이 Import할 수 있고, 실제 서버 시작 때는 선택한 Provider 설정을 확인한다.

## 6. CORS와 인증을 혼동하지 않기

허용한 프런트엔드 주소는 기본적으로 http://localhost:5173이다. React 개발 서버가 다른 주소를 쓰면 FRONTEND_ORIGINS를 맞춘다. http://127.0.0.1:5173과 http://localhost:5173은 같은 Origin으로 취급하지 않는다.

CORS는 브라우저가 응답을 읽는 규칙이며 사용자 인증 기능이 아니다. 허용하지 않은 Origin의 실제 POST가 서버에서 처리될 수 있다. 인증·권한이 구현됐다고 해석하지 않는다. 이번에는 허용/비허용 Preflight와 이 차이를 계약 테스트로 확인했다.

## 7. 학생이 남길 기준 기록

| 기록할 것 | 내가 확인한 값·미확인 조건 |
|---|---|
| 작업 브랜치·커밋 | 작성 |
| Python·설치 패키지 | 작성 |
| /ai/chat 요청·응답 필드 | 작성 |
| 정상·공백·길이 초과·Provider 오류 결과 | 작성 |
| 선택한 Provider·모델 | 작성. 계약 데모면 그대로 표시 |
| 실제 생성 여부 | 미실행 / 실행 실패 / 실행 성공 중 선택하고 근거 기록 |
| React 화면 여부 | 미검증 / 검증 중 / 검증 완료 구분 |

완료 기준은 Client 계약을 설명하고, 계약 테스트·데모와 실제 생성 모델의 증거를 구분하는 것이다. [이번 L0 검증 결과](../../reports/KEDU-PRODUCTION-002/RESULT.md)에 제작 환경에서 확인한 범위를 기록했다.

다음에는 같은 Service/Provider 경계에 Prompt와 Context 구성을 더하고, 이후 Harness가 실행·검증·실패·중단을 관찰하도록 확장한다. 이번 L0 안내를 70개 단원에 추가로 중복 집계하지 않는다.
