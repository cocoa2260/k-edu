# Day 3 - 2교시. Base/Pre-trained Model과 Instruction-tuned Model의 차이 (v0.2)

## 개요 — 같은 Model Family인데, 왜 응답 방식이 다를까?

Day 3 - 1교시에는 Gemma를 사례로 **Family → Generation → Variant**를 구분했습니다. 이번에는 Variant 이름을 읽는 것에서 한 단계 나아가 **학습 목적의 차이가 실제 응답 행동에 어떻게 나타나는지** 관찰합니다.

앞 교시에서 `Base`, `Pre-trained`, `Instruct`, `IT`, `Chat`이라는 표기를 만났다면, 오늘의 질문은 다음과 같습니다.

> **같은 계열의 모델인데 왜 어떤 모델은 입력된 글을 이어 쓰고, 어떤 모델은 요청된 일을 수행하는 답변을 만들기 쉬운가?**

오늘의 목표는 모델을 직접 추가 학습하는 것이 아닙니다. **학습 단계가 서로 다른 모델을 구분하고, 동일한 과제에서 나타나는 행동 차이를 설명하는 것**입니다. 답변의 옳고 그름, 지시한 형식을 지켰는지, 입력 형식이 적합했는지를 구분하여 관찰합니다.

**이번 교시에서 다루지 않을 것:** Day 2의 Training Loop 재구현, Tokenizer·Tensor 생성 코드 재실습, 새로운 Ollama 명령어, 실제 Fine-tuning 수행, RAG 구성, Model Size·Quantization 계산, 정식 Model Selection 평가 및 Provider 통합 구현. 해당 사항은 앞 교시에서 학습했거나 후속 과정의 담당 범위입니다.

---

# 1. 학습 목표와 완료 기준

이 교시를 마치면 학습자는 다음을 할 수 있어야 합니다.

1. **Pre-training과 Instruction 관련 Post-training의 목적 차이**를 설명할 수 있다.
2. Base/Pre-trained와 Instruction-tuned가 무엇을 의미하는지 **사용 목적을 중심으로** 구분한다.
3. 두 Variant 모두 Language Model의 생성 능력을 사용한다는 점을 설명한다.
4. `Instruction Tuning`과 **현재 입력을 설계하는 Prompt 작성**을 구분한다.
5. Chat/Instruction Variant의 **권장 입력 형식이 결과에 영향을 줄 수 있음**을 설명한다.
6. 동일한 과제를 두 Variant에 제시할 때 **관찰 조건과 기록 항목**을 정한다.
7. **Instruction Following, 형식 준수, 사실 정확성**을 별개의 관찰 항목으로 기록한다.
8. 실제 실행 결과와 강사의 예시·예상 결과를 구별한다.
9. Gemma 계열 Model Card에서 **Pre-trained/Instruction-tuned 관련 표기와 근거**를 찾는다.
10. 모델의 크기·최적화·배포 방식이 아니라 **모델이 어떤 행동을 하도록 조정되었는가**에 대해 답한다.

**완료 산출물:** 두 Variant의 공식 표기와 입력 방식 확인표 1개, 같은 과제의 비교 관찰표 1개, 관찰 결과 해석문 3~5문장.

---

# 2. 이전 교시에서 가져오는 것과 새로 배우는 것

| 선행 학습에서 이미 확인한 내용 | 이번 교시에서 새롭게 확인할 내용 |
|---|---|
| Day1: 생성형 AI가 입력을 바탕으로 결과를 생성함 | **같은 생성 모델 계열**이더라도 추가 조정 목적이 다를 수 있음 |
| Day2 1교시: Language Model의 Token 생성 | 생성 원리 자체보다 **어떤 응답을 선호하도록 학습되었는가** |
| Day2 3교시: Training은 Parameter를 조정함 | 학습 데이터의 **목표 행동**에 따라 결과의 성격이 달라지는 점 |
| Day2 4교시: Model Card에서 정보를 확인함 | `Base`/`IT`/`Chat`의 실제 의미를 **선정 모델 문서에서 판정** |
| Day2 5교시: Model에 맞는 Chat Template 사용 | 그 입력 형식이 **Variant 비교의 공정성에 왜 필요한가** |
| Day3 1교시: Family·Generation·Variant 식별 | 같은 계열에서 **학습 목적이 다른 Variant 비교** |

예를 들어 Day2 3교시의 `nn.Linear` 예제를 다시 학습시킬 필요는 없습니다. 다만 **추가 Training을 하면 Parameter가 달라질 수 있다**는 사실은 오늘 두 Variant의 차이를 이해하는 전제입니다.

핵심은 개념 복습의 길이가 아니라 **새로운 관찰 질문**입니다. `Model이 무엇인가?` 대신 `이 모델은 어떤 방식으로 답변하도록 조정되었는가?`를 묻습니다.

---

# 3. Pre-training은 어떤 목적의 학습인가?

원본 강의는 대규모 Language Model의 Pre-training을 **많은 Text Data의 Language Pattern을 학습하는 단계**로 설명합니다. 이미 배운 Training 단계의 `Loss → Gradient → Parameter Update`를 여기서 다시 구현하지는 않습니다.

개념적 흐름만 연결합니다.

