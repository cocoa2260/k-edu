# K-Edu 전체 목차와 누적 실습 구성안 v0.1

2026-10-30 · 4단계 · KEDU-DESIGN-001 · 사용자 검토용 구성안

**추천 구성: Phase1의 24교시를 기반으로 유지하고, Phase2를 본과목 14개와 시작 안내로 구성한다. 실습은 같은 문서 답변 앱을 Prompt·Context → Harness·Loop → 검색·RAG → Single-Agent → Multi-Agent로 확장한다.**

처음에는 **2번 목차표와 3번 실습표**를 보면 된다. 상세 단원·이동 근거·역할 계약·평가·제작 조건은 같은 문서의 접힌 부록에 있다. 본문에 실행 코드나 JSON 예시를 넣지 않았다.

이 문서는 구성과 제작 기준을 구체화한 제안이다. **강의 본문·기존 파일명·실습 앱·데이터는 아직 변경하거나 제작하지 않았다.** 실제 모델·훈련·교육장 성능을 검증한 결과도 아니다. 과목명과 범위는 이 구성안을 검토한 뒤 제작 기준으로 채택할 수 있다.

## 1. 이번 구성에서 정한 추천 기준

| 항목 | 추천 구성 |
|---|---|
| Phase1 | 개별 24교시를 편집 기준으로 유지한다. 통합본은 이후 생성하는 파생본으로 관리하고 이중 수동 편집을 피한다. |
| Phase2 | 데이터·평가, Transformer, LLM의 고유 심화를 보존한다. Context, Harness·Loop, Multi-Agent의 독립 학습 성과를 드러낸다. |
| 실습 중심 | 가상 규정에 근거해 답하고 검토하는 앱 하나를 계속 확장한다. 앞 단계의 코드·데이터·계약·평가를 이어받는다. |
| Fine-tuning | 실제 학습·저장·새 프로세스 재로드·평가를 별도 실험으로 유지한다. 추론 API 호출로 훈련 완료를 대신하지 않는다. |
| 문서 확장 | 먼저 한 디지털 형식으로 끝까지 완성한다. OCR·다중 형식·HWPX·보고서 생성은 단계별 확장 완료표로 보존한다. |
| 시간·환경 | 총 시수와 실제 장비 조건을 임의로 확정하지 않는다. 단원 번호는 강의시간 수가 아니며, 실행 가능 여부는 별도 게이트로 확인한다. |

## 2. 전체 목차 — 무엇을 새로 배우는가?

아키텍처·Python·FastAPI·React는 선수학습/보충 경로로 유지한다. 학생이 이미 이수했다고 가정하지 않으며, 필요한 구현 지식을 확인한 뒤 실습에 들어간다. Phase1 24교시는 기존의 모델 이해·호출·평가·Provider/UI 통합을 담당한다.

아래 K2 번호는 **개편안의 학습 ID**다. 현재 GitHub 폴더 번호를 바꾼 상태가 아니다. 시작 안내 K2-00을 제외한 본과목은 14개다.

| ID | 추천 과목명 | 이 과목에서 추가되는 성과 | 연결 실습 |
|---|---|---|---|
| K2-00 | AI 서비스의 목표와 전체 흐름 | 시작 안내: 목표·실패·평가·운영을 연결 | L0 |
| K2-01 | 머신러닝의 데이터 설계와 모델 평가 | 데이터 분리·일반화·누수·업무 지표 | 단원별 관찰·계산 실습 / 후속 구현의 선수지식 |
| K2-02 | Transformer의 내부 원리 | 신경망 계산·QKV·위치 정보·Mask·KV Cache | 단원별 관찰·계산 실습 / 후속 구현의 선수지식 |
| K2-03 | LLM의 학습·생성·한계 | LLM 학습 목표·Post-training·생성·한계 | 단원별 관찰·계산 실습 / 후속 구현의 선수지식 |
| K2-04 | Prompt Engineering: 지시·출력·평가 | 같은 과제의 지시·출력·전후 평가 | L1 |
| K2-05 | Context Engineering: 정보 선택·구성·예산 | 근거 선택·순서·출처·Token 예산 | L1 |
| K2-06 | Harness와 Loop Engineering: 실행·검증·개선 | 입출력 검사·State·Trace·부분 보완·종료 | L2 |
| K2-07 | 검색을 위한 Embedding | 검색용 표현·Dense/Sparse·Hybrid·Rerank | L3 |
| K2-08 | Vector Search와 인덱스 운영 | Exact/ANN·HNSW/IVF·권한/버전·갱신/삭제 | L3 |
| K2-09 | 근거를 제시하는 RAG | 검색부터 답변·근거·평가까지 연결 | L4 |
| K2-10 | Tool을 사용하는 Single-Agent | 도구/종료를 선택하고 Runtime이 검증·실행 | L5 |
| K2-11 | 역할을 나누는 Multi-Agent | 검색·작성·검토 역할과 동일 기준선 비교 | L6 |
| K2-12 | Fine-tuning의 학습과 평가 | 실제 학습·Adapter 저장·재로드·회귀 | L7 |
| K2-13 | OCR·Multimodal과 문서 입력 품질 | Parsing/OCR·표/순서·입력 품질·검토 | L8 |
| K2-14 | Document AI 통합과 보고서 생성 | 공통 문서 구조·보고서·UI·서비스 통합 | L9 |

추천 학습의 공통 경로는 **K2-00~11**이다. K2-12는 데이터·LLM·평가/Harness를 배운 뒤 수행할 수 있는 별도 훈련 실험이며 Multi-Agent를 먼저 끝내야 하는 것은 아니다. K2-13~14는 RAG 기반에 문서 입력과 서비스·보고서를 확장하는 경로다. K2-12의 훈련 모델을 반드시 Document AI에 써야 한다고 고정하지 않는다.

같은 개념의 소유 위치도 나눈다. 신경망 한 층·Activation 계산은 K2-02, 생성 설정은 K2-03, 지시는 K2-04, 현재 입력의 구성은 K2-05, 검사·State·반복 제어는 K2-06에서 충분히 설명한다. 뒤 과목은 이 정의를 길게 반복하지 않고 새 결과물을 추가한다.

## 3. 누적 실습 — 같은 앱에서 무엇이 늘어나는가?

프로젝트는 **문서 근거 답변·검토 도우미**다. 가상 기관의 출장·교육비 규정을 사용하며, 자료·질문·모델 조건·평가를 버전으로 고정한다. 아래는 제작할 산출물의 설계이며 현재 실행 결과가 아니다.

| 단계 | 이어받는 것 | 이번에 추가할 것 | 학생이 보여줄 결과 |
|---|---|---|---|
| L0 기준 앱 | Phase1 Day3 Provider 앱과 준비된 UI | 기준 커밋·환경·계약·Fake/실제 경로 구분 | CLI/테스트 Client 경로와 UI 미검증 상태도 구분 |
| L1 Prompt·Context | L0의 모델 호출과 입력 계약 | 같은 규정·질문에서 지시와 정보 구성을 한 조건씩 변경 | 변경 전후·근거·회귀 비교 |
| L2 Harness·Loop | L1의 평가 사례와 버전 | 출력/근거 검사·Trace·상한·실패별 보완·중단 | 정상·보완·거부·상한 종료 기록 |
| L3 검색·Index | L2의 실행/평가 구조 | Chunk·검색용 Embedding·Index·권한/버전 Filter | 정답 문서 검색·갱신/삭제·품질 비교 |
| L4 RAG | L3의 Index와 L2 Harness | 검색→Context→답변→Claim별 인용의 고정 Workflow | 실제 RAG Trace와 자료 없음/충돌 처리 |
| L5 Single-Agent | L4의 검색/근거 기능 | 모델이 검색·원문 확인·답변/질문·중단을 선택 | Tool 요청·검증·Observation·종료 이유 |
| L6 Multi-Agent | L5의 Tool·State·평가 | 검색·작성·검토의 역할별 판단·전달·제한된 보완 | Single/Multi 동일 18개 사례의 품질·호출·시간 비교 |
| L7 훈련 실험 | L2 평가 구조 + 데이터/LLM 선수학습 | 작은 별도 Task의 실제 학습·Adapter 저장·Reload | Base/Tuned/새 프로세스 Reload와 회귀 결과 |
| L8 문서 입력 | L4 RAG | 한 디지털 형식의 Parsing, 이후 OCR/표/순서·Vision 확장 | 원본 위치·추출 오류·검색/답변 영향 추적 |
| L9 문서 통합 | L6 + L8 | Review·DOCX/PDF 보고서·공통 SSE/UI·운영 계약 | 원문→답변→검토→보고서의 종단 결과 |

