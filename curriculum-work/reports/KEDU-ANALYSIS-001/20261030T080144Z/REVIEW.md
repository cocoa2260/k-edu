# K-Edu 전체 강의 비교·분석 — 3단계 검토본

2026-10-30 · KEDU-ANALYSIS-001 · 기준: GitHub `docs/academy-curriculum-v0.1` / `bc58756866cd6bdee20c102fb54340f21e65ad56`

**결론: Phase1의 기반을 유지하고, Phase2를 “같은 개념의 재소개”에서 “새 원리·검증·누적 구현”으로 전환하는 방향을 추천한다.**

이 문서 하나에서 결과와 판단 근거를 검토할 수 있다. 먼저 1~4를 읽으면 주요 제안과 다음 결정 사항을 볼 수 있고, 상세 근거와 전체 파일별 처리는 아래 접힌 부록에 있다. 실행용 코드나 JSON 예시를 본문에 넣지 않았다.

현재 상태는 **전체 자료를 대상으로 한 개편 방향 분석·검증 완료, 사용자 검토 대기**다. 강의 본문·파일명·목차·시수·실습 코드를 변경한 상태가 아니다. 아래 제목과 배치는 모두 후보이며 승인된 교육과정이 아니다.

## 1. 먼저 볼 여섯 가지 판단

| 구분 | 분석 결과 |
|---|---|
| 유지할 기반 | Phase1은 이미 호출·학습 관찰·모델 선택·Provider 교체·React 통합까지 갖췄다. 이를 입력으로 재사용한다. |
| 반복이 큰 구간 | Phase2-01 전체 지도, 02 기초 개요, 04의 Token/학습 재소개, 12의 기본 Backend 통합은 역할 조정이 필요하다. |
| 남겨야 할 심화 | Attention/Mask/KV Cache, 데이터 분리·누수·평가, 검색 표현·ANN, RAG 근거, Tool Runtime, 튜닝 실험, 문서 구조·인용·생성. |
| 새로 묶을 것 | Prompt·Context·Harness·평가·반복 제어의 재료는 이미 있다. 같은 프로젝트의 변경 전후를 비교하는 누적 실습으로 연결해야 한다. |
| Multi-Agent | 개념 소개는 있다. Single-Agent와 같은 데이터/기준으로 역할 분담의 효과·비용·실패를 비교하는 실행 실습은 별도 제작이 필요하다. |
| 우선 보완 | React/FastAPI Streaming 계약, Tool 승인 경계의 모의 예제, Python 예제 경로, 교안 사이 Unit 참조를 정리해야 한다. |

여기서 중복은 같은 용어가 등장한다는 뜻이 아니다. **설명·예시·도달 목표가 겹치는 부분**을 줄이고, 같은 개념으로 새로운 계산·판단·구현을 하는 부분은 보존한다. 자동 검사로 중복률을 계산해 과목을 삭제하는 방식은 사용하지 않았다.

## 2. Phase2 13개 과목의 추천 역할

다음 표는 개편 방향이며 최종 목차나 수업 순서가 아니다. 과목명 변경·통합·이동은 4단계에서 결정한다.

| 현재 과목 | 반복을 줄일 부분 | 남기거나 확장할 학습 성과 |
|---|---|---|
| 01 AI 최신 동향 및 전체 지도 | AI/ML/DL·제품·도구 목록 재소개 | 문제 선택·AI Lifecycle·평가·운영·Responsible AI. 오리엔테이션/이름 조정 검토 |
| 02 AI·머신러닝·딥러닝 개요 | 기본 정의·구조 발전·Training/Loss 재소개 | **「머신러닝의 데이터 설계와 모델 평가」** 후보. Split·일반화·누수·지표·Pipeline |
| 03 Transformer | 등장 역사·Tensor·GPU 일반론 | QKV 계산·Attention·Mask·내부 구조·생성/KV Cache |
| 04 LLM | Token·Parameter·Training·Base/Instruction 첫 설명 | 학습 목표·Post-training·Decoding·Context/Memory·평가·실행 비용 |
| 05 Prompt Engineering | 기본 역할/요청·JSON 모양 소개 | Prompt 변경 전후 평가·Shot/실행 전략·Injection·Regression·Version |
| 06 Embedding | 벡터의 최초 정의 반복 | 검색용 표현·Dense/Sparse/BM25·Hybrid/Reranking·모델 선택/재색인 |
| 07 VectorDB | 거리·Cosine의 재설명 | Exact/ANN·HNSW/IVF·Metadata/권한·갱신/삭제·검색 품질/속도 |
| 08 RAG | Embedding/DB 전 과정 재정의 | 검색 결과를 Context로 만들고 답변·근거·권한·실패를 연결 |
| 09 Agent | Phase1의 Tool/Framework 소개와 파일 내부 개요 중첩 | Single-Agent Runtime·Schema·State·권한·종료·Trace·평가. 이후 역할 분담 비교 |
| 10 Fine-tuning | 학습/추론·Parameter 전략의 첫 정의 | 작은 Task의 Baseline·Dataset·학습·Adapter Reload·회귀. 훈련 환경은 별도 검증 |
| 11 OCR/Multimodal | Modality 일반 소개 | PDF 유형·OCR/Parsing·표/순서·인식 오류·Vision 한계·Review |
| 12 AI Integration | 기본 API·Service·Provider·UI 재구축 | 기존 앱에 Harness·Capability·Stream/State·Budget·관찰/평가를 추가 |
| 13 Document AI | 일반 OCR/RAG/Agent 개념 재강의 | 형식별 Parsing·공통 문서 구조·Locator/권한·Claim 인용·검토·문서 생성 |

특히 03·06·07·08은 모두 벡터를 다루지만 **모델 내부 계산 → 검색용 표현 → 검색 인덱스 → 근거 답변**으로 결과물이 다르다. 이를 한 과목으로 줄여야 한다는 결론이 아니다. 11과 13도 **입력 인식 품질 → 문서 구조·근거·산출물 통합**으로 역할을 나눌 수 있다.

## 3. Prompt·Context·Harness·Loop·Multi-Agent는 얼마나 있는가?

| 항목 | 현재 자료에 있는 것 | 이번에 확인한 연결 과제 |
|---|---|---|
| Prompt | 설계 기법·출력 검증·Golden Dataset·회귀/버전 | 실행 가능한 Provider·Dataset·평가 결과를 묶고 전후 차이를 설명 |
| Context | Instruction 구분, Window/Memory, RAG Context, State→Context, Budget | 같은 질문에서 선택·순서·출처·예산을 바꾸는 비교 실습 |
| Harness | P2-12의 명시적 소개, Runtime·Tool·State·검증·종료·테스트·관찰 | 최소 실행 구조를 직접 만들고 Fake/실제 모델 경로를 구분해 검사 |
| Loop | 회귀 평가·버전·오류 분리·Retry/Stop·실험 기록이 분산 | 평가→원인→관련 부분 수정→같은 사례 재평가, 반복 상한·종료 이유를 하나로 연결 |
| Multi-Agent | 역할 분담·비용·오류 전파·Single 대비 필요성 소개 | 역할 간 계약·상태 전달·검수·중단을 실행하고 Single 기준선과 비교하는 누적 프로젝트 |

**“개념이 없으니 새 장을 많이 추가하자”가 아니라, 이미 있는 설명을 연결하고 실행 산출물이 부족한 구간을 채우자는 제안이다.** 한 모델에 역할 이름만 바꾸어 세 번 질문하는 것으로 Multi-Agent의 실행 책임·상태 전달을 학습했다고 처리하지 않는다.

## 4. 다음 단계에서 결정할 네 가지

지금 바로 모두 답할 필요는 없다. 4단계에서 아래 안을 실제 목차·실습 설계로 구체화해 검토할 수 있다.

| 결정 | 추천하는 출발안 | 아직 확정하지 않은 것 |
|---|---|---|
| 편집 기준과 과목 역할 | 개별 Phase1 24교시를 기준으로 두고 통합본은 파생본으로 관리. Phase2-01/02/04/12의 반복 역할 조정 | 통합본 처리·최종 과목명·과목 통합/이동 |
| 누적 실습의 중심 | 같은 문서·질문·평가를 유지하며 **RAG → Single-Agent → 역할 분담 비교**로 확장 | 기능별 시작/완료 코드, 역할 수·계약·Framework |
| 필수 범위와 확장 | 먼저 텍스트 또는 한 종류 디지털 문서로 끝까지 완성. OCR·다중 형식·보고서 생성은 확장 단계로 구분 | 현재 Document AI의 최소 3형식 요구를 어디에 둘지, Fine-tuning 필수 범위와 실제 훈련 환경 |
| 선수학습·시간·실행 조건 | Python/HTTP/FastAPI/React 이수·시연·학생 실행을 구분하고 실제 장비에서 단계별 검증 | 최종 시수·수업 순서·모델/리비전·양자화·동시 사용·지연 허용값 |

훈련이 목표인 Fine-tuning은 추론 API 호출로 대체하지 않는다. 저사양 학생 PC에서 어떤 부분을 수행하고 별도 훈련·추론 환경이 필요한지는 실제 검증 후 정한다. 이번 분석만으로 “3~4B면 된다”, “4-bit면 3GB GPU에서 충분하다” 같은 실행 보장을 하지 않았다.

---

## 부록 — 근거가 필요할 때만 펼쳐 보기

<details>
<summary>분석 범위·방법·검증 한계</summary>

### 분석 기준

현재 GitHub의 펼친 교육자료를 기준으로 Markdown **79개**, 독립 Python 예제 **84개**, requirements **1개**, 총 **164개 텍스트 파일**을 수집했다. 각 파일의 바이트로 Git Blob SHA를 재계산해 기준과 일치하는지 확인했다. 보관된 curriculum.zip은 존재를 기록했지만 또 다른 강의 원본으로 펼쳐 합산하지 않았다.