```text
Large Text Data
      ↓
Pre-training
      ↓
Language Modeling을 수행하는 기반 모델
```

Pre-training에서 모델은 다양한 문장과 표현, 데이터에 나타난 관계를 학습할 수 있습니다. 그렇다고 이 모델이 자동으로 **사람의 모든 지시를 순서대로 따르는 Chat Assistant**로 조정되었다는 의미는 아닙니다.

학생에게는 다음 질문을 던집니다.

> 책과 문서에 나타나는 문장 패턴을 잘 이어 쓰는 능력과, 사용자가 지정한 조건에 맞춰 답변하는 능력은 반드시 같은 것일까요?

두 능력은 관련되어 있지만 **동일하다고 단정할 수 없습니다.** 이것이 다음 단원의 출발점입니다.

---

# 4. Base/Pre-trained Model — 입력을 어떻게 받아들이는가?

Base/Pre-trained Language Model은 일반적으로 기반 Pre-training 결과와 가까운 Variant입니다. 원본의 핵심 표현은 **Text Continuation**, 즉 앞에 제공된 Text Sequence에 이어질 내용을 생성하는 관점입니다.

가령 다음과 같은 입력이 있다고 합시다.

```text
질문: 인공지능이란 무엇인가?
답변: 인공지능은
```

이것은 원본 강의에 등장한 **질문·답변 형식의 텍스트 예시**입니다. Base Model이 이 패턴을 이어 작성할 가능성은 있습니다. 하지만 그 결과가 반드시 사용자의 요청 조건을 지키거나 Assistant처럼 행동한다는 보장은 없습니다.

Base Model이 보일 수 있는 행동의 예:

- 질문의 답을 이어서 생성한다.
- 입력된 문구를 완결하지 않고 다른 설명으로 이어간다.
- 학습된 문서·대화 형식과 닮은 문장을 더 생성한다.

이 목록은 **가능한 행동의 유형**이지, 특정 모델을 실제 실행한 결과가 아닙니다. Base Model도 질문에 적절히 답할 수 있으며, 사용자가 요청한 형식을 지키는 경우도 있습니다.

**핵심 판정:** `Base = 질문에 답할 수 없는 모델`이 아니라, `Instruction Following에 맞춰 추가 조정된 모델이라고는 볼 수 없다`입니다.

---

# 5. 왜 Instruction Following이 별도의 목표인가?

사용자는 단순히 다음 문장을 이어 써 달라는 경우도 있지만, 실제 Application에서는 **수행할 작업과 결과 형식을 지정**합니다.

원본에 나온 요청 형태를 하나 선택해 봅시다.

```text
AI와 머신러닝의 차이를 표로 정리해줘.
```

이 요청에는 두 가지 요구가 들어 있습니다.

1. **수행할 일:** 두 개념의 차이를 설명할 것.
2. **출력 조건:** 자연어 문단이 아니라 표 형태로 정리할 것.

Model은 요청에 등장한 단어를 이어 쓰는 것뿐 아니라 **어떤 일을 시켰고 어떻게 보여 달라고 했는지** 파악해 응답해야 합니다. Instruction Tuning은 이러한 Instruction–Response 관계를 더 잘 처리하도록 모델을 조정하는 접근입니다.

그러나 `Instruction을 잘 따른다`는 `생성된 정보가 언제나 사실이다`라는 뜻은 아닙니다. 오늘은 이 둘을 끝까지 분리해서 봅니다.

---

# 6. Instruction Tuning — 모델에서 무엇이 달라지는가?

원본은 Instruction Tuning을 **다양한 Instruction에 적절한 Response를 생성하도록 추가적으로 조정하는 Training 접근**으로 설명합니다.

개념적인 학습 자료의 짝은 다음과 같습니다.

```text
Instruction: "다음 문장을 요약해줘."
Input:       "긴 문서..."
Expected:    "요약 결과..."
```

여기서 학습의 초점은 단순한 텍스트 나열이 아니라 **Instruction과 바람직한 Response의 대응 관계**입니다.

```text
Pre-training으로 준비된 Base Model
               ↓
Instruction에 반응하도록 추가 조정
               ↓
Instruction-tuned Model
```

이 추가 조정은 모델에 반영되는 **학습 과정**입니다. 따라서 일반적으로 학습된 Parameter의 일부 또는 전부가 변경될 수 있습니다. 어느 Parameter를 조정하는지, 어떤 최적화 절차를 쓰는지는 학습 방법과 모델에 따라 달라집니다.

여기서 유의할 점이 두 가지 있습니다.

- 공개된 모든 Model Family가 **똑같은 Post-training Pipeline**을 사용하는 것은 아닙니다.
- 실제 제품 또는 공개 모델의 조정 방식에는 여러 기법이 포함될 수 있으므로, 특정 모델이 `Instruction-tuned`라고 해서 **오직 한 단계의 Instruction 학습만 거쳤다**고 단정하지 않습니다.

구체적인 학습 알고리즘과 Fine-tuning 구현은 후속 과정에서 다룹니다. **지금은 ‘변경하려는 모델의 행동이 무엇인가’를 이해하는 데 집중**합니다.

---