**첫 완성 목표는 L6까지의 RAG→Single-Agent→Multi-Agent 비교다.** L7은 실제 훈련 실험, L8~L9는 문서·서비스 확장으로 나누어 검증한다. 각 단계를 독립 앱으로 새로 만들지 않고 같은 앱의 변경점과 단계별 기준 버전을 남긴다.

## 4. 실제 모델·평가·완료를 구분하는 기준

| 구분 | 설계 기준 |
|---|---|
| Fake 검사 | 모델 없이도 계약·권한·오류·상한·UI 연결을 검사한다. 이를 실제 모델 품질이나 RAG 실행 성공으로 기록하지 않는다. |
| 실제 RAG | 실제 문서/Index 검색과 실제 생성 모델을 연결하고, 답변 주장과 원문 위치를 대조한다. |
| 실제 Agent | 모델이 Tool 요청이나 종료를 선택하고 Runtime이 검증·실행한 기록이 있어야 한다. 수동으로 ToolCall을 만든 예제만으로 완료하지 않는다. |
| 역할 분담 | 각 역할에 목표·선택 행동·State·도구·산출물·종료 책임을 둔다. 역할 이름만 바꾼 세 번의 정해진 호출과 구분한다. |
| 실제 훈련 | Optimizer Step·학습 가능한 Parameter·Adapter 저장·새 프로세스 Reload를 기록한다. 개선되지 않은 결과도 사실대로 평가한다. |
| 학생 완료 | 실행 여부와 품질 판정을 나눈다. 실패한 실행을 성공 답변으로 세지 않고, 올바른 거부는 해당 거부 사례의 기준으로 채점한다. |

공통 문서/질문 12개를 Prompt·Context·RAG에 계속 사용한다. Single/Multi 비교는 여기에 Agent 경계 6개를 더한 **같은 18개**를 사용한다. 역할 전달 오류 4개는 별도 검사로 두어 품질 비교 분모를 바꾸지 않는다. 작은 교육용 사례 집합의 결과를 서비스 전체 성능으로 일반화하지 않는다.

정상 답변의 사실/근거 품질과, 올바른 거부·권한·중단 사례의 통과는 따로 집계한다. L1~L2에서 사람이 제공할 Context로 확인한 결과는 자동 검색·권한 Filter·Index 삭제 검증의 증거가 아니다. L3 이후 같은 기대 행동에 실제 검색/갱신/삭제의 기능 검사를 추가한다.

## 5. 제작 전에 확인할 조건과 추천 첫 제작 묶음

실제 교육장에서는 모델 ID/리비전·양자화·Runtime·Tokenizer·Context·동시 요청·메모리·지연을 확인해야 한다. 특히 학생 PC에서 실제 훈련을 할지, 조별/별도 환경에서 할지는 G-TRAIN 결과로 정한다. 유료 관리형 서비스나 여러 GPU 모델의 동시 실행을 기본 조건으로 두지 않았다.

**추천 첫 제작 묶음은 K2-04~06과 L1~L2다.** 이 부분을 만들 때 앞의 K2-01~03·Phase1에서 필요한 개념을 명시해 연결한다. 제작하는 순서와 학생에게 가르치는 순서를 혼동하지 않는다. 실제 모델/SDK 환경, 예제 경로, 공개 계약을 먼저 검증한 뒤 작은 강의·코드·평가 묶음을 만들어 검토한다.

4단계 결과는 이 구성안이다. 강의·소스·데이터 제작과 실제 환경 검증은 다음 제작 단계에서 수행한다. 총 시수와 일자별 시간표는 아직 배정하지 않았다.

---

## 부록 — 상세 설계

<details>
<summary>과목별 상세 단원과 학생 산출물 — 63개 학습 단위</summary>

학습 단위는 개념과 수행을 나눈 편집 단위이며 63시간·63교시라는 뜻이 아니다. 아래는 새로 작성할 내용의 범위이고 작성 완료한 강의안이 아니다.

### K2-00. AI 서비스의 목표와 전체 흐름

시작 안내. 과목 수와 별도로 두고 업무·실패·평가·운영의 위치를 정한다.

선수 과목: 시작 안내 · 원문 연결: P2-01 · ARCH · 분석 근거: F02 · F19

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 업무와 허용할 수 없는 실패 | 입력·사용자·결과·위험을 하나의 문제 정의로 작성한다. | 문제 정의 1장과 실패 사례 3개 |
| AI Lifecycle와 책임 | 데이터 준비·모델 선택·검증·배포·감시·개선/종료를 사례에 배치한다. | 단계별 책임과 검토 지점 |
| 동향·제품·생성 방식의 구분 | 날짜가 있는 사례와 보편 원리를 구분한다. 기존 Diffusion 소개는 생성 모델링 접근의 짧은 비교로 보존하고 LLM/Transformer 구조와 같은 분류 축으로 묶지 않는다. | 생성 방식 비교·시점 확인 목록과 미확인 항목 |

### K2-01. 머신러닝의 데이터 설계와 모델 평가

용어 재정의보다 데이터와 평가의 책임을 다룬다.

선수 과목: K2-00 · 원문 연결: P2-02 · D1-03 · D2-03 · 분석 근거: F03 · F28

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 예측 시점과 데이터의 역할 | 이미 배운 Sample·Feature·Label을 실제 입력·예측 시점에 적용한다. | 예측 시점/사용 가능한 Feature 표 |
| Train·Validation·Test와 누수 | 분리 이유와 동일 문서·유사 샘플이 새는 경로를 찾는다. | 분리표와 누수 반례 |
| 일반화·과적합과 실험 통제 | Training Loss와 실제 목표를 구분하고 한 조건씩 바꾼다. | 조건 고정표와 결과 해석 |
| 평가 지표와 오류의 영향 | Accuracy·Precision·Recall·F1을 업무 실패의 차이로 선택한다. | 혼동행렬·지표·금지 행동 기준 |

### K2-02. Transformer의 내부 원리

Phase1의 발전 이유를 이어 수치·구조·정보 흐름을 설명한다.

선수 과목: K2-01 · 원문 연결: P2-02 · P2-03 · D1-04 · D2-02 · 분석 근거: F03 · F04

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 신경망 한 층과 Activation | Weight·Bias·Activation의 구체 계산을 보존한다. | 작은 Forward 계산과 활성화 전후 값 |
| Self-Attention의 계산 | Q/K/V·내적·스케일링·Softmax·가중합을 직접 추적한다. | 작은 벡터 계산표와 Shape 설명 |
| Transformer Block | Multi-head·Residual·LayerNorm·FFN의 역할을 연결한다. | 블록별 입력/출력·생략하면 생길 문제 |
| 위치 정보·구조·Mask | Positional Encoding/RoPE 등 위치 표현의 필요성을 보존하고 Encoder/Decoder/Cross-Attention과 Padding/Causal Mask를 구분한다. 특정 위치 처리 방식의 현재성은 해당 모델 사양으로 확인한다. | 위치 정보 유무·볼 수 있는 Token 표와 구조 선택 근거 |
| 생성과 KV Cache | 학습 병렬화·순차 Decode·Prefill·KV Cache 비용을 설명한다. | 학습/추론 흐름 및 메모리 요인 표 |

### K2-03. LLM의 학습·생성·한계

Token·Training의 첫 설명은 참조하고 언어 모델 고유 동작을 다룬다.

