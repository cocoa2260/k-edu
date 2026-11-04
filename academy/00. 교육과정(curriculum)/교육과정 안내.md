# 강의와 실습을 따라가는 순서

이 과정에서는 규정을 찾아 답하는 문서 도우미를 만든다. 먼저 무엇을 돕고 어떤 실패를 막을지 정하고, 모델 입력·검색·답변 검토·도구 실행을 차례로 연결한다. 뒤에서는 학습 데이터를 준비하고 작은 모델 갱신을 실험하며, PDF와 보고서까지 확장한다. 사례의 기관·규정·금액은 교육용 가상 자료다.

각 과목은 **강의의 설명과 예제 → 해당 활동지 또는 연결 실습 → 결과를 자기 말로 해석해 제출**하는 순서로 진행한다. 처음부터 제작 보고서·관리 JSON을 읽을 필요는 없다. 강의 안의 코드는 ‘실행 명령’, ‘설명용 예’, ‘저장된 과거 결과’ 중 어떤 것인지 먼저 읽고, 실행할 때는 그 절에서 지정한 폴더와 환경을 사용한다.

## 1. 문제와 모델을 이해하기

| 순서 | 읽을 강의 | 함께 할 활동과 제출물 | 다음에 가져갈 것 |
|---|---|---|---|
| 1 | [AI 서비스의 목표와 전체 흐름](lessons/orientation/lesson.md) | [활동지](lessons/orientation/worksheet.md): 업무 정의, 막아야 할 실패, 단계별 책임, 기술 분류와 미확인 조건 | 무엇을 잘해야 하고 언제 멈춰야 하는지 정한 기준 |
| 2 | [데이터 설계와 모델 평가](lessons/data-evaluation/lesson.md) | [활동지](lessons/data-evaluation/worksheet.md): 입력 시점·라벨, 출처/분리/증강, 조건 통제, 혼동행렬과 오류 영향 | 학습/평가 자료의 구분과 결과 판단 근거 |
| 3 | [Transformer의 내부 원리](lessons/transformer-basics/lesson.md) | [활동지](lessons/transformer-basics/worksheet.md): 작은 Forward·Attention 계산, Shape·Mask, 생성과 Cache | 입력과 출력이 바뀌는 원리. 작은 계산을 실제 모델 성능으로 해석하지 않기 |
| 4 | [언어 모델의 학습·생성·평가](lessons/llm-basics/lesson.md) → [Hugging Face 첫 방문·Model Card·Tokenizer](lessons/huggingface/README.md) | LLM [활동지](lessons/llm-basics/worksheet.md) 뒤에 HF [작성용 답안](practice/huggingface-tokenizer/WORKSHEET.md): 후보 선택 근거, 실제 입력 ID·길이·Padding·대화 형식 | 모델/파일 버전, 실제로 전달되는 입력, 관찰한 것과 미확인인 것 |

앞의 표·계산 활동은 GPU나 유료 API 없이 진행한다. Hugging Face 화면 활동도 모델을 실행하지 않는다. **Tokenizer 직접 실행**부터는 Python·의존성·Tokenizer 파일이 필요하다. [실행 안내](practice/huggingface-tokenizer/README.md)의 준비 검사 뒤 실제 관찰과 캐시 반복까지 수행한다. 파일 준비 때문에 실행하지 못했다면 화면/개념 활동과 실행 과제를 별도로 기록한다.

## 2. 같은 문서 도우미를 단계별로 확장하기

코딩을 시작하기 전에 [기준 대화 앱](lessons/baseline/lesson.md)을 진행한다. Python 함수·예외·가상환경, HTTP·JSON·FastAPI 기초가 필요하다. Phase1의 관련 학습이 부족하면 여기서 보충한 뒤 진행한다. 모델 없는 계약 데모로 질문이 API·Service·Provider를 거쳐 돌아오는 경로를 설명하고, 사용 환경·입출력·오류 관찰을 남긴다. 실제 Provider 연결은 별도 준비와 생성 확인이 필요하다.

