# 기존 교육자료·연결 실습 검사와 수정 범위

2026-11-02 · 검사 기준: [현재 제작·검수 프롬프트](../../loop/prompts.md) · 대상 커밋: `7c3171182f67be818980a94afebab437b9858030`.

이 문서는 제작자/강사용 수정 목록이다. 표의 단원 ID는 관리 매핑을 위한 값이며 학생용 교안에 복사할 문구가 아니다. 원인을 설명하고 다음 수정 범위를 지정하는 문서 검수이며, 이번에 교육자료나 실행 코드를 고치지는 않았다.

## 판정과 확인 범위

70개 단원의 공통 본문 21개, 직접 연결된 안내·활동지·교사 해설 등 25개 문서를 읽었다. 별도로 후속 학습 결과 한 문서와 코드 네 파일의 관련 부분을 대조했다. 읽기 범위와 소스 해시는 [validation.json](validation.json)에 있다. 같은 작성자의 후속 검수이며 독립 강사/학습자 검수 결과가 아니다.

현재 70개 모두 새 기준에서는 **보완 필요**로 기록한다. 기초 강의의 설명·활동을 폐기하라는 뜻은 아니다. 관리 코드와 제작 진행 상태를 학생의 읽기 흐름에서 정리할 공통 문제가 있으며, 그 외 설명 결함은 아래 단원별로 다르다. 기존의 파일 작성·자체 검토 기록을 새 기준의 합격 수로 바꾸지 않는다.

설명·실습의 문서 연결은 검사했지만 실행 구현 전체, 모든 CLI 인수/패키지의 조합, 모델 생성/훈련/브라우저를 이번에 전부 재검증하지 않았다. 새 실행은 0회다. 이미지/PDF/DOCX의 시각 품질과 외부 공식 문서·사이트의 최신 상태도 다시 검증하지 않았다. 관련 주장을 기존 증거보다 확대하지 않는다.

## 먼저 적용할 공통 수정

- 학생용 제목·본문은 업무/개념 이름으로 읽히게 한다. 기존 사례 ID·JSON 열·실제 변수/API·Q/K/V·모델 ID를 일괄 개명하지 않는다. 실행에 필요한 이름은 뜻과 실제 위치를 함께 보여준다.
- 핵심 학습 흐름은 설명→풀어쓴 예제→직접 바꿀 부분→실행/관찰→해석이다. 제작 RESULT/REVIEW를 핵심 개념 설명 대신 필수로 읽게 하지 않는다. 기존 보고서는 증거/교사용 참고로 보존한다.
- Markdown의 코드/JSON을 무조건 없애지 않는다. 필요한 핵심 줄·입력·출력은 종류와 역할을 명시해 해설하고, 긴 실행/검사 도구는 정확한 파일과 명령으로 연결한다.
- 단계별 초기 상태·이번에 추가하는 기능·현재 전체 코드의 상태를 구분한다. 과거 구현을 직접 실행시키려면 재현 가능한 파일/커밋·명령이 있어야 한다. 실제 코드를 읽지 않고 전 단계의 미구현 설명을 현재 기능으로 단정하지 않는다.
- 반복된 일반 확인 질문을 해당 개념의 예상·오류·비교 질문으로 바꾸고 강사용 판정 이유를 둔다. 양식만 새로 복제하지 않는다.

## 코드/기록과 대조해서 확인한 불일치