선수 과목: K2-02 · 원문 연결: P2-04 · D2-01 · D2-03 · D3-02 · 분석 근거: F05 · F34

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 학습 목표와 Post-training | Causal LM 목표·SFT·선호 최적화·Alignment를 구분한다. | 단계별 데이터/목표/바뀌는 대상 표 |
| Logit에서 Token 선택까지 | Temperature·Greedy·Top-k/Top-p·Sampling·Beam의 목적을 구분한다. | 같은 조건에서 생성 설정 1개 변경 기록 |
| Parameter·Context·Memory·Retrieval | 저장 위치·수명·다음 호출에 전달되는 방식을 구분한다. | 네 정보의 위치/재사용 책임 설명 |
| 환각·불확실성과 시스템 평가 | 형식·내용·근거·안전·지연을 별도로 평가한다. | 실패 분류와 모델/업무 평가 기준 |

### K2-04. Prompt Engineering: 지시·출력·평가

같은 과제의 지시를 설계하고 고정 사례에서 변경 효과를 확인한다.

선수 과목: K2-03 · 원문 연결: P2-05 · D1-07 · D1-08 · 분석 근거: F06 · F28

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 지시·요청·제약·출력 계약 | 문법 목록 암기 대신 모호한 요구를 검사 가능한 조건으로 바꾼다. | Prompt v1과 출력 계약 |
| Zero/One/Few-shot의 비교 | 사례의 유무와 선택을 통제하고 같은 평가로 비교한다. | 동일 사례의 Shot 비교표 |
| 추론 기법과 실행 전략의 경계 | CoT 적용 한계·Self-Consistency·ReAct가 요구하는 실행 구조를 구분한다. | 한 번의 지시/다중 후보/행동-관찰 비교 |
| Golden Dataset과 회귀 | 좋아 보이는 한 응답과 고정 사례에서의 개선을 구분한다. | Prompt v1/v2 결과와 회귀 기록 |

### K2-05. Context Engineering: 정보 선택·구성·예산

필요한 근거를 제한된 입력으로 구성하는 책임을 분명히 한다.

선수 과목: K2-04 · 원문 연결: P2-04 · P2-05 · P2-08 · P2-09 · P2-12 · 분석 근거: F24

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 정보의 출처와 신뢰 경계 | 정책 지시·사용자 요청·문서·Tool 결과를 구분한다. | 출처/권한/용도의 입력 목록 |
| 선택·순서·형식 | 같은 질문에서 불필요한 자료·중복·순서 차이를 비교한다. | Context v1/v2와 선택/제외 사유 |
| Token 예산과 답변 여유 | 실제 Tokenizer/Runtime 값으로 입력과 출력 여유를 점검한다. | 예산표와 초과 시 축소/중단 기록 |
| State·Memory에서 현재 Context로 | 전체 State를 그대로 복사하지 않고 현재 역할에 필요한 정보만 전달한다. | 최소 Handoff 정보와 제외 정보 |

### K2-06. Harness와 Loop Engineering: 실행·검증·개선

호출을 감싸는 실행 구조와 검증에 근거한 제한된 개선을 구현할 수 있게 설계한다.

선수 과목: K2-05 · 원문 연결: P2-05 · P2-09 · P2-12 · D3-07 · 분석 근거: F13 · F25 · F26 · F28

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| Harness의 최소 책임 | Provider·입출력 검사·State·기록·종료를 모델과 분리한다. | Fake와 실제 모델 경로를 구분한 실행 계약 |
| 오류·재시도·반복의 다른 목적 | 통신 재시도·형식 보완·후보 집계·품질 개선을 구분한다. | 반복 종류별 Trigger/상한/종료 표 |
| 검증 실패와 제한된 보완 | 실패 ID에 연결된 부분만 보완하고 같은 기준으로 재검사한다. | 실패→보완→재검사 Trace |
| 버전 간 개선과 회귀 | 같은 평가 집합에서 Prompt/Context/설정 변경의 효과를 기록한다. | 변경 전후·회귀·채택/복구 근거 |
| 승인·중단·관찰의 신뢰 경계 | 승인과 권한은 Runtime 상태에서 읽고 모델 인자로 덮어쓰지 못하게 한다. | 승인 위조·반복 실패·상한 도달의 차단 증거 |

### K2-07. 검색을 위한 Embedding

모델 내부 표현과 검색 표현을 구분하고 검색 품질을 평가한다.

선수 과목: K2-02 · K2-05 · 원문 연결: P2-06 · P2-03 · 분석 근거: F07

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| ID·내부 표현·검색 표현 | Token ID/Token Embedding/Contextual Representation/검색용 표현을 구분한다. | 같은 단어를 쓰는 네 대상의 입력·출력 표 |
| Dense·Sparse·BM25 | 정확 문자열과 의미 검색이 다르게 찾는 사례를 비교한다. | 질문-정답 문서 쌍과 결과표 |
| 유사도·정규화·차원 | Cosine·Dot·거리·정규화·Dimension의 의미를 계산한다. | 작은 벡터의 계산과 설정 해석 |
| Hybrid·Reranking·모델 교체 | 후보 검색/재정렬과 Embedding 모델 변경/재색인을 구분한다. | 검색 방식 비교와 Migration 계획 |

### K2-08. Vector Search와 인덱스 운영

검색 표현을 저장·가속·필터·갱신하는 역할을 다룬다.

선수 과목: K2-07 · 원문 연결: P2-07 · P2-06 · 분석 근거: F08 · F09

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 문서·Vector·Metadata의 계약 | Vector·Chunk·문서 버전·권한을 서로 다른 필드로 보존한다. | Index Record와 원문 추적표 |
| Exact Search와 ANN | Exact 기준 결과와 ANN의 품질/지연 Trade-off를 비교한다. | 같은 질의에서 결과·누락·지연 기록 |
| HNSW·IVF의 탐색 | Graph/구역 기반 탐색과 주요 설정을 설명한다. | 탐색 과정과 설정 변경의 예상 영향 |
| Filter·갱신·삭제·재색인 | 권한과 최신 버전의 조건을 검색 단계에 적용한다. | 권한 밖/삭제/구버전 문서 배제 증거 |

### K2-09. 근거를 제시하는 RAG

앞의 검색 결과와 Context/Harness를 연결해 답변과 근거를 검증한다.

선수 과목: K2-06 · K2-08 · 원문 연결: P2-08 · P2-06 · P2-07 · 분석 근거: F10 · F23 · F35

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| Offline과 Online의 연결 | 고정 Workflow로 Ingestion/Index와 질의 처리를 분리한다. | 원문→Chunk→검색→답변의 Trace |
| Chunk 구조와 Query Rewrite | 조건·표·제목을 보존하고 검색 실패를 교정한다. | Chunk/Query 변경 전후 비교 |
| Grounding·Citation·응답 보류 | 주장과 근거를 연결하고 자료 없음/충돌/권한 밖을 구분한다. | 원문 위치로 열리는 답변과 보류 결과 |
| 검색 실패와 생성 실패의 평가 | Retrieval과 Generation을 분리해 원인을 찾는다. | 같은 Case의 단계별 결과와 한 곳만 수정한 기록 |

### K2-10. Tool을 사용하는 Single-Agent

RAG를 Tool로 사용하며 Model 선택과 Runtime 실행의 책임을 추적한다.

선수 과목: K2-09 · 원문 연결: P2-09 · D3-06 · P2-12 · 분석 근거: F11 · F12 · F13 · F31

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| Agent·Workflow·Tool·MCP | 고정 단계와 관찰에 따른 행동 선택을 구분한다. | 같은 문제의 RAG Workflow/Agent 차이 |
| Tool Schema·Registry·검증 | 모델이 함수 코드를 자동 실행하지 않음을 Tool 요청으로 확인한다. | 잘못된 Tool/인수/권한 요청의 거부 |
| State·Observation·종료 | 검색·원문 확인·답변/추가 질문/중단을 제한 안에서 선택한다. | 실제 선택·Tool 결과·종료 이유 Trace |
| Single-Agent 평가와 Framework 포팅 | 직접 Runtime으로 경계를 이해한 뒤 Framework에서도 같은 계약을 유지한다. | 공통 Golden/Trace 계약 비교와 API 검증 기록 |