# 7. Base와 Instruction-tuned — 서로 다른 모델인가, 다른 생성 원리인가?

두 Variant의 차이를 `하나는 Token을 생성하고, 다른 하나는 명령을 바로 실행한다`로 설명하면 잘못입니다.

Autoregressive Language Model을 전제로 하면 두 모델 모두 Context에 이어질 Token을 선택·생성하는 방식으로 응답할 수 있습니다. 달라지는 것은 **어떤 Response Pattern이 나오도록 Parameter가 조정되었는가**입니다.

| 비교 항목 | Base / Pre-trained | Instruction-tuned |
|---|---|---|
| 학습의 중심 | Language Modeling의 기반 확보 | Instruction에 대한 응답 행동 개선 |
| 같은 질문을 받았을 때 | 연속 문장 생성 성격이 드러날 수 있음 | 요청한 작업을 수행하는 답변에 더 적합하도록 조정됨 |
| 결과 형식 | 지시한 형식 준수가 보장되지 않음 | 준수 가능성이 높아질 수 있으나 보장하지 않음 |
| Chat/Assistant 목적 | 추가 설계나 조정이 필요할 수 있음 | 일반적으로 먼저 검토할 수 있는 유형 |
| 추가 학습·연구 목적 | 출발 모델로 활용될 수 있음 | 특정 목적에 따라 활용될 수 있음 |
| 정확성 | Model/Task에 따라 평가 필요 | Model/Task에 따라 평가 필요 |

이 표의 `가능성`, `일반적으로` 같은 표현은 중요합니다. 특정 두 모델의 성능을 직접 측정한 결과가 아니며 **경향과 사용 목적의 차이**를 설명합니다.

---

# 8. `Instruct`, `IT`, `Chat` — 이름만 보고 결론 내리면 안 된다

Model Repository에서는 `Base`, `Pre-trained`, `Instruct`, `IT`, `Chat` 등 여러 표기를 만날 수 있습니다. 원본의 Gemma 사례 역시 이런 이름을 Model Card에서 찾아보도록 구성되어 있습니다.

이름은 **후보를 찾는 단서**가 될 수 있지만 최종 근거는 아닙니다.

| 보이는 표기 | 먼저 해 볼 질문 | 확인할 곳 |
|---|---|---|
| `Base` / `Pre-trained` | 기반 학습 결과로 소개되는가? | 정확한 Variant의 공식 설명 |
| `Instruct` / `Instruction-tuned` | 지시 수행을 개선한 모델인가? | Training/Post-training 및 Intended Use |
| `IT` | 이 Family에서는 어떤 약어인가? | Naming Rule 또는 Model Card |
| `Chat` | 대화용 입력 형식과 사용 예제를 제공하는가? | Usage Example, Chat Template 설명 |

**주의:** `Chat`이라는 이름이 붙었다고 모든 모델이 동일한 Role이나 Chat Template을 사용한다는 의미는 아닙니다. 또 `IT` 같은 약어가 Family마다 반드시 같은 뜻인 것도 아닙니다.

Day3 1교시에서 작성한 Variant 식별 카드를 활용하되, 오늘은 **학습 목적과 입력 형식에 해당하는 칸만 새로 확인**합니다. 모델 계열 전체를 처음부터 재분류하지 않습니다.

---

# 9. Chat Model은 반드시 Instruction-tuned인가?

원본은 `Chat`, `Instruct`, `Instruction-tuned`, `IT`가 Assistant/Conversation 용도로 조정된 Variant를 가리키는 경우가 많다고 설명합니다. 다만 **모든 Family가 같은 명칭과 동일한 학습 방법을 쓰는 것은 아닙니다.**

실무에서는 용어만으로 단정하기보다 아래를 확인합니다.

- 사용자와 Assistant의 **다중 메시지 입력**을 지원하도록 소개되어 있는가?
- 공식 사용 예제에 요구되는 **Conversation Format**이 있는가?
- Intended Use가 일반적인 Chat Assistant에 맞는가?
- 단순 Text Continuation과 Instruction Following 중 무엇이 문서에서 강조되는가?

예를 들어 같은 Family의 Base Variant와 Chat Variant가 있더라도, 두 모델의 이름과 Model Card를 함께 봐야 비교 대상인지 판단할 수 있습니다.

이 교시에서는 Chat의 내부 학습법을 더 쪼개어 가르치지 않습니다. **모델이 어떤 입력 형식을 기대하는지와, 관찰하려는 행동이 무엇인지**를 연결하는 것으로 충분합니다.

---

# 10. Chat Template — ‘같은 질문’을 공정하게 비교하려면

Day2 5교시에서 Chat Model을 실행할 때 공식 Chat Template을 확인해야 한다고 배웠습니다. 이번에는 사용법을 다시 작성하지 않고 **왜 비교 결과의 해석에 영향을 주는지**만 다룹니다.

두 모델에 아래의 의미를 동일하게 전달한다고 가정해 봅시다.

```text
요청: "AI와 머신러닝의 차이를 표로 정리해줘."
```

Base Model은 일반 Text Prefix를 기대할 수 있고, Instruction-tuned Model은 특정 Role/Special Token을 포함하는 Chat Format을 기대할 수 있습니다. 같은 사람이 읽는 요청 문장을 입력하더라도 **실제 Model에 전달되는 Token Sequence나 구성 방식은 다를 수 있습니다.**

