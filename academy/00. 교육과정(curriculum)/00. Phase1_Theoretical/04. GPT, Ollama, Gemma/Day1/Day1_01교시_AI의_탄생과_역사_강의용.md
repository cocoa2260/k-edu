# Day 1 - 1교시. AI의 탄생과 역사

## 개요

이번 교시는 특정 제품인 GPT를 배우기 전에, **AI라는 분야가 왜 등장했고 어떤 문제를 해결하려고 발전해 왔는지** 큰 흐름을 이해하는 시간입니다.

AI의 역사를 연도 암기식으로 배우지 않습니다. 각 시대의 핵심 질문이 어떻게 바뀌었는지를 중심으로 살펴봅니다.

```text
사람의 지능을 기계로 만들 수 있을까?
        ↓
사람의 지식과 규칙을 기계에 넣으면 될까?
        ↓
기계가 데이터에서 규칙을 학습하면 어떨까?
        ↓
신경망이 복잡한 표현까지 학습하면 어떨까?
        ↓
학습한 모델이 새로운 콘텐츠까지 생성할 수 있을까?
```

> **이번 교시의 핵심 질문**
>
> 오늘날의 생성형 AI는 갑자기 등장한 기술일까요?

---

# 1. 학습 목표

이번 교시가 끝나면 학생은 다음 내용을 자신의 말로 설명할 수 있어야 합니다.

1. Artificial Intelligence라는 연구 분야가 어떤 문제의식에서 출발했는지 설명할 수 있다.
2. 초기 Symbolic AI와 현대 Machine Learning 접근의 큰 차이를 설명할 수 있다.
3. AI 발전 과정에서 AI Winter가 발생한 이유를 개략적으로 설명할 수 있다.
4. Machine Learning과 Deep Learning의 발전이 현대 AI에 어떤 변화를 만들었는지 설명할 수 있다.
5. Transformer와 생성형 AI의 등장이 전체 AI 역사에서 어떤 위치에 있는지 설명할 수 있다.
6. ChatGPT와 같은 서비스가 AI 전체와 동일한 개념이 아님을 설명할 수 있다.

---

# 2. 왜 AI의 역사부터 배우는가?

현재 AI를 처음 접하는 사람은 흔히 다음과 같이 생각하기 쉽습니다.

```text
AI = ChatGPT
```

하지만 ChatGPT와 생성형 AI는 긴 AI 발전 과정의 최근 결과 중 하나입니다.

AI의 역사를 먼저 보면 다음 질문에 답하기 쉬워집니다.

- 왜 과거에는 사람이 규칙을 직접 입력했을까?
- 왜 Machine Learning이 필요해졌을까?
- 왜 데이터와 GPU가 중요해졌을까?
- 왜 최근에는 Model이라는 말을 자주 사용할까?
- 왜 생성형 AI는 기존 AI와 다른 경험을 제공할까?

따라서 이번 교시의 목적은 역사 자체를 외우는 것이 아니라 **AI를 만드는 방법이 어떻게 변해왔는지 이해하는 것**입니다.

---

# 3. AI 이전에도 컴퓨터는 똑똑했을까?

컴퓨터는 매우 빠르게 계산할 수 있습니다.

예를 들어 다음 코드는 명확한 규칙을 실행합니다.

```python
score = 75

if score >= 60:
    print("PASS")
else:
    print("FAIL")
```

여기서 컴퓨터가 스스로 합격 기준을 알아낸 것은 아닙니다.

```text
개발자
↓
규칙 작성
↓
프로그램
↓
입력
↓
규칙 실행
↓
출력
```

즉, 전통적인 프로그램에서는 **어떻게 판단할지를 사람이 코드로 작성**합니다.

그렇다면 이런 질문이 생깁니다.

> 사람처럼 판단하거나 문제를 해결하는 능력도 프로그램으로 만들 수 있을까?

이 질문이 AI 연구의 중요한 출발점 중 하나입니다.

---

# 4. 1950년 - "기계가 생각할 수 있는가?"

1950년 Alan Turing은 논문 *Computing Machinery and Intelligence*에서 기계 지능에 관한 중요한 문제를 제기했습니다.

