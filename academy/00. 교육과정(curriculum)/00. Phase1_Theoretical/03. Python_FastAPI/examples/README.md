# Python & FastAPI for AI Backend v1.2 예제

각 Module에는 다음 두 종류의 예제가 있습니다.

1. 핵심 개념을 확인하는 최소 예제
2. AI Backend 상황에 적용하는 예제

## 환경 준비

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell에서는 가상환경을 다음과 같이 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

일반 Python 예제는 파일을 직접 실행합니다.

```bash
python module_01/collection_basics.py
```

FastAPI 예제는 파일이 있는 디렉터리에서 Uvicorn으로 실행합니다.

```bash
cd module_16
uvicorn hello_app:app --reload
```

실제 OpenAI 호출 예제를 제외한 모든 AI Client 예제는 Fake 구현을 사용합니다.
`module_37/optional_openai_client.py`만 `OPENAI_API_KEY`가 있을 때 실제 API를 호출합니다.

## Module별 예제

### Module 01

- [collection_basics.py](module_01/collection_basics.py): List·Tuple·Set·Dictionary의 선택 기준을 확인합니다.
- [ai_payload_collection.py](module_01/ai_payload_collection.py): AI 요청과 검색 결과를 Collection으로 모델링합니다.

### Module 02

- [list_operations.py](module_02/list_operations.py): List의 추가·수정·삭제·순회를 연습합니다.
- [chat_messages.py](module_02/chat_messages.py): 대화 메시지를 List로 누적하고 마지막 메시지를 조회합니다.

### Module 03

- [comprehension_basics.py](module_03/comprehension_basics.py): List Comprehension의 변환과 필터링을 확인합니다.
- [filter_documents.py](module_03/filter_documents.py): 문서 검색 결과를 필터링하고 응답 형태로 변환합니다.

### Module 04

- [dictionary_basics.py](module_04/dictionary_basics.py): Dictionary의 생성·조회·수정과 안전한 조회를 연습합니다.
- [api_payload.py](module_04/api_payload.py): JSON 요청에 대응하는 Dictionary를 구성합니다.

### Module 05

- [nested_access.py](module_05/nested_access.py): 중첩 Dictionary와 List의 데이터에 접근합니다.
- [group_documents.py](module_05/group_documents.py): 문서를 상태별로 그룹화하는 활용 패턴을 연습합니다.

### Module 06

- [decorator_timing.py](module_06/decorator_timing.py): Decorator로 함수 실행 시간을 측정합니다.
- [route_decorator_model.py](module_06/route_decorator_model.py): 간단한 Route Registry로 @ 문법의 원리를 확인합니다.

### Module 07

- [function_to_service.py](module_07/function_to_service.py): 관련 데이터와 동작을 Class로 묶는 이유를 확인합니다.
- [chat_service_responsibility.py](module_07/chat_service_responsibility.py): ChatService가 하나의 Use Case를 담당하도록 설계합니다.

### Module 08

- [class_objects.py](module_08/class_objects.py): 생성자·인스턴스 변수·메서드를 연습합니다.
- [document_service.py](module_08/document_service.py): 객체별 상태가 독립적으로 유지되는지 확인합니다.

### Module 09

- [inheritance_basics.py](module_09/inheritance_basics.py): 부모 Class의 공통 기능을 자식 Class가 물려받습니다.
- [base_model_analogy.py](module_09/base_model_analogy.py): 기반 Class를 상속해 공통 검증 규칙을 재사용합니다.

### Module 10

- [type_hints.py](module_10/type_hints.py): 함수와 Collection에 Type Hint를 적용합니다.
- [generic_result.py](module_10/generic_result.py): Generic Result로 여러 결과 타입을 안전하게 표현합니다.

### Module 11

- [minimal_fastapi.py](module_11/minimal_fastapi.py): 가장 작은 FastAPI 애플리케이션을 실행합니다.
- [ai_boundary_fastapi.py](module_11/ai_boundary_fastapi.py): Client와 AI 처리 사이에 Backend 경계를 둡니다.

### Module 12