### K2-11. 역할을 나누는 Multi-Agent

같은 기준선에서 역할별 선택·정보 전달·검토의 효과와 비용을 비교한다.

선수 과목: K2-10 · 원문 연결: P2-09 · P2-12 · 분석 근거: F27 · F28 · F29

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 역할 분리가 필요한 문제 | Single-Agent로 충분한 경우와 독립적인 검색·작성·검토가 필요한 경우를 구분한다. | Single/Multi 선택 이유와 기대 효과 |
| 역할별 상태·Tool·입출력 | 역할 이름 외에 행동 선택·Context·권한·산출물·종료 책임을 분리한다. | 세 역할의 실행 계약과 Handoff 기록 |
| 검토와 한 번의 보완 | 검토자가 근거 부족을 되돌리고 상한 내에서 수정/기각한다. | 판정·보완 요청·종료 사유 |
| 실패 전파와 동일 조건 비교 | 잘못된 전달·타임아웃·동일 실패·비용 증가를 관찰한다. | 같은 18개 Case의 품질/호출/시간 비교 |

### K2-12. Fine-tuning의 학습과 평가

실제 Parameter 적응·저장·재로드·평가를 별도 학습 실험으로 수행한다.

선수 과목: K2-01 · K2-03 · K2-04 · K2-06 · 원문 연결: P2-10 · Q33 · D3-02 · 분석 근거: F14 · F29 · F34

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 학습 목표와 Parameter 전략 | SFT/Instruction/선호 목표와 Full/Partial/LoRA/QLoRA 전략을 분리한다. | 목표×전략 표와 선택 근거 |
| 작은 Task의 Baseline과 Dataset | 고정 Prompt/Decoding·Train/Validation/Test·누수·Chat Template/Loss 범위를 정한다. | 분리된 데이터 목록·원본 기준선 |
| 실제 학습과 자원 기록 | 고정 Base에서 학습 가능한 Parameter와 Optimizer Step을 확인한다. | 실제 학습 로그·설정·메모리·Adapter |
| 저장·새 프로세스 Reload·회귀 | Adapter를 다시 로드해 같은 Test와 일반 능력/안전 사례를 비교한다. | Base/Tuned/Reload 결과·회귀와 실패 해석 |

### K2-13. OCR·Multimodal과 문서 입력 품질

문서 입력의 오류가 검색과 답변으로 어떻게 전파되는지 확인한다.

선수 과목: K2-09 · 원문 연결: P2-11 · P2-13 · 분석 근거: F15 · F17

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| PDF 유형·Parsing·OCR 선택 | Digital/Scanned/Mixed를 구분하고 필요한 경로를 선택한다. | 입력별 처리 경로와 추출 결과 |
| Layout·표·Reading Order | 제목·표 머리글·행/열·페이지 위치를 보존한다. | 의미가 깨진 추출의 전후 비교 |
| OCR와 Vision의 품질·한계 | CLIP의 표현/매칭과 VLM의 생성, OCR-free·Layout-aware 접근을 구분한다. Confidence·CER/WER/필드·표·순서와 Vision 환각을 별도로 평가한다. | 인식/표현/생성 경로 비교·단계별 오류표·Review 조건 |
| 문서 안의 지시·권한·원문 추적 | 추출 내용은 자료로 다루고 Locator와 권한을 이어간다. | Injection/권한 사례와 원문 연결 증거 |

### K2-14. Document AI 통합과 보고서 생성

누적 앱에 문서 구조·검토·생성·서비스 운영 계약을 통합한다.

선수 과목: K2-11 · K2-13 · 원문 연결: P2-12 · P2-13 · ARCH · REACT · FASTAPI · 분석 근거: F16 · F17 · F18 · F21 · F33

| 학습 단위 | 새로 배우는 것 | 학생이 제출할 근거 |
|---|---|---|
| 형식·원본·공통 문서 구조 | Hash/Version·PDF/DOCX/HWPX/HWP의 차이를 DocumentElement/Record/Locator로 연결한다. | 원본→IR→Chunk의 매핑과 지원/미지원 명세 |
| 문서 상태·권한·삭제 | Upload부터 Index/Review/삭제·재색인의 상태와 Idempotency를 정한다. | 권한/삭제/구버전/중복 작업 검사 |
| 근거·검토·문서 생성 | Claim별 Citation과 검토 결과를 DocumentSpec·Template 기반 DOCX/PDF 산출물로 연결한다. | 원문에서 보고서까지 추적·형식/내용/레이아웃 검사 |
| Provider 기능과 운영 예산 | Capability·Routing/Fallback·Readiness·Context/시간 예산·Trace를 기존 앱에 추가한다. | 기능 불일치·Timeout·Fallback의 계약 검사 |
| React와 Streaming 통합 | SSE를 공통 Parser로 읽고 대기·취소·오류·최종 판정을 표시한다. | 잘린 이벤트·오류·종료·취소의 통합 결과 |
| 다중 형식 확장과 최종 평가 | 세 형식 이상·OCR/Vision·HWP/HWPX·보고서 출력 범위를 점진 확장한다. | 지원 형식별 Golden 문서·실패·비용·최종 배포 전 검토 |

</details>

<details>
<summary>기존 Phase2 13과목의 내용은 어디로 이동하는가?</summary>

주교안 42개와 3단계 판단 35건 모두 연결 대상을 기록했다. 아래는 Phase2의 이동표이며, Phase1 24교시와 아키텍처·개발 기초는 기반/선수 경로로 보존한다. 실제 원문을 이동·삭제한 상태는 아니다.

| 기존 과목 | 새 연결 | 처리 의도 |
|---|---|---|
| [P2-01 AI 최신 동향 및 전체 지도](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/01.%20AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84/AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1091-L1101) | K2-00 · K2-14 | 전체 지도 반복을 시작 안내로 압축하고 Lifecycle·Responsible AI는 보존. |
| [P2-02 AI·머신러닝·딥러닝 개요](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1432-L1442) | K2-00 · K2-01 · K2-02 · K2-03 | 데이터·평가를 중심에 두고 Diffusion의 짧은 비교는 K2-00, 신경망/위치 정보는 K2-02, 사전학습 연결은 K2-03으로 이동. |
| [P2-03 Transformer](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3355-L3365) | K2-02 | 내부 계산·구조·Mask·KV Cache 보존. 역사·일반 GPU 설명은 Phase1 참조. |
| [P2-04 LLM](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2643-L2653) | K2-03 · K2-05 | LLM 고유 동작과 Context/Memory 실습을 구분. |
| [P2-05 Prompt Engineering](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L787-L797) | K2-04 · K2-05 · K2-06 | 지시 설계·Context 구성·검증/개선 실행의 소유 위치를 분리. |
| [P2-06 Embedding](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L840-L850) | K2-07 | 검색용 표현·검색 품질·Migration을 보존. |
| [P2-07 VectorDB](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L767-L777) | K2-08 | 검색 인덱스와 운영 중심으로 제목/설명 정리. |
| [P2-08 RAG](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1017-L1027) | K2-09 · K2-05 | RAG 종단 Trace와 Context 구성으로 연결. 관리형 제품 사례는 비교 보충. |
| [P2-09 Agent](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L513-L523) | K2-06 · K2-10 · K2-11 | Runtime 공통 기반·Single 실행·Multi 역할 분담을 분리하고 파일 내부 중복을 통합. |
| [P2-10 Fine-tuning](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1002-L1012) | K2-12 | 실제 학습·Reload·평가 목표를 별도 실험 트랙으로 보존. |
| [P2-11 OCR/Multimodal](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1440-L1450) | K2-13 · K2-14 | 입력 인식 품질과 공통 문서 구조/프로젝트 통합을 연결. |
| [P2-12 AI Integration](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1282-L1292) | K2-06 · K2-10 · K2-14 | 기본 Provider 앱은 재사용하고 Harness·Framework 실행·운영 통합을 각 위치에서 확장. |
| [P2-13 Document AI](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1452-L1462) | K2-13 · K2-14 | 한 디지털 형식의 첫 완성과 세 형식 이상·OCR/HWPX·보고서 확장의 완료 기준을 분리. |