유명한 출발 질문은 다음과 같습니다.

> **Can machines think?**

Turing은 단순히 철학적 정의를 반복하기보다, 기계의 행동을 대화를 통해 평가하는 접근을 논의했습니다. 이후 흔히 **Turing Test**라고 불리는 아이디어와 연결됩니다.

### 강의 포인트

여기서 학생들에게 중요한 것은 "Turing Test를 통과하면 진짜 인간처럼 생각한다"고 단정하는 것이 아닙니다.

핵심은 다음입니다.

```text
컴퓨터를
단순 계산 기계로만 볼 것인가?

아니면
지능적인 행동을 수행할 수 있는 기계로 볼 수 있는가?
```

AI 연구가 다루게 될 질문이 본격적으로 등장하기 시작합니다.

---

# 5. 1956년 - Artificial Intelligence라는 연구 분야

1956년 Dartmouth Summer Research Project on Artificial Intelligence는 AI 역사에서 중요한 사건으로 다뤄집니다.

John McCarthy를 비롯한 연구자들이 참여했고, **Artificial Intelligence**라는 표현이 연구 분야의 이름으로 자리 잡는 데 중요한 계기가 되었습니다.

당시 연구자들은 인간의 학습과 지능의 여러 측면을 기계로 기술하고 구현할 수 있다는 매우 큰 기대를 가지고 있었습니다.

```text
인간의 추론
문제 해결
언어
학습

↓

기계로 구현할 수 있을까?
```

이때부터 AI는 하나의 장기적인 연구 분야로 발전하기 시작합니다.

---

# 6. 초기 AI - 사람이 지식을 규칙으로 넣는다

초기 AI의 중요한 접근 중 하나는 **Symbolic AI**입니다.

사람이 알고 있는 지식과 논리를 Symbol과 Rule로 표현하고, 컴퓨터가 이를 이용해 추론하도록 만드는 방식입니다.

예를 들어 아주 단순화하면 다음과 같습니다.

```text
IF 체온 > 38
AND 기침 = TRUE
THEN 감염 가능성 확인
```

구조적으로 보면 다음과 같습니다.

```text
사람의 지식
↓
Rule
↓
Knowledge Base
↓
Inference
↓
결과
```

### 장점

규칙이 명확한 영역에서는 판단 과정을 사람이 이해하기 쉽습니다.

### 어려움

현실 세계의 모든 상황을 사람이 규칙으로 작성하기는 어렵습니다.

예를 들어 고양이 사진을 판별한다고 생각해봅시다.

```text
귀가 삼각형이면 고양이?
수염이 있으면 고양이?
털이 있으면 고양이?
눈이 두 개면 고양이?
```

개별 규칙만으로 현실의 모든 고양이를 표현하기는 어렵습니다.

여기서 AI 발전의 중요한 문제가 나타납니다.

> **사람이 모든 규칙을 작성하지 않고 컴퓨터가 데이터에서 패턴을 찾게 할 수 없을까?**

---

# 7. Expert System의 시대

1970~1980년대에는 특정 전문 분야의 지식을 규칙으로 구성한 **Expert System**이 큰 관심을 받았습니다.

개념적으로는 다음과 같습니다.

```text
전문가의 지식
↓
Knowledge Base
+
Inference Engine
↓
질문에 대한 판단
```

의료, 화학, 장비 설정 등 제한된 전문 영역에서 연구와 실제 활용이 이루어졌습니다.

하지만 문제가 있었습니다.

### Knowledge Acquisition Bottleneck

전문가가 알고 있는 수많은 지식을 규칙으로 추출하고 지속적으로 관리하는 일이 어렵습니다.

```text
현실 변화
↓
새로운 규칙 필요
↓
전문가 확인
↓
개발자 수정
↓
규칙 증가
↓
관리 복잡도 증가
```

이 문제는 현대 개발에서도 생각해볼 가치가 있습니다.

> 모든 판단 규칙을 사람이 코드로 관리할 수 있는가?

---

# 8. AI Winter - AI는 계속 성공하기만 했을까?

아닙니다.

AI 역사에는 기대가 크게 높아졌다가 연구 투자와 관심이 감소한 시기가 있었으며 이를 흔히 **AI Winter**라고 부릅니다.