| 순서 | 읽을 강의 | 연결 실습과 제출할 근거 | 앞 과목에서 이어지는 것 |
|---|---|---|---|
| 5 | [Prompt: 작성 지시와 예시](lessons/prompt/lesson.md) | [지시 비교 실습](practice/document-assistant/L1.md): 바뀐 지시/예시, 유지한 질문/자료, 한 조건 변경과 회귀 기준 | 같은 자료라도 원하는 답의 조건을 분명히 적기 |
| 6 | [Context: 필요한 자료와 입력 예산](lessons/context/lesson.md) | [자료 선택 실습](practice/document-assistant/CONTEXT.md): 출처·허용 범위, 자료 순서, 답변 여유, 현재 전달 자료 | 지시는 유지하고 어떤 자료를 보여줄지 바꾸기 |
| 7 | [Harness: 호출·검사·보완·종료](lessons/harness/lesson.md) | [실행기 실습](practice/document-assistant/L2.md): 재시도/보완 차이, 호출 상한, Trace와 종료 이유, 형식/내용의 다른 판정 | 준비 입력을 호출하고 실패를 제한 안에서 다루기 |
| 8 | [Embedding: 검색할 숫자 표현](lessons/embedding/lesson.md) | [검색 실습의 Embedding 활동](practice/document-assistant/L3.md): 벡터 계산, 어휘/의미 검색의 차이, 실제 검색 기록의 필요한 줄 | 사람이 고르던 자료를 질문에 따라 찾기 |
| 9 | [Index: 저장·탐색·갱신·삭제](lessons/vector-index/lesson.md) | [같은 검색 실습의 Index 활동](practice/document-assistant/L3.md): 원문/버전 연결, 탐색 누락, 필터·갱신/삭제 후 재조회 | 검색 벡터와 본문·원문·상태를 함께 관리하기 |
| 10 | [RAG: 찾은 자료로 답하고 근거 확인](lessons/rag/lesson.md) | [RAG 실습](practice/document-assistant/L4.md): 검색→실제 입력→원응답→보완→주장/인용 대조, 실패 원인과 한 조건 비교 | 검색과 Harness를 연결하되 인용 유무와 내용 정확성을 따로 보기 |
| 11 | [Single-Agent: 도구 요청과 실행 책임](lessons/single-agent/lesson.md) | [도구 실행 실습](practice/document-assistant/L5.md): 요청과 함수 진입, 인자·승인·출처 검사, 관찰/상태/종료 | 모델이 다음 행동을 요청해도 실행 권한과 상한은 실행기가 지키기 |
| 12 | [Multi-Agent: 역할과 근거 전달](lessons/multi-agent/lesson.md) | [역할 전달 실습](practice/document-assistant/L6.md): 전달한 자료, 수신 범위, 보완 횟수, 전체 예산, 최종/부분 초안 | 같은 검색·출처 검사와 전체 예산을 역할 사이에서도 유지하기 |

입력 준비와 고정 응답 실습은 실제 모델이 답을 생성한 것이 아니다. 검색 이후에는 작은 계산·현재 제어 코드·과거 모델 기록 읽기와 **본인의 새 모델 실행**이 나뉜다. 각 실습의 준비 표를 따라 선택하고, 실제 실행 과제를 기록 읽기로 완료 처리하지 않는다. 과거의 틀린 답도 실패를 분석할 자료다. 품질을 검토하지 않은 답변을 정답 예제로 채택하지 않는다.

## 3. 학습 실험과 문서 처리로 넓히기

아래 강의도 전체 교육과정의 범위다. 실제 훈련·재로드와 문서 확장 실행은 본편 앱과 구별해 준비한다. **실행 준비가 부족해 연기한 활동은 미완료로 남긴다.**