주요 보존 항목은 다음과 같다. 특히 기존에 고유 성과로 확인한 항목을 새로운 제목 아래에서 빠뜨리지 않도록 단원까지 연결했다.

| 보존할 성과 | 구체 위치 |
|---|---|
| Split·일반화·누수·업무 지표 | K2-01 |
| 신경망 한 층·Weight/Bias/Activation의 계산 | K2-02.U01 |
| QKV·내적/스케일링/Softmax·가중합·Block | K2-02.U02 · K2-02.U03 |
| Mask·Encoder/Decoder·학습/생성·KV Cache | K2-02.U04 · K2-02.U05 |
| Causal LM·Post-training·Decoding·환각/평가 | K2-03 |
| Shot·CoT 한계·Self-Consistency·ReAct·Golden/Regression | K2-04 · K2-06.U02 |
| 출처/권한·선택·순서·예산·State/Memory | K2-05 |
| Schema·State·Trusted Permission/Approval·기록/종료 | K2-06 |
| 실패 ID·부분 보완·같은 평가·회귀·상한/종료 | K2-06.U03 · K2-06.U04 · K2-06.U05 |
| 검색/내부 표현·Dense/Sparse/BM25·Hybrid/Rerank·재색인 | K2-07 |
| Exact/ANN·HNSW/IVF·Filter·갱신/삭제 | K2-08 |
| Offline/Online·구조 Chunk·Grounding/Citation·권한/버전/평가 | K2-09 |
| Schema/Runtime·State/Observation·MCP·권한/종료 | K2-10 |
| 역할별 선택/상태/전달/검토·Single 기준선 | K2-11 |
| 목표×Parameter 전략·Full/Partial/LoRA/QLoRA·Dataset/Baseline | K2-12.U01 · K2-12.U02 |
| 실제 훈련·Adapter 저장·새 프로세스 Reload·회귀 | K2-12.U03 · K2-12.U04 |
| PDF 유형·Parsing/OCR·Layout/표/순서·CER/WER/Field/Review | K2-13 |
| 형식별 처리·IR·Locator·문서 권한/상태·HWP/HWPX | K2-14.U01 · K2-14.U02 · K2-14.U06 |
| Claim 인용·Review·DocumentSpec/Template·DOCX/PDF 생성/검수 | K2-14.U03 |
| Capability·Readiness·Budget·Trace·Routing/Fallback | K2-14.U04 |
| SSE 계약·UI 취소/대기/오류·Parser/종료 | K2-14.U05 |
| 업무/실패·Lifecycle·Responsible AI·동향 시점 | K2-00 |
| 위치 정보·Positional Encoding/RoPE의 필요성과 구조별 차이 | K2-02.U04 |
| Diffusion의 생성 접근 소개와 구조/생성 방식 분류의 구분 | K2-00.U03 |
| CLIP/VLM·OCR-free·Layout-aware의 역할과 품질 차이 | K2-13.U03 |

Q&A 33개에 대한 기존 처리 목록도 이어받았다. Phase1 대상은 유지하고 Phase2 대상은 위 이동표로 연결한다. Transformer 대본은 K2-02의 강사 보충, 빈 FastAPI 메모와 LLM 편집 요청문은 교육 본문과 구분한다. 특정 모델 공개현황과 Transfer Learning·Prompt/RAG의 용어 경계는 기술 검증 대기 항목으로 유지했다.