- [http_contracts.py](module_12/http_contracts.py): 기능별 HTTP Method·Path·Status Code 계약을 설계합니다.
- [rest_routes.py](module_12/rest_routes.py): REST 관점의 문서 생성·조회 Route를 작성합니다.

### Module 13

- [async_sequential.py](module_13/async_sequential.py): 두 I/O 작업을 순차적으로 기다립니다.
- [async_concurrent.py](module_13/async_concurrent.py): asyncio.gather로 독립적인 I/O를 동시에 처리합니다.

### Module 14

- [raw_asgi_app.py](module_14/raw_asgi_app.py): Framework 없이 ASGI 호출 규약을 확인합니다.
- [fastapi_asgi_app.py](module_14/fastapi_asgi_app.py): Uvicorn이 불러올 FastAPI ASGI 객체를 만듭니다.

### Module 15

- [environment_check.py](module_15/environment_check.py): 현재 Python 실행 환경과 가상환경 여부를 확인합니다.
- [dependency_versions.py](module_15/dependency_versions.py): 주요 Package의 설치 여부와 버전을 확인합니다.

### Module 16

- [hello_app.py](module_16/hello_app.py): 첫 Endpoint와 Health Check를 구현합니다.
- [chat_app.py](module_16/chat_app.py): 간단한 질문을 받아 응답하는 첫 AI 형태의 API를 만듭니다.

### Module 17

- [openapi_metadata.py](module_17/openapi_metadata.py): OpenAPI 문서에 제목·설명·Tag를 추가합니다.
- [schema_examples.py](module_17/schema_examples.py): Request Model에 Swagger 입력 예시를 제공합니다.

### Module 18

- [route_order.py](module_18/route_order.py): 고정 Path를 동적 Path보다 먼저 선언합니다.
- [separate_features.py](module_18/separate_features.py): Chat과 Document Route를 URL 기준으로 분리합니다.

### Module 19

- [get_documents.py](module_19/get_documents.py): GET으로 문서 목록을 조회합니다.
- [get_model_status.py](module_19/get_model_status.py): GET으로 AI Provider 상태를 표현합니다.

### Module 20

- [path_document.py](module_20/path_document.py): Path Parameter로 단일 리소스를 식별합니다.
- [path_validation.py](module_20/path_validation.py): Path에 숫자 범위 제약을 적용합니다.

### Module 21

- [query_filter.py](module_21/query_filter.py): Query Parameter로 상태와 개수를 필터링합니다.
- [pagination.py](module_21/pagination.py): offset과 limit으로 간단한 Pagination을 구현합니다.

### Module 22

- [post_job.py](module_22/post_job.py): POST로 새로운 AI 작업을 접수합니다.
- [post_status_codes.py](module_22/post_status_codes.py): 201과 202 응답의 용도를 비교합니다.

### Module 23

- [request_body.py](module_23/request_body.py): Pydantic Model로 JSON Request Body를 받습니다.
- [nested_body.py](module_23/nested_body.py): 중첩 Request Model로 복합 JSON을 표현합니다.

### Module 24

- [pydantic_mapping.py](module_24/pydantic_mapping.py): Dictionary가 Pydantic 객체로 변환되는 과정을 확인합니다.
- [pydantic_serialization.py](module_24/pydantic_serialization.py): Pydantic 객체를 Dictionary와 JSON으로 직렬화합니다.

### Module 25

- [field_constraints.py](module_25/field_constraints.py): Field 제약으로 질문 길이와 숫자 범위를 검증합니다.
- [model_validator.py](module_25/model_validator.py): 여러 Field 사이의 비즈니스 입력 규칙을 검증합니다.

### Module 26

- [response_model.py](module_26/response_model.py): Response Model로 출력 계약을 고정합니다.
- [private_field_filter.py](module_26/private_field_filter.py): response_model이 내부 Field 노출을 차단하는지 확인합니다.

### Module 27

- [dataclass_basic.py](module_27/dataclass_basic.py): Data Class가 생성자·표현·비교를 자동 생성하는지 확인합니다.
- [dataclass_result.py](module_27/dataclass_result.py): Service 내부 결과를 불변 Data Class로 표현합니다.

### Module 28