원인은 한 가지가 아닙니다.

당시의 높은 기대에 비해 실제 시스템의 능력이 제한적이었고, 컴퓨팅 자원과 데이터, 알고리즘 등의 제약도 컸습니다.

```text
높은 기대
↓
기술적 한계
↓
기대만큼 성과가 나오지 않음
↓
투자와 관심 감소
```

### 강의 포인트

AI 역사는 다음과 같은 직선이 아닙니다.

```text
AI 탄생
↓
계속 발전
↓
ChatGPT
```

실제로는

```text
기대
↗
성과
↘
침체
↗
새로운 기술
↗
다시 기대
```

가 반복되어 왔습니다.

이 관점은 현재 AI 기술을 볼 때도 중요합니다.

---

# 9. Machine Learning - 규칙을 직접 작성하지 않는 방향

AI의 중요한 발전 방향 중 하나는 Machine Learning입니다.

전통적인 프로그램을 단순화하면:

```text
Data + Rules
↓
Program
↓
Answer
```

Machine Learning은 관점을 바꿉니다.

```text
Data + 정답/목표 또는 학습 신호
↓
Learning Algorithm
↓
Model
```

그리고 만들어진 Model을 사용합니다.

```text
새로운 Data
↓
Model
↓
Prediction
```

예를 들어 스팸 메일을 판별한다고 생각해봅시다.

### Rule 방식

사람이 직접 작성합니다.

```text
"무료"가 있으면 +1
"당첨"이 있으면 +2
URL이 많으면 +1
...
```

### Machine Learning 방식

```text
많은 이메일 데이터
+
Spam / Normal Label
↓
학습
↓
Model
↓
새 이메일 분류
```

중요한 변화는 다음입니다.

> **판단 규칙의 일부를 사람이 일일이 작성하는 대신 데이터와 학습 과정으로 Model을 만든다.**

Machine Learning의 세부 유형과 학습 알고리즘은 이후 AI 과정에서 자세히 학습합니다.

관련 Wiki Link: [[머신러닝(Machine Learning)]]

---

# 10. Deep Learning - 표현도 학습한다

Machine Learning에서도 오랫동안 사람이 어떤 Feature를 사용할지 설계하는 일이 중요했습니다.

예를 들어 이미지 판별이라면:

```text
Edge
Shape
Color
Texture
```

같은 특징을 어떻게 표현할지 고민해야 했습니다.

Deep Learning은 여러 층의 Neural Network를 이용하여 데이터에서 유용한 표현을 학습할 수 있게 하면서 이미지, 음성, 자연어 등 다양한 분야의 발전에 크게 기여했습니다.

단순화하면:

```text
Data
↓
Neural Network
↓
여러 단계의 Representation 학습
↓
Output
```

여기서 중요한 것은 Neural Network 내부 수학을 배우는 것이 아닙니다.

이번 교시에서는 다음만 기억합니다.

> **Deep Learning은 현대 AI 발전의 핵심 기반 기술 중 하나이다.**

관련 Wiki Link: [[딥러닝(Deep Learning)]] [[신경망(Neural Network)]]

---

# 11. 2012년 이후 - Deep Learning의 큰 도약

2012년 ImageNet 이미지 분류 대회에서 AlexNet이 뛰어난 성능을 보이며 Deep Learning, 특히 GPU를 활용한 대규모 Neural Network 학습의 가능성을 강하게 보여주었습니다.

이후 이미지 인식뿐 아니라 음성 인식, 자연어 처리 등 다양한 영역에서 Deep Learning이 빠르게 확산됩니다.

여기에는 여러 조건이 함께 작용했습니다.

```text
더 많은 Data
+
더 강력한 Computing 자원
+
GPU 활용
+
Neural Network 연구 발전
+
학습 기법과 Software 생태계 발전
```

즉, AI 발전은 알고리즘 하나만으로 설명할 수 없습니다.

### 실무 팁

현대 AI를 이해할 때 항상 다음 네 요소를 같이 보세요.

```text
Algorithm
Data
Compute
Software / Infrastructure
```

모델 성능과 AI 산업의 변화는 이 요소들이 함께 발전한 결과인 경우가 많습니다.