| 분류 | 수량 | 처리 |
|---|---:|---|
| Phase1 GPT/Ollama/Gemma 개별 교시 | 24 | 각 교시의 역할·선수/후속 연결을 비교 |
| Phase2 주교안 | 13 | 과목별 새 학습 성과·중복·실습 연결 비교 |
| 아키텍처 주교안 | 1 | 서비스/자동화 입문과 후속 통합 경계 비교 |
| React·환경 보충·Python·FastAPI | 4 | 전체 구조/개념 검색과 AI 실습에 직접 연결되는 계약·코드 구간 대조 |
| GPT/Ollama/Gemma 통합본 | 1 | 개별본과 차이가 있는 대조본. 추가 24교시로 세지 않음 |
| Q&A·설명류 | 33 | 32개 내용 있는 자료를 연결하고 빈 메모 1개를 별도 표시 |
| Transformer 대본·LLM 편집 메모 | 2 | 보조 자료와 편집 잔여물로 구분 |
| Python 예제 README | 1 | 파일 경로를 실제 tree와 대조 |

**전수의 의미:** 모든 대상 파일의 전체 텍스트를 구조화·검색하고, 주교안 42개에 교육적 역할을 부여하며 개념별로 원문 구간을 대조했다. 각 문장·수식·모든 코드 조각의 정확성을 전부 승인하거나 모든 강의 쌍을 기계적으로 1:1 비교했다는 뜻은 아니다. 세부 설명 교정·수업 시간·실행 성능은 제작/검증 단계에서 확인한다.

본문 전체의 줄 구간을 기계적으로 추적한 기록과 교육적 의미 검토는 구분했다. 자동 검사는 원본·범위 기록·근거·출력 상태의 일관성을 검사하며, 교육적 완성도나 비교 범위의 충분성을 자동 판정하지 않는다. 의미 검토는 같은 Work 세션의 순차 검토이며 독립 평가자가 아니다.

첨부된 세 운영 문서는 2026-10-19 이력이다. 과거의 ZIP 단일 원본·49개 Q&A·AI Integration 32 Unit·Unit32 실습 경로·검사 수치를 현재 결과로 복사하지 않았다. 이번 대화의 GitHub 최신 원본 지시와 현재 파일을 우선했다.

</details>

<details>
<summary>상세 판단 35건과 원문 근거</summary>

### F01. 개별 24교시와 통합본은 서로 다른 본문이다

**확인·판단:** 통합본은 개별 v0.2 파일을 그대로 이어 붙인 동일본이 아니다. 예를 들어 통합본 Day1 8교시는 모듈 최상단에 OpenAI Client를 만들고 모델명을 고정하지만, 개별 교시는 함수 안 생성·환경 변수·Mock 테스트의 이유를 설명한다.

**보존할 성과:** 통합본의 과목 전체 안내와 역사적 비교 가치. 서로 다른 본문을 한 강의 두 개로 집계하지 않는다.

**제안:** 이번 비교는 개별 24교시를 주교안, 통합본을 별도 대조본으로 취급했다. 4단계에서 앞으로 편집할 기준을 명시하고 파생본 생성 방식을 정한다.

근거: [GPT-MERGED L10568–10601](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/GPT_Ollama_Gemma_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L10568-L10601) · [D1-08 L159–188](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L159-L188) · [D1-08 L323–336](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L323-L336)

### F02. Phase2-01: 전체 지도 재설명과 시스템 생명주기 구분

**확인·판단:** AI 포함 관계·생성형 모델·개발 도구 전체 지도를 다시 길게 설명하면 Day1의 역사·전체 지도·모델/제품/도구 구분과 학습 결과가 겹친다.

**보존할 성과:** AI Lifecycle, 업무별 실패 영향, Responsible AI, 동향과 제품 사례의 시점 구분.

**제안:** 전체 지도는 선수학습 확인으로 줄이고, 업무 선택·평가·운영 책임을 묶는 오리엔테이션 역할로 차별화한다. 과목 유지/통합과 이름은 4단계 판단이다.

근거: [D1-02 L181–227](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L181-L227) · [D1-06 L251–283](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_06_%ED%98%84%EB%8C%80_AI_%EA%B0%9C%EB%B0%9C_%EC%83%9D%ED%83%9C%EA%B3%84%EC%99%80_%ED%95%B5%EC%8B%AC_%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%9F%AC%EB%A6%AC_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L251-L283) · [P2-01 L1031–1039](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/01.%20AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84/AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1031-L1039) · [P2-01 L1091–1132](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/01.%20AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84/AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1091-L1132)

### F03. Phase2-02: 기초 개요에서 데이터 설계·평가로

**확인·판단:** 기초 정의, Rule/ML 차이, Feature Engineering, CNN/RNN/Transformer 등장 이유, Training/Inference/Loss의 재소개가 Phase1과 겹친다. 시범 추가 비교의 판단을 현재 원문으로 다시 연결했다.

**보존할 성과:** Sample/Feature/Label 적용, Train/Validation/Test, 일반화·과적합·누수·평가 지표. Activation의 구체 계산과 위치 정보·Diffusion 언급은 일괄 삭제하지 않는다.

**제안:** 「머신러닝의 데이터 설계와 모델 평가」를 제목 후보로 유지한다. 수식·신경망 계산 등 이동 후보는 목적지와 선수지식을 지정한 뒤 편집한다.

근거: [D1-04 L215–394](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L215-L394) · [D2-03 L148–251](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L251) · [P2-02 L1389–1452](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1389-L1452) · [P2-02 L1479–1545](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1479-L1545)

### F04. Transformer: 등장 역사와 내부 계산은 다른 성과

**확인·판단:** CNN→RNN→Attention의 등장 이유와 일반 GPU 소개는 Phase1과 겹치지만, 같은 이유로 Attention 계산과 Mask까지 중복으로 판정하면 심화 내용이 사라진다.

**보존할 성과:** Q/K/V, 내적·스케일링·Softmax·가중합, Multi-head, Residual/LayerNorm/FFN, Encoder/Decoder, Padding/Causal Mask, 학습 병렬화와 순차 생성, KV Cache.

**제안:** 배경은 짧게 연결하고 작은 수치 계산·Shape 추적·Mask 적용·생성 메모리 설명으로 심화한다. GPU 소개는 Day3 하드웨어 결과를 입력으로 재사용한다.

근거: [D1-04 L308–394](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L308-L394) · [D2-02 L353–395](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_02_AI%EC%9D%98_%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%99%80_Tensor_NumPy%EC%99%80_PyTorch_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L353-L395) · [P2-03 L1723–1744](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1723-L1744) · [P2-03 L3355–3388](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3355-L3388) · [P2-03 L3431–3495](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3431-L3495)

### F05. LLM: Token·학습 재소개와 LLM 고유 심화 분리

**확인·판단:** Token/Parameter/Training의 기본 정의와 Base/Instruction의 첫 구분은 Day2 1·3교시와 Day3 2교시에 있다. 다시 기초부터 반복할 필요가 없다.

**보존할 성과:** Causal LM의 학습 목표와 Post-training 연결, Logit→확률→후보 제한→선택, Temperature/top-k/top-p, 환각·불확실성, Context/Memory/검색, Prefill/Decode.

**제안:** Phase1의 Tokenizer 출력과 작은 Training Loop를 선수 결과로 사용하고, LLM 생성·조정·평가·실행 비용에 집중한다.

근거: [D2-01 L112–147](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_01_Language_Model_LLM%EA%B3%BC_Token_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L112-L147) · [D2-03 L321–359](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L359) · [D3-02 L123–174](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_02_Base_Pretrained_Model%EA%B3%BC_Instruction_tuned_Model%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L123-L174) · [P2-04 L2643–2711](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2643-L2711) · [P2-04 L3704–3847](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3704-L3847)

### F06. Prompt: 역할·출력 모양보다 평가 가능한 변경으로

**확인·판단:** Day1 API 실습에 instructions/input, 출력 제약 관찰과 Structured Output 검증이 이미 있다. Prompt 과목에서 Schema의 첫 정의를 장문 반복하는 것은 줄일 수 있다.

**보존할 성과:** Shot의 실제 예시 기준, Prompt 구조가 고정 문법이 아님, CoT 적용 한계, Self-Consistency가 다중 실행 전략이라는 구분, ReAct의 실행 경계, Golden Dataset·Regression·Version.

**제안:** 같은 과제의 Prompt 변경 전후를 같은 사례로 비교한다. Day1의 형식 검증을 재사용하고 근거·내용·보안·회귀 평가를 추가한다.