1. **문서 입력 지원:** [intake의 DOCX 거부 설명](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/intake.md#L30)과 [L9 초기 안내](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/L9.md#L19)는 현재 [Registry의 docx 파싱 분기](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/backend/app/document_registry.py#L23) 및 [업로드 허용 형식](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/backend/app/document_registry.py#L81)과 다르다. 후속 단원에서 기능을 추가한 연혁 자체가 잘못은 아니다. 같은 현재 소스로 수강하는 학생이 어느 상태를 실행하는지 알 수 없게 된 문서/수업 시작 상태의 불일치다. 기존 DOCX 지원을 새로 만들지 말고 단계와 현재 실행 경로를 정리한다.
2. **학습 진행 상태:** [훈련 본문](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L50)은 전체 Train·18회귀를 이후 작업으로 쓰지만 [말미](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L75)와 [후속 결과](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/reports/KEDU-PRODUCTION-011/RESULT.md#L1)는 완료를 기록한다. `lora_lab`은 실제 4 Step 초기 경로이고 `lora_full_lab`은 전체 예제 28 Step 경로이므로 명령도 구분해야 한다. [L7](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/L7.md#L1)과 Backend 안내의 과거 미완료 문장을 함께 정리한다. 다중 Seed·QLoRA·품질 채택은 여전히 미완료다.
3. **수강 순서와 제작 순서:** [마지막 단원의 최종 채택 표/마무리](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/evaluation.md#L61)에 54/70·남은16개·다음 시작 안내 제작이 남아 있다. 현재 인덱스의 70개 초안과도 다르며, 시작 안내를 먼저 배우는 학생의 수강 흐름에도 맞지 않는다. 역사적인 제작 보고서는 그대로 두고 현재 교안의 제작 연혁을 정리한다.
4. **실습 명령의 발견 가능성:** [문서 실습](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/L8.md#L18)·L9·[Streaming 실행 안내](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/practice/document-assistant/stream-ui/README.md#L1)가 정확한 명령을 Python 첫 설명으로 넘긴다. `document_lab`의 실제 필수 인수는 `--specimens`, `--tessdata-dir`, `--output`이다. 잘못된 옵션이라고 판정한 것이 아니라, 실행 안내를 읽은 초보자가 다시 소스에서 명령을 조립해야 하는 교육적 연결 문제다.

## 단원별 수정 범위

각 행의 근거 링크는 검사 당시 고정 커밋의 해당 단원/부분이다. 공통 표기·관리 분리 결함 외에 심화 보강이 필요한 곳은 행에 구체적으로 적었다. 과목 아래의 재사용/재검증 문장이 그 과목의 모든 행에 적용된다.

### 시작 안내

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-00.U01 · 업무와 허용할 수 없는 실패](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/orientation/lesson.md#L13) | 합성 환불 규정 카드→문제 정의 여덟 항목→서로 다른 실패 세 개→활동지·해설이 연결된다. | 이 전개를 유지한다. 단원·실패 관리 코드를 학습 제목으로 앞세우지 않고 자연어 사례명과 관리 매핑을 분리한다. |
| [K2-00.U02 · AI Lifecycle와 책임](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/orientation/lesson.md#L58) | 변경된 규정과 비공개 문서 노출을 책임자·증거·재개 판단에 연결한 예제가 있다. | 단계표와 두 변경 대응을 유지한다. 뒤 강의 연결에서 관리 단원 번호보다 무엇을 배울지 먼저 안내한다. |
| [K2-00.U03 · 동향·제품·생성 방식의 구분](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/orientation/lesson.md#L95) | 기술 분류, 자기회귀/Diffusion, 원리와 시점이 필요한 주장을 사례로 구분한다. | 분류·날짜 판단 예제와 미확인 처리 해설은 유지한다. 학생용 표기와 과목 연결만 정리한다. |

**재사용:** 합성 규정 카드·문제/실패/책임 표, 활동지 A~C와 teacher-guide를 유지한다.

**재검증:** 코드 실행을 요구하지 않는 토론/설계 활동이다. 설명·표기 수정 후 활동지·해설 대응을 다시 읽으면 된다. 실제 수업 소요 시간은 미측정이다.

### 데이터 설계와 평가

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-01.U01 · 예측 시점과 데이터의 역할](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/data-evaluation/lesson.md#L25) | 판단 시점을 고정하고 질문·미래 결론·정답·관리 열을 구분하는 반례가 있다. | 시점 반례와 활동지·교사 판정은 유지한다. 관리용 열 이름은 실제 파일에서 찾을 때 뜻과 함께 제시한다. |
| [K2-01.U02 · 데이터 제작 원칙·분리와 누수](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/data-evaluation/lesson.md#L48) | 라벨 지침·보류, 그룹 누수, Train 증강의 원문/변형 반례와 Dataset Card가 이어진다. | 기존 설명을 보존한다. 그룹 ID를 처음 만날 때 문의 내용/계보를 먼저 보여주고, 표기 정리 시 CSV 열은 바꾸지 않는다. |
| [K2-01.U03 · 일반화·과적합과 실험 통제](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/data-evaluation/lesson.md#L128) | 가상 Loss 세 회차와 임계값 하나만 바꾸는 통제표가 있고 일반화와 업무 품질을 구분한다. | 가상/실측 구분과 과적합 해석을 유지한다. 비교 실행 이름은 자연어 의미를 먼저 설명한다. |
| [K2-01.U04 · 평가 지표와 오류의 영향](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/data-evaluation/lesson.md#L165) | 20개 가상 점수→혼동행렬→네 지표→오류 영향의 계산이 완결되어 있고 해설도 대응한다. | 계산을 다시 만들지 않는다. 사례 ID보다 입력 값과 양성의 의미를 앞세우고 기존 활동지/해설 연결을 유지한다. |

**재사용:** split-examples.csv·metric-examples.csv, Dataset Card·활동지·해설과 기존 수치/분리 검사 결과를 유지한다.

**재검증:** 설명만 고치면 전체 ML 실행은 필요 없다. CSV·라벨/분리·지표가 바뀔 때 해당 자료 검사와 손계산을 재확인한다.

### Transformer 원리

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-02.U01 · 신경망 한 층과 Activation](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/transformer-basics/lesson.md#L21) | xW+b와 ReLU를 두 성분으로 계산하고 Shape·Bias 변경 활동으로 연결한다. | 기존 수치·설명·활동을 유지한다. 학생용 제목의 관리 번호와 결과 보고서 안내를 정리한다. |
| [K2-02.U02 · Self-Attention의 계산](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/transformer-basics/lesson.md#L51) | 한 Query의 Q/K/V→내적→스케일→Softmax→Value 가중합이 실제 숫자로 이어진다. | 계산표·반올림 조건·Attention과 어휘 확률의 구분을 보존한다. 새 예제를 억지로 추가하지 않는다. |
| [K2-02.U03 · Transformer Block](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/transformer-basics/lesson.md#L91) | Head 연결/투영, Residual, 정규화·FFN에 각각 작은 계산과 적용 조건이 있다. | 별도 작은 예제라는 표시를 유지한다. 전체 Block을 한 번에 실행한 결과로 합치지 않고 학생용 표기만 보정한다. |
| [K2-02.U04 · 위치 정보·구조·Mask](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/transformer-basics/lesson.md#L137) | Sinusoidal·회전 예제, Q/K/V 출처, Mask 표와 미래 차단 전후 계산이 있다. | 기존 수치와 Mask/권한 구분을 보존한다. 단원 관리 코드와 의미 중심 안내를 분리한다. |
| [K2-02.U05 · 생성과 KV Cache](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/transformer-basics/lesson.md#L187) | Teacher Forcing·Prefill/Decode의 Cache 시점과 메모리 곱셈 예제가 연결된다. | 가상 계산과 실제 모델 검증의 구분을 유지한다. Cache 비교 코드/수치는 재작성 대상에서 제외한다. |

**재사용:** 기존 합성 행렬·Softmax·Mask·Cache 계산과 활동지·해설을 유지한다.

**재검증:** 표기만 바꾸면 실제 모델 실행은 필요 없다. 수식/숫자/계산 코드가 바뀔 때 해당 예제 계산을 다시 확인한다.

### LLM·Hugging Face

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-03.U01 · 학습 목표와 Post-training](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/llm-basics/lesson.md#L14) | 학습 목표·데이터·갱신 대상과 환불 업무 사례를 연결하고 SFT와 LoRA의 축을 나눈다. | 현재 전개와 교사 해설을 유지한다. 선호 쌍 활동의 근거와 학생용 과목 연결을 다듬는다. |
| [K2-03.U02 · Logit에서 Token 선택까지](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/llm-basics/lesson.md#L51) | Logit 확률표·필터 재정규화·같은 조회값의 Temperature 비교·Beam 반례가 있다. | 손계산은 유지한다. 실제 생성 비교는 미실행으로 계속 분리하고, 후속 실제 실행 경로/선수 준비를 명확히 연결한다. |
| [K2-03.U03 · Parameter·Context·Memory·Retrieval](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/llm-basics/lesson.md#L109) | 저장 위치/수명/전달 책임과 규정 갱신·대화 재개 사례를 구체적으로 설명한다. | 표와 네 상황의 해석은 유지한다. 짧은 Context 강의로 이어질 때 이미 배운 내용과 새 조립 실습의 차이를 안내한다. |
| [K2-03.U04 · 환각·불확실성과 시스템 평가](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/llm-basics/lesson.md#L141) | 여섯 합성 응답을 다섯 평가 축으로 나누고 교사 해설에서 미확인까지 판정한다. | 합성 응답·시간과 실측을 나누는 기준을 보존한다. 제작 상태 설명은 교사용 참고로 옮긴다. |
| [K2-03.U05 · Hugging Face 첫 방문과 공식 예제 찾기](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/huggingface/README.md#L17) | 실제 Docs 화면과 목적별 메뉴, 따라하기·확인 질문이 연결된다. | 화면·질문·라이브러리 역할을 유지한다. PRE-HF/단원/제작본 표기는 관리 측으로 옮긴다. 화면의 시각적 최신성은 이번에 재검증하지 않았다. |
| [K2-03.U06 · Model Card·파일·실행 경로 읽기](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/huggingface/README.md#L54) | 실제 모델 페이지, Card/Files/실행 경로와 후보 비교 활동이 있다. | 화면은 보존하고 실제 Card 한 항목을 근거 문장→판단→미확인으로 읽은 짧은 완성 예를 보강한다. 라이선스/파일의 실제 기술 이름은 유지한다. |
| [K2-03.U07 · Tokenizer·Chat Template 관찰](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/huggingface/README.md#L111) | Tokenizer 목적·명령·짧은 핵심 코드 링크·실측 Token 수·변경 활동·오류 안내가 연결된다. | 현재 실행과 관찰 흐름을 유지한다. 핵심 코드의 입력/반환 한 부분을 본문에서 설명하면 도구 전체를 오갈 부담을 줄일 수 있다. 새 실행 여부는 따로 표시한다. |

**재사용:** 합성 Logit/평가 사례·활동지/해설, 실제 화면과 Tokenizer 도구·입력/고정 모델 목록·기존 관찰 증거를 유지한다.

**재검증:** 실제 생성 설정 비교는 여전히 미실행이다. Tokenizer 입력/옵션/코드 변경 시 해당 프로필 관찰·캐시 재실행만 재검증한다. 캡처의 화면 최신성/시각 품질은 별도 확인이다.

### Prompt

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-04.U01 · 지시·요청·제약·출력 계약](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/prompt/lesson.md#L9) | 첫 단원부터 C01·baseline/instruction 비교를 요구하지만 실제 질문과 완성 지시 전후가 본문에 없다. | 식비 문의의 원문·질문을 먼저 보여주고 지시/자료/요청/출력 조건을 풀어 설명한다. 준비된 입력과 실제 답변을 구분한 완성 비교 예를 쓴다. |
| [K2-04.U02 · Zero/One/Few-shot의 비교](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/prompt/lesson.md#L19) | 예시 개수의 주의점 뒤 바로 12개 사례 비교표 작성을 요구한다. 완전한 one/few-shot 입력 예가 없다. | 평가와 분리한 도서 대출 예제 하나를 끝까지 읽고, 예시 0/1/2개에서 실제로 추가되는 부분과 Token/편향의 의미를 설명한다. |
| [K2-04.U03 · 추론 기법과 실행 전략의 경계](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/prompt/lesson.md#L29) | Self-Consistency·ReAct를 짧게 소개한 다음 실행 주체·호출 수 분류로 넘어간다. | 후보를 여러 개 비교하는 작은 사례와 행동→도구 검사→관찰 흐름을 설명한다. 실제 구현/미구현을 분리하고 단원 고유 질문·해설을 만든다. |
| [K2-04.U04 · Golden Dataset과 회귀](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/prompt/lesson.md#L39) | core-v1·C01/C03로 회귀를 정의하지만 실제 답안·판정 전후 예가 없고 네 단원의 유일한 확인 질문이 같다. | 정상 답 하나와 자료 부족 사례 하나의 채점/회귀를 풀어 보여준다. 예시 답은 합성인지 실측인지 명시하고 개념별 질문·판정 이유를 작성한다. |

**재사용:** L1의 documents-v1.json·core-v1.json·shots-v1.json, 입력 준비·기준 Token 관찰과 기존 Backend 계약을 재사용한다.

**재검증:** 대표 수정 때 생성 입력과 사례 원문·변경 조건을 대조한다. 명령/입력/준비 코드가 바뀔 때 준비 결과와 Token 계산을 재검증한다. 새 모델 답변을 싣는 경우 그 실행·평가가 별도로 필요하다.

### Context

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-05.U01 · 정보의 출처와 신뢰 경계](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/context/lesson.md#L9) | 공격 메모와 제한 자료를 DOC-I/DOC-R·C06/C07로 먼저 소개한다. | 신뢰할 지시와 참고 문서의 차이를 읽을 수 있는 실제 짧은 입력으로 설명한다. 자연어 사례명 뒤 필요한 설정 ID를 안내한다. |
| [K2-05.U02 · 선택·순서·형식](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/context/lesson.md#L19) | instruction/focused 비교와 선택·순서 원칙은 있지만 조립한 입력의 전후 예가 없다. | 같은 질문에 불필요한 자료/핵심 자료를 선택하고 배치한 두 입력을 보여준다. 사람이 고른 선택과 자동 검색을 구분한다. |
| [K2-05.U03 · Token 예산과 답변 여유](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/context/lesson.md#L29) | 문자 2000과 Token 한도·출력 여유를 구분하지만 한 예제의 계산·초과 조치가 연결되지 않는다. | Template 포함 입력 길이→출력 여유→총한도→초과 시 제외/중단을 실제 입력 하나로 계산하고 관찰값을 해석한다. |
| [K2-05.U04 · State·Memory에서 현재 Context로](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/context/lesson.md#L39) | State·Memory의 전달 항목 표 뒤 활동으로 넘어가며 실제 상태에서 현재 입력을 고르는 예가 없다. | 저장한 정보 중 무엇을 제외/선택하고 현재 Context에 넣는지 하나의 완성 예를 추가한다. 지속 Memory 미구현은 유지한다. 반복 일반 질문을 바꾼다. |

**재사용:** 같은 L1 자료·focused 조건·실제 입력/Token 기록을 재사용한다. Memory를 새로 구현할 필요는 없다.

**재검증:** 새 완성 예의 실제 조립 입력/길이를 확인한다. Context 선택·직렬화·예산 로직을 바꾸면 관련 입력·Token·경계 검사만 다시 실행한다.

### Harness

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-06.U01 · Harness의 최소 책임](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/harness/lesson.md#L9) | 최소 책임 설명은 있으나 valid_shape·OUTPUT_CONTRACT 같은 실행 이름을 중심으로 따라가게 한다. | 간단한 요청→응답→검사→초안/종료를 한 번 끝까지 읽은 뒤 실제 제어 코드의 핵심 분기를 연결한다. |
| [K2-06.U02 · 오류·재시도·반복의 다른 목적](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/harness/lesson.md#L30) | 재시도와 보완의 목적·3회 상한 예는 유용하지만 실제 입력/Trace의 차이를 본문에서 따라가기 어렵다. | 같은 입력 재시도와 실패 이유를 넣은 보완의 짧은 Trace를 나란히 해설한다. 상수 암기보다 공유 예산의 이유를 설명한다. |
| [K2-06.U03 · 검증 실패와 제한된 보완](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/harness/lesson.md#L49) | 형식 검사를 통과하는 틀린 금액 반례는 좋지만 실패→보완 입력→재검사의 읽기 예가 빠져 있다. | 기존 반례를 유지하고 잘못된 응답·실패 이유·한 번의 보완·같은 검사 결과를 순서대로 보인다. |
| [K2-06.U04 · 버전 간 개선과 회귀](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/harness/lesson.md#L69) | A/B·C01/C07과 회귀 표를 요구하나 학생이 판정하는 작은 전후 기록이 없다. | 두 고정 출력의 개선과 다른 사례 회귀를 실제 의미로 해설한다. 모델 성능이 아닌 고정 응답 실험이라는 한계를 유지한다. |
| [K2-06.U05 · 승인·중단·관찰의 신뢰 경계](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/harness/lesson.md#L81) | 90초 전후 검사와 강제 취소의 차이는 정확히 한정하지만 상태·승인/Trace 용어가 압축돼 있다. | 취소 전/후 또는 상한 도달 한 타임라인으로 종료와 남는 초안을 설명하고, 실패별 질문·해설을 붙인다. |

**재사용:** 기존 harness.py·harness_demo.py와 고정 응답/경계 검사·Trace를 재사용한다.

**재검증:** Trace 발췌는 실제 시나리오와 대조한다. 제어 코드/상한/출력 계약을 바꿀 때 관련 retry/repair/종료 회귀를 실행한다. 고정 응답을 실제 모델 품질로 표시하지 않는다.

### Embedding

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-07.U01 · ID·내부 표현·검색 표현](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/embedding/lesson.md#L9) | 표현 네 종류를 나누지만 384차원·Pooling·접두어 설정으로 빠르게 넘어간다. | 문장→Tokenizer ID→내부 표현→검색 벡터의 작은 연결 예와 실제 encode/Pooling 핵심 줄을 해설한다. 전체 도구 코드는 유지한다. |
| [K2-07.U02 · Dense·Sparse·BM25](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/embedding/lesson.md#L28) | 검색 방식과 8사례 관찰표는 있으나 한 질문의 토큰/후보/순위가 어떻게 달라졌는지 압축돼 있다. | 기존 실제 관찰을 보존하고 바꿔 물은 질문 한 개의 BM25/Dense 결과를 원문과 함께 해설한다. 전체 성능 순위로 일반화하지 않는다. |
| [K2-07.U03 · 유사도·정규화·차원](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/embedding/lesson.md#L48) | q·A·B의 내적과 Cosine 순위 반례는 이미 좋은 수치 예제다. | 이 계산은 보존한다. 노름/정규화가 순위를 바꾸는 중간 계산과 질문별 해설을 보강하고 관리 표기만 정리한다. |
| [K2-07.U04 · Hybrid·Reranking·모델 교체](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/embedding/lesson.md#L62) | RRF 식과 Reranking/모델 교체 주의는 있으나 두 순위 목록의 합산 과정이 없다. | 후보 세 개의 두 순위→RRF 합→재정렬을 계산한다. 학습된 Reranker 미실행과 같은 모델 길이 설정 재색인 범위는 유지한다. |

**재사용:** 기존 E5 encoder·BM25/Dense/Hybrid 관찰, 수치 예제와 L3 자료를 재사용한다.

**재검증:** 추가 작은 계산만 검산한다. Encoder/Pooling/접두어/정규화·모델/질의/데이터 변경 시 해당 실제 검색을 재검증한다. 학습된 Reranker는 미실행이다.

### 검색 인덱스

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-08.U01 · 문서·Vector·Metadata의 계약](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/vector-index/lesson.md#L9) | 문서/벡터/Metadata·논리/물리 출처의 책임표는 있으나 실제 작은 레코드 추적이 빠져 있다. | 사람이 읽을 문장 한 개에서 저장 레코드·Chunk·원문 위치로 돌아가는 완성 예를 추가한다. |
| [K2-08.U02 · Exact Search와 ANN](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/vector-index/lesson.md#L30) | Exact/ANN 비교의 한계를 설명한 뒤 바로 4096개 합성 벡터 실험을 요구한다. | 몇 개 점의 정확한 순위와 일부 후보만 찾는 탐색을 먼저 풀어 설명한 뒤 큰 실험의 Recall/지연을 해석한다. |
| [K2-08.U03 · HNSW·IVF의 탐색](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/vector-index/lesson.md#L42) | HNSW·IVF 원리는 짧은 문단 뒤 M/ef/nlist/nprobe 설정표로 넘어간다. | 작은 그래프의 이웃 이동과 군집/탐색 구역 선택을 각각 예로 설명한다. 두 알고리즘을 단순한 상수 비교로 가르치지 않는다. |
| [K2-08.U04 · Filter·갱신·삭제·재색인](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/vector-index/lesson.md#L61) | 갱신/삭제/세대 번호 거부의 실제 동작 설명은 살릴 수 있으나 상태가 바뀌는 순서를 읽기 어렵다. | 문서 개정→이전 검색 선택 거부→재검색→삭제의 작은 시간순 예로 풀고 실제 SQLite 결과와 원문 버전을 연결한다. |

**재사용:** LocalIndex·L3의 실제 갱신/삭제/재색인과 합성 ANN 비교 증거를 재사용한다.

**재검증:** 새 그래프/군집 예는 설명용임을 표시하고 논리를 검토한다. Index 계약/필터/갱신/삭제 로직 변경 시 해당 생명주기·출처·오래된 선택 거부 회귀가 필요하다.

### RAG

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-09.U01 · Offline과 Online의 연결](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/rag/lesson.md#L9) | 단계별 책임은 상세하지만 한 질문이 검색→Context→생성→근거 검토를 거치는 완성 예가 없다. | 하나의 질문·원문 발췌·검색 결과·최종 입력·실제 초안/실패를 묶어 해설하고 작은 핵심 연결 코드를 붙인다. |
| [K2-09.U02 · Chunk 구조와 Query Rewrite](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/rag/lesson.md#L31) | C07 rewrite·C09 neighbors를 실험 이름으로 안내하지만 바꾸기 전후 질의/문맥의 실물이 없다. | 바꾼 검색어와 그대로인 사용자 질문, 추가된 주변 줄을 보여준다. 비교 조건을 분리한 기존 실험은 유지한다. |
| [K2-09.U03 · Grounding·Citation·응답 보류](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/rag/lesson.md#L51) | 30000원 인용으로 50000원 주장이 통과할 수 있다는 반례가 좋다. | 반례를 보존하고 주장→인용→실제 조항→검토 결론을 직접 읽게 한다. Source ID/부분 문자열 검사와 의미 검토를 구분한다. |
| [K2-09.U04 · 검색 실패와 생성 실패의 평가](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/rag/lesson.md#L73) | 검색·문맥·생성 실패의 분류와 제출 표는 있지만 한 실패를 고치는 판단 과정이 없다. | 실제 실패 하나의 증거→원인 후보→한 변경→재평가→남은 한계를 해설한다. 기존 Qwen 품질 보류를 성공으로 바꾸지 않는다. |

**재사용:** 기존 E5+Qwen 실행·v1/v2 비교·질의/주변 줄 실험·실제 실패/인용 기록을 보존한다.

**재검증:** 기존 결과를 발췌해 해설하면 전량 재생성하지 않는다. 입력/검색/모델 조건 변경 시 관련 사례를 재실행하고 의미·조건·예외를 원문 대조한다. 답변 품질 미통과는 유지한다.

### Single-Agent

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-10.U01 · Agent·Workflow·Tool·MCP](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/single-agent/lesson.md#L9) | Workflow/Agent 표는 유용하지만 모델의 도구 요청이 실제 관찰로 돌아오는 완성 예가 없다. | 검색 요청→실행기 검사→도구 결과→원문 읽기→최종 초안/중단을 작은 Trace로 설명한다. MCP는 현재 구현과 구분한다. |
| [K2-10.U02 · Tool Schema·Registry·검증](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/single-agent/lesson.md#L31) | Schema/Registry·인수/승인 검사의 경계는 있으나 유효 요청과 거부 요청의 실제 쌍이 없다. | 자연어 작업 목적 뒤 요청 JSON 두 개와 핵심 dispatch 분기를 읽는다. 실제 필드명은 설명과 함께 보존한다. |
| [K2-10.U03 · State·Observation·종료](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/single-agent/lesson.md#L51) | State/Observation/상한·dispatch 계수의 구분이 압축돼 있다. | 한 회차의 입력 상태·선택·도구 시도·반환·다음 상태를 연결하고 반복 실패/종료를 해설한다. |
| [K2-10.U04 · Single-Agent 평가와 Framework 포팅](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/single-agent/lesson.md#L73) | 18사례 평가·StructuredTool 범위는 한정하지만 Framework 포팅의 실제 학습 예가 부족하다. | 기존 읽기 도구 invoke와 공통 Registry 결과를 작은 코드/관찰로 설명한다. Framework Agent 전체·MCP·실제 인증은 미구현으로 계속 남긴다. |

**재사용:** 기존 Registry/Schema·18사례·고정 경계·실제 모델 Trace·StructuredTool 연결을 재사용한다.

**재검증:** 학습용 Trace를 실제 로그와 대조한다. 요청/도구/상태 로직 변경 시 관련 경계 회귀와 실제 해당 행동을 확인한다. Framework Agent 전체/MCP/실제 인증은 별도 미완료다.

### Multi-Agent

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-11.U01 · 역할 분리가 필요한 문제](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/multi-agent/lesson.md#L9) | 역할별 목표/도구/예산 표가 먼저 나오고 같은 질문을 나누는 실제 이유/교환 내용은 생략돼 있다. | 한 질문을 단일 실행과 검색자/작성자/검토자로 나눠 보는 작은 사례를 먼저 설명한다. 예산 차이가 있는 비교의 한계를 유지한다. |
| [K2-11.U02 · 역할별 상태·Tool·입출력](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/multi-agent/lesson.md#L27) | Handoff 필드와 NO_EVIDENCE 등 상태 이름을 압축해서 제시한다. | 실제로 읽은 근거를 어떤 정보와 함께 넘기고 수신자가 무엇을 못 읽는지 메시지 하나를 풀어 해설한다. |
| [K2-11.U03 · 검토와 한 번의 보완](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/multi-agent/lesson.md#L47) | M02의 추가 근거 요청 순서는 있지만 초안→반려/요청→보완 결과의 내용이 없다. | 기존 고정 응답 경계 실험에서 한 사례를 완성 예로 해설한다. 전체 공통 보완 예산을 재진입 때도 유지하는 이유를 설명한다. |
| [K2-11.U04 · 실패 전파와 동일 조건 비교](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/multi-agent/lesson.md#L68) | Single/Multi 비교와 별도 Role Probe의 한계는 잘 한정했지만 학생의 판정 예가 없다. | 같은 사례의 도달 단계/종료/호출을 읽고 채택 여부를 설명한다. 별도 역할 성공을 전체 성공으로 세지 않는다. |

**재사용:** 기존 역할 계약·고정 M01~M04·실제 비교/별도 Role Probe를 재사용한다.

**재검증:** Handoff/보완 예를 실제 입력·출력과 대조한다. 계약·예산·재진입 코드가 바뀌면 관련 경계와 비교 조건을 재검증한다. 별도 Probe를 통합 성공으로 바꾸지 않는다.

### Dataset·미세조정

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-12.U01 · 학습 목표·PEFT 계열과 전략 선택](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/lesson.md#L7) | SFT와 PEFT 계열을 구분하는 표는 있으나 대안이 많고 실패→선택의 판단 예가 없다. | 한 업무 실패를 Prompt/검색/데이터/학습으로 어디서 고칠지 먼저 판단한다. LoRA를 중심으로 계열 지도를 읽고 IA3/DoRA 전수 실행을 필수로 늘리지 않는다. |
| [K2-12.U02 · Dataset 설계·제작·검수·분리](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/lesson.md#L39) | Dataset 구성/검수 규칙은 있으나 좋은/나쁜 실제 예제를 제작 REVIEW로 넘긴다. | 시설 규정 원문 한 개→질문→교사 응답→검수/그룹 분리→Datasets 행의 완성 예를 본문에 넣고 핵심 변환 코드를 해설한다. |
| [K2-12.U03 · Train 데이터 증강·합성·품질 관리](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/lesson.md#L64) | 증강 채택/기각 표는 있지만 부모 질문과 실제 변형·라벨 판정의 문장이 없다. | 기존 고정 후보 중 의미 유지/조건 변경/잘못된 인용을 실제 문장으로 비교한다. Train 한정·부모 계보·독립 검수 부재는 유지한다. |
| [K2-12.U04 · 학습 입력·Chat Template·Loss 범위](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/lesson.md#L84) | assistant~EOS와 -100을 기술하지만 작은 Token/label 정렬 예가 본문에 없다. | 실제 한 행의 메시지→Template→Token→label→Padding을 해설한다. Attention mask와 Loss 범위를 구분하고 코드 배제 문구를 고친다. |
| [K2-12.U05 · LoRA 원리·설정·실제 훈련](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L7) | LoRA Parameter 수 예는 있으나 두 작은 행렬의 곱/출력 갱신이 없다. 본문은 초기 4 Step 실험 중심이다. | 작은 ΔW 계산과 학습 가능 값의 역할을 설명한다. 초기 확인과 전체 데이터 28 Step 실행을 명확히 구분해 현재 기본 실습 경로를 정한다. |
| [K2-12.U06 · QLoRA·양자화와 자원 조건](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L27) | NF4·이중 양자화·dtype·Optimizer를 짧게 묶고 곧바로 장비 검증을 요구한다. | Weight 저장/계산과 전체 훈련 메모리의 구성 요소를 예로 설명한다. QLoRA 훈련/저장/재로드는 미검증이며 4bit 추론으로 대체 완료하지 않는다. |
| [K2-12.U07 · 동일 기준 평가·실패 진단·선택 기법 비교](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L44) | 본문은 전체20/28개 학습·18회귀를 이후 할 일로 쓰지만 말미와 후속 결과는 이미 실행했다고 한다. | 현재 완료/미완료를 하나의 기준표로 정리하고 실제 답 한 개를 Base/Tuned/Loss/행동/근거로 해석한다. 다중 Seed·독립 검수·선택 기법 실행은 별개 미완료다. |
| [K2-12.U08 · Adapter 저장·새 프로세스 Reload·결과 Card](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/fine-tuning/training.md#L56) | 새 프로세스 Reload의 이유와 파일 역할은 있으나 저장→종료→다시 로드의 코어 절차가 없다. | 기존 Adapter/검증을 보존하고 핵심 저장/로드 코드와 정확한 명령·비교 결과를 해설한다. 병합·변환 검증과 구분한다. |

**재사용:** finetuning-v1의 40원본/8채택 증강과 검수/분리 Manifest, Datasets/Mask 관찰, 초기 4 Step·후속 20/28예제 28 Step·18회귀/Reload의 각 증거를 보존한다.

**재검증:** 데이터/Template/label 변경 시 데이터·Mask와 영향 받는 학습/평가를 재검증한다. 문서의 경로/현재 상태 정리 때문에 기존 훈련 전체를 다시 하지 않는다. QLoRA·IA3/DoRA·다중 Seed·독립 품질 검증은 미완료다.

### 문서 Parsing·OCR

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-13.U01 · PDF 유형·Parsing·OCR 선택](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-parsing/lesson.md#L7) | 디지털/스캔/혼합 PDF와 실제 미리보기, 선택 기준은 살릴 설명이다. | 이미지·비교를 유지한다. L8 안내에 실제 첫 명령·입력 경로·출력에서 볼 부분을 넣어 Python 소스의 docstring을 찾아야 하는 부담을 줄인다. |
| [K2-13.U02 · Layout·표·Reading Order](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-parsing/lesson.md#L24) | 두 열 읽기 순서·표의 행/열 관계와 실제 화면 예가 있다. | 그림을 없애지 않고 추출 전후 텍스트를 함께 읽게 한다. 사람이 정한 두 열/표 한 개의 범위를 일반 문서 처리로 확대하지 않는다. |
| [K2-13.U03 · OCR와 Vision의 품질·한계](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-parsing/lesson.md#L47) | 실제 OCR 오독과 CER/WER·Vision 계열 비교가 있으나 편집 오류 계산/작업별 입출력이 압축돼 있다. | 짧은 정답/오독의 치환·삽입·삭제 계산을 풀고 OCR와 Vision 입력/출력을 한 작업으로 비교한다. 실제 VLM 실행 미완료는 유지한다. |
| [K2-13.U04 · 문서 안의 지시·권한·원문 추적](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-parsing/lesson.md#L82) | 논리 출처와 물리 Locator·문서 지시/권한을 구분하지만 좌표를 실제 페이지로 읽는 예가 없다. | 원문 하나의 페이지/사각형→정규화 좌표/화면 위치를 해설한다. 기존 권한 거부/원문 추적 자료는 재사용한다. |

**재사용:** 합성 PDF·정답·이미지·추출/OCR·원문 위치·기존 경계 결과를 재사용한다.

**재검증:** CLI 안내 수정 때 실제 인수/경로와 맞춘다. Parser/OCR 옵션·입력·좌표/Locator가 바뀌면 해당 추출·오류·출처 계산과 필요한 화면을 재검증한다. 일반 문서/Vision 품질은 별도다.

### 문서 AI·보고서·화면

| 단원·근거 위치 | 확인한 상태·학습자가 막힐 부분 | 유지/수정할 내용 |
|---|---|---|
| [K2-14.U01 · 형식·원본·공통 문서 구조](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/intake.md#L7) | intake의 DOCX 거부/어댑터 미구현은 현재 Registry의 docx 분기·허용 형식과 다르다. | 이전 단계 상태와 현재 완성 코드를 구분한다. 지원 범위를 현재 코드와 맞추고 원문→Element→Chunk→Locator 한 레코드를 풀어 설명한다. |
| [K2-14.U02 · 문서 상태·권한·삭제](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/intake.md#L46) | 상태·요청 키·세대 무효화 설명은 있으나 실제 재업로드/삭제의 전체 예가 없다. | 같은 파일 재전송→개정 업로드→이전 선택 거부→삭제를 작은 기록으로 읽게 한다. 후속 보고서 기능과 이번 학습 시작/종료 상태를 구분한다. |
| [K2-14.U03 · 근거·검토·문서 생성](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/report.md#L5) | 7일 주장과 30일 인용의 반례, 실제 DOCX/PDF는 있으나 검토→출력의 완성 학습 절차가 부족하다. | 주장/근거/검토 결정/고정 명세→두 출력의 흐름과 핵심 코드를 설명한다. v1 출력과 후속 v2 템플릿의 기준을 분리한다. |
| [K2-14.U04 · Provider 기능과 운영 예산](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/provider.md#L5) | Capability/Readiness·Context/공유 예산의 구분과 21×2=42 계산은 살릴 내용이다. | 계산을 보존하고 한 실제 요청의 허용/거부 Trace와 정확한 실행 명령을 해설한다. 별도 Router와 웹 Factory 미통합 범위를 유지한다. |
| [K2-14.U05 · React와 Streaming 통합](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/streaming.md#L7) | 바이트/SSE/Token과 취소 경합 설명은 있으나 실제 이벤트 묶음과 화면 상태의 연결 예가 없다. | 작은 raw SSE 입력→파싱된 이벤트→React 부분/확정/취소 화면을 해설하고 정확한 시작 명령을 넣는다. 고정 답변 분할과 실제 모델 Token Streaming을 구분한다. |
| [K2-14.U06 · 다중 형식 확장과 최종 평가](https://github.com/cocoa2260/k-edu/blob/7c3171182f67be818980a94afebab437b9858030/curriculum-work/lessons/document-ai/evaluation.md#L7) | 최종 본문에 54/70·남은16개·다음 시작안내 제작이 남아 수강 순서와 현재 제작 상태를 혼동시킨다. | 제작 수/다음 제작 안내를 관리 기록으로 옮긴다. 세 형식의 원문→구조→주장→보고서 비교를 최종 학습 과제·해설로 완결하고 기존 품질 보류를 유지한다. |

**재사용:** 현재 PDF/TXT/DOCX Registry·IR, 보고서 명세/출력·Router·SSE/React와 실제 다중 형식 증거를 재사용한다.

**재검증:** 현재 코드와 과거 단계 시연을 구분해 실행 위치/명령을 정리한다. 코드가 바뀌면 해당 Registry/보고서/Router/Parser·UI 회귀만 실행한다. 실제 모델 Streaming·FastAPI 전체 통합·인증·운영/수업 품질은 미완료다.

## 다음 수정의 범위와 종료 조건

대표본은 **Prompt 강의 전체 네 단원과 연결된 입력 비교 실습(L1)**으로 정한다. 첫 설명·완성 예제·질문 결함이 한 문서에 분명하고 기존 자료/준비 코드/Token 관찰을 활용할 수 있다. Context는 바로 이어지는 자료지만 이번 대표 수정에서 전체를 동시에 재작성하지 않는다. Prompt 수정으로 직접 바뀌는 연결만 맞춘다.

학생용 본문과 필요한 강사용 해설을 먼저 완성한다. 식비 문의 하나를 원문→질문→지시 전후→예시 추가→평가로 읽을 수 있어야 한다. 실제 실행된 입력, 합성 설명 예, 실제 모델 응답/미실행을 구분한다. 대표본 검수에서는 학습자가 왜 비교하는지, 무엇을 바꾸고 관찰하는지, 잘못된 결론을 어떻게 가리는지 실제 문장/예제로 다시 판단한다. 문장 수나 테스트 수로 통과시키지 않는다.

명령·코드·입력/출력이 바뀌었거나 새 실행 증거가 필요한 범위를 확인하고 그 부분만 검증한다. 설명만 바꾸었는데 전체 모델/훈련을 다시 돌릴 필요는 없다. 대표본에 같은 결함이 남으면 후속 교안으로 확대하지 않는다. 이후 Context/Harness→검색/RAG→Agent→Dataset/학습→문서/화면 순서로 실제 내용이 필요한 부분을 고치고, 기존 설명이 충분한 기초 자료는 표기·연결 위주로 정비한다.

다음 추천 추론 강도는 **High**다. 기준 재설계/전수 범위 판단을 마쳤고 대표본의 대상·결함·재사용 자료가 정해졌기 때문이다. 실제 설정을 자동 변경한 것은 아니다.