---

# 12. 자연어 처리의 발전

컴퓨터가 사람의 언어를 다루는 분야를 Natural Language Processing, 즉 NLP라고 합니다.

과거에도 다양한 언어 처리 기술이 존재했습니다.

```text
Rule 기반 언어 처리
↓
통계적 언어 모델
↓
Machine Learning
↓
Neural Network 기반 NLP
↓
RNN / LSTM 등
↓
Transformer
↓
대규모 언어 모델
```

여기서 RNN과 LSTM의 구조를 배우지는 않습니다.

중요한 것은 다음 질문입니다.

> **긴 문맥과 단어 사이의 관계를 더 효과적으로 처리할 방법은 없을까?**

이 흐름에서 Transformer가 중요한 전환점으로 등장합니다.

---

# 13. 2017년 - Transformer

2017년 논문 *Attention Is All You Need*에서 Transformer Architecture가 제안되었습니다.

Transformer는 이후 자연어 처리 발전에 매우 큰 영향을 주었고, 현대의 많은 LLM의 기반 Architecture가 되었습니다.

이번 과정에서는 내부 구조를 학습하지 않습니다.

```text
Transformer
│
├── Attention
├── 여러 Layer
└── 다양한 내부 구조
```

이것은 Phase 2의 [[트랜스포머(Transformer)]] 과정에서 자세히 배웁니다.

이번에는 다음 관계만 기억합니다.

```text
Deep Learning
↓
Transformer의 등장과 발전
↓
대규모 사전학습 언어 모델 발전
↓
현대 LLM / 생성형 AI 발전
```

> **주의사항**
>
> 모든 AI가 Transformer인 것은 아닙니다. Transformer는 현대 AI, 특히 LLM과 여러 Multimodal Model에서 매우 중요한 Architecture이지만 AI 전체와 동일한 개념은 아닙니다.

---

# 14. 2018년 이후 - GPT와 대규모 사전학습 모델

GPT는 **Generative Pre-trained Transformer**의 약자입니다.

이름 안에 중요한 개념이 들어 있습니다.

```text
Generative
→ 생성

Pre-trained
→ 대규모 데이터로 사전 학습

Transformer
→ 기반 Architecture
```

2018년 첫 GPT 연구 이후 GPT-2, GPT-3 등 더 큰 언어 모델 연구가 이어졌습니다.

여기서 중요한 변화는 특정 작업 하나만을 위한 모델보다, 대규모 데이터로 먼저 학습한 모델을 다양한 언어 작업에 활용하는 방향이 강해졌다는 점입니다.

```text
대규모 사전학습
↓
범용적인 언어 능력
↓
다양한 Downstream Task에 활용
```

이 흐름은 이후 Foundation Model이라는 개념을 이해하는 데 연결됩니다.

관련 Wiki Link: [[GPT]] [[대규모 언어 모델(LLM)]] [[Foundation Model]]

---

# 15. 2022년 - ChatGPT와 생성형 AI의 대중화

2022년 ChatGPT 공개 이후 일반 사용자도 자연어 대화를 통해 강력한 언어 모델을 쉽게 경험할 수 있게 되면서 생성형 AI가 빠르게 대중화되었습니다.

중요한 것은 ChatGPT가 AI의 시작이 아니라는 점입니다.

```text
수십 년의 AI 연구
↓
Machine Learning
↓
Deep Learning
↓
Transformer
↓
Large Language Model
↓
대화형 AI Application
↓
ChatGPT의 대중화
```

따라서 다음 표현은 정확하지 않습니다.

```text
AI가 2022년에 등장했다.
```

더 적절한 설명은:

> **AI는 오랜 연구 역사를 가지고 있으며, 2022년 이후 생성형 AI 기반 서비스가 일반 사용자에게 폭발적으로 확산되었다.**

입니다.

---

# 16. 생성형 AI 시대

기존 AI의 대표적인 활용은 다음과 같았습니다.

```text
분류
예측
추천
탐지
인식
```

생성형 AI는 새로운 결과물을 생성하는 능력을 전면에 가져왔습니다.

```text
Text
Image
Code
Audio
Speech
Video
```

예를 들어:

```text
질문 → 답변 생성
문서 → 요약 생성
설명 → 이미지 생성
요구사항 → Code 생성
음성 → 다른 형태의 콘텐츠 생성
```

하지만 여기서도 주의해야 합니다.

> **Generative AI가 기존 AI를 모두 대체한 것은 아닙니다.**

추천, 이상 탐지, 수요 예측, 최적화 등에서는 전통적인 Machine Learning과 다양한 AI 기술이 여전히 사용됩니다.

관련 Wiki Link: [[생성형 AI(Generative AI)]]

---

# 17. 현재 AI는 언어만 다루지 않는다

현대 AI는 다양한 Modality를 처리합니다.

```text
Text
Image
Audio
Video
Sensor Data
```

그리고 여러 형태의 정보를 함께 처리하는 Multimodal AI가 빠르게 발전했습니다.

```text
Text + Image
↓
Multimodal Model
↓
설명 / 분석 / 생성
```

예를 들어:

- 이미지에 대해 질문하기
- 문서 화면 분석하기
- 음성과 텍스트를 함께 처리하기
- 이미지와 텍스트를 함께 입력하여 콘텐츠 생성하기

등이 가능합니다.

Multimodal의 내부 원리와 OCR과의 차이는 이후 [[멀티모달(Multimodal)]] 과정에서 자세히 다룹니다.

---

# 18. AI는 이제 '답변'에서 '행동'으로 확장되고 있다

현대 AI Application에서는 모델이 텍스트를 생성하는 것에 그치지 않고 외부 Tool과 연결되기도 합니다.

```text
사용자 요청
↓
AI Application
↓
Model
↓
필요한 Tool 선택
↓
Search / Database / Calendar / API
↓
결과
```

이러한 흐름은 Agent, Tool Calling, AI Automation 같은 기술로 연결됩니다.

하지만 이번 시간에는 내부 구조를 배우지 않습니다.

중요한 것은 AI가 발전하면서 Application의 범위가 다음과 같이 확장되고 있다는 점입니다.

```text
Prediction
↓
Generation
↓
Multimodal Interaction
↓
Tool Use / Automation
```

관련 Wiki Link: [[AI 에이전트(Agent)]] [[Tool Calling]] [[AI Automation]]

---

# 19. AI 발전을 한 장으로 정리하기

정확한 기술 계보는 여러 연구 흐름이 병렬적으로 발전했기 때문에 하나의 직선으로만 표현할 수 없습니다.

다만 입문 단계에서는 큰 변화를 다음처럼 정리할 수 있습니다.

```text
1950s
기계 지능에 대한 질문
        ↓
Symbolic AI / Rule-based approaches
        ↓
Expert Systems
        ↓
AI Winter를 포함한 기대와 침체의 반복
        ↓
Machine Learning의 확대
        ↓
Deep Learning의 발전
        ↓
대규모 Data + GPU + Software 생태계
        ↓
2017 Transformer
        ↓
대규모 Pre-trained Model
        ↓
LLM / Foundation Model
        ↓
Generative AI 대중화
        ↓
Multimodal / Tool Use / Agent / AI Application
```

이 그림에서 가장 중요한 것은 연도가 아닙니다.

**AI를 구현하는 접근이 변해왔다는 것**입니다.

---

# 20. AI 개발 방식의 변화

## 1단계 - 사람이 규칙을 작성

```text
Knowledge
↓
Human
↓
Rule
↓
Program
```

## 2단계 - 데이터에서 패턴을 학습

```text
Data
↓
Learning
↓
Model
↓
Prediction
```

## 3단계 - 대규모 사전학습 모델 활용

```text
Large-scale Pre-training
↓
Foundation / Generative Model
↓
Instruction / Context
↓
다양한 Task
```

그리고 AI Application 개발자는 반드시 Model을 직접 학습할 필요가 없습니다.

```text
AI Application
↓
API / Runtime / Library
↓
Pre-trained Model
```

이 지점이 앞으로 GPT, Ollama, Gemma를 배우는 이유와 연결됩니다.

---

# 21. 앞으로 우리가 배우게 될 것

이번 3일 과정에서 특정 제품만 배우는 것이 목표가 아닙니다.