따라서 비교할 때 중요한 원칙은 다음과 같습니다.

1. **과제의 의미는 같게 유지**합니다.
2. 각 Model에 **공식적으로 권장된 입력 형식**을 사용합니다.
3. 다른 조건도 가능한 범위에서 동일하게 기록합니다.
4. 두 모델의 실제 입력 방식이 달랐다면 **그 차이 자체를 관찰표에 남깁니다.**

이 경우 두 모델이 정확히 같은 Token ID를 입력받는 실험은 아닙니다. 따라서 결과 차이를 **Instruction Tuning 하나의 효과라고 인과적으로 단정하지 않도록** 주의해야 합니다.

---

# 11. `System / User / Assistant`는 왜 등장하는가?

원본은 Chat Model에서 흔히 보게 되는 세 가지 Role을 제시합니다.

| Role | 메시지 안에서 나타내는 역할 |
|---|---|
| System | 응답 행동에 대한 상위 지시가 담길 수 있는 부분 |
| User | 사용자 요청이 전달되는 부분 |
| Assistant | 모델의 답변 또는 대화 기록이 구분되는 부분 |

이 역할 구분은 **대화 데이터를 구성하는 표현**입니다. 모델에 실제로 전달되는 형식은 해당 Model의 Template과 Runtime이 처리하는 방식에 따라 달라집니다.

`messages`라는 Python 자료 구조를 모델이 그대로 ‘읽는다’고 생각하면 안 됩니다. 필요한 경우 해당 모델의 권장 형식으로 변환되어 입력됩니다. 그 변환 코드는 이미 Day2 5교시에서 다뤘으므로 **이번 교시에서는 다시 코딩하지 않습니다.**

여기서 학생이 답해야 할 질문은 `Chat Template 메서드 이름이 무엇인가?`가 아닙니다.

> **모델의 기대 형식에 맞지 않은 입력으로 테스트하면 왜 두 Variant의 행동을 제대로 비교하기 어려운가?**

형식이 맞지 않아 발생한 문제를 `Base Model이기 때문`, `Instruction Model이라서 성능이 나쁘다` 같은 단정으로 설명하지 않기 위해서입니다.

---

# 12. Prompt를 수정한 것과 Model을 추가 학습한 것은 다르다

Day2 7교시에서는 같은 Local Model에 다른 Prompt를 넣어 결과를 비교했습니다. 이번 교시에서는 **실험 결과가 달라졌을 때 무엇이 변했는지**를 구분합니다.

| 상황 | 달라진 것 | 이번 교시에서의 판정 |
|---|---|---|
| 하나의 Model에 Prompt 문장만 바꿈 | 현재 입력 내용 | **Model의 추가 학습이 아님** |
| 이전 대화 내용을 함께 전달함 | 현재 요청에 포함된 Context | **Parameter 업데이트가 아님** |
| Base Model을 별도의 Instruction-tuned Variant로 바꿈 | 사용한 모델 및 학습된 Parameter 상태 | **다른 학습 상태의 모델을 사용** |
| Instruction Tuning을 실제 수행함 | 학습 과정에 따라 Model Parameter | **Training 과정** |

특히 `모델이 방금 대화한 것을 기억하는 것처럼 답했다`는 관찰만으로 **이번 대화에서 Model이 Training되었다고 주장할 수 없습니다.**

새로운 지식이나 사내 문서를 최신으로 반영하려는 문제는 Instruction Tuning의 정의만으로 해결할 수 없습니다. 외부 정보 활용이나 다른 학습·검색 접근은 이후 별도 과정에서 다루며 **이번 교시에 구현하지 않습니다.**

---

# 13. 동일한 과제 비교 실험 — 무엇을 통제할까?

오늘의 대표 활동은 **가능한 한 관련성이 높은 Base Variant와 Instruction-tuned Variant를 비교**하는 것입니다. 이 활동은 Day3 5교시에서 수행할 정식 Model Selection 평가를 대신하지 않습니다.

강사는 먼저 교육과정 원본에 제시된 기준대로 **공식 문서에서 확인 가능한 Gemma 계열의 두 Variant**를 준비합니다. 다만 실제 Model ID와 세대·크기·접근 조건은 교육장 환경에서 확정해야 하며, 문서에 임의로 ‘실행 완료된 모델’ 이름을 만들어 쓰지 않습니다.

### 13.1 실험 전 기록할 조건

| 항목 | Base Variant | Instruction-tuned Variant | 비교 시 확인할 점 |
|---|---|---|---|
| Family / Generation | 강사 입력 | 강사 입력 | 가급적 동일한 계열 |
| 정확한 Model ID | 강사 입력 | 강사 입력 | 이름 추측 금지 |
| Parameter 규모 | 강사 입력 | 강사 입력 | 가능한 한 같은 규모 |
| Model Card상 유형 | 강사 확인 | 강사 확인 | Pre-trained / Instruction의 근거 |
| 권장 입력 형식 | 강사 확인 | 강사 확인 | Text / Chat Template 등 |
| 실행 환경 | 강사 확인 | 강사 확인 | 각 Model 지원 방식 |
| Generation 길이 상한 | 강사 지정 | 강사 지정 | 비교 가능한 범위에서 통일 |
| Sampling 조건 | 강사 지정 | 강사 지정 | 다르면 기록 |
| 대화 History | 없음/있음 | 없음/있음 | 입력 Context 차이 통제 |