근거: [D1-07 L541–570](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_07_Cloud_AI_API%EC%99%80_OpenAI_SDK_%EC%8B%A4%EC%8A%B5_v0.2.md#L541-L570) · [D1-08 L468–505](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L468-L505) · [P2-05 L746–825](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L746-L825) · [P2-05 L2877–2923](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2877-L2923) · [P2-05 L3429–3484](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3429-L3484)

### F07. Embedding: 내부 표현과 검색용 표현을 합치지 않기

**확인·판단:** Transformer의 Token Embedding과 검색용 Sentence/Document Embedding은 같은 단어를 쓰지만 입력·학습 목적·평가 대상이 다르다. 통합 삭제 대상이 아니다.

**보존할 성과:** Token ID/Token Embedding/Contextual Representation/검색용 Embedding의 경계, Query/Document 비대칭, Dense/Sparse/BM25, Hybrid·Reranker, 유사도·정규화·차원·재색인.

**제안:** 벡터 수학은 한곳에서 충분히 설명하고, 검색 과목에서는 질문-정답 문서 쌍과 검색 결과를 비교해 검색용 표현의 역할을 입증한다.

근거: [D2-01 L148–191](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_01_Language_Model_LLM%EA%B3%BC_Token_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L191) · [P2-03 L2682–2733](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2682-L2733) · [P2-06 L840–944](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L840-L944) · [P2-06 L1617–1721](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1617-L1721)

### F08. VectorDB: 유사도 재설명보다 인덱스·검색 운영

**확인·판단:** Cosine·거리의 첫 원리는 Embedding과 겹친다. VectorDB는 검색을 저장·가속·필터·갱신하는 책임으로 차별화할 수 있다.

**보존할 성과:** Exact/ANN, HNSW/IVF의 탐색 방식과 설정, Metadata와 권한 Filter, 업데이트·삭제·재색인, Recall/Latency 균형.

**제안:** 동일한 작은 문서 집합에서 Exact 기준 결과와 ANN 결과·필터 적용 전후를 비교하는 실습으로 연결한다. DB 제품 채택은 아직 정하지 않는다.

근거: [P2-06 L1355–1451](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1355-L1451) · [P2-07 L767–984](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L767-L984) · [P2-07 L1095–1157](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1095-L1157) · [P2-07 L1247–1345](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1247-L1345)

### F09. VectorDB의 자극적 제목은 본문 보정과 맞추기

**확인·판단:** 「왜 일반 데이터베이스로는 AI 검색을 할 수 없는가?」라는 Unit 제목이 남아 있지만 바로 아래 주석과 SQL 설명은 관계형 DB의 벡터 검색 가능성을 명확히 보정한다. 본문 전체가 이를 모른다고 보고하면 잘못이다.

**보존할 성과:** SQL은 질의 언어이고 LIKE 조건의 한계가 모든 DB의 한계가 아니라는 기존 설명.

**제안:** Unit 제목을 「의미 검색에 필요한 저장·인덱스·필터는 무엇인가?」 같은 비교 질문으로 바꿀 후보로 기록한다.

근거: [P2-07 L109–111](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L109-L111) · [P2-07 L206–234](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L206-L234)

### F10. RAG: 구성 요소 재정의보다 전체 실패 추적

**확인·판단:** Embedding·VectorDB·Chunking 전체를 처음부터 다시 설명하면 앞 과목과 겹친다. 반면 Offline/Online 연결과 근거 정책·실패 분리는 독립 성과다.

**보존할 성과:** 구조를 보존하는 Chunking, Query Rewrite, 권한 Filter, Retrieval/Generation 평가 분리, Grounding/Citation의 차이, 미확인 답변·버전 충돌 처리.

**제안:** 앞 단계의 인덱스를 입력으로 이어받아 검색→Context→답변→근거 검증을 완성하고, 검색 실패와 생성 실패를 분리해 수정하게 한다.

근거: [P2-06 L1742–1811](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1742-L1811) · [P2-08 L955–1015](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L955-L1015) · [P2-08 L1017–1047](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1017-L1047) · [P2-08 L1101–1237](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1101-L1237) · [P2-08 L1238–1276](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1238-L1276)

### F11. Agent: Phase1의 도구 지도와 실제 실행 구조 구분

**확인·판단:** Day3 6교시는 Framework·Tool·Workflow·Agent의 위치를 이미 소개하지만 구현은 후속으로 남긴다. Phase2에서는 Registry·Schema·State·Runtime·종료·권한을 실제 코드와 Trace로 다룰 이유가 있다.

**보존할 성과:** Model의 요청과 Runtime 실행 구분, Tool Registry와 인자 검증, Context/State/Memory, Human Review, Timeout/Retry/Idempotency, MCP의 연결 역할.

**제안:** Phase1의 정의는 짧게 참조하고 RAG 검색을 읽기 전용 Tool로 감싼 Single-Agent로 확장한다. Framework 없이 핵심 경계를 관찰한 뒤 도입 가치를 비교한다.

근거: [D3-06 L56–68](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_06_AI_Application_Framework_%EC%83%9D%ED%83%9C%EA%B3%84_LangChain%EA%B3%BC_LlamaIndex_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L56-L68) · [D3-06 L226–326](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_06_AI_Application_Framework_%EC%83%9D%ED%83%9C%EA%B3%84_LangChain%EA%B3%BC_LlamaIndex_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L226-L326) · [D3-08 L939–951](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L939-L951) · [P2-09 L513–624](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L513-L624) · [P2-09 L711–789](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L711-L789)

### F12. Agent 과목 내부에도 중첩된 개요가 있다

**확인·판단:** 앞의 Part 1~14 뒤에 다시 Unit 1·보강 학습이 이어지며 Workflow/Agent·Tool Calling·반복·권한을 재설명한다. 외부 과목 간 중복 외에 한 파일 내부 편집도 필요하다.

**보존할 성과:** 앞 부분의 상세 Runtime·평가와 뒤 부분의 비유·학생 활동 중 독립적인 설명 가치.

**제안:** 앞의 실행 구조를 주 흐름으로 삼고, 뒤의 유효한 비유·확인 질문·반례를 해당 위치에 통합하는 후보를 만든다. 단순 뒷부분 전삭제는 하지 않는다.

근거: [P2-09 L240–307](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L240-L307) · [P2-09 L1650–1689](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1650-L1689) · [P2-09 L1801–1834](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1801-L1834) · [P2-09 L2570–2608](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2570-L2608)

### F13. Tool 인자가 승인 근거가 되어서는 안 된다

**확인·판단:** 교육용 Registry 예제는 approved 값을 ToolCall.arguments에서 받아 함수로 전달한다. 원문 그대로 실행한 뒤 approved=True를 넣자 모의 함수가 created를 반환했다. 이 예제만으로 독립적인 사람 승인을 구현했다고 가르칠 수 없다.

**보존할 성과:** 원문은 모의 실행 예제임을 밝히며 approved=False의 차단을 보여준다. 실제 일정 시스템을 호출하는 코드가 아니다.

**제안:** 제작 단계에서 승인 상태는 신뢰하는 Runtime/사용자 상태에서 읽고, 모델이 만든 인자로 승인 값을 덮어쓰지 못하도록 바꾼다. 승인 위조 입력 거부를 완료 조건에 넣는다.

근거: [P2-09 L1264–1338](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1264-L1338) · [P2-09 L2584–2598](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2584-L2598)

### F14. Fine-tuning: 개념 구분은 재사용하고 학습 실험을 보존

**확인·판단:** Training/Inference·Base/Instruction·메모리의 첫 설명은 Phase1과 겹친다. Q&A에는 Full/Partial/LoRA/QLoRA와 Trainer 설명도 있다. 하지만 실제 적응 목표·데이터·학습/재로드·회귀 평가는 별도 성과다.

**보존할 성과:** 학습 목적과 Parameter 전략을 분리하는 축, Baseline, 분리·누수, Chat Template/Loss 범위, Adapter 저장/Reload/Merge, Base 대비 업무 성능·일반 능력 회귀.

**제안:** 작은 Task의 학습 전후 비교와 Adapter 재로드를 산출물로 삼는다. 훈련 실습을 유료 추론 API 호출로 대신했다고 처리하지 않는다. 실습 장소·모델·필수/선택 여부는 환경 검증과 함께 결정한다.

근거: [D3-02 L123–174](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_02_Base_Pretrained_Model%EA%B3%BC_Instruction_tuned_Model%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L123-L174) · [Q33 L181–248](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%26A.%20Fine-tuning,%20Full%20Fine-tuning,%20LoRA,%20QLoRA.md#L181-L248) · [P2-10 L1002–1081](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1002-L1081) · [P2-10 L1161–1275](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1161-L1275) · [P2-10 L1626–1686](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1626-L1686)

### F15. OCR/Multimodal: 문서 입력 품질의 독립 성과

**확인·판단:** Day1·Day3의 Modality 소개와 같은 범주 설명은 연결로 줄일 수 있다. OCR/Parsing/레이아웃·표·인식 오류 평가까지 중복으로 처리하면 문서 검색의 입력 기반이 사라진다.

**보존할 성과:** Digital/Scanned/Mixed PDF 판별, 추출 순서·표 관계, OCR Confidence 해석, CER/WER/Field/Table/Reading Order 평가, Vision 결과의 환각·보안·사람 검토.

**제안:** 정상 디지털 문서와 스캔 문서의 추출 결과를 비교하고 어떤 오류가 검색·답변까지 전파되는지 추적한다. 모든 입력에 OCR/큰 VLM을 의무 적용하지 않는다.

근거: [D1-05 L315–357](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_05_%EC%83%9D%EC%84%B1%ED%98%95_AI%EC%99%80_Foundation_Model_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L315-L357) · [P2-11 L416–568](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L416-L568) · [P2-11 L1281–1369](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1281-L1369) · [P2-11 L1440–1512](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1440-L1512)

### F16. AI Integration: 이미 만든 Backend를 다시 시작하지 않기

**확인·판단:** Day1 8교시·Day2 8교시·Day3 7~8교시와 FastAPI 후반에 Route/Service/Provider·Cloud/Local 교체·테스트·UI 연결이 이미 있다. P2-12의 같은 기본 구조를 새 프로젝트로 반복하면 중복 제작이 된다.

**보존할 성과:** Capability Matrix, Streaming/Conversation, Tool Gateway, Readiness, 오류·비용·Context Budget, Observability/Evaluation, Harness의 실행 책임.

**제안:** Phase1의 기존 앱에 추가 기능을 붙이는 통합 지점으로 재배치하고 기존 경계의 변화만 설명한다. P2-12를 전체 삭제하는 제안은 아니다.

근거: [D3-07 L775–790](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_07_AI_Provider_%EC%B6%94%EC%83%81%ED%99%94_OpenAI%EC%99%80_Ollama_FastAPI_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L775-L790) · [D3-08 L939–951](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L939-L951) · [FASTAPI L21015–21073](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L21015-L21073) · [P2-12 L9–61](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L9-L61) · [P2-12 L2138–2219](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2138-L2219)

### F17. Document AI: 일반 RAG 반복과 문서 고유 책임 구분

**확인·판단:** OCR·Retrieval·Agent 일반 정의를 다시 길게 배우는 부분은 앞 과목을 참조할 수 있다. 형식별 Parsing, 공통 중간 구조, Source Locator, 표 인용·문서 생성은 통합 프로젝트의 새로운 책임이다.

**보존할 성과:** 원본 불변/Hash, PDF·DOCX·HWPX 구조, DocumentElement/Record, Locator/권한, Claim 단위 Citation, Human Review, Template 기반 DOCX/PDF 생성과 Validation.

**제안:** 공통 검색·Agent 코드는 앞 단계의 산출물을 재사용하고 문서 형식·원문 위치·보고서 생성에 집중한다. 고급 문서 형식과 운영 기능의 범위는 4단계에서 나눈다.

근거: [P2-11 L1063–1088](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1063-L1088) · [P2-13 L1452–1565](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1452-L1565) · [P2-13 L1635–1770](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1635-L1770) · [P2-13 L1996–2091](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1996-L2091) · [P2-13 L2413–2509](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2413-L2509)

### F18. Document AI의 현재 최소 프로젝트도 범위가 크다

**확인·판단:** 현재 종합 프로젝트는 세 가지 이상 문서 형식, OCR/정규화/권한/검색/인용/사람 검토/보고서 생성까지 최소 기능으로 적고 있다. 이것을 RAG→Single-Agent→Multi-Agent의 첫 완성 목표와 동시에 요구하면 범위가 커진다.

**보존할 성과:** 최종 확장 프로젝트로서 다양한 형식·오류·근거 추적을 요구하는 교육 가치.

**제안:** 우선 텍스트 입력 또는 한 종류의 디지털 문서로 동일한 RAG→Agent→역할 분담 비교를 완성하고, OCR·다중 형식·문서 생성은 다음 확장으로 나누는 안을 검토한다. 삭제나 필수 해제는 아직 확정하지 않는다.

근거: [P2-13 L3249–3340](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3249-L3340) · [D3-08 L939–949](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L939-L949)

### F19. 아키텍처 입문과 운영 통합의 설명 깊이 분리

**확인·판단:** ARCH의 Browser/Client/Server·HTTP/JSON·Model/Application·자동화 지도는 초보 입문 기능이다. 같은 전체 구조를 Day1·P2-12·P2-13에서 매번 처음부터 설명하면 반복이 된다.

**보존할 성과:** 웹/AI 요청 경로, DB와 파일 Storage 구분, Workflow/Agent 선택, 실패·Retry·상태 전이의 첫 직관.

**제안:** 입문은 구성요소의 최초 이해로 보존하고 후속 과목은 실제 계약·상태·실패 추적을 다룬다. 원문에 적힌 개별 예제의 계약을 통합 프로젝트의 확정 계약으로 자동 승격하지 않는다.

근거: [ARCH L350–447](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/01.%20AI%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98/AI_%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98_%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.3.1.md#L350-L447) · [ARCH L1516–1538](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/01.%20AI%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98/AI_%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98_%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.3.1.md#L1516-L1538) · [ARCH L2370–2405](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/01.%20AI%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98/AI_%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98_%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.3.1.md#L2370-L2405) · [ARCH L5443–5492](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/01.%20AI%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98/AI_%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98_%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.3.1.md#L5443-L5492) · [P2-12 L290–406](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L290-L406)

### F20. React·Python·FastAPI는 AI 실습의 선수학습이다

**확인·판단:** Day1 7~8교시는 함수·환경 변수·예외·Pydantic·FastAPI·Mock 테스트를, Day2는 Tensor/Import를, Day3는 Protocol/DI·React를 사용한다. 파일 경로의 Phase1 순서만으로 실제 학습 순서를 확정할 수 없다.

**보존할 성과:** Python 15 Unit과 실전 Python 모듈, FastAPI 11~42, React 핵심/상태/Fetch/취소/파일 UI. 같은 HTTP·JSON도 서버 검증과 UI 처리의 역할은 다르다.

**제안:** 4단계에서 이미 이수한 선수학습, 강사 시연, 학생 완전 실행을 구분한다. Module 1~10·27~28은 Python 문서에 있어 빠졌다고 보고하지 않는다.

근거: [D1-07 L48–63](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_07_Cloud_AI_API%EC%99%80_OpenAI_SDK_%EC%8B%A4%EC%8A%B5_v0.2.md#L48-L63) · [D1-08 L89–110](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L89-L110) · [PYTHON L13398–13444](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/Python_for_AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L13398-L13444) · [PYTHON L22549–22564](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/Python_for_AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L22549-L22564) · [FASTAPI L47–91](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L47-L91) · [REACT L13397–13425](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L13397-L13425)

### F21. Streaming 계약이 교안 사이에서 맞지 않는다

**확인·판단:** React Unit34는 /api/v1/streaming-summaries를 FastAPI 교안 기준이라고 연결하면서 받은 바이트 문자열을 그대로 화면에 누적한다. FastAPI Module42는 event/data 형식 SSE와 delta/completed/error Parser를 제시한다. 같은 연결로 쓰면 SSE 제어 정보까지 화면에 나타날 수 있다.

**보존할 성과:** React의 취소·대기·오류 상태와 TextDecoder 사용, FastAPI의 이벤트·종료·오류 의미. React에도 Parser가 추가로 필요하다는 주석이 이미 있다.

**제안:** 제작 단계에서 하나의 공개 Stream Event 계약과 Parser를 사용하고, 잘린 이벤트·다중 이벤트·error·종료·취소를 통합 검증한다. 서로 다른 독립 예제의 Endpoint 이름이 다르다는 이유만으로 오류로 세지 않는다.

근거: [REACT L15576–15631](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L15576-L15631) · [REACT L15645–15657](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L15645-L15657) · [FASTAPI L39789–39799](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L39789-L39799) · [FASTAPI L40810–40835](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L40810-L40835)

### F22. 예제 네 파일은 있지만 여덟 링크가 다른 폴더를 가리킨다

**확인·판단:** Python 본문 네 링크와 examples README 네 링크는 module_27/module_28을 가리키지만 실제 Git tree의 폴더명은 module_27(없음)/module_28(없음)이다. 파일 자체가 없는 문제와 경로 문제를 구분했다.

**보존할 성과:** dataclass_basic/result, composition_basic/provider_injection 네 원본 예제.

**제안:** 해당 네 파일의 배치 또는 여덟 링크를 함께 정리하는 작업으로 기록한다. 전체 84개 Python 예제의 AST 문법 검사는 통과했으나 Import·의존성·서버·모델 실행 검증은 아니다.

근거: [PYTHON L22551–22557](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/Python_for_AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L22551-L22557) · [PYTHON L23371–23377](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/Python_for_AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L23371-L23377) · [EXAMPLES-README L170–178](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/examples/README.md#L170-L178)

### F23. 실행 프로젝트와 Markdown 코드 예시는 구분해야 한다

**확인·판단:** 현재 펼친 academy 트리에서 독립 Python 파일 84개는 모두 Python_FastAPI/examples 아래에 있다. RAG→Agent→Multi-Agent를 누적으로 실행하는 별도 패키지·Dataset·단계별 시작/완료 코드 묶음은 이 트리에서 확인되지 않았다. 각 교안의 코드·설치 지시 자체가 없다는 뜻은 아니다.

**보존할 성과:** Day1~Day3의 파일별 완성 코드·Mock 테스트와 P2의 계산/Registry/Parsing 예시. Prompt 평가 예제의 call_llm은 교체할 자리임을 명시한다.

**제안:** 5단계에서는 설명용 조각·실행용 파일·학생 수정 지점·실제 결과를 표시하고, 4단계에서 정한 누적 프로젝트의 단계별 실행/검증 묶음을 만든다. 저장소 내 ZIP 내부나 외부 실습 폴더의 존재까지 부정하지 않는다.

근거: [REACT L50–55](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L50-L55) · [D3-08 L231–246](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L231-L246) · [P2-05 L3429–3447](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3429-L3447) · [P2-12 L2198–2219](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2198-L2219)

### F24. Context Engineering은 없지 않고 여러 과목에 나뉘어 있다

**확인·판단:** Prompt의 Instruction/Context 구분, LLM의 Context/Memory, RAG의 근거 선택, Agent의 State→Context 구성, Integration의 Context Budget이 이미 있다.

**보존할 성과:** 기존 개념의 올바른 경계와 실제 Context 구성 책임.

**제안:** 새 정의를 반복 추가하기보다 같은 과제에서 어떤 정보·순서·출처·예산을 넣었고 결과가 어떻게 달라졌는지 비교하는 공통 실습으로 연결한다.

근거: [P2-05 L746–757](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L746-L757) · [P2-04 L3793–3819](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3793-L3819) · [P2-08 L1017–1047](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1017-L1047) · [P2-09 L741–765](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L741-L765) · [P2-12 L2078–2106](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2078-L2106)

### F25. Harness는 이미 소개되지만 학습 결과물을 명확히 해야 한다

**확인·판단:** P2-12는 Model+Harness와 Prompt/Tool/Middleware/State/Guardrail을 설명한다. P2-09와 Phase1에는 검증·State·테스트·실행 책임이 있다. Harness라는 이름이 전혀 없다는 진단은 틀리다.

**보존할 성과:** 모델 바깥 Runtime의 인자 검증·권한·상태·종료·테스트·관찰 책임.

**제안:** Framework 이름 암기 대신 Fake Model/Tool로도 검사할 수 있는 최소 실행 구조를 학생 산출물로 삼는다. Runner나 Harness가 프롬프트 문서만으로 구현되었다고 표현하지 않는다.

근거: [D3-07 L584–610](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_07_AI_Provider_%EC%B6%94%EC%83%81%ED%99%94_OpenAI%EC%99%80_Ollama_FastAPI_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L584-L610) · [P2-09 L595–624](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L595-L624) · [P2-12 L1282–1312](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1282-L1312) · [P2-12 L1386–1420](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1386-L1420)

### F26. Loop Engineering: 재시도와 개선을 같은 것으로 세지 않기

**확인·판단:** Prompt 회귀 평가·버전, RAG 실패 분리, Agent 최대 반복·재시도·종료, Fine-tuning 실험 기록은 이미 있다. 그러나 강의 전체를 잇는 평가→원인→부분 수정→재평가의 하나의 누적 실습 계약은 현재 자료에서 확인되지 않았다.

**보존할 성과:** 기존 Golden Dataset·Version·Trace·Stop Condition과 학습 전후 비교.

**제안:** 같은 입력/기준을 고정하고 실패 ID와 수정 대상·반복 상한·종료 이유를 남기는 실습으로 묶는다. Tool을 다시 호출한 횟수나 긴 답변을 품질 개선으로 간주하지 않는다.

근거: [P2-05 L787–825](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L787-L825) · [P2-08 L1238–1276](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1238-L1276) · [P2-09 L2600–2608](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2600-L2608) · [P2-10 L1723–1748](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1723-L1748)

### F27. Multi-Agent: 소개는 있으나 실행 비교 프로젝트는 별도 필요

**확인·판단:** P2-09는 역할 분담과 비용·오류 전파·Single 대비 필요성을 설명한다. 따라서 개념 누락은 아니다. 현재 펼친 트리에 역할 간 입력/출력·상태 전달·검토·중단을 실행하는 별도 Multi-Agent 실습 패키지는 없다.

**보존할 성과:** Single Workflow/Single-Agent 기준선과 여러 Agent가 항상 우월하지 않다는 기존 설명.

**제안:** 같은 문서·질문·평가로 Single-Agent와 검색/작성/검토 역할 분담을 비교하는 작은 실습을 설계한다. Multi-Agent 학습 목표는 유지하되 동시 GPU 모델 여러 개가 필수인 구조로 미리 고정하지 않는다.

근거: [P2-09 L1136–1177](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1136-L1177) · [P2-09 L2435–2450](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2435-L2450) · [D3-08 L939–949](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L939-L949)

### F28. 평가·보안의 반복은 단계별 실패 책임으로 구분

**확인·판단:** 여러 과목에 평가·권한·로그가 반복 등장한다. 같은 원칙 소개는 공유할 수 있지만 Dataset 분리, Retrieval Recall, Tool 승인, OCR 필드 오류는 다른 실패를 검사하므로 일괄 삭제할 수 없다.

**보존할 성과:** 고정 Case ID/문서 버전, 단계별 Metric, 위험 입력·무근거 질문·권한 밖 검색·도구 실패·회귀 사례.

**제안:** 공통 Golden Scenario와 Trace ID를 재사용하되 단계마다 새 검사 항목만 추가한다. 문법·Schema·근거 문자열 일치·내용 타당성·실제 모델 성능을 서로 다른 증거로 표시한다.

근거: [D3-05 L215–238](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_05_AI_Model_Selection%EA%B3%BC_%EC%9A%B4%EC%98%81_Hugging_Face_Model_Card_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L215-L238) · [P2-05 L787–810](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L787-L810) · [P2-07 L1334–1345](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1334-L1345) · [P2-09 L1181–1247](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1181-L1247) · [P2-11 L1440–1512](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1440-L1512) · [P2-13 L2743–2835](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2743-L2835)

### F29. 저사양 가능성은 이번 비교만으로 확정할 수 없다

**확인·판단:** Day3는 Weight와 Runtime 메모리·Context·동시 요청을 분리하고, Agent는 작은 모델도 Tool/Schema/종료를 실제 Task로 평가하라고 설명한다. 특정 B 수나 4-bit 표기만으로 교육장 실행을 보장할 수 없다.

**보존할 성과:** 하드웨어 관찰표, Fake Provider 테스트, 학습/추론 자원 구분. 실제 튜닝 목표가 있으면 훈련·Adapter Reload까지 포함한 환경 검증이 필요하다.

**제안:** 4단계의 구성 결정 후 실제 교육장 조건에서 추론·검색·Agent·튜닝을 구분해 실측한다. 모델 ID/리비전/양자화/입출력 길이/메모리/지연을 기록하며, 유료 API를 기본 해결책으로 정하지 않는다.

근거: [D3-03 L330–392](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_03_Model_Size_Parameter%EC%99%80_Quantization_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L330-L392) · [D3-04 L289–309](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_04_AI_Model_%EC%8B%A4%ED%96%89%EA%B3%BC_Hardware_CPU_GPU_RAM_VRAM_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L289-L309) · [D3-04 L498–532](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_04_AI_Model_%EC%8B%A4%ED%96%89%EA%B3%BC_Hardware_CPU_GPU_RAM_VRAM_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L498-L532) · [P2-09 L1040–1132](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1040-L1132)

### F30. 보충 자료는 이력 수량을 복사하지 않고 현재 내용으로 연결

**확인·판단:** 현재 Markdown 79개 중 Q&A/설명류 33개(빈 FastAPI 메모 1개 포함), Transformer 강의대본, LLM의 짧은 편집 요청 메모, 통합본과 예제 README가 있다. 과거 49개 집계를 이번 완료 건수로 쓰지 않았다.

**보존할 성과:** Dropout/train/eval, safetensors 호환, Framework 실행·관찰, Full/Partial/LoRA/QLoRA 등 실제 보충 성과. 강의대본은 교안과 다른 독립 과목으로 세지 않는다.

**제안:** 부록의 파일별 연결표를 기준으로 본문에 흡수하거나 선택 보충 링크로 남긴다. 빈 파일·편집 요청문은 교육 내용과 구분하고, 특정 모델 공개현황을 단정하는 Q&A는 배포 전 시점 검증 대상으로 둔다.

근거: [Q11 L143–175](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%203%EA%B5%90%EC%8B%9C%2039..md#L143-L175) · [Q15 L1–40](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2031%20-%20%EA%B0%99%EC%9D%80%20parameter%EB%A5%BC%20%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94%20%EB%AA%A8%EB%8D%B8%EC%9D%98%20%EA%B2%BD%EC%9A%B0%20.safetensors%20%ED%8C%8C%EC%9D%BC%EC%9D%84%20%EA%B5%90%EC%B2%B4%ED%95%B4%EB%8F%84%20%EA%B4%9C%EC%B0%AE%EC%9D%80%EA%B0%80.md#L1-L40) · [Q23 L1–15](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2020..md#L1-L15) · [Q33 L181–248](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%26A.%20Fine-tuning,%20Full%20Fine-tuning,%20LoRA,%20QLoRA.md#L181-L248) · [TRANSCRIPT L1–12](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%EA%B0%95%EC%9D%98%EB%8C%80%EB%B3%B8.md#L1-L12) · [LLM-NOTE L1–4](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%AC%B4%EC%A0%9C.md#L1-L4)

### F31. 교안 사이의 Unit 번호 연결도 최신 구조에 맞춰야 한다

**확인·판단:** Agent 보강은 AI Integration의 「Unit 11. LangChain 활용 경계, Test와 Observability」를 가리키지만 현재 Integration의 Unit11은 Tool Calling이며 LangChain은 Unit23 이후, Test는 Unit20, Observability는 Unit21이다.

**보존할 성과:** 상태·실행 관찰로 이어지는 원래 의도.

**제안:** 4단계 목차가 결정되면 번호가 아닌 안정적인 개념/학습 성과 연결을 정하고 현재 잘못된 Unit 안내를 수정한다.

근거: [P2-09 L2600–2606](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2600-L2606) · [P2-12 L673–680](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L673-L680) · [P2-12 L1095–1108](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1095-L1108) · [P2-12 L1146–1156](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1146-L1156) · [P2-12 L1224–1238](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1224-L1238)

### F32. 모델·SDK·MCP의 현재성은 강의 비교와 별도 검증

**확인·판단:** 여러 교안에 특정 검증일·모델명·현재 Framework/API라는 표현이 있다. 이번 분석은 해당 서술의 분포와 교육적 역할을 비교했으며, 외부 공식 사양을 새로 조회해 기술 현재성을 승인하지 않았다.

**보존할 성과:** 모델 ID·버전·검증 시점을 남기는 기존 원칙과 미실행 구분.

**제안:** 제작 전 별도 기술 검증 목록으로 Model/SDK/Chat Template/License/MCP 버전·설정·API 호환성을 묶고, 실습 환경 고정과 실행 결과에 연결한다. 과거 검증일을 이번 실행 완료일로 바꾸지 않는다.

근거: [D1-08 L159–188](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L159-L188) · [P2-09 L1022–1038](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1022-L1038) · [P2-12 L1316–1353](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1316-L1353) · [Q23 L1–15](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2020..md#L1-L15)

### F33. FastAPI 교안 기준과 예제 패키지 고정값이 다르다

**확인·판단:** FastAPI 본문은 Python 3.12·FastAPI 0.141 계열을 설명 기준으로 적지만, 함께 제공된 examples/requirements.txt는 fastapi==0.139.0으로 고정한다. 버전 차이만으로 실행 불가라고 단정하지는 않지만, 수업 재현 기준이 하나로 연결되어 있지 않다.

**보존할 성과:** 예제에 고정된 requirements 파일과 교안의 환경 기준 표시. 둘 다 없는 것으로 보고하지 않는다.

**제안:** 제작 단계에서 실제 검증한 한 환경과 선택 기능별 의존성을 정하고, 본문·예제·실행 가이드의 재현 기준을 맞춘다. 이번에는 패키지를 설치하거나 호환성을 판정하지 않았다.

근거: [FASTAPI L79–89](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L79-L89) · [CODE85 L1–5](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/examples/requirements.txt#L1-L5)

### F34. 시범에서 남은 Transfer Learning 용어 문제는 아직 미해결이다

**확인·판단:** P2-02는 학습된 모델의 재사용을 설명하면서 Fine-tuning과 Prompt/RAG 적용을 Transfer Learning 문단 안에 함께 적는다. 이번 전체 분석만으로 Prompt/RAG를 Transfer Learning의 같은 기술 범주로 확정하지 않았다.

**보존할 성과:** 사전학습된 능력을 업무에 재사용한다는 상위 흐름과 Parameter 변경/현재 Context 제공의 구분.

**제안:** 외부 기술 검증에서 상위 설명과 학습·추론 기법의 엄밀한 용어 경계를 확인한다. 시범의 미해결 항목을 전체 분석 완료라는 이유로 닫지 않는다.

근거: [P2-02 L1546–1560](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1546-L1560) · [P2-10 L1749–1794](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1749-L1794)

### F35. 관리형 RAG 제품 사례를 로컬 실습 완료로 해석하지 않기

**확인·판단:** RAG 본문에는 OpenAI Retrieval/File Search의 관리형 Chunking·Embedding·Indexing 사례가 있고, 원문도 이것이 RAG의 보편적 필수 구조가 아니라고 명시한다. 따라서 구현 연결이 전혀 언급되지 않았다는 진단은 틀리다.

**보존할 성과:** 교과 개념이 제품 기능으로 나타나는 방식을 설명하는 기존 비교 사례.

**제안:** 로컬 교육용 누적 실습은 문서·Chunk·검색·Context·인용 책임을 직접 추적할 수 있는 경로로 설계하고, 관리형 제품 사례와 별도로 표시한다. 이 분석에서 유료 관리형 서비스를 필수로 채택하거나 그 실행을 검증하지 않았다.

근거: [P2-08 L1403–1429](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1403-L1429) · [P2-08 L1017–1047](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1017-L1047)

</details>

<details>
<summary>Phase1·Phase2 주교안 42개의 역할과 연결</summary>

각 행은 과목 수준의 분석 결과다. 이 표가 모든 문장과 코드의 정확성을 검증했다는 의미는 아니다. 각 링크는 해당 역할을 확인할 수 있는 대표 구간이며, 전체 파일 범위와 개념별 비교 근거는 함께 보존했다.

| 교안 | 보존할 역할 | 후속 연결·차별화 |
|---|---|---|
| [ARCH](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/01.%20AI%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98/AI_%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98_%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.3.1.md#L350-L360) | 서비스/요청/자동화의 최초 지도 | Browser·Backend·모델·저장소·Workflow의 책임을 읽는 입문. 후속에서는 같은 그림보다 계약·상태·실패를 확장. (F19) |
| [REACT-ENV](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_Unit4_%EA%B0%9C%EB%B0%9C%ED%99%98%EA%B2%BD_%EC%8B%A4%EC%8A%B5_Windows_CMD_VSCode.md#L193-L203) | Windows 실행 환경 보충 | React Unit4와 경쟁하는 별도 과정이 아니라 설치·프로젝트 시작 절차의 환경별 보충으로 연결. (F20) |
| [REACT](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/02.%20React/React_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L15576-L15586) | Frontend 기초와 사용자 흐름 | Props/State/Effect/Router→요청·파일·취소·오류·AI UI. 서버 구현 설명은 참조하고 Streaming Parser 계약을 정리. (F21) |
| [PYTHON](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/Python_for_AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L13398-L13408) | 언어·실전 객체/자료 구조 선수학습 | 15 Unit과 실전 Python Module1~10·27~28. 문법·함수·파일·JSON·객체·타입을 AI 실습의 입력으로 연결. (F20) |
| [FASTAPI](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L21019-L21029) | HTTP 계약과 Backend 구현 | Module11~26·29~42. 검증·계층·DI·Provider·오류·Async·Streaming을 구현하고 Phase2는 해당 결과를 확장. (F16) |
| [D1-01](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_01%EA%B5%90%EC%8B%9C_AI%EC%9D%98_%ED%83%84%EC%83%9D%EA%B3%BC_%EC%97%AD%EC%82%AC_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L103-L113) | 역사와 문제의식 | 연도 암기보다 규칙→데이터→사전학습으로 바뀐 이유. 이후 포함 관계·역사는 짧은 연결. (F02) |
| [D1-02](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L181-L191) | AI 전체 지도 | 작업·접근·모델·서비스를 서로 다른 축으로 구분. 뒤의 전체 지도 반복을 줄일 기준점. (F02) |
| [D1-03](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L134) | 규칙과 데이터 학습 | Dataset/Feature/Label·Parameter·Training/Inference를 작은 선형회귀와 업무 책임으로 첫 이해. (F03) |
| [D1-04](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L215-L225) | 표현 학습과 구조의 등장 이유 | Feature Engineering→CNN/RNN/LSTM/Attention/Transformer와 Tensor의 관찰. 내부 Attention 계산은 Phase2 심화. (F04) |
| [D1-05](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_05_%EC%83%9D%EC%84%B1%ED%98%95_AI%EC%99%80_Foundation_Model_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L494-L504) | 생성형 모델의 능력과 한계 | 분류/생성·Foundation/Base/Instruction·환각·Context·형식/내용 검증의 첫 경계. (F05) |
| [D1-06](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_06_%ED%98%84%EB%8C%80_AI_%EA%B0%9C%EB%B0%9C_%EC%83%9D%ED%83%9C%EA%B3%84%EC%99%80_%ED%95%B5%EC%8B%AC_%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%9F%AC%EB%A6%AC_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L251-L261) | 도구 생태계와 책임 | Library/Model/Hub/SDK/Runtime/Framework를 분류. 모든 도구를 설치하는 과목으로 만들지 않음. (F02) |
| [D1-07](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_07_Cloud_AI_API%EC%99%80_OpenAI_SDK_%EC%8B%A4%EC%8A%B5_v0.2.md#L512-L522) | Cloud 호출 관찰 | 환경·키·instructions/input·입력 검증·Usage·실패 관찰. 모델/API 현재성은 배포 전 확인. (F06) |
| [D1-08](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_08_FastAPI%EC%99%80_AI_%ED%86%B5%ED%95%A9_Structured_Output_%EC%8B%A4%EC%8A%B5_v0.2.md#L468-L478) | Structured Output HTTP API | Pydantic·Service·Route·Mock 계약 테스트와 형식/내용 분리. 뒤에서는 같은 앱을 재사용. (F06) |
| [D2-01](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_01_Language_Model_LLM%EA%B3%BC_Token_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L112-L122) | Tokenizer와 ID·Mask | Encode/Decode·Special Token·Padding/Mask·실제 토큰 수 관찰. LLM 심화의 선수 결과. (F05) |
| [D2-02](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_02_AI%EC%9D%98_%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%99%80_Tensor_NumPy%EC%99%80_PyTorch_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L353-L363) | Tensor·Shape·dtype·Device | NumPy/PyTorch 배열·행렬곱·메모리·Shape 오류 관찰. Attention 계산의 선수지식. (F04) |
| [D2-03](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L331) | 학습 코드의 변화 추적 | Loss/Gradient/Optimizer·5단계 학습·Parameter 전후·train/eval/no_grad. LLM·튜닝에서는 목표와 데이터가 달라짐. (F05) |
| [D2-04](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_04_Pretrained_Model_%EC%83%9D%ED%83%9C%EA%B3%84%EC%99%80_Hugging_Face_Hub_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L407-L417) | 모델 저장소를 읽는 법 | Task/Language/License/Runtime·파일·config/checkpoint·접근 제한을 읽어 후보를 찾음. (F28) |
| [D2-05](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_05_Transformers%EB%A1%9C_Pretrained_Model_%EC%A7%81%EC%A0%91_%EC%8B%A4%ED%96%89%ED%95%98%EA%B8%B0_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L365-L375) | 선택한 모델 직접 실행 | Tokenizer→Tensor→generate→새 토큰 구간·Cache/Device/Chat Template 관찰. (F05) |
| [D2-06](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_06_Inference_Runtime_Model_Serving_Transformers%EC%99%80_Ollama_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L144-L154) | 직접 실행과 Serving | 프로세스·Runtime·HTTP·공유 모델의 책임. Local/Server/Private를 구분하는 설계. (F19) |
| [D2-07](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_07_Ollama%EB%A1%9C_Local_LLM_%EC%A7%81%EC%A0%91_%EC%8B%A4%ED%96%89%ED%95%98%EA%B8%B0_%EC%8B%A4%EC%8A%B5_v0.2.md#L144-L154) | Ollama 실행 상태 | ls/ps/run/bye/stop/rm과 자원 관찰. 설치 성공과 모델 실행·API 성공을 구분. (F29) |
| [D2-08](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_08_Python_FastAPI_Ollama_Local_API_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L696-L706) | Local API를 Backend에 연결 | Service/Route·응답 구조·설정·Mock·실패 위치. Cloud 예제의 구조는 가져오고 달라진 부분만 설명. (F16) |
| [D3-01](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_01_AI_Model_Family%EC%9D%98_%EC%9D%B4%ED%95%B4_Gemma%EB%A5%BC_%EC%82%AC%EB%A1%80%EB%A1%9C_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L208-L218) | Family·Variant 식별 | Gemma를 사례로 계열·세대·Variant·Revision·입출력 Capability를 근거로 식별. (F32) |
| [D3-02](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_02_Base_Pretrained_Model%EA%B3%BC_Instruction_tuned_Model%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L273-L283) | Base/Instruction의 공정 비교 | 추가 학습과 Prompt 변경·Chat Template·실제/예상 출력을 분리. 튜닝 원리 첫 경계를 보존. (F14) |
| [D3-03](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_03_Model_Size_Parameter%EC%99%80_Quantization_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L330-L340) | Weight 크기와 양자화 | Parameter×bit 이론값·실파일·Runtime Memory를 구분. 4-bit 표기만으로 실행 보장하지 않음. (F29) |
| [D3-04](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_04_AI_Model_%EC%8B%A4%ED%96%89%EA%B3%BC_Hardware_CPU_GPU_RAM_VRAM_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L289-L299) | 실행 자원·병목 관찰 | CPU/GPU/RAM/VRAM·전송·환경 진단·OOM 원인을 관찰. GPU 없는 경로도 설명. (F29) |
| [D3-05](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_05_AI_Model_Selection%EA%B3%BC_%EC%9A%B4%EC%98%81_Hugging_Face_Model_Card_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L215-L225) | 모델 선정의 근거와 회귀 | Model Card 재소개 대신 작은 평가 Dataset·CSV 채점·선정/보류·Version 갱신을 기록. (F28) |
| [D3-06](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_06_AI_Application_Framework_%EC%83%9D%ED%83%9C%EA%B3%84_LangChain%EA%B3%BC_LlamaIndex_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L56-L66) | Framework 도입 판단 | Tool/Runtime/Workflow/Agent·LangGraph/LangSmith·Retrieval의 자리. 구현은 Phase2로 연결. (F11) |
| [D3-07](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_07_AI_Provider_%EC%B6%94%EC%83%81%ED%99%94_OpenAI%EC%99%80_Ollama_FastAPI_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L775-L785) | Provider 교체 계약 | Interface/Factory/설정·오류·Mock·테스트로 교체 가능성을 입증. P2 Integration의 기준 앱. (F16) |
| [D3-08](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Day3_08_React_FastAPI_AI_Provider_Model_%EC%B5%9C%EC%A2%85_%ED%86%B5%ED%95%A9_%EC%8B%A4%EC%8A%B5_v0.2.md#L939-L949) | React→Backend→Provider 통합 | CORS·Fetch·상태·취소·실패·설정 전환을 관찰. 원문도 RAG·Agent 구현은 이후로 남김. (F16) |
| [P2-01](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/01.%20AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84/AI%20%EC%B5%9C%EC%8B%A0%20%EB%8F%99%ED%96%A5%20%EB%B0%8F%20%EC%A0%84%EC%B2%B4%20%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1091-L1101) | 생명주기·업무 선택 오리엔테이션 | 기초 전체 지도는 짧게 연결하고 평가·데이터·운영·Responsible AI를 차별화. 제목/통합은 제안. (F02) |
| [P2-02](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1432-L1442) | 데이터 설계와 모델 평가 | 기초 재설명은 축소하고 일반화·Split·누수·지표·Pipeline 설계를 중심으로 재구성 후보. (F03) |
| [P2-03](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/03.%20%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8(Transformer)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L3355-L3365) | Transformer 내부 계산 | QKV/Attention·Mask·Residual/Norm/FFN·구조·KV Cache. 역사와 GPU 일반론은 연결. (F04) |
| [P2-04](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/04.%20%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)/%EB%8C%80%EA%B7%9C%EB%AA%A8%20%EC%96%B8%EC%96%B4%20%EB%AA%A8%EB%8D%B8(LLM)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L2643-L2653) | LLM 학습·생성·Context 심화 | 기초 Token/Training을 재사용하고 Post-training·Decoding·Memory/검색·평가·비용으로 확장. (F05) |
| [P2-05](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/05.%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)/%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81(Prompt%20Engineering)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L787-L797) | Prompt 설계·평가·운영 | 입출력 계약·Shot·실행 전략·보안·Golden/Regression·Version을 같은 과제의 전후 비교로 연결. (F06) |
| [P2-06](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/06.%20%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)/%EC%9E%84%EB%B2%A0%EB%94%A9(Embedding)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L840-L850) | 검색용 표현과 검색 품질 | Token/검색 Embedding 구분·Dense/Sparse/BM25·Hybrid/Reranker·유사도·재색인. (F07) |
| [P2-07](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/07.%20%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)/%EB%B2%A1%ED%84%B0%20%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B2%A0%EC%9D%B4%EC%8A%A4(VectorDB)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L767-L777) | 검색 인덱스·필터·운영 | 거리 재정의보다 Exact/ANN·HNSW/IVF·Metadata/권한·갱신/삭제·품질/속도 비교. (F08) |
| [P2-08](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/08.%20%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)/%EA%B2%80%EC%83%89%20%EC%A6%9D%EA%B0%95%20%EC%83%9D%EC%84%B1(RAG)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1017-L1027) | 근거 기반 RAG와 실패 추적 | 앞의 검색 산출물을 이어 Offline/Online·Context·Grounding/Citation·평가·권한을 완성. (F10) |
| [P2-09](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/09.%20AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)/AI%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8(Agent)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L513-L523) | Single-Agent 실행·통제 | Registry/Schema/State/승인/종료/평가, Multi-Agent 도입 판단. 내부 중복과 승인 예제 보완 필요. (F11) |
| [P2-10](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/10.%20%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)/%EB%AF%B8%EC%84%B8%EC%A1%B0%EC%A0%95(Fine-tuning)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1002-L1012) | 모델 적응 실험 | 목적/Parameter 전략·LoRA/QLoRA·Dataset/Leakage·Baseline·학습/Reload·회귀 평가를 보존. (F14) |
| [P2-11](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/11.%20%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)/%EA%B4%91%ED%95%99%20%EB%AC%B8%EC%9E%90%20%EC%9D%B8%EC%8B%9D%EA%B3%BC%20%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC(OCR_Multimodal)_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1440-L1450) | 문서 입력 인식과 품질 | PDF 유형·OCR/Parsing·표/순서·Vision 한계·단계별 평가·Review를 후속 문서 입력으로 연결. (F15) |
| [P2-12](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/12.%20AI%20Integration/AI%20Integration_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1282-L1292) | 실행 구조와 서비스 통합 확장 | 기존 앱을 이어 Harness·Capability·Stream/State·Budget·Tool Gateway·Observability를 추가. (F16) |
| [P2-13](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/13.%20Document%20AI/Document%20AI_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1452-L1462) | 문서 처리·근거·생성 통합 | 형식/IR/Locator·문서 권한·Claim 인용·Review·DOCX/PDF 생성. 현재의 큰 최소 범위를 분리 검토. (F17) |

</details>

<details>
<summary>Q&A·보충 파일을 어디에 연결할지</summary>

아래는 이번 단계의 연결 제안이다. 실제 본문에 반영한 상태가 아니다. Q01은 빈 파일이므로 내용 있는 보충 자료 수에 포함하지 않는다.

| 자료 | 주제 | 연결 후보 | 처리 |
|---|---|---|
| [Q01](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/03.%20Python_FastAPI/FastAPI%20Q%26A/%EB%B9%84%EB%8F%99%EA%B8%B0%EC%B2%98%EB%A6%AC(Asynchronous).md) | 비동기처리(Asynchronous).md | FASTAPI | 빈 파일: 교육 내용 없음. 비동기 본문이 없다는 근거로 사용하지 않음. |
| [Q02](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%202%EA%B5%90%EC%8B%9C%2011.%20Machine%20Learning%20%EC%84%A4%EB%AA%85.md) | Q - Day1 2교시 11. Machine Learning 설명.md | D1-03 | 본문 연결: ML 설명은 첫 학습에 흡수하고 재정의 반복은 줄임. |
| [Q03](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%202%EA%B5%90%EC%8B%9C%2024.%20%EB%8B%B5.md) | Q - Day1 2교시 24. 답.md | D1-02 | 확인 질문: Rule/ML 판정 활동의 답안 근거로 연결. |
| [Q04](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%203%EA%B5%90%EC%8B%9C%2013%20Inference(%EC%B6%94%EB%A1%A0).md) | Q - Day1 3교시 13 Inference(추론).md | D2-03 | 본문 연결: Inference 첫 정의와 실제 Parameter 불변 관찰로 연결. |
| [Q05](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%203%EA%B5%90%EC%8B%9C%2018%20Deterministic%EA%B3%BC%20Probabilistic%EC%9D%98%20%EC%A7%81%EA%B4%80.md) | Q - Day1 3교시 18 Deterministic과 Probabilistic의 직관.md | D1-03 | 본문 연결: 결정성/확률성과 같은 입력·상태·생성 조건의 차이를 연결. |
| [Q06](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%203%EA%B5%90%EC%8B%9C%205%20-%20Supervised%20Machine%20Learning(%EC%A7%80%EB%8F%84%ED%95%99%EC%8A%B5).md) | Q - Day1 3교시 5 - Supervised Machine Learning(지도학습).md | D1-03 | 본문 연결: 입력과 Label을 이용한 지도학습 사례에 연결. |
| [Q07](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%204%EA%B5%90%EC%8B%9C%204%20-%20AI%EC%97%90%EC%84%9C%20%EC%9D%B4%EC%95%BC%EA%B8%B0%ED%95%98%EB%8A%94%20feature%EC%9D%98%20%EA%B0%9C%EB%85%90%EA%B3%BC%20dataset%EC%9D%B4%20%EA%B0%99%EC%9D%80%20%EB%A7%A5%EB%9D%BD%EC%9D%B4%EB%9D%BC%EA%B3%A0%20%EC%9D%B4%ED%95%B4%ED%95%B4%EB%8F%84%20%EB%90%A0%EA%B9%8C.md) | Q - Day1 4교시 4 - AI에서 이야기하는 feature의 개념과 dataset이 같은 맥락이라고 이해해도 될까.md | D1-03 | 본문 연결: Dataset과 Feature의 혼동을 표로 구분. P2-02는 데이터 설계로 확장. |
| [Q08](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%205%EA%B5%90%EC%8B%9C%2024.md) | Q - Day1 5교시 24.md | D1-05 | 본문 연결: 비결정성과 실제 평가·반복 관찰로 연결. |
| [Q09](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Q%20-%20Day1%205%EA%B5%90%EC%8B%9C%2029.md) | Q - Day1 5교시 29.md | D3-01 | 본문 연결: Family/Variant의 첫 설명에 연결. |
| [Q10](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%203%EA%B5%90%EC%8B%9C%2033..md) | Q - Day2 3교시 33..md | D2-03 | 코드 해설 보존: 5단계 Training과 Parameter 변화의 상세 해설을 보충으로 보존. |
| [Q11](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%203%EA%B5%90%EC%8B%9C%2039..md) | Q - Day2 3교시 39..md | D2-03 | 심화 보충 보존: train/eval·Dropout의 학습/추론 동작은 단순 중복 삭제하지 않음. |
| [Q12](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2018%20-%20Model%20Repository%EC%97%90%20%EC%9E%88%EB%8A%94%20Model%20Card%20%EC%A0%95%EB%B3%B4%EC%97%90%20%EC%9E%88%EB%8A%94%20%EC%9D%B4%20%EB%82%B4%EC%9A%A9%EB%93%A4%EC%9D%84%20%EC%9A%B0%EB%A6%AC%EA%B0%80%20%EB%B3%BC%20%EC%88%98%20%EC%9E%88%EC%96%B4.md) | Q - Day2 4교시 18 - Model Repository에 있는 Model Card 정보에 있는 이 내용들을 우리가 볼 수 있어.md | D2-04 | 활동 연결: Model Card에서 확인/미확인 정보를 구분하는 근거표로 연결. |
| [Q13](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2026..md) | Q - Day2 4교시 26..md | D2-04 | 본문 연결: Limitation 읽기의 판단 항목으로 흡수. |
| [Q14](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2027..md) | Q - Day2 4교시 27..md | D3-05 | 활동 연결: Benchmark 점수와 실제 업무 평가를 구분. |
| [Q15](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2031%20-%20%EA%B0%99%EC%9D%80%20parameter%EB%A5%BC%20%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94%20%EB%AA%A8%EB%8D%B8%EC%9D%98%20%EA%B2%BD%EC%9A%B0%20.safetensors%20%ED%8C%8C%EC%9D%BC%EC%9D%84%20%EA%B5%90%EC%B2%B4%ED%95%B4%EB%8F%84%20%EA%B4%9C%EC%B0%AE%EC%9D%80%EA%B0%80.md) | Q - Day2 4교시 31 - 같은 parameter를 사용하는 모델의 경우 .safetensors 파일을 교체해도 괜찮은가.md | D2-04 | 심화 보충 보존: safetensors 교체는 Parameter 수 외 config/tokenizer/shape 호환을 봄. |
| [Q16](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%204%EA%B5%90%EC%8B%9C%2037~38..md) | Q - Day2 4교시 37~38..md | D2-05 | 본문 연결: Auto 클래스와 Task/Model ID를 실제 로딩과 연결. |
| [Q17](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%206%EA%B5%90%EC%8B%9C%2011.%20%EC%9C%84%EC%97%90%EC%84%9C%20%EC%9D%B4%EC%95%BC%EA%B8%B0%ED%95%98%EB%8A%94%20%EB%82%B4%EC%9A%A9%EB%93%A4%EC%9D%B4%20%EB%8B%A4%20%EC%86%8C%EC%8A%A4%EC%83%81%EC%97%90%20%EC%98%B5%EC%85%98%EC%9C%BC%EB%A1%9C%20%EB%84%A3%EC%9D%84%20%EC%88%98%20%EC%9E%88%EB%8A%94%EA%B1%B4%EA%B0%80.md) | Q - Day2 6교시 11. 위에서 이야기하는 내용들이 다 소스상에 옵션으로 넣을 수 있는건가.md | D2-06 | 심화 보충 보존: generate 옵션과 구조·dtype·Device·학습 코드 수정의 범위를 구분. |
| [Q18](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%206%EA%B5%90%EC%8B%9C%2016..md) | Q - Day2 6교시 16..md | D2-06 | 본문 연결: Serving의 요청/자원/장애 책임으로 연결. |
| [Q19](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%206%EA%B5%90%EC%8B%9C%2026..md) | Q - Day2 6교시 26..md | D3-07 | 본문 연결: Provider 개념은 계약과 교체 코드로 확장. |
| [Q20](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Q%20-%20Day2%206%EA%B5%90%EC%8B%9C%2035..md) | Q - Day2 6교시 35..md | D3-03 | 본문 연결: 양자화와 Parameter 수·저장/Runtime 메모리의 차이로 연결. |
| [Q21](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/LangChain%EA%B3%BC%20LlamaIndex%EC%97%90%20%EB%8C%80%ED%95%9C%20%EC%84%A4%EB%AA%85.md) | LangChain과 LlamaIndex에 대한 설명.md | D3-06 | 선택 보충: LangChain/LlamaIndex 비교 비유는 대표 설명 하나만 사용. 구현은 Phase2로 연결. |
| [Q22](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2015..md) | Q - Day3 1교시 15..md | D3-03 | 본문 연결: Parameter 수와 자원·품질을 단일 등식으로 단정하지 않음. |
| [Q23](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2020..md) | Q - Day3 1교시 20..md | D3-01 | 시점 검증 필요: 특정 세대의 공개현황을 단정하는 Q&A. 현재성 확인 전 최신 모델 사실로 전파하지 않음. |
| [Q24](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2025..md) | Q - Day3 1교시 25..md | D3-01 | 본문 연결: Capability는 입력/출력 Modality·Task·조건별로 구분. |
| [Q25](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2033..md) | Q - Day3 1교시 33..md | D3-05 | 활동 연결: 요구→조건→후보→평가→선정의 근거를 작성. |
| [Q26](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2035..md) | Q - Day3 1교시 35..md | D3-01 | 보충 보존: sLLM을 고정 B 구간으로 단정하지 않고 실제 Task/환경 제약으로 연결. |
| [Q27](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%201%EA%B5%90%EC%8B%9C%2039..md) | Q - Day3 1교시 39..md | D3-05 | 활동 연결: 모델 업데이트 시 출력·지연·메모리·호환 회귀를 확인. |
| [Q28](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%206%EA%B5%90%EC%8B%9C%2010..md) | Q - Day3 6교시 10..md | D3-07 | 구현 연결: 공통 Interface의 가치와 실제 Provider 기능 차이를 연결. |
| [Q29](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%206%EA%B5%90%EC%8B%9C%2012..md) | Q - Day3 6교시 12..md | D3-06 | 본문 연결: 공통 Model 호출과 Agent Loop가 같은 것이 아님을 보존. |
| [Q30](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%206%EA%B5%90%EC%8B%9C%2014~17..md) | Q - Day3 6교시 14~17..md | P2-09 | 심화 보충 보존: Model→Tool 요청→Runtime 실행→Observation을 코드 추적과 연결. |
| [Q31](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%206%EA%B5%90%EC%8B%9C%2019~20..md) | Q - Day3 6교시 19~20..md | P2-12 | 심화 보충 보존: LangGraph State/Orchestration과 LangSmith 관찰을 구분. Framework 현재 API는 별도 검증. |
| [Q32](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%20-%20Day3%206%EA%B5%90%EC%8B%9C%20%EA%B0%9C%EC%9A%94..md) | Q - Day3 6교시 개요..md | D3-06 | 본문 연결: Framework가 기존 Service/Provider 사이에서 담당할 자리를 설명. |
| [Q33](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day3/Q%26A.%20Fine-tuning,%20Full%20Fine-tuning,%20LoRA,%20QLoRA.md) | Q&A. Fine-tuning, Full Fine-tuning, LoRA, QLoRA.md | P2-10 | 심화 보충 보존: Full/Partial/LoRA/QLoRA·Trainer·지식 회귀를 해당 튜닝 Unit에 연결. |

Transformer `강의대본.md`는 P2-03의 강사 보충이다. 현재 교안과 시간·설명·예제가 맞는지는 제작 단계의 수업 가능성 검수 대상이다. LLM `무제.md`는 대본 작성을 요청하는 4줄의 편집 메모이며 강의 본문이나 이번 작업 지시로 취급하지 않았다.

</details>

<details>
<summary>우선 보완할 실습 연결과 실제 수행한 검사</summary>

### 먼저 정리할 연결

| 우선 | 위치 | 이번 확인 | 후속 작업 |
|---|---|---|
| P0 | React Unit34 ↔ FastAPI Module42 | 같은 Streaming URL을 연결하지만 raw 문자열 누적과 SSE 이벤트 처리가 다름 | 공개 이벤트 계약·Parser·오류/종료/취소 통합 |
| P0 | Agent Registry 모의 예제 | Tool 인수의 approved=True만으로 모의 created 반환 | 승인 상태를 Runtime에서 신뢰하게 전달하고 위조 인수 거부 |
| P0 | Python/예제 README | 파일 4개의 실제 폴더명과 다른 링크 8곳 | 경로 또는 배치 동시 교정 |
| P1 | Agent ↔ Integration Unit 참조 | Unit11 안내가 현재 Unit 내용과 다름 | 최종 목차·안정적인 연결 기준으로 정정 |
| P0 | FastAPI 본문 ↔ examples requirements | 본문 0.141 계열과 예제 고정값 0.139.0이 다름 | 실제 검증한 환경을 정하고 교안·예제 재현 기준을 연결 |
| P1 | RAG→Agent→Multi-Agent 실습 묶음 | 코드 조각·설계는 있으나 현재 펼친 tree의 누적 실행 패키지로 연결되지 않음 | Dataset·시작/완료 코드·설정·테스트·실제 결과를 단계별로 제공 |

### 실제 수행 범위

| 항목 | 수행·증거 수준 |
|---|---|
| 원문 수집·무결성 | 164개 텍스트 파일의 Git Blob SHA 재계산·일치 |
| 독립 Python 예제 문법 | 84개 AST Parsing 통과. Import/실행/서버/모델 성공을 의미하지 않음 |
| 예제 링크 | module27/28 관련 8곳의 경로 불일치 확인. 대상 파일 4개는 다른 폴더명으로 존재 |
| Agent 승인 경계 | 원문의 모의 함수 예제만 실제 실행. approved=False 차단, 인수 approved=True에서 모의 created를 확인. 외부 일정·Tool·LLM 호출 없음 |
| 확대 분석 검사기 | 이 범위에 맞는 별도 검사기로 원본·필수 정보·근거·범위·원본 보호·문서·실행 주장·시도 기록 검사 |
| 의미 검토 | 같은 Work 세션에서 중복과 심화, 범위, 이미 있는 내용, 제안/실행/확정을 구분해 순차 검토 |
| 미실행 | 실제 Cloud/Ollama·RAG E2E·Multi-Agent E2E·Fine-tuning·React Build·교육장 성능 검증 |

개편 방향을 작성하면서 Context/Harness/Multi-Agent를 “없음”으로 묶지 않고 **분산 설명/소개 있음·누적 실행 연결 부족**으로 교정했다. VectorDB도 제목의 오해 가능성과 이미 있는 본문 보정을 구분했다. Python Module1~10·27~28이 다른 교안에 배치된 점을 확인해 강의 누락으로 보고하지 않았다.

초안 의미 검토 후 한 번 보완했다. FastAPI의 설명 기준/예제 고정값 차이(F33), 시범에서 남은 Transfer Learning 용어의 미해결 상태(F34), 이미 있는 관리형 RAG 구현 사례와 로컬 누적 실습의 경계(F35)를 추가했다. 새 항목을 확인했다고 기존 강의를 수정한 것은 아니다.

반복은 최초 작성과 필요한 부분 보완으로 제한한다. 검증 결과와 실제 보완 기록은 내부 기록에 남기며, 모델 Token·전체 Tool 호출 수처럼 노출되지 않은 값은 추정하지 않는다. 독립 자동 Runner나 추론 강도 자동 전환을 새로 구현한 작업이 아니다.

</details>

---

**다음 위치는 4단계다.** 이 분석을 입력으로 전체 목차와 누적 실습의 단계·입출력·완료 조건을 설계한다. 이번 문서를 GitHub에 보관하는 것은 강의 삭제·통합·제목 변경·시수 확정을 승인했다는 뜻이 아니다.