| 순서 | 읽을 강의 | 활동과 제출물 | 연결에서 주의할 점 |
|---|---|---|---|
| 13 | [학습 데이터·PEFT 전략](lessons/fine-tuning/lesson.md) → [LoRA·QLoRA·평가·재로드](lessons/fine-tuning/training.md) | [데이터/훈련 실습](practice/document-assistant/L7.md): 행동 목표·원본 가족 분리·증강 채택/기각·정답 Token 범위, 작은 갱신 계산·자원 계획·평가 반례·재현 기록 | 출장비 사례에서 가상 회의실 규정으로 바뀐다. 실제 LoRA 훈련/새 프로세스 재로드는 별도 실행. QLoRA는 자원/Backend 준비 후 검증하며 LoRA 성공으로 대체하지 않음 |
| 14 | [PDF·표·OCR와 원문 위치](lessons/document-parsing/lesson.md) | [문서 추출 실습](practice/document-assistant/L8.md): 페이지 경로·표의 조건/금액·OCR 오류 영향·권한/원문 위치 | 검색 앞의 문서 준비로 돌아간다. 가상 환불 PDF를 사용하며 디지털 추출·저장 OCR 지표 읽기·새 OCR를 구분 |
| 15 | [문서 등록](lessons/document-ai/intake.md) → [근거 보고서](lessons/document-ai/report.md) → [Provider](lessons/document-ai/provider.md) → [Streaming](lessons/document-ai/streaming.md) → [최종 평가](lessons/document-ai/evaluation.md) | [통합 실습](practice/document-assistant/L9.md): 형식별 위치·버전/권한/삭제·주장 검토, 공유 예산, 부분/확정 상태, 세 형식의 채택/보류 근거 | 합성 PDF/TXT/단순 DOCX와 고정 응답부터 확인. 보고서 출력·글꼴/렌더링, 별도 React 화면은 각각 실행 준비가 필요 |

## 실행 전에 확인할 준비

| 할 일 | 준비와 정확한 안내 |
|---|---|
| Tokenizer 직접 관찰 | Python 3.12·고정 의존성·선택 revision의 Tokenizer 파일. [별도 폴더 안내](practice/huggingface-tokenizer/README.md). 생성 모델 가중치/GPU는 필요 없음 |
| 기준 앱·입력 준비·현재 제어 코드 | [Backend 안내](practice/document-assistant/backend/README.md)의 가상환경과 요구 패키지. 명령은 주로 그 backend 폴더에서 실행 |
| 실제 Embedding·RAG·Agent | [검색 준비](practice/document-assistant/L3.md) 뒤 각 실습의 모델/캐시·CPU 환경을 추가 확인. 기존 API를 켰다고 이 명령행 실행기가 자동 연결되지는 않음 |
| 실제 LoRA·재로드·QLoRA | [훈련 실행 준비](practice/document-assistant/L7.md). 모델/Tokenizer·학습 패키지·저장 공간·자원 조건 확인. QLoRA 장비/Backend는 별도이며 임의로 실행 가능하다고 가정하지 않음 |
| PDF/OCR·보고서 | [PDF 준비](practice/document-assistant/L8.md), [통합 준비](practice/document-assistant/L9.md). PDF 패키지, 새 OCR에는 엔진/한국어 데이터, 출력에는 글꼴과 렌더링 환경 확인 |
| React/SSE 화면 | [화면 실행 안내](practice/document-assistant/stream-ui/README.md)의 Node/npm·고정 빌드·별도 로컬 서버. 자동 브라우저 검사에는 추가 도구가 필요 |

Tokenizer 폴더의 가상환경과 Backend의 기본/모델/문서 환경은 용도가 다르다. 모든 requirements 파일을 한 환경에 무조건 합치지 말고 해당 안내의 설치 순서를 따른다. 다른 운영체제·교육생 장비·동시 수강 실행까지 보장된 상태는 아니다.

## 제출할 때 함께 적기

각 활동의 표·계산·설명을 제출하되 다음 네 가지를 붙인다. 새로운 관리 코드나 별도 JSON 양식은 필요 없다.

1. 사용한 강의/활동, 입력 자료와 파일 버전.
2. 직접 실행·저장 기록 읽기·손계산 중 무엇을 했는지와 실제 관찰값.
3. 원문·입력·출력에서 판단한 이유, 예상과 다른 점.
4. 실행하지 못했거나 추가 확인이 필요한 부분과 다음 확인 방법.

강사는 과목별 해설로 **개념 이해, 실행 증거, 답변/문서 품질**을 구분해 피드백한다. 전체 경로는 시작 안내와 본과목 14개, 총 70학습 단원이다. 70은 수업 시간이나 검증 통과 수가 아니다. 강사용 현재 상태와 남은 검증은 [제작 현황](PROGRESS.md)과 [연결 점검 결과](reports/KEDU-TEACHING-INTEGRATION-001/RESULT.md)에 있다.

수업에서 사용할 직접 활동, 기록 시연과 장비별 확인 범위는 [실습별 검증 종합](reports/KEDU-RUNTIME-REVALIDATION-010/RESULT.md)에서 확인할 수 있다.