**같은 Family라면 다른 조건도 자동으로 같아지는 것은 아닙니다.** Runtime의 기본 Generation 설정, Chat Template, 모델마다 제공되는 Special Token 등이 달라질 수 있기 때문입니다.

완전히 동일한 조건을 만들 수 없다면 그 차이를 기록하고 **기본적인 관찰 비교**로 해석합니다. 확인되지 않은 사양을 채워 넣지 않습니다.

### 13.2 비교할 과제

원본의 `AI와 머신러닝의 차이를 표로 정리해줘.`를 이번 활동의 기준 요청으로 사용합니다. 학생은 아래 항목을 예상합니다.

- 두 개념을 **서로 비교하는 내용**이 포함되는가?
- 요청한 **표 형식**이 나타나는가?
- 출력이 **질문 문장을 되풀이하거나 새로운 문장을 이어 쓰는 형태**로 흘러가는가?
- 응답이 확인 가능한 사실을 바탕으로 작성되었는가?

이 질문은 특정 모델이 반드시 어느 형태로 출력할지를 미리 정답으로 지정하지 않습니다. **각 Variant에서 무엇을 확인할지 정하는 관찰 기준**입니다.

---

# 14. 결과를 볼 때 구분할 세 가지

같은 질문에 그럴듯한 표가 생성되었다고 곧바로 좋은 Model이라고 판정하지 않습니다. 원본에서 강조한 `Instruction Following`과 `Factual Accuracy`를 분리합니다.

### 14.1 작업 수행 여부 — Instruction Following

요청한 일을 실제로 했는가? 예를 들어 `두 개념의 차이`를 다뤘는가? **질문과 관련된 글을 길게 이어 쓴 것**과 **지시한 작업을 수행한 것**은 다를 수 있습니다.

### 14.2 출력 형식 준수 여부 — Format Following

요청이 `표로 정리해줘`였다면 표 구조를 지켰는가? 단순 문단이나 추가 설명만 출력했다면 형식 조건을 지키지 않은 것입니다.

### 14.3 내용의 사실성 — Factual Accuracy

표가 형식상 완벽하더라도 개념 설명에 사실 오류가 있을 수 있습니다. **명령 수행 능력과 정답의 정확성은 독립적으로 검토**해야 합니다.

| 관찰 질문 | 예시 판정 | 유의점 |
|---|---|---|
| 과제를 수행했는가? | 충족 / 부분 충족 / 미충족 | 출력이 길다고 충족은 아님 |
| 요구한 형식을 지켰는가? | 충족 / 부분 충족 / 미충족 | 형식과 사실성 분리 |
| 핵심 내용이 정확한가? | 확인 / 오류 발견 / 추가 검토 | 실제 문장에 대한 근거 필요 |

이것은 **수업용 관찰 항목**입니다. 정확도 점수나 Benchmark 결과가 아닙니다. 측정값을 숫자로 만들고 후보를 최종 선정하는 평가는 후속 교시에서 다룹니다.

---

# 15. 실제 출력과 ‘개념적 예상’은 반드시 구분한다

강의실에서 모델을 실행하기 전, 다음과 같은 관찰 유형을 학생과 미리 검토할 수 있습니다.

| 관찰 유형 | 출력에서 나타날 수 있는 양상 | 해석 시 주의할 점 |
|---|---|---|
| Text Continuation | 질문/답변 문서가 계속 이어지는 듯한 문장 | Base 모델에 한정되는 현상이라고 단정 금지 |
| Instruction Following | 요청한 비교 내용과 형식을 맞춰 답함 | Instruction-tuned만 가능한 행동이라고 단정 금지 |
| Format Miss | 설명은 하지만 표 대신 문단으로 답함 | 입력 형식·설정도 원인일 수 있음 |
| Factual Error | 겉보기에는 표지만 설명 내용이 틀림 | Instruction Following과 사실성은 별개 |
| Incomplete Response | 출력이 중간에 끝남 | Generation 길이 상한 등도 확인 |

**이 표는 실행 로그가 아니라 개념적 관찰 범주입니다.** 강사는 실행 직후 받은 실제 답변과 적용된 설정을 기록해야 합니다. 어떤 Variant가 반드시 더 정확하거나 모든 지시를 지킨다는 식으로 결과를 미리 정해 주지 않습니다.

실제 모델을 두 개 모두 실행하기 어렵다면, **모의 출력임을 분명히 밝힌 별도의 예시**로 판정 기준 연습을 할 수 있습니다. 다만 이 경우 `Base와 Instruction-tuned의 실측 비교 완료`라고 기록하지 않습니다.

---

# 16. 학생 활동 A — 두 Model의 실제 유형 확인

Day3 1교시에서 배운 식별 절차를 반복 작성하지 않습니다. 이미 확보한 Model ID 두 개에 대해 **이번 교시에 필요한 정보만** 찾아 작성합니다.