GPT, Ollama, Gemma는 현대 AI를 이해하고 직접 사용해보기 위한 도구입니다.

```text
AI
↓
Generative AI
↓
Language Model / LLM
↓
AI Model 생태계
↓
Cloud AI / Local AI
↓
AI 개발 Library / Runtime
↓
AI Application
```

앞으로 다음 질문을 하나씩 해결합니다.

```text
AI Model은 무엇인가?

Model은 어떻게 학습되고 어떻게 사용되는가?

Cloud AI와 Local AI는 무엇이 다른가?

PyTorch, Transformers 같은 Library는 왜 필요한가?

Ollama는 Model인가?

Gemma는 무엇인가?

AI를 FastAPI Application에 어떻게 연결하는가?
```

---

# 22. 강사 시연 / 참여 활동

이번 교시는 학생 실습 시간이 아니라 **개념 수업 + 짧은 참여 활동**으로 운영합니다.

## 활동 1. 이것도 AI일까?

다음 기술을 보여주고 학생에게 AI인지 생각하게 합니다.

```text
계산기
스팸 메일 필터
YouTube 추천
얼굴 인식
OCR
ChatGPT
자동 번역
자동차 차선 인식
상품 수요 예측
이미지 생성
```

### 강사 포인트

AI를 Chatbot으로만 생각하지 않도록 합니다.

---

## 활동 2. Rule로 만들 수 있을까?

질문합니다.

> 고양이 사진을 판별하는 프로그램을 `if` 문만으로 작성한다면 어떤 규칙이 필요할까요?

학생들의 규칙을 받아봅니다.

```text
귀 모양
털
수염
눈
꼬리
크기
```

그리고 반례를 제시합니다.

```text
귀가 안 보이는 고양이
털이 없는 고양이
사진 일부만 나온 고양이
장난감 고양이
```

이를 통해 현실 데이터를 Rule로 완전히 표현하기 어려운 문제를 직관적으로 이해시킵니다.

---

## 활동 3. AI 역사에서 가장 중요한 변화는 무엇이었을까?

학생에게 다음 중 하나를 선택하게 합니다.

```text
더 좋은 Algorithm
더 많은 Data
더 빠른 Hardware
더 좋은 Software
```

정답을 하나로 정하지 않습니다.

현대 AI 발전은 여러 요소의 결합이라는 점을 설명합니다.

---

# 23. 자주 발생하는 오해

## 오해 1. AI는 ChatGPT다

아닙니다.

```text
AI
>
Generative AI
>
LLM 기반 기술/서비스
```

이라는 더 큰 관계가 있습니다.

---

## 오해 2. Machine Learning 이전에는 AI가 없었다

아닙니다.

Symbolic AI, Search, Planning, Expert System 등 다양한 AI 연구가 Machine Learning 중심 시대 이전부터 존재했습니다.

---

## 오해 3. Deep Learning = AI

아닙니다.

Deep Learning은 AI를 구현하는 중요한 접근 중 하나입니다.

---

## 오해 4. Transformer = ChatGPT

아닙니다.

Transformer는 Architecture이고, 이를 기반으로 다양한 Model이 만들어질 수 있습니다.

---

## 오해 5. 생성형 AI가 모든 기존 AI를 대체한다

아닙니다.

문제에 따라 전통적인 Algorithm, Machine Learning, Deep Learning, 생성형 AI를 선택하거나 함께 사용할 수 있습니다.

---

# 24. 실무 팁

AI 프로젝트를 시작할 때 가장 먼저 "어떤 LLM을 사용할까?"부터 결정하지 마세요.

먼저 문제를 정의해야 합니다.

```text
우리가 해결할 문제는 무엇인가?
↓
AI가 정말 필요한가?
↓
분류 / 예측 / 검색 / 생성 중 무엇인가?
↓
기존 Algorithm으로 충분한가?
↓
Machine Learning이 필요한가?
↓
Generative AI가 필요한가?
↓
필요한 Model / Library / Architecture 선택
```

AI는 목적이 아니라 문제를 해결하기 위한 기술입니다.

---

# 25. 핵심 요약

이번 교시에서 반드시 기억해야 할 내용입니다.