원문별 상세 분석은 [3단계 분석 검토본](https://github.com/cocoa2260/k-edu/blob/be205182880a445cabbd08bb3eda06e02c454904/curriculum-work/reports/KEDU-ANALYSIS-001/20261030T080144Z/REVIEW.md)에서 확인할 수 있다. 이 구성안이 원문이나 그 분석 기록을 덮어쓰지 않는다.

</details>

<details>
<summary>실습 단계별 입력·변경점·출력·완료 조건</summary>

### L0. Phase1 앱을 기준선으로 고정

이어받을 단계: Phase1 기준 앱 · 담당 과목: K2-00

| 항목 | 설계 |
|---|---|
| 추가할 기능 | Day3 7~8교시의 Provider/Service/React 계약을 준비 상태로 확인 / 같은 앱의 작업 디렉터리·환경·버전·실패 위치를 기록 |
| 산출물 | 기준 커밋/환경표 / Fake 계약 검사 결과 / 실제 Provider 준비 결과를 별도 표시 |
| 완료 확인 | G-PY/G-API 충족 또는 해당 보충 완료. UI 미이수는 CLI 경로를 허용하고 UI 완료는 미표시 / 기존 /ai/chat 계약을 확인 / Fake 성공을 실제 모델 실행으로 기록하지 않음 |
| 실제 모델/도구의 증거 | 실제 Provider 준비는 G-MODEL에서 별도 검사. L0의 Fake 계약 통과만으로 실제 모델 검증을 뜻하지 않음. |

### L1. Prompt·Context를 같은 질문으로 비교

이어받을 단계: L0 · 담당 과목: K2-04 · K2-05

| 항목 | 설계 |
|---|---|
| 추가할 기능 | 가상 규정과 질문·근거를 수동 입력 / Prompt v1/v2와 Context 선택·순서를 통제 |
| 산출물 | Prompt/Context 버전 / core-v1 12개 사례의 전후 결과 / 입력 Token/자료 선택 사유 |
| 완료 확인 | 질문·정답 근거·금지 행동을 고정 / 한 번에 한 조건 변경 / 형식과 사실/근거를 별도 채점 |
| 실제 모델/도구의 증거 | G-MODEL 통과 뒤 같은 실제 모델/설정으로 비교. Fake는 검사 준비용으로 별도 표기. |

### L2. 검증·중단·보완이 있는 Harness

이어받을 단계: L1 · 담당 과목: K2-06

| 항목 | 설계 |
|---|---|
| 추가할 기능 | Provider Adapter·출력/근거 검사·Trace·상한 / 형식 보완과 버전 간 품질 개선을 구분 |
| 산출물 | 입출력 계약·검사기 / 실패 ID와 보완/중단 Trace / 고정 사례의 회귀 결과 |
| 완료 확인 | 미지원 응답/상한/동일 실패에서 종료 / 모델 인수로 승인/권한 변경 불가 / 실패 상태를 정상 답변으로 바꾸지 않음 |
| 실제 모델/도구의 증거 | Fake로 경계를 확인하고 실제 모델 경로에서도 정상·보완·안전 종료를 관찰. |

### L3. 검색용 표현과 Index를 추가

이어받을 단계: L2 · 담당 과목: K2-07 · K2-08

| 항목 | 설계 |
|---|---|
| 추가할 기능 | Chunk/Metadata/권한·버전 / 정확 검색 기준과 Dense 검색, 선택적인 Hybrid/ANN 비교 |
| 산출물 | Index Manifest / 질문-정답 문서 쌍 / 권한/구버전 Filter 결과·검색 품질표 |
| 완료 확인 | 검색용 Embedding 모델/리비전·차원 기록 / 권한 밖 문서가 모델 Context와 결과에 들어가지 않음 / 삭제/모델 변경 시 재색인 검증 |
| 실제 모델/도구의 증거 | 실제 Embedding/검색 경로를 확인. 답변 생성 모델 호출은 이 단계의 필수 증거가 아님. |

### L4. 근거 답변을 만드는 RAG

이어받을 단계: L3 · 담당 과목: K2-09

| 항목 | 설계 |
|---|---|
| 추가할 기능 | 고정 검색 Workflow로 Context 구성 / Claim별 Citation과 자료 없음/버전 충돌 처리 |
| 산출물 | 질문→검색→Context→답변 Trace / 정답 근거와 보류 결과 / Retrieval/Generation 분리 평가 |
| 완료 확인 | core-v1 12개를 같은 기준으로 실행 / 인용은 실제 Source Locator로 연결 / 조회 실패와 생성 실패를 구분 |
| 실제 모델/도구의 증거 | 실제 검색+실제 생성 모델의 종단 실행이 있어야 실제 RAG 실행 확인. Mock 전체 통과는 별도. |

### L5. RAG를 사용하는 Single-Agent

이어받을 단계: L4 · 담당 과목: K2-10

| 항목 | 설계 |
|---|---|
| 추가할 기능 | search_documents/read_evidence 두 읽기 Tool / 모델의 도구/최종 답변/추가 질문/중단 선택 |
| 산출물 | Agent State·Tool 요청/검증/Observation Trace / core 12+agent 6의 결과 / 호출 수·종료 이유 |
| 완료 확인 | 도구를 안 써도 되는 질문에서 불필요 호출 비교 / 잘못된 Tool/인수·Timeout·반복에 유한 종료 / 권한 판단은 Runtime에서 적용 |
| 실제 모델/도구의 증거 | 실제 모델이 Tool 요청 또는 종료를 선택하고 Runtime이 실행하는 경로를 증명. 수동 ToolCall 예제만으로 완료하지 않음. |

### L6. 검색·작성·검토 역할을 분리

이어받을 단계: L5 · 담당 과목: K2-11

| 항목 | 설계 |
|---|---|
| 추가할 기능 | 역할별 Context/State/Tool/판정 / 근거 부족의 한 번 보완과 전체 호출 상한 |
| 산출물 | 세 역할과 Handoff 계약 / Single/Multi 동일 18개 사례의 비교 / 전달 오류·검토 반려·상한 종료 검사 |
| 완료 확인 | role label 외에 선택 가능한 행동·관찰·종료 책임 존재 / 동일 모델/문서/질문/채점 기준 사용 / 추가 4개 Handoff 검사는 품질 비교 분모와 분리 |
| 실제 모델/도구의 증거 | 세 역할 모두 실제 모델 경로에서 선택과 종료를 기록. 하나의 모델 프로세스를 순차 호출하는 구성을 우선. |

### L7. 실제 Fine-tuning·Reload 실험

이어받을 단계: L2 · 담당 과목: K2-12

| 항목 | 설계 |
|---|---|
| 추가할 기능 | 문서 질문 유형 분류의 별도 작은 SFT Task / 동일 Base/Prompt/Decoding으로 학습 전후·Reload 비교 |
| 산출물 | 분리된 Train/Validation/Test Manifest / Optimizer Step·자원·Adapter 로그 / 새 프로세스 Reload·Base/Tuned/회귀 결과 |
| 완료 확인 | 실제 훈련 단계/학습 가능한 Parameter/Adapter 저장 증거 / Test를 학습/튜닝 선택에 사용하지 않음 / 좋아지지 않은 결과도 정확히 기록하고 원인 설명 |
| 실제 모델/도구의 증거 | G-TRAIN 통과가 필요. 추론 API 호출이나 이론 설명만으로 훈련 완료라고 하지 않음. 개인/조별/시연 운영은 장비 검증 후 결정. |

### L8. 실제 문서의 추출·인식 품질을 연결

이어받을 단계: L4 · 담당 과목: K2-13

| 항목 | 설계 |
|---|---|
| 추가할 기능 | Digital PDF 한 형식의 Parsing을 우선 연결 / 스캔/OCR·표/순서·Vision 비교를 추가 |
| 산출물 | 원본/Hash·추출/IR·Locator / 인식 오류가 검색/답변에 미친 영향 / Review 기준과 결과 |
| 완료 확인 | 원본과 정규화 Text를 분리 / OCR 숫자·표 관계 오류를 답변으로 전파하지 않도록 확인 / 입력 유형별 지원/미지원/실행 상태 표시 |
| 실제 모델/도구의 증거 | 실제 Parser/OCR 실행을 각각 기록. Vision을 호출하지 않은 결과를 Multimodal 모델 검증으로 쓰지 않음. |

### L9. 문서 검토·보고서·서비스 통합

이어받을 단계: L6 · L8 · 담당 과목: K2-14

| 항목 | 설계 |
|---|---|
| 추가할 기능 | 기존 앱에 문서 상태·Review·보고서 생성·SSE Parser 연결 / 다중 형식·Provider Capability·Audit 확장 |
| 산출물 | 원문→답변→Review→DOCX/PDF의 추적 결과 / UI/Stream/오류/취소·권한 검사 / 형식별 실행표와 최종 평가 |
| 완료 확인 | 첫 완성은 한 디지털 형식으로 끝까지 연결 / 세 형식 이상과 OCR/HWPX 등은 별도 확장 완료표로 보존 / DOCX/PDF는 내용·출처·레이아웃을 별도 확인 |
| 실제 모델/도구의 증거 | 선택한 실제 Parser/모델/생성 도구로 종단 검증. 서비스 배포나 실제 사용자 데이터 투입은 별도. |

</details>

<details>
<summary>Multi-Agent 역할·전달·상한과 Loop의 의미</summary>

### 세 역할의 계약

하나의 모델 프로세스를 역할별 Context로 순차 호출하는 구성을 우선한다. Orchestrator는 전달·검증·상한을 집행하는 프로그램이며 별도의 Manager 모델을 추가한 것으로 세지 않는다. 순차 실행도 역할별 선택과 State를 분리하면 학습할 수 있지만, 실제 자원 적합성은 검증해야 한다.

| 역할 | 목표·선택 | 도구 | 입출력 | 역할 모델 호출 상한 |
|---|---|---|---|---|
| 검색 담당 | 질문을 뒷받침하는 허용된 최신 근거를 찾는다. query_or_rewrite · read_candidate · request_clarification · finish_evidence · stop | search_documents · read_evidence | question · trusted_scope · allowed_document_versions → evidence_bundle · missing_information · search_trace | 4 |
| 작성 담당 | 받은 근거로 답하거나 근거 부족/조건 불명확을 판단한다. read_selected_source · draft_answer · request_evidence_once · ask_clarification · stop | read_evidence | question · evidence_bundle · answer_contract → answer_draft · claim_citations · evidence_request | 2 |
| 검토 담당 | 주장·인용·권한·조건을 확인해 통과/한 번 보완/기각을 판정한다. inspect_claim · approve_draft · request_repair_once · reject · stop | read_evidence · validate_citations | question · answer_draft · claim_citations · rubric_version → verdict · failure_ids · repair_request | 3 |

검색자는 질의/재검색·원문 확인·근거 부족/완료를, 작성자는 근거 확인·초안/추가 근거 요청·질문/중단을, 검토자는 근거 확인·통과/보완/기각을 선택한다. 단순히 정해진 문장 한 번씩 생성하는 과제라면 역할 Workflow로 표시하고 Multi-Agent 구현 완료로 채점하지 않는다.

### Handoff에서 검사할 것

run_id·role_id·question_id·자료 버전·evidence_ids·claim_citations·상태·failure_ids·사용한 예산을 전달한다. 다음 역할은 전달된 ID가 실제 Manifest에 있고 현재 사용자 권한/버전에 맞는지 확인한다. 전체 대화와 모든 문서를 무조건 복사하지 않는다. 권한·승인 상태와 예산 한도는 Runtime이 보유하며 모델 출력으로 변경하지 못한다.

전달되는 사용 예산은 Runtime이 작성한 스냅샷이다. 역할이 그 값을 다시 만들어 실제 카운터를 덮어쓰지 못한다. 작성자의 추가 근거 요청과 검토자의 보완 요청은 하나의 전체 보완 카운터를 공유한다. 역할별 호출 상한과 전체 8회 상한 중 먼저 닿는 조건을 적용하며, 역할별 상한을 더해 전체 호출 수를 늘리지 않는다.

### 초기 실행 상한 — 성능 측정값 아님

| 항목 | Single-Agent | Multi-Agent |
|---|---|---|
| 전체 모델 호출 | 최대 4회 | 최대 8회 |
| 전체 Tool 실행 | 최대 3회 | 최대 6회 |
| 보완 | 최대 1회 | 추가 근거 요청과 검토 반려를 합쳐 전체 최대 1회 |
| 동일 실패 재발 | 보완 뒤 남으면 중단 | 보완 뒤 남으면 중단 |
| 전체 실행 상한 | 120초 | 240초 |
| 모델 동시 호출 | 한 번에 1개 | 한 번에 1개 |

이 값은 실측 전의 교육용 출발 상한이다. 모델/장비 검증 후 명세 버전을 바꾸어 조정하며, 이 시간 안에 항상 답한다는 약속이 아니다. 통신 재시도 최대 1회도 전체 호출·시간 예산에 포함한다. 권한·잘못된 Schema·없는 Tool·동일 실패는 통신 재시도로 숨기지 않는다. 다운로드·초기 로딩과 요청 처리는 측정 구간을 구분해 기록한다.

### 반복을 구분하는 수업

| 반복 | 목적 | 확인할 것 |
|---|---|---|
| 통신 재시도 | 일시 장애의 복구 | 같은 작업/중복 실행·횟수·시간 |
| 형식/근거 보완 | 정해진 검사 실패를 제한적으로 수정 | 실패 ID·수정한 부분·같은 기준 재검사 |
| Self-Consistency | 여러 후보를 생성해 집계/검증 | 샘플 수·답 추출·집계·추가 비용 |
| 버전 간 개선 Loop | Prompt/Context/설정 변경의 효과를 판단 | 고정 평가·변경 원인·회귀·채택/복구 |
| Fine-tuning Training Loop | 학습 신호로 Parameter를 적응 | Loss·Optimizer Step·Parameter·저장/Reload |

검사 통과를 위해 평가 기준을 낮추지 않는다. 감사 기록에는 선택한 행동·검증·관찰·종료 이유를 남기며, 모델의 숨은 사고 과정을 추출하는 것을 목표로 삼지 않는다.

</details>

<details>
<summary>예정 데이터·평가 사례·훈련 실험</summary>

자료 파일과 정답 데이터는 아직 생성하지 않았다. 아래는 제작할 Fixture와 평가 집합의 설계다. 가상 수치·조건을 확정할 때 문서 버전과 정답 근거를 함께 고정한다.

| 자료 ID | 용도 | 권한·버전 |
|---|---|---|
| DOC-A | 현행 출장 규정 | staff / 현행 |
| DOC-B | 현행 교육비 규정 | staff / 현행 |
| DOC-A-OLD | 구버전 출장 규정 | staff / 구버전 |
| DOC-R | 가상 제한 문서 | restricted / 현행 |
| DOC-I | 악성 지시가 포함된 가상 문서 | staff / 현행 |
| DOC-T | 표·레이아웃 문서 확장용 | staff / 현행 |

| Case | 유형 | 질문/실패 상황 | 기대 행동 |
|---|---|---|---|
| C01 | core-v1 | 규정에 명시된 조건/금액 질문 | 정확한 값과 원문 근거 |
| C02 | core-v1 | 교육비 신청 조건 질문 | 조건과 예외를 구분해 인용 |
| C03 | core-v1 | 근거가 없는 질문 | 자료 부족을 표시하고 지어내지 않음 |
| C04 | core-v1 | 조건이 모호한 질문 | 필요 조건을 되묻거나 범위를 명시 |
| C05 | core-v1 | 구버전/현행 규정이 함께 검색 | 기준 날짜/현행 메타데이터를 확인하고 충돌 표시 |
| C06 | core-v1 | 열람 권한 밖 자료를 요청 | 검색·Context·답변에서 배제, 비공개 내용 노출 없음 |
| C07 | core-v1 | 문서 안의 악성 지시 | 지시로 실행하지 않고 자료로만 처리 |
| C08 | core-v1 | 키워드와 표현이 다른 질문 | 정답 문서 검색 여부와 근거 답변을 따로 채점 |
| C09 | core-v1 | 유사 문서가 섞인 질문 | 다른 규정의 조건을 섞지 않음 |
| C10 | core-v1 | 빈 입력/형식 오류 | 모델 호출 전에 Request 검증으로 거부 |
| C11 | core-v1 | 근거 ID는 맞지만 내용이 불일치 | 주장-근거 관계 실패로 검출 |
| C12 | core-v1 | 문서 갱신/삭제 후 질문 | 이전 Index/권한 정보가 답변에 남지 않음 |
| A01 | agent-v1 | Tool 없이 가능한 요청 | 불필요한 호출과 지연을 비교 |
| A02 | agent-v1 | 자료를 더 읽어야 하는 질문 | 검색→원문 확인의 선택 근거 |
| A03 | agent-v1 | 존재하지 않는 Tool 이름 | 실행 전 거부 |
| A04 | agent-v1 | 잘못된 인수/권한·승인 위조 | 검증·신뢰 상태에서 거부 |
| A05 | agent-v1 | Tool Timeout/일시 오류 | 허용된 재시도와 전체 상한 준수 |
| A06 | agent-v1 | 같은 실패 반복/목표 미완료 | 반복을 멈추고 이유를 기록 |
| M01 | handoff-v1 | 다음 역할에 없는 근거 ID 전달 | Handoff 검사에서 거부 |
| M02 | handoff-v1 | 작성자가 근거 추가를 요청 | 연구자에게 한 번 보완하고 전체 상한 유지 |
| M03 | handoff-v1 | 검토자 반려 후 동일 실패 | 추가 반복하지 않고 review_required/failed로 종료 |
| M04 | handoff-v1 | 역할 Timeout/전체 예산 소진 | 전체 Task를 안전하게 종료하고 부분 결과 구분 |

Prompt·Context·RAG는 core-v1 12개, Single/Multi는 core-v1+agent-v1 18개를 사용한다. Handoff-v1 4개는 Multi의 기능/실패 경계 검사다. 표본이 작은 학습용 집합이며 통계적으로 충분한 성능 평가를 뜻하지 않는다.

훈련 실험은 질문 유형 5개 분류를 별도 Task로 두고 Train 40·Validation 10·Test 20개를 출발 설계로 잡는다. 실제 작성한 문장/그룹이 겹치지 않는지 확인한 뒤 고정한다. 이 수량은 학습·Reload·평가 절차를 이해하기 위한 가상 소규모 설계이며 고품질 모델이 만들어진다는 근거가 아니다.

모델을 실제 학습하고 Adapter를 저장한 뒤 새 프로세스에서 재로드한다. Base/Tuned/Reload를 같은 Prompt·Decoding·Test로 비교하며 형식·라벨·일반 능력/안전 회귀를 분리한다. 좋아지지 않으면 실패 원인을 기록한다. 훈련 환경이 준비되지 않으면 훈련 실습은 미검증이며 다른 과제의 추론 결과로 완료하지 않는다.

</details>

<details>
<summary>공개 API·Streaming·입력 예산의 설계</summary>

### 기존 계약과 확장 계약

L0에서 Day3의 /ai/chat 필드를 먼저 확인해 고정한다. 새 질의 처리는 POST /ai/ask에 question·mode·선택 conversation_id를 받는 확장안으로 둔다. mode는 rag/single/multi이며 사용자 권한은 Runtime 또는 명시적으로 표시한 교육용 인증 Fixture에서 가져온다. 모델이 생성한 actor/allowed_documents/approved 값을 권한의 근거로 쓰지 않는다.

Agent의 요청은 실제 모델이 제공자의 지원되는 Tool Calling 또는 검증된 구조화 Action 형식으로 선택하게 한다. 두 형식은 같은 Runtime ToolCall 계약으로 변환한다. 모델 출력이 잘못되면 거부/보완/중단하며, 프로그램이 임의로 성공한 모델 결정을 만들어 채우지 않는다. 교육용 인증 Fixture로 검증한 권한 경계는 실제 사용자 인증을 구현했다는 뜻이 아니다.

응답은 request_id·run_id·status·answer·citations·model_version·측정 가능한 usage를 연결한다. usage를 얻지 못하면 null로 남긴다. Citation에는 claim_id·document_id·문서 버전·Element/Chunk ID·원문 위치를 둔다. 실패·자료 부족·사람 검토 필요를 정상 답변과 구분한다.

### 공통 Streaming 계약

SSE의 JSON payload를 공통 Parser로 읽는다. start·delta·completed·error를 구분하고 request_id/run_id/type을 연결한다. completed 또는 error 종단 이벤트는 한 번만 보내며 completed에 최종 검증 결과를 담는다. 잠정 delta를 표시한다면 UI에서 잠정 상태를 드러내고 승인된 최종 답변과 구분한다.

잘린 이벤트·한 Chunk의 여러 이벤트·UTF-8 분할·delta 뒤 error·취소·종단 누락을 검사한다. React가 바이트 문자열을 그대로 최종 답변에 누적하는 코드와 FastAPI 이벤트 의미가 충돌하지 않게 한다.

### 입력 예산의 출발값

Context 상한 2,048 Token·출력 여유 256 Token·검색 top-k 3·Chunk 목표 320 Token을 초기 설계값으로 둔다. 실제 모델/Tokenizer/Runtime의 검증된 한도에서 지시·질문·이력·근거·Tool 결과를 함께 계산해야 하며, 이 값만으로 특정 GPU의 적합성을 판단하지 않는다. 초과 시 기록된 우선순위로 자료를 줄이거나 명시적으로 중단한다.

</details>

<details>
<summary>선수학습·환경·기술 검증 게이트</summary>

| Gate | 확인할 것 | 미충족 시 처리 |
|---|---|---|
| G-PY Python 코드 이해 | 함수/클래스/Dictionary·예외·Import·환경 변수 / JSON·파일·Type Hint·가상환경 | Python/실전 Python 보충 뒤 구현. 개념 시연과 학생 실행을 구분. |
| G-API HTTP·FastAPI 계약 | Request/Response·Pydantic·Service/Provider·Mock / 표준 오류·설정·DI·독립 예제 경로 | FastAPI 해당 모듈을 먼저 이수. Module 번호와 교안 위치를 연결. |
| G-UI React 통합 준비 | State/Fetch·대기/오류·취소·CORS / Backend를 먼저 확인한 UI 연결 | L1~L8은 CLI/테스트 Client로 진행할 수 있으나 UI 완료를 주장하지 않음. UI 이수 뒤 L9에서 검증. |
| G-MODEL 실제 추론 경로 | 모델 ID/리비전/형식/양자화/Runtime·Tokenizer / 한국어·출력/Tool Schema·Context·메모리·지연의 실제 확인 / 한 요청과 전체 수업 동시 요청 조건 구분 | Fake는 경계 검사에만 사용. 실제 모델 과제는 미검증으로 남기고 모델/환경을 다시 선정. |
| G-EMBED 실제 검색용 표현 | 검색용 모델/리비전·차원·전처리 / 한국어 질의-정답 문서·권한 Filter·Index 재현 | 키워드 기준 검색으로 동작 분리를 확인하고 Dense 검색 검증은 보류. 서로 같은 실습 완료로 합치지 않음. |
| G-TRAIN 실제 훈련·Reload 환경 | Base·학습가능 Parameter·전략·Split/Template/Loss 범위 / Optimizer Step·Adapter 저장·새 프로세스 Reload / 훈련 메모리·시간과 Base/Tuned/회귀 결과 | 훈련 목표는 유지하되 실행 환경/운영 방식 재검토. 추론 API·이론·가짜 로그로 대체 완료하지 않음. |
| G-DOC 문서 도구와 형식 | 선택 Parser/OCR/생성 도구의 설치·버전·입출력 / 지원 형식별 원문·위치·오류·레이아웃 검수 | 실제 실행한 형식만 완료 표시. HWP 변환/미지원은 명시하고 조용히 Skip하지 않음. |
| G-SPEC 기술 사양·환경 정합성 | FastAPI 본문/requirements의 한 재현 기준 / 모델·SDK·Framework/MCP·Chat Template·라이선스의 공식 현재성 / Transfer Learning과 Prompt/RAG 용어 경계 검토 | 관련 설명/실습은 배포 전 기술 검증 대기. 구성안 준비와 실행 가능 검증을 구분. |

G-UI는 L0에서 준비 상태를 확인하는 진단 항목이며 CLI/테스트 Client의 L1~L8 진행을 막지 않는다. UI 통합을 완료했다고 표시하려면 L9에서 G-UI를 충족해야 한다. 다른 게이트도 실제로 요구되는 단계와 미검증 상태를 함께 기록한다.

특히 기존 FastAPI 본문의 설명 기준과 examples/requirements의 버전 차이, Module27/28 예제 링크, Agent의 승인 예제, Streaming 계약, 모델/SDK/Framework/MCP의 현재성과 Transfer Learning 용어 경계는 제작 전 확인 목록으로 유지한다. 구성안을 작성했다고 해결된 것으로 처리하지 않았다.

</details>

<details>
<summary>제작 방식·후속 파일 구조·이번 설계의 검증 범위</summary>

### 후속 제작 순서

| 순서 | 제작할 것 |
|---|---|
| 1 | Resolve G-SPEC and example path/streaming boundaries |
| 2 | Prepare L0 baseline and frozen dataset/score rubrics |
| 3 | Build/review K2-04~06 with L1/L2 as the first small production batch |
| 4 | Extend L3/L4 and retrieval lessons |
| 5 | Add L5 then L6 without restarting the app |
| 6 | Run L7 on an actually validated training environment |
| 7 | Add L8/L9 and document generation |
| 8 | Complete cross-lesson teaching QA and release packaging |

한 제작 묶음은 강의 설명, 실행 파일, 시작/완료 상태, 고정 데이터/정답, 오류 실습, 실제 실행 기록을 함께 다룬다. 코드 문법 통과·Fake 계약·실제 Provider 호출·내용 품질·수업 가능성을 분리해서 검수한다. 강의의 최초 설명은 충분히 두고 후속에서는 기존 결과와 변경점을 연결한다.

### 제안한 후속 저장 위치

| 위치 | 용도 |
|---|---|
| curriculum-work/curriculum/ | approved index and source mapping |
| curriculum-work/lessons/ | canonical revised teaching sources |
| curriculum-work/practice/document-assistant/ | one cumulative app |
| curriculum-work/practice/document-assistant/data/ | versioned synthetic fixtures |
| curriculum-work/practice/document-assistant/evals/ | rubrics, baseline and results |
| curriculum-work/practice/document-assistant/milestones/ | stage manifests/patch references |
| curriculum-work/reports/ | Work design/build/check records, separate from student runtime traces |

위 표는 후속 구조안이다. 이번에 lessons/practice 앱·Dataset·실습 시작 코드를 생성한 것은 아니다. 한 앱의 단계별 기준 Manifest/패치 또는 Git 이력을 사용하고 모든 단계를 별도 복제 프로젝트로 관리하지 않는다. Work의 제작 기록과 학생 앱의 Runtime Trace도 구분한다.

### 이번 검사가 입증하는 것

구성안의 입력 버전·과목/단원 ID·선수 그래프·실습 연결·고유 성과 보존·역할/상한·자료/평가 집합·미실행 상태를 정적으로 검사한다. 의미 검토는 같은 Work 세션에서 수행하며 독립 교육 평가자가 아니다. 실제 모델·훈련·교육장 성능·강의 시간은 이번 검사의 통과 대상이 아니다. 상세 결과는 운영 기록에 보관한다.

이 구성안에서 새로 바뀌는 것은 추천 목차·역할·제작 기준이다. 기존 academy 원문과 3단계 분석 기록은 보존한다.

</details>

**다음은 구성안 검토 후 5단계의 작은 제작 묶음으로 진행하는 것이다.** 시수·장비·실제 SDK 호환성이 아직 확인되지 않은 부분은 게이트 상태를 유지한다.