| 확인 항목 | Base 후보 | Instruction-tuned 후보 |
|---|---|---|
| Exact Model ID |  |  |
| Model Card의 유형 표기 |  |  |
| 공식 설명에서 강조하는 사용 목적 |  |  |
| 공식 Usage Example의 입력 형태 |  |  |
| Chat Template 안내 여부 |  |  |
| 유형을 판단한 문장·위치 |  |  |

**규칙:** 이름 끝에 `it`가 있다고 해서 확인을 끝내지 않습니다. Model Card의 해당 모델 설명을 근거로 남깁니다. 정보가 없으면 `미확인`으로 표시합니다.

**제출 문장 예시(틀만 제시):** `후보 A는 Model Card의 [확인 위치]에 [표기]가 있어 Base 계열로 기록했습니다.`

---

# 17. 학생 활동 B — 같은 요청의 응답 비교

두 Model의 입력 형식이 다를 수 있다는 점을 먼저 확인한 뒤, **동일한 의미의 요청**을 전달합니다.

```text
AI와 머신러닝의 차이를 표로 정리해줘.
```

| 기록할 항목 | Base 결과 | Instruction-tuned 결과 |
|---|---|---|
| 응답의 앞부분 실제 문장 |  |  |
| 표 형태로 출력했는가? |  |  |
| 비교 내용이 두 개념 모두를 다루는가? |  |  |
| 설명 중 사실 오류가 의심되는가? |  |  |
| 추가 문장 이어 쓰기·형식 이탈이 나타났는가? |  |  |
| 적용한 입력 형식 |  |  |
| Generation 설정상 차이 |  |  |
| 관찰 결과에서 확정할 수 없는 점 |  |  |

**판정 방식:** `Instruction-tuned가 무조건 승리`라는 답을 쓰지 않습니다. **관찰한 결과가 왜 그 Variant의 목적과 연결될 수 있는지**, 그리고 **다른 원인 가능성은 무엇인지** 함께 씁니다.

해석 예시의 구조:

> `후보 B는 표 형식을 지켰으나, 그것만으로 사실성까지 우수하다고 말할 수는 없습니다. 두 후보의 입력 형식도 달랐으므로 전체 차이가 Instruction Tuning 때문이라고 단정하지 않았습니다.`

이 문장은 **작성 형식 예시**이지 이번 수업에서 확보한 실제 비교 결과는 아닙니다.

---

# 18. 학생 활동 C — 무엇이 바뀐 실험인가?

다음 상황에서 **바뀐 대상**을 구분합니다.

| 상황 | 무엇이 바뀌었는가? | 학습이 수행되었는가? |
|---|---|---|
| A. 같은 Model에 `세 문장으로 답해줘`를 추가 | 현재 Prompt | **아니오** |
| B. 같은 Model의 이전 대화를 함께 전달 | Request Context | **아니오** |
| C. Base Model 대신 이미 준비된 Instruction-tuned Model을 실행 | 사용한 Model의 학습 상태 | **이번 요청에서 학습한 것은 아님** |
| D. 실제로 Instruction Data를 이용해 추가 조정 | Model Parameter의 학습 | **예, Training 작업** |

**강사 질문:** C와 D가 왜 다른가요?

C는 **이미 존재하는 다른 Variant를 선택하여 사용**한 것입니다. D는 **새로운 학습 작업을 수행**한 것입니다. 이를 혼동하면 모델 파일을 바꾸거나 대화를 이어 쓴 것만으로 모델이 새로 학습되었다고 생각할 수 있습니다.

---

# 19. 학생 활동 D — 목적에 맞는 Variant 방향 정하기

원본 강의에 나온 사용 목적을 적용합니다. 이번 활동은 **Variant 유형을 먼저 검토할 방향**만 결정하며, 실제 모델의 최종 적합성 평가를 대신하지 않습니다.

| 사용 목적 | 먼저 검토할 유형 | 이유를 설명할 때의 초점 |
|---|---|---|
| 일반 사용자 Chat Assistant | Instruction-tuned 계열 | 사용자 요청을 수행하는 행동 |
| 문서 내용을 일정 형식으로 요약하는 API | Instruction-tuned 계열 | 요청된 작업·형식 준수 |
| Python 함수 작성 요청 | Instruction-tuned 계열 | Code Capability와 Instruction Following |
| 자체 Post-training 실험의 출발 모델 | Base/Pre-trained 계열 검토 가능 | 추가 학습 목적에 맞는 기반 Model |
| Model 내부 Representation 연구 | Model Card의 목적 확인 후 판단 | 연구 목적과 접근 가능한 자원 |

**단정 금지:** 이 표의 `먼저 검토`는 `무조건 선택`이 아닙니다. 실제 기능, License, 지원 언어와 성능 등은 별도 확인이 필요합니다. 각 항목의 상세 평가 방법은 Day3 후속 교시의 담당 범위입니다.

학생에게는 각 경우 **왜 그런 유형을 우선 검토하는가**를 두 문장으로 설명하게 합니다.

---

# 20. 잘못된 설명을 판별하고 수정하기

아래 문장을 읽고 정확하지 않은 부분을 찾아 수정합니다. 정답 문장은 학생의 표현으로 작성할 수 있지만 아래 의미를 포함해야 합니다.