- [composition_basic.py](module_28/composition_basic.py): 상속 대신 필요한 객체를 속성으로 전달합니다.
- [provider_injection.py](module_28/provider_injection.py): Service에 AI Client를 합성하여 구현을 교체합니다.

### Module 29

- [thin_router.py](module_29/thin_router.py): Router는 HTTP를 처리하고 Service가 규칙을 담당합니다.
- [service_unit_demo.py](module_29/service_unit_demo.py): HTTP 없이 Service의 Business Logic을 검증합니다.

### Module 30

- [router_prefix.py](module_30/router_prefix.py): APIRouter Prefix와 Tag로 기능 Route를 묶습니다.
- [multi_router_app.py](module_30/multi_router_app.py): 여러 APIRouter를 하나의 애플리케이션에 조립합니다.

### Module 31

- [layered_single_file.py](module_31/layered_single_file.py): Router·Service·Client의 의존 방향을 한 파일에서 확인합니다.
- [dependency_direction.py](module_31/dependency_direction.py): 상위 계층이 구체 Provider 대신 Protocol에 의존하게 만듭니다.

### Module 32

- [depends_service.py](module_32/depends_service.py): Depends로 Service 생성과 주입을 FastAPI에 맡깁니다.
- [override_dependency.py](module_32/override_dependency.py): Dependency Override로 실제 구현을 Fake로 교체합니다.

### Module 33

- [settings_env.py](module_33/settings_env.py): Pydantic Settings로 환경변수를 타입 안전하게 읽습니다.
- [cached_settings.py](module_33/cached_settings.py): Settings 객체를 캐시해 재사용합니다.

### Module 34

- [domain_exception.py](module_34/domain_exception.py): Domain Exception을 HTTP 오류 응답으로 변환합니다.
- [standard_error.py](module_34/standard_error.py): 표준 Error Response Model을 사용합니다.

### Module 35

- [provider_boundary.py](module_35/provider_boundary.py): 외부 Provider 응답을 내부 모델로 변환합니다.
- [internal_result.py](module_35/internal_result.py): Provider가 달라도 동일한 내부 결과 계약을 유지합니다.

### Module 36

- [provider_factory.py](module_36/provider_factory.py): 설정값에 따라 Fake·OpenAI Provider 구현을 선택합니다.
- [secret_settings.py](module_36/secret_settings.py): SecretStr로 API Key가 출력되는 것을 방지합니다.

### Module 37

- [fake_openai_client.py](module_37/fake_openai_client.py): OpenAI와 같은 비동기 계약을 Fake Client로 연습합니다.
- [optional_openai_client.py](module_37/optional_openai_client.py): API Key가 있을 때만 실제 OpenAI Responses API를 호출합니다.

### Module 38

- [summary_service.py](module_38/summary_service.py): Prompt 조립과 Client 호출을 AI Service에 둡니다.
- [fake_service_test.py](module_38/fake_service_test.py): Fake Client로 Service를 외부 호출 없이 검증합니다.

### Module 39

- [concurrent_ai.py](module_39/concurrent_ai.py): 여러 AI 요청을 asyncio.gather로 동시에 처리합니다.
- [semaphore_limit.py](module_39/semaphore_limit.py): Semaphore로 동시 AI 호출 수를 제한합니다.

### Module 40

- [prompt_builder.py](module_40/prompt_builder.py): System 규칙과 사용자 입력을 분리해 Prompt를 구성합니다.
- [prompt_request_model.py](module_40/prompt_request_model.py): Pydantic으로 Prompt 요청의 허용 범위를 검증합니다.

### Module 41

- [timeout.py](module_41/timeout.py): asyncio.timeout으로 Provider 응답 대기 시간을 제한합니다.
- [retry.py](module_41/retry.py): 재시도 가능한 오류만 제한된 횟수로 재시도합니다.

### Module 42

- [streaming_plain.py](module_42/streaming_plain.py): Async Generator가 Chunk를 순서대로 생성하는지 확인합니다.
- [streaming_response.py](module_42/streaming_response.py): FastAPI StreamingResponse로 NDJSON Event를 전송합니다.