1. AI는 ChatGPT와 함께 시작된 기술이 아니라 수십 년의 연구 역사를 가진 분야입니다.
2. 초기 AI에서는 사람이 지식과 Rule을 직접 표현하는 Symbolic 접근이 중요했습니다.
3. Machine Learning은 데이터에서 패턴을 학습하여 Model을 만드는 접근을 크게 확산시켰습니다.
4. Deep Learning은 현대 이미지·음성·언어 AI 발전에 중요한 기반이 되었습니다.
5. Data, Compute, Algorithm, Software 생태계의 발전이 현대 AI 발전을 함께 이끌었습니다.
6. Transformer는 현대 LLM 발전의 핵심 Architecture 중 하나입니다.
7. 생성형 AI는 텍스트뿐 아니라 이미지, 음성, 코드 등 다양한 콘텐츠 생성으로 확장되었습니다.
8. 현대 AI Application은 생성뿐 아니라 Multimodal, Tool Use, Automation으로 범위를 넓히고 있습니다.
9. GPT, Ollama, Gemma는 앞으로 AI를 이해하기 위해 사용할 Model/도구 생태계의 일부이며 AI 전체가 아닙니다.

---

# 26. 이해도 확인

학생이 자신의 말로 답하도록 합니다.

1. 전통적인 프로그램과 Machine Learning의 가장 큰 차이는 무엇인가요?
2. Symbolic AI에서는 지식을 주로 어떤 방식으로 표현했나요?
3. AI Winter라는 표현은 무엇을 의미하나요?
4. Deep Learning의 발전에 Algorithm 외에 어떤 요소들이 영향을 주었나요?
5. Transformer가 AI 역사에서 중요한 이유는 무엇인가요?
6. ChatGPT가 AI 전체와 같은 개념이 아닌 이유를 설명해보세요.
7. 생성형 AI 이전에도 AI가 사용되었던 사례를 세 가지 들어보세요.
8. 현대 AI가 `Prediction → Generation → Tool Use`로 확장된다는 말은 어떤 의미인가요?

---

# 27. 다음 교시 연결

이번 시간에는 AI가 **어떻게 여기까지 왔는지** 살펴봤습니다.

하지만 아직 중요한 질문이 남아 있습니다.

```text
그래서 AI란 정확히 무엇인가?

Machine Learning은 AI와 어떤 관계인가?

Deep Learning은 Machine Learning과 무엇이 다른가?

생성형 AI는 이 지도에서 어디에 있는가?
```

다음 교시에서는 AI 기술의 전체 지도를 그리면서 이 관계를 정리합니다.

```text
Day 1 - 1교시
AI의 탄생과 역사
        ↓
Day 1 - 2교시
AI란 무엇인가 - AI 전체 지도
```

---

# 참고자료

강의 자료의 역사적 사실을 검수할 때 우선 확인할 원문/공식·학술 자료입니다.

- Alan M. Turing, *Computing Machinery and Intelligence*, Mind, 1950.
- Dartmouth Summer Research Project on Artificial Intelligence proposal, 1955/1956.
- Alex Krizhevsky, Ilya Sutskever, Geoffrey E. Hinton, *ImageNet Classification with Deep Convolutional Neural Networks*, 2012.
- Ashish Vaswani et al., *Attention Is All You Need*, 2017.
- Alec Radford et al., *Improving Language Understanding by Generative Pre-Training*, 2018.

---

# 관련 Wiki Link

```text
[[인공지능(Artificial Intelligence)]]
[[AI 역사]]
[[Symbolic AI]]
[[Expert System]]
[[머신러닝(Machine Learning)]]
[[딥러닝(Deep Learning)]]
[[신경망(Neural Network)]]
[[트랜스포머(Transformer)]]
[[대규모 언어 모델(LLM)]]
[[생성형 AI(Generative AI)]]
[[Foundation Model]]
[[멀티모달(Multimodal)]]
[[AI 에이전트(Agent)]]
[[AI Automation]]
```

---

# AIKOS 저장 위치 제안

```text
Academy/
└── 00. 교육과정(curriculum)/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day1/
                └── 01. AI의 탄생과 역사_강의용.md
```