**문장 1.** `Instruction Model은 더 이상 다음 Token을 예측하지 않는다.`

→ **수정 기준:** Autoregressive Language Model이라면 Instruction-tuned도 Token Generation을 기반으로 응답할 수 있습니다.

**문장 2.** `Base Model은 사용자의 질문에 절대로 대답하지 못한다.`

→ **수정 기준:** Base Model도 질문·답변 패턴과 유사한 출력을 만들 수 있지만, Instruction Following에 특화된 추가 조정을 거쳤다고 볼 수는 없습니다.

**문장 3.** `Prompt를 더 구체적으로 쓰면 Model이 Instruction Tuning된다.`

→ **수정 기준:** Prompt 변경은 현재 입력의 변경이고 Instruction Tuning은 학습을 통한 Model 조정입니다.

**문장 4.** `Chat Template을 쓰지 않아도 모든 Chat Model에서 비교 결과가 똑같다.`

→ **수정 기준:** Model마다 기대하는 입력 형식이 달라질 수 있으므로 공식 사용 형식을 확인해야 합니다.

**문장 5.** `Instruction Model이 표를 만들었으니 표의 내용도 모두 정확하다.`

→ **수정 기준:** 형식 준수와 사실성은 별개의 판단입니다.

**문장 6.** `추가 학습 없이 이전 대화 Context를 전달한 것은 Model Parameter를 업데이트한 것이다.`

→ **수정 기준:** Context 전달만으로 Parameter가 학습되는 것은 아닙니다.

---

# 21. 자주 묻는 질문 — 답이 필요한 범위까지만

### Q1. Base Model이 Instruction을 어느 정도 수행했다면, Base가 아닌가요?

그렇지 않습니다. 어떤 한 요청의 결과만으로 학습 이력을 판정할 수 없습니다. Model Card의 Variant 설명과 학습 목적을 확인합니다. 원본이 강조하듯 **Pre-training Data에도 질문·답변이나 Instruction 형태의 패턴이 포함될 수 있습니다.**

### Q2. Instruction-tuned Model은 더 정확한 모델인가요?

반드시 그렇지 않습니다. **요청한 행동을 따르는 것**과 **생성한 내용이 정확한 것**은 별개입니다. 정답을 정해 놓고 평가한 자료가 없다면 `사실성까지 개선되었다`고 단정하지 않습니다.

### Q3. `model.eval()`을 호출하면 Base가 Instruction-tuned가 되나요?

아닙니다. Day2 3교시에서 배운 `eval()`은 실행 시 일부 Layer의 동작 모드를 바꾸는 기능이며 새로운 Instruction 학습을 수행하지 않습니다. **실행 모드와 모델의 학습 상태를 구분**합니다.

### Q4. Input이 같은데 결과가 다르면 반드시 Instruction Tuning 때문인가요?

단정할 수 없습니다. 같은 Family라도 Model Variant, 입력 형식, Sampling, Generation 길이 상한 등이 다를 수 있습니다. **관찰 조건과 차이를 먼저 기록**합니다.

### Q5. 모든 Instruction Model의 Chat Template이 같나요?

아닙니다. Model Family별 Post-training 형식과 Special Token에 차이가 있을 수 있습니다. 정확한 방법은 해당 모델의 공식 사용 예제를 확인합니다.

### Q6. Instruction Tuning은 새로운 문서를 모델에 넣는 유일한 방법인가요?

아닙니다. 원본은 Instruction Tuning을 단순히 자료를 외우게 만드는 기술로 설명하지 말라고 강조합니다. 새로운 문서나 외부 정보를 활용하는 기술의 상세한 설계는 다른 교육 단원에서 다룹니다.

---

# 22. 강사 시연 운영안과 실습 준비 주의사항

이 교시는 **실제 결과를 비교하는 관찰 수업**입니다. 강사의 시연 전제조건이 빠지면 학생이 결과 차이를 과도하게 일반화할 수 있습니다.

1. **Model Card 확보:** 비교할 Base와 Instruction-tuned 후보가 실제로 해당 유형인지 공식 문서에서 확인합니다.
2. **실행 가능성 확인:** 두 Variant가 교육장 환경에서 실행 가능한지 사전에 확인합니다. 같은 Family여도 접근 제약이나 Runtime 지원 조건이 다를 수 있습니다.
3. **조건 기록:** 정확한 Model ID, 입력 형식, Prompt, Sampling, Generation 길이 상한을 기록합니다.
4. **실제 출력 보존:** 한쪽 모델의 실패·형식 이탈도 삭제하지 않고 원인 분석 대상으로 남깁니다.
5. **미확인 결과 명시:** 모델을 실행하지 못한 경우에는 예상 유형만 설명하고 실측 결과가 있다고 말하지 않습니다.
6. **범위 준수:** 새로운 Training이나 Provider 추상화 코드를 만드는 데 수업 시간을 쓰지 않습니다.

**시연 순서:** 두 Variant의 근거 확인 → 실험 조건 공개 → 동일 과제 입력 → 실제 출력 나란히 제시 → 세 가지 관찰 항목 판정 → 학생의 제한적 결론 발표.

Model의 실제 Text 출력은 세대·버전·실행 환경에 따라 달라질 수 있습니다. 따라서 이 문서에는 실측하지 않은 생성 문장을 정답처럼 제공하지 않습니다.

---

# 23. 학습 확인 — 학생 스스로 설명하기

아래 질문에 **각각 한두 문장으로** 답할 수 있으면 이번 교시의 기본 목표를 달성한 것입니다.

1. Base Model과 Instruction-tuned Model은 **무엇을 다르게 배우도록 조정**되었나요?
2. Instruction-tuned Model도 Autoregressive Language Model의 방식으로 응답할 수 있나요?
3. 같은 Prompt에서 표가 나온 것만으로 사실성이 더 좋다고 판단할 수 있나요?
4. Chat Template이 다른 두 Model의 응답을 어떻게 비교해야 하나요?
5. Prompt 문장을 바꾸는 것과 Instruction Tuning은 무엇이 다른가요?
6. Base/Instruction 모델의 정확한 유형을 무엇을 근거로 판정해야 하나요?
7. 이번 교시의 관찰 결과와 Day3 5교시의 모델 최종 선정·평가 작업은 왜 다른가요?

**강사용 확인 포인트:** 학생이 `Instruction Following ≠ Factual Accuracy`, `입력 변경 ≠ Training`, `모델 이름 ≠ 공식 유형 검증`을 자신의 말로 설명하는지 확인합니다.

---

# 24. 이번 교시 핵심 정리

```text
[기반 학습]
Pre-training
     ↓
Base / Pre-trained Model
     │
     └─ Language Modeling을 수행하는 기반 능력

[추가 행동 조정]
Base Model
     ↓
Instruction에 대응하도록 추가 Training / Post-training
     ↓
Instruction-tuned Model
     └─ 지시를 따르는 Response를 더 잘 생성하도록 조정
```

두 Variant를 구분할 때는 다음 세 가지를 기억합니다.

- **생성 원리:** Autoregressive Language Model이라면 둘 다 Token을 생성할 수 있습니다.
- **학습 목적:** Instruction-tuned는 사용자의 Instruction에 대한 **응답 행동**을 개선하도록 조정된 Variant입니다.
- **관찰 방법:** 같은 과제를 비교하더라도 입력 형식과 실행 조건을 기록하며, **작업 수행·형식 준수·사실 정확성**을 각각 판단합니다.

> **가장 중요한 문장:** Instruction-tuned Model은 언어 생성 원리가 완전히 바뀐 모델이 아니라, 언어 모델의 기반 능력 위에서 **사용자의 지시에 맞는 응답을 더 잘 만들도록 추가 조정한 모델**입니다.

---

# 25. 다음 교시 연결 — Model Size와 Quantization은 별도 질문이다

이번 교시에서는 `같은 Family의 모델이 왜 다른 행동을 보일 수 있는가?`를 살폈습니다. 다음 Day3 3교시에서는 모델 이름에 나타나는 **1B·4B·12B·27B 같은 Parameter 규모**가 저장·실행 조건과 어떤 관계가 있는지를 다룹니다.

여기서는 개념만 분리해 둡니다.

```text
오늘: Base / Instruction-tuned
      → 어떤 응답 행동을 위해 조정되었는가?

다음: Model Size / Quantization
      → Model Parameter를 어떤 규모·표현으로 다루는가?
```

**이번 교시에서는 Parameter Memory 계산, bit별 저장량, GGUF 및 Quantization 과정, GPU·RAM·VRAM 하드웨어 판단을 설명하거나 실습하지 않습니다.** 후속 교시에서 각각 배웁니다.

---

# 참고자료 — 교육과정 원본에 기재된 항목

- Google AI for Developers — Gemma 공식 문서 및 Model Card
- Hugging Face Transformers 공식 문서
- Hugging Face Chat Templates 공식 문서
- 각 Model Family의 공식 Model Card

이 항목은 **원본 강의에서 안내한 참고자료 목록**입니다. 이번 개정에서 외부 자료의 최신 내용을 추가 확인하거나 실측했다고 의미하지 않습니다. 실제 수업에서는 해당 Model ID, Model Card의 학습 유형, 권장 입력 형식을 별도 확인해야 합니다.

# 관련 Wiki Link

`[[Base Model]]` · `[[Pre-trained Model]]` · `[[Instruction Tuning]]` · `[[Instruction-tuned Model]]` · `[[Language Model]]` · `[[Post-training]]` · `[[Prompt Engineering]]` · `[[Context]]` · `[[Chat Template]]` · `[[Gemma]]` · `[[Model Family]]` · `[[Model Card]]` · `[[Fine-tuning]]` · `[[RAG]]`

# 저장 위치 제안

```text
Academy/
└── 00. 교육과정(curriculum)/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day3_02교시_Base_Pretrained_Model과_Instruction_tuned_Model의_차이_강의용.md
```

> **검수 상태:** 본 문서는 원본 Day3 2교시의 내용을 기준으로 새로 구성한 수정본입니다. Model ID를 고정한 실제 Base/Instruction 비교, 교육장 실행 결과 및 최신 Model Card의 사실 검증은 아직 수행하지 않았습니다.
