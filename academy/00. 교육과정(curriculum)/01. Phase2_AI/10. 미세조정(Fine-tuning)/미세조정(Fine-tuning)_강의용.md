# Phase 2 — 10. 미세조정(Fine-tuning)

> **과목 목적**  
> Fine-tuning을 “회사 문서를 모델에 넣는 방법” 정도로 이해하지 않고,  
> **무엇을 학습시킬 것인가**, **어떤 Parameter를 어떤 방식으로 업데이트할 것인가**,  
> **학습 결과가 실제로 좋아졌는지 어떻게 검증할 것인가**를 하나의 흐름으로 이해한다.

---

# 0. 전체 학습 지도

앞에서 우리는 다음을 배웠다.

```text
Transformer
↓
LLM
↓
Prompt Engineering
↓
Embedding
↓
Vector DB
↓
RAG
↓
Agent
```

이제 질문은 다음과 같다.

> Prompt를 바꾸거나 외부 문서를 검색하는 것만으로 부족하다면,  
> **모델 자체의 행동을 바꿀 수 있을까?**

그때 검토하는 대표적인 방법이 Fine-tuning이다.

이번 과목의 전체 흐름은 다음과 같다.

```text
Base Model
↓
Fine-tuning 필요성 판단
↓
학습 목표 정의
├─ Continued Pre-training
├─ SFT / Instruction Tuning
└─ Preference Tuning
↓
Parameter 전략 선택
├─ Full Fine-tuning
├─ 일부 Layer Freeze
└─ PEFT
   └─ LoRA
      └─ QLoRA
↓
Dataset 설계
↓
Train / Validation / Test
↓
Tokenization / Chat Template
↓
Training
↓
Validation
↓
Checkpoint / Adapter 저장
↓
새 프로세스에서 Reload
↓
잠근 Test 평가
↓
Base Model과 비교
↓
배포 또는 Rollback
```

이번 과목에서 가장 먼저 기억할 것은 다음이다.

```text
무엇을 학습할 것인가?
≠
어떤 Parameter를 학습할 것인가?
```

예를 들어 **SFT**와 **LoRA**는 서로 경쟁하는 개념이 아니다.

```text
SFT
→ 어떤 Dataset과 학습 목표를 사용할 것인가?

LoRA
→ Parameter를 어떤 방식으로 효율적으로 학습할 것인가?
```

따라서 다음 표현이 가능하다.

```text
Instruction Dataset
↓
SFT
↓
LoRA 방식으로 학습
↓
Fine-tuned Model
```

---

# 1. 학습 목표

이번 과목이 끝나면 다음 질문에 자신의 언어로 답할 수 있어야 한다.

1. Fine-tuning과 RAG의 차이는 무엇인가?
2. Fine-tuning에서 실제로 무엇이 바뀌는가?
3. Full Fine-tuning과 LoRA는 무엇이 다른가?
4. LoRA와 QLoRA는 무엇이 다른가?
5. Instruction Tuning과 LoRA는 왜 같은 분류 기준이 아닌가?
6. Fine-tuning을 하면 기존 지식을 모두 잃는가?
7. Dataset을 Train / Validation / Test로 왜 나누는가?
8. Data Leakage가 왜 위험한가?
9. Training Loss가 내려갔다고 성공이라고 할 수 없는 이유는 무엇인가?
10. Prompt / RAG / Fine-tuning 중 무엇을 선택할지 어떻게 판단하는가?

---

# Unit 1. 왜 Fine-tuning을 배우는가?

## 1-1. 가장 흔한 질문

기업에서 AI를 도입하면 자주 나오는 질문이 있다.

> “회사 문서를 모델에 학습시키면 되지 않나요?”

예를 들어 회사에 다음 문서가 있다고 하자.

```text
인사 규정
업무 매뉴얼
계약서
제품 설명서
프로젝트 문서
```

겉으로 보면 두 가지 방법이 떠오를 수 있다.

```text
방법 A

회사 문서
↓
Fine-tuning
↓
Model이 회사 내용을 알게 한다
```

```text
방법 B

회사 문서
↓
검색 가능하게 Index
↓
질문할 때 관련 문서 검색
↓
LLM에게 제공
```

방법 B는 우리가 앞에서 배운 RAG다.

둘은 겉으로는 비슷해 보이지만 핵심이 다르다.

---

## 1-2. RAG는 외부 정보를 현재 Context에 가져온다

RAG의 기본 구조는 다음과 같다.

```text
사용자 질문
↓
검색
↓
관련 문서
↓
Prompt / Context에 추가
↓
LLM
↓
답변
```

여기서 중요한 점은:

```text
Model Parameter
→ 변경하지 않음
```

이다.

즉 RAG는 모델 자체를 다시 학습시키지 않는다.

---

## 1-3. Fine-tuning은 학습을 다시 수행한다

Fine-tuning은 이미 학습된 모델에서 출발하여 추가 Dataset으로 Training을 수행한다.

```text
Pre-trained Model
↓
추가 Dataset
↓
Training
↓
Parameter 또는 Adapter Update
↓
Fine-tuned Model
```

따라서 Fine-tuning의 핵심 단어는:

> **학습**

이다.

---

## 1-4. 비유: 외우기와 오픈북

학생이 시험을 본다고 하자.

최신 법률 내용을 알아야 한다.

### 방법 A

```text
새 법률을 다시 공부하고
기억하도록 훈련
```

Fine-tuning에 비유할 수 있다.

### 방법 B

```text
시험장에서 최신 법전을 검색해서
필요한 부분을 읽음
```

RAG에 비유할 수 있다.

최신 규정이 자주 바뀐다면 오픈북 구조가 관리하기 쉽다.

반대로:

```text
항상 같은 형식으로 답하기
특정 Label로 분류하기
특정 작업 절차를 따르기
회사 상담 말투를 유지하기
```

같은 반복되는 행동은 Fine-tuning을 검토할 수 있다.

---

# Unit 2. Fine-tuning이란 무엇인가?

## 2-1. 정의

Fine-tuning은 다음과 같이 정의할 수 있다.

> **이미 학습된 Model을 추가 Dataset으로 다시 학습하여 특정 Task, Domain 또는 행동에 맞게 Model을 조정하는 과정**

핵심은 세 가지다.

```text
이미 학습된 Model
+
추가 Dataset
+
추가 Training
```

---

## 2-2. Pre-training과 Fine-tuning

아주 단순화하면 다음과 같다.

```text
대규모 일반 Dataset
↓
Pre-training
↓
Base Model
```

그 뒤:

```text
특정 목적 Dataset
↓
Fine-tuning
↓
Custom Model
```

예를 들어 Base Model이 이미 다음 능력을 가지고 있다고 하자.

```text
한국어
영어
문법
일반 지식
코드
요약
기본 추론
```

Fine-tuning의 목적은 보통 이 능력을 모두 지우는 것이 아니라:

```text
기존 능력
+
특정 행동 강화
```

이다.

---

## 2-3. Parameter는 무엇인가?

LLM에는 매우 많은 Parameter가 있다.

Parameter는 단순한 문서 저장칸이 아니다.

```text
Parameter
=
학습을 통해 조정되는 수많은 숫자
```

이 숫자들이 함께 작동하며 다음과 같은 패턴을 표현한다.

```text
언어 패턴
문법
관계
작업 능력
행동 경향
지식의 일부
```

따라서 다음 식으로 생각하면 안 된다.

```text
Parameter 12345
=
회사 규정 3페이지
```

Model Parameter는 일반 Database처럼 원문을 문서 ID로 저장하는 구조가 아니다.

---

# Unit 3. Fine-tuning에서 실제로 무엇이 바뀌는가?

## 3-1. Training의 기본 구조

Fine-tuning도 결국 Training이다.

```text
Input
↓
Forward
↓
Prediction
↓
Loss
↓
Backward
↓
Gradient
↓
Optimizer Step
↓
Parameter Update
```

PyTorch 수준의 최소 흐름은 다음과 같다.

```python
optimizer.zero_grad()

outputs = model(input_ids=input_ids, labels=labels)
loss = outputs.loss

loss.backward()
optimizer.step()
```

핵심은:

```text
loss.backward()
→ Gradient 계산

optimizer.step()
→ Trainable Parameter 업데이트
```

이다.

Fine-tuning이라는 특별한 마법 명령이 따로 있는 것이 아니다.

---

## 3-2. Trainable Parameter와 Frozen Parameter

PyTorch Parameter에는 다음 속성이 있다.

```python
parameter.requires_grad
```

개념적으로:

```text
requires_grad = True
→ 학습 대상

requires_grad = False
→ Frozen
```

예를 들어:

```python
for param in model.parameters():
    param.requires_grad = False
```

라고 하면 모든 기존 Parameter를 Freeze할 수 있다.

특정 Layer만 열 수도 있다.

```python
for param in model.classifier.parameters():
    param.requires_grad = True
```

즉 어떤 Parameter를 Optimizer가 업데이트할 수 있도록 구성했는지가 중요하다.

---

# Unit 4. Fine-tuning의 여러 종류

Fine-tuning이라는 단어는 실제로 여러 종류의 학습을 넓게 가리킬 수 있다.

---

## 4-1. Continued Pre-training

도메인 원문을 사용해 Language Modeling 학습을 계속하는 방식이다.

```text
Base Model
+
법률 원문 / 의료 원문 / 회사 도메인 Text
↓
Next Token Prediction 학습 계속
↓
Domain-adapted Model
```

목적은 특정 Instruction에 답하는 형식을 직접 가르치는 것보다:

```text
도메인 언어
도메인 표현
전문 용어
통계적 패턴
```

을 추가로 학습시키는 데 가깝다.

---

## 4-2. Supervised Fine-Tuning(SFT)

입력과 원하는 정답을 함께 제공한다.

예:

```json
{
  "prompt": "다음 문의를 분류하세요: 결제가 두 번 됐어요",
  "completion": "중복결제"
}
```

또는 대화형 Dataset:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "다음 문의를 분류하세요: 결제가 두 번 됐어요"
    },
    {
      "role": "assistant",
      "content": "중복결제"
    }
  ]
}
```

이런 Dataset으로 Model에게:

```text
이 입력
→ 이런 출력을 내라
```

를 학습시킨다.

---

## 4-3. Instruction Tuning

Instruction Tuning은 일반적으로 다양한 지시와 모범 응답을 사용해:

```text
Instruction을 이해하고
↓
요구된 Task를 수행하고
↓
적절한 형식으로 답하는 행동
```

을 강화하는 SFT 성격의 학습을 말한다.

중요한 점:

```text
Instruction Tuning
→ 무엇을 학습시키는가?

Full / LoRA / QLoRA
→ Parameter를 어떻게 학습시키는가?
```

이다.

---

## 4-4. Preference Tuning

두 답변 중 어떤 것이 더 좋은지 같은 선호 정보를 사용할 수 있다.

예:

```text
Prompt

A 응답
B 응답

Human Preference
→ B가 더 좋음
```

이런 선호 Dataset으로 Model 행동을 조정하는 방법들이 있다.

대표적으로 DPO 같은 방식도 있다.

이 부분은 Fine-tuning 과목에서는 개념만 이해한다.

---

# Unit 5. Full Fine-tuning

## 5-1. 개념

Full Fine-tuning은 기존 Model의 많은 또는 전체 Parameter를 직접 학습 대상으로 두는 방식이다.

```text
Base Model

Parameter A ← Update
Parameter B ← Update
Parameter C ← Update
Parameter D ← Update
...
```

개념적으로는:

```python
for param in model.parameters():
    param.requires_grad = True
```

에 가까운 그림을 생각할 수 있다.

실제 라이브러리는 더 많은 설정을 처리하지만 핵심 원리는 같다.

---

## 5-2. 장점

Full Fine-tuning은 높은 표현력을 가질 수 있다.

Model 전체가 Task에 맞게 조정될 수 있기 때문이다.

---

## 5-3. 비용

하지만 비용이 크다.

```text
GPU Memory
Compute
Training Time
Optimizer State
Gradient Memory
Checkpoint Storage
```

가 필요하다.

Model이 커질수록 부담은 빠르게 증가한다.

---

## 5-4. 기존 능력 회귀

Parameter를 크게 변경하면 목표 Task는 좋아졌지만 다른 능력이 저하될 수 있다.

예:

```text
Base Model

한국어     좋음
영어       좋음
Code       좋음
일반 지식  좋음

↓ 특정 Dataset으로 강한 Fine-tuning

Fine-tuned Model

특정 Task  매우 좋음
영어       일부 저하
Code       일부 저하
안전 행동  일부 저하 가능
```

이런 문제와 연결되는 대표 개념이:

```text
Catastrophic Forgetting
```

이다.

---

# Unit 6. Fine-tuning을 하면 기존 지식을 잃는가?

정확한 답은:

> **반드시 모두 잃는 것은 아니지만, 일부 기존 능력이 저하될 수 있다.**

이다.

---

## 6-1. 잘못된 이해

```text
Parameter가 바뀜
=
기존 지식 전부 삭제
```

는 아니다.

Instruction Tuning의 일반적인 목적은:

```text
기존 Language Model 능력
+
Instruction Following 향상
```

이다.

---

## 6-2. 그러나 손실 가능성은 있다

추가 학습이 너무 강하거나 Dataset이 편향되어 있으면:

```text
새 능력 ↑
기존 능력 ↓
```

가 나타날 수 있다.

그래서 Fine-tuning 평가는 목표 Task만 보면 안 된다.

```text
목표 Task 성능
+
기존 일반 능력
+
안전성
+
거절 정책
+
다른 언어
+
Code 능력
```

등을 함께 확인해야 한다.

---

# Unit 7. Parameter-Efficient Fine-Tuning(PEFT)

## 7-1. 왜 PEFT가 필요한가?

대규모 Model의 모든 Parameter를 업데이트하면 비용이 크다.

그래서 등장한 접근이:

```text
PEFT
Parameter-Efficient Fine-Tuning
```

이다.

핵심 아이디어는:

> 전체 Model을 모두 학습하지 않고도 적은 Trainable Parameter로 Model을 적응시키자.

이다.

---

## 7-2. PEFT는 하나의 알고리즘 이름이 아니다

PEFT는 큰 범주의 접근이다.

```text
PEFT
├─ LoRA
├─ Prefix / Prompt 계열
├─ Adapter 계열
└─ 기타 방법
```

이번 과정에서는 가장 대표적인 LoRA를 중심으로 본다.

---

# Unit 8. LoRA

## 8-1. 가장 중요한 오해

LoRA를 다음처럼 설명하면 부정확하다.

```text
기존 Weight 중 일부만 골라 수정한다.
```

LoRA의 대표적인 아이디어는:

```text
기존 Weight W
→ 대부분 Freeze

+

작은 Trainable Matrix
A, B
→ 학습
```

이다.

---

## 8-2. 직관

큰 Weight 행렬을 직접 모두 바꾸는 대신 변화량을 낮은 Rank의 두 작은 행렬로 표현한다.

```text
W' = W + ΔW

ΔW ≈ B × A
```

여기서:

```text
W
→ 기존 Base Weight
→ 고정

A, B
→ 새롭게 추가한 작은 Trainable Parameter
→ 학습
```

이다.

---

## 8-3. Rank

LoRA에서 중요한 Hyperparameter 중 하나가:

```text
r
```

이다.

Rank가 커지면 일반적으로:

```text
Trainable Parameter ↑
표현 능력 ↑ 가능
Memory / Compute ↑
```

가 될 수 있다.

하지만:

```text
Rank가 높음
=
무조건 성능 향상
```

은 아니다.

Dataset과 Task에 맞게 실험해야 한다.

---

## 8-4. Target Module

LoRA Adapter를 어느 Module에 붙일지도 중요하다.

예를 들어 Model Architecture에 따라:

```text
q_proj
k_proj
v_proj
o_proj
up_proj
down_proj
gate_proj
```

등이 있을 수 있다.

개념적인 설정:

```python
from peft import LoraConfig

config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules="all-linear",
    task_type="CAUSAL_LM",
)
```

실제 Module 이름과 권장 Target은 Model Architecture와 사용 중인 PEFT 버전을 확인해야 한다.

---

# Unit 9. LoRA와 일부 Layer Freeze는 다른 개념이다

학생들이 자주 혼동하는 부분이다.

---

## 9-1. 일부 기존 Layer만 학습

```text
Layer 1  🔒
Layer 2  🔒
Layer 3  ← Update
Layer 4  ← Update
```

기존 Weight 일부를 직접 변경한다.

---

## 9-2. LoRA

```text
Base Weight
→ 대부분 Freeze

+

LoRA Adapter
→ 새 Parameter 추가
→ Adapter만 Training
```

즉:

```text
일부 Layer Freeze
≠
LoRA
```

이다.

---

# Unit 10. QLoRA

## 10-1. QLoRA란?

QLoRA는 LoRA 기반 Fine-tuning을 더 적은 Memory로 수행하기 위한 대표적인 접근이다.

개념적으로:

```text
Base Model
↓
저비트 Quantization
↓
Base Weight Freeze
↓
LoRA Adapter 추가
↓
Adapter Training
```

이다.

---

## 10-2. 핵심

일반적인 설명 수준에서 QLoRA는:

```text
Quantized Base Model
+
LoRA Adapter Training
```

으로 이해하면 된다.

Google의 현재 Gemma QLoRA 가이드도 4-bit로 양자화한 Base Weight를 고정하고 LoRA Adapter를 학습하는 흐름을 사용한다.

---

## 10-3. QLoRA가 해결하지 않는 것

QLoRA는 Memory 부담을 줄이는 데 도움을 줄 수 있지만 다음 문제를 자동으로 해결하지 않는다.

```text
잘못된 Dataset
Label 불일치
Data Leakage
Overfitting
잘못된 Chat Template
나쁜 Evaluation
잘못된 Business Objective
```

즉 자원이 줄었다고 학습 설계가 쉬워지는 것은 아니다.

---

# Unit 11. 학습 목표와 Parameter 전략을 분리하라

이 과목에서 가장 중요한 표 중 하나다.

| 질문 | 대표 선택지 |
|---|---|
| 무엇을 학습할 것인가? | Continued Pre-training / SFT / Preference Tuning |
| 어떤 Parameter를 업데이트할 것인가? | Full / Partial Freeze / PEFT |
| PEFT를 어떤 방식으로 할 것인가? | LoRA 등 |
| Base Model Memory 부담을 더 줄일 것인가? | QLoRA 같은 Quantized Fine-tuning |

예를 들어:

```text
Instruction Dataset
↓
SFT
↓
QLoRA
↓
Instruction-following Adapter
```

가 가능하다.

---

# Unit 12. Fine-tuning 전에 먼저 할 일

## 12-1. Task 계약 정의

“우리 회사용 AI를 Fine-tuning하자”는 목표가 아니다.

측정 가능한 Task를 정의해야 한다.

예:

```text
입력:
고객 문의 Text

출력:
다음 Label 중 정확히 하나

- 결제
- 중복결제
- 환불
- 배송
- 기타
```

이렇게 정의해야 평가할 수 있다.

---

## 12-2. Baseline

학습 전에 Base Model 성능을 먼저 측정한다.

```text
Base Model
+
고정 Prompt
+
고정 Test Case
+
고정 Decoding
↓
Baseline
```

Baseline이 없으면:

```text
Fine-tuning 후 92점
```

이라는 숫자가 좋은지 알 수 없다.

Base가 이미 94점이었다면 오히려 나빠진 것이다.

---

## 12-3. 먼저 Prompt와 RAG를 검토한다

Fine-tuning은 비용이 가장 큰 선택지 중 하나다.

따라서 일반적으로:

```text
Prompt로 해결 가능한가?
↓
Structured Output / Validation으로 가능한가?
↓
RAG가 필요한가?
↓
그래도 반복되는 Model 행동 문제가 남는가?
↓
Fine-tuning 검토
```

순서가 유용하다.

---

# Unit 13. Dataset 설계

Fine-tuning의 성능은 Dataset 품질에 매우 크게 좌우된다.

---

## 13-1. 좋은 Dataset의 조건

```text
Task 정의가 명확
Label 일관성
정답 품질
중복 최소화
개인정보 검토
라이선스 / 권리 확인
다양한 표현 포함
실제 운영 분포 반영
```

---

## 13-2. 나쁜 Dataset

다음 Dataset은 문제가 있다.

```json
{"text": "결제가 두 번 됐어요", "label": "중복결제"}
{"text": "결제가 두번 됐어요", "label": "결제"}
{"text": "두 번 결제되었습니다", "label": "환불"}
```

비슷한 의미에 서로 다른 Label이 붙으면 Model도 일관된 규칙을 배우기 어렵다.

---

## 13-3. 개인정보와 기밀 정보

Fine-tuning Dataset에 다음 정보가 들어간다면 반드시 검토해야 한다.

```text
주민등록번호
계좌번호
실명 고객 정보
의료 정보
계약 기밀
회사 내부 비밀
API Key
Password
```

Parameter는 Database가 아니지만 학습 데이터가 재현되거나 암기될 가능성을 완전히 무시할 수 없다.

---

# Unit 14. Train / Validation / Test

## 14-1. Train

실제 Parameter를 업데이트하는 데 사용한다.

```text
Train Dataset
↓
Loss
↓
Backward
↓
Parameter Update
```

---

## 14-2. Validation

학습 중 설정과 Checkpoint를 비교한다.

```text
Epoch 1
↓
Validation

Epoch 2
↓
Validation

Epoch 3
↓
Validation
```

Validation을 보며:

```text
Overfitting
Learning Rate
Epoch
Checkpoint
```

등을 판단할 수 있다.

---

## 14-3. Test

최종적으로 한 번 평가하기 위한 잠근 Dataset이다.

```text
Train
→ 학습

Validation
→ 선택

Test
→ 최종 평가
```

Test 결과를 계속 보면서 Hyperparameter를 수정하면 Test가 사실상 Validation이 된다.

---

# Unit 15. Data Leakage

Fine-tuning 평가에서 매우 중요한 문제다.

예를 들어 하나의 원본 문의에서 문장만 조금 바꾼 Sample을 만들었다고 하자.

```text
A:
결제가 두 번 됐어요.

B:
결제가 두 번 처리됐습니다.

C:
중복으로 결제됐어요.
```

이 세 문장을 무작위로 나누어:

```text
A → Train
B → Validation
C → Test
```

에 넣으면 의미상 거의 같은 Case가 모든 Split에 들어간다.

결과:

```text
Test Score 높음
```

하지만 실제 신규 사용자에게 일반화된 것인지 알기 어렵다.

따라서 원본 그룹 단위로 분리할 수 있다.

```text
semantic_group_id
document_id
customer_case_id
conversation_id
```

같은 Group 기준을 활용한다.

---

# Unit 16. Chat Template과 Tokenization

Chat Model 학습에서는 단순 Text만 중요한 것이 아니다.

다음 구조가 실제 Token Sequence로 변환된다.

```text
System
User
Assistant
```

Model Family별 Chat Template이 다를 수 있다.

따라서:

```text
Training 때 사용한 Template
≠
Inference 때 사용한 Template
```

이면 성능 문제가 발생할 수 있다.

---

## 16-1. Conversational Dataset

예:

```python
example = {
    "messages": [
        {
            "role": "user",
            "content": "다음 문의를 분류하세요: 결제가 두 번 됐어요",
        },
        {
            "role": "assistant",
            "content": "중복결제",
        },
    ]
}
```

TRL의 `SFTTrainer`는 대화형 Dataset 형식을 지원하며 Chat Template을 적용할 수 있다.

---

## 16-2. 어디에 Loss를 걸 것인가?

Instruction Tuning에서는 경우에 따라 User Prompt가 아니라 Assistant 응답 Token에만 Loss를 계산하고 싶을 수 있다.

개념적으로:

```text
User Token
→ 입력 Context

Assistant Token
→ 정답으로 학습
```

TRL은 조건이 맞는 대화형 Dataset에서 Assistant Message만 Loss에 포함하는 설정을 지원한다.

---

# Unit 17. Trainer는 무엇을 해주는가?

Hugging Face를 사용하면 코드가 다음처럼 보일 수 있다.

```python
trainer.train()
```

학생은 이렇게 생각할 수 있다.

> `train()`이 Fine-tuning을 해주는 특별한 알고리즘인가?

아니다.

내부 개념은 여전히:

```text
Batch
↓
Forward
↓
Loss
↓
Backward
↓
Gradient
↓
Optimizer Step
↓
Learning Rate Scheduler
↓
반복
```

이다.

Trainer는 이 Training Loop를 추상화해준다.

---

# Unit 18. 최소 SFT + LoRA 구조

아래 코드는 구조를 이해하기 위한 예제다.

실제 Model ID, GPU 환경, Package Version은 수업 시작 전에 고정해야 한다.

```python
from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

MODEL_ID = "YOUR_MODEL_ID"

dataset = Dataset.from_list(
    [
        {
            "messages": [
                {
                    "role": "user",
                    "content": "다음 문의를 분류하세요: 결제가 두 번 됐어요",
                },
                {
                    "role": "assistant",
                    "content": "중복결제",
                },
            ]
        },
        {
            "messages": [
                {
                    "role": "user",
                    "content": "다음 문의를 분류하세요: 주문을 취소하고 싶어요",
                },
                {
                    "role": "assistant",
                    "content": "환불",
                },
            ]
        },
    ]
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules="all-linear",
    task_type="CAUSAL_LM",
)

training_args = SFTConfig(
    output_dir="./outputs",
    num_train_epochs=1,
    learning_rate=1e-4,
)

trainer = SFTTrainer(
    model=MODEL_ID,
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config,
)

trainer.train()
trainer.save_model("./adapter")
```

> **주의**  
> 이 코드는 실행 가능한 구조를 보여주지만 실제 모델마다 Chat Template, Precision, GPU Memory, Target Module, Batch Size를 확인해야 한다.  
> 수업에서는 검증한 Model ID와 Package Lock을 제공해야 한다.

---

# Unit 19. QLoRA 구조

QLoRA에서는 Base Model을 Quantized 상태로 로드하고 LoRA Adapter를 학습한다.

대표적인 구조는:

```text
Base Model
↓
4-bit Load
↓
Base Weight Freeze
↓
LoRA Adapter
↓
SFT
```

현재 Google의 Gemma 공식 QLoRA 예제도 Hugging Face Transformers, TRL, PEFT를 사용해 이 구조를 구현한다.

---

# Unit 20. Fine-tuning에서 중요한 Hyperparameter

대표적인 Hyperparameter는 다음과 같다.

```text
learning_rate
num_train_epochs
batch_size
gradient_accumulation
max_length
warmup
weight_decay
LoRA rank r
lora_alpha
lora_dropout
target_modules
```

하지만 초보자가 가장 조심해야 할 것은:

```text
Parameter를 많이 바꿈
=
무조건 더 잘 학습
```

이 아니라는 점이다.

학습 품질은:

```text
Dataset
Task 정의
Split
Model 선택
Template
Loss 설계
Hyperparameter
Evaluation
```

전체에 의해 결정된다.

---

# Unit 21. Training Loss를 어떻게 봐야 하는가?

Training Loss가 줄어드는 것은 학습이 진행되고 있다는 하나의 신호다.

하지만:

```text
Training Loss ↓
=
실제 서비스 품질 ↑
```

는 아니다.

예를 들어 Model이 Train Dataset을 외워도 Training Loss는 낮아질 수 있다.

따라서:

```text
Training Loss
+
Validation Metric
+
잠근 Test
+
실제 Failure Case
```

를 함께 본다.

---

# Unit 22. Fine-tuning 평가

## 22-1. Task Metric

분류 Task라면:

```text
Accuracy
Precision
Recall
F1
Confusion Matrix
```

등을 사용할 수 있다.

형식 출력 Task라면:

```text
Exact Match
Schema Validity
Field Accuracy
```

등을 볼 수 있다.

---

## 22-2. 일반 능력 회귀

목표 Task만 평가하면 안 된다.

```text
Base Model
vs
Fine-tuned Model
```

을 같은 Case로 비교한다.

확인 대상:

```text
일반 질의
다국어
Code
안전 거절
사실성
기존 서비스 기능
```

---

## 22-3. Success / Failure / Boundary

Test Case를 다음처럼 나누는 것도 좋다.

```text
Success Case
→ 반드시 성공해야 하는 요청

Failure Case
→ 거절하거나 실패해야 하는 요청

Boundary Case
→ 애매하지만 정의된 경계 안에서 처리해야 하는 요청
```

---

# Unit 23. Adapter 저장과 Reload

LoRA를 학습하면 일반적으로 Adapter Weight를 저장한다.

```text
Base Model
+
Adapter
=
Fine-tuned 동작
```

중요한 점:

```text
Adapter만 있음
=
완전한 재현 가능
```

이 아니다.

함께 기록해야 할 정보:

```text
Base Model ID
Base Revision
Tokenizer / Processor
Chat Template
Adapter Version
PEFT Config
Dataset Version
Package Version
```

---

## 23-1. Reload 검증

학습이 끝난 현재 프로세스에서만 테스트하지 않는다.

```text
Training Process
↓
Adapter 저장
↓
Process 종료
↓
새 Process
↓
Base Model 다시 Load
↓
Adapter Load
↓
같은 Test 실행
```

이 과정을 통해 Artifact가 실제로 재사용 가능한지 확인한다.

---

# Unit 24. Adapter를 Merge할 것인가?

LoRA Adapter를 Base Model과 별도로 유지할 수도 있고, 지원되는 환경에서는 Merge하여 하나의 Weight로 저장할 수도 있다.

### 별도 Adapter

```text
Base Model
+
LoRA Adapter
```

장점:

```text
Adapter 작음
여러 Adapter 관리 가능
Base 공유 가능
```

### Merge

```text
Base Weight
+
LoRA 변화량
↓
Merged Model
```

일부 Serving 환경에서는 배포가 단순해질 수 있다.

하지만 Merge에 필요한 CPU/GPU Memory와 배포 방식은 Model과 Framework에 따라 확인해야 한다.

---

# Unit 25. Fine-tuning Experiment를 재현 가능하게 만들기

Fine-tuning은 코드 한 번 실행하는 작업이 아니다.

하나의 Experiment를 다음 자산으로 관리해야 한다.

```text
Experiment
├─ Base Model ID / Revision
├─ Dataset Version
├─ Split Manifest
├─ Prompt / Template Version
├─ Seed
├─ Hyperparameter
├─ Package Lock
├─ Hardware
├─ Checkpoint
├─ Adapter
├─ Baseline 결과
├─ Validation 결과
├─ Test 결과
└─ Known Failure
```

---

# Unit 26. Prompt / RAG / Fine-tuning 선택 기준

## 26-1. Prompt

다음과 같은 경우 먼저 Prompt를 검토한다.

```text
지시가 불명확
출력 형식이 흔들림
역할을 명확히 하면 해결 가능
Few-shot Example로 해결 가능
```

---

## 26-2. RAG

다음은 RAG가 적합한 경우가 많다.

```text
최신 회사 규정
자주 바뀌는 상품 정보
출처가 필요한 답변
원문 근거가 필요한 업무
권한별 문서 검색
```

---

## 26-3. Fine-tuning

다음은 Fine-tuning을 검토할 수 있다.

```text
반복되는 특정 분류 Task
특정 추출 Task
특정 응답 스타일
특정 업무 형식
Base Model이 지속적으로 같은 종류의 실패
Prompt만으로 안정화가 어려움
```

---

## 26-4. 함께 사용할 수도 있다

예:

```text
사용자 질문
↓
RAG
→ 최신 회사 정보

↓
Fine-tuned Model
→ 회사 상담 스타일 / Task 행동

↓
Agent
→ Tool 실행

↓
최종 결과
```

---

# Unit 27. Fine-tuning이 적절하지 않은 사례

## 사례 1. 매일 바뀌는 환율

```text
환율을 Model에 Fine-tuning
```

하는 것보다:

```text
API / Retrieval
```

이 적절하다.

---

## 사례 2. 회사 규정 Version 관리

규정이 바뀔 때마다 Model을 다시 학습시키는 것보다:

```text
문서 Version
+
RAG
```

가 관리하기 쉽다.

---

## 사례 3. 단순 JSON 형식 문제

Model이 이미 충분히 잘하고 있다면:

```text
Structured Output
+
Schema Validation
```

으로 해결할 수 있다.

---

# Unit 28. Fine-tuning 실패 사례

## 실패 1. Dataset이 너무 작고 반복적

```text
Train 성능 좋음
Test 성능 나쁨
```

→ Overfitting 가능성

---

## 실패 2. Train/Test Leakage

비슷한 Sample이 모든 Split에 존재

→ Test Score 과대평가

---

## 실패 3. Base Model보다 나쁨

Baseline을 안 만들면 알아차리기 어렵다.

---

## 실패 4. Adapter는 저장했지만 Reload 안 됨

Base Revision이나 Tokenizer Version을 기록하지 않은 경우.

---

## 실패 5. 목표 Task는 향상, 안전성 저하

Task Metric만 본 경우.

---

# Unit 29. 실습 1 — Prompt / RAG / Fine-tuning 선택

다음 요구사항에서 첫 번째로 검토할 방법을 선택한다.

| 요구사항 | 선택 후보 |
|---|---|
| 매주 바뀌는 상품 금리 | Prompt / RAG / Fine-tuning |
| 고객 문의를 20개 Label로 분류 | Prompt / Fine-tuning |
| 회사 JSON Schema 출력 | Prompt / Structured Output / Fine-tuning |
| 사내 규정 검색 + 회사 상담 말투 | RAG + Fine-tuning 가능 |
| 오늘 날씨 | Tool / API |

각 항목에 대해 “왜”를 한 문장으로 설명한다.

---

# Unit 30. 실습 2 — Dataset 품질 검사

다음 Dataset을 보고 문제를 찾는다.

```text
1. "결제가 두 번 됐어요" → 중복결제
2. "두 번 결제됐습니다" → 환불
3. "배송이 아직 안 왔습니다" → 배송
4. "배송이 안 왔어요" → 배송
5. "카드가 두 번 승인됐어요" → 중복결제
```

확인할 것:

```text
Label 일관성
중복
Semantic Group
Train/Test Leakage 가능성
운영 분포
```

---

# Unit 31. 실습 3 — Parameter 전략 구분

다음 설명을 분류한다.

```text
A.
기존 Weight 대부분을 직접 Update

B.
기존 Weight 중 일부 Layer만 Update

C.
Base Weight 대부분 Freeze
+ LoRA Adapter Training

D.
Quantized Base Weight Freeze
+ LoRA Adapter Training
```

정답:

```text
A → Full Fine-tuning
B → Partial Freeze
C → LoRA
D → QLoRA
```

---

# Unit 32. 실습 4 — Training Loop 이해

다음 코드를 실행해 PyTorch Training Loop의 기본 흐름을 확인한다.

```python
import torch
from torch import nn

torch.manual_seed(42)

x = torch.tensor(
    [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0],
    ]
)

y = torch.tensor([[0.0], [1.0], [1.0], [1.0]])

model = nn.Linear(2, 1)

optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.1,
)

loss_fn = nn.BCEWithLogitsLoss()

for step in range(200):
    optimizer.zero_grad()

    logits = model(x)
    loss = loss_fn(logits, y)

    loss.backward()
    optimizer.step()

with torch.no_grad():
    probs = torch.sigmoid(model(x))

print(probs)
```

확인할 것:

```text
Forward
Loss
Backward
Optimizer Step
Parameter Update
```

이 작은 예제의 Training Loop와 LLM Fine-tuning의 기본 원리는 같다.

차이는 Model 규모와 Dataset, Hardware, Training 전략의 복잡도다.

---

# Unit 33. 실습 5 — Base vs Tuned 평가표 만들기

다음 표를 직접 작성한다.

| Case | Base | Tuned | 기대 결과 | 판정 |
|---|---|---|---|---|
| 정상 분류 1 |  |  | 중복결제 |  |
| 정상 분류 2 |  |  | 환불 |  |
| 모호한 문의 |  |  | 기타/보류 |  |
| 일반 질문 |  |  | 기존 능력 유지 |  |
| 악성 입력 |  |  | 정책에 따른 처리 |  |

목표는:

```text
Fine-tuning 전
vs
Fine-tuning 후
```

를 같은 Case로 비교하는 것이다.

---

# Unit 34. 실습 6 — Fine-tuning Experiment Contract

각 팀은 다음 내용을 한 페이지로 작성한다.

```text
1. Base Model
2. Task
3. Input Schema
4. Output Schema
5. Dataset 출처
6. Train / Validation / Test 기준
7. Leakage 방지 Group
8. Fine-tuning 방식
9. LoRA / QLoRA 사용 여부
10. Baseline
11. Metric
12. Regression Test
13. 저장 Artifact
14. Rollback 방법
```

이 문서가 없는 Fine-tuning Experiment는 재현과 비교가 어렵다.

---

# Unit 35. 실무 팁

## 35-1. 작은 Dataset일수록 Split이 더 중요하다

Dataset이 작을수록 비슷한 Sample이 Train/Test에 섞였을 때 평가 왜곡이 커질 수 있다.

---

## 35-2. Adapter 크기만 보고 성공 판단하지 않는다

```text
Adapter 저장 완료
```

는 기술적으로 파일이 생겼다는 뜻일 뿐:

```text
품질 향상
```

을 의미하지 않는다.

---

## 35-3. Training Loss보다 Business Metric

실제 서비스가 원하는 것은:

```text
Loss 0.312
```

가 아니라:

```text
분류 정확도
Schema 준수
오류 감소
사람 검토 시간 감소
안전성
```

이다.

---

## 35-4. Dataset Version을 반드시 남긴다

Model Version만 기록하고 Dataset Version을 기록하지 않으면 결과를 재현하기 어렵다.

---

## 35-5. Base Model License 확인

Open-weight Model을 Fine-tuning할 때는 반드시:

```text
Model License
Dataset License
상업적 이용 조건
재배포 조건
```

을 확인해야 한다.

---

# Unit 36. 주의사항

1. Fine-tuning을 최신 사실 저장소로 생각하지 않는다.
2. Training Loss 감소만으로 품질을 판단하지 않는다.
3. Test Dataset을 반복해서 보며 조정하지 않는다.
4. Train/Test에 의미상 같은 Sample이 섞이지 않게 한다.
5. LoRA를 “기존 Weight 일부 직접 수정”으로만 설명하지 않는다.
6. QLoRA를 새로운 학습 목표가 아니라 자원 효율 전략으로 이해한다.
7. Base Model보다 실제로 좋아졌는지 반드시 비교한다.
8. 목표 Task 외의 회귀를 확인한다.
9. Adapter와 Base Model Version을 함께 기록한다.
10. 개인정보·기밀·저작권이 있는 Dataset을 무심코 학습시키지 않는다.

---

# Unit 37. 최종 요약

이번 과목의 핵심을 한 줄씩 정리한다.

### Fine-tuning

```text
Pre-trained Model을
추가 Dataset으로 다시 학습해
행동·능력을 조정
```

### RAG

```text
Model Parameter는 그대로 두고
필요한 외부 정보를 검색해
현재 Context에 제공
```

### Full Fine-tuning

```text
기존 Parameter의 많은/전체 부분을
직접 Update
```

### LoRA

```text
Base Weight 대부분 Freeze
+
작은 Low-rank Adapter Parameter 학습
```

### QLoRA

```text
Quantized Base Model
+
LoRA Adapter Training
```

### SFT

```text
입력과 모범 답변을 이용한
Supervised Fine-tuning
```

### 가장 중요한 구분

```text
SFT / Instruction Tuning
→ 무엇을 학습할 것인가?

Full / LoRA / QLoRA
→ Parameter를 어떤 방식으로 학습할 것인가?
```

---

# 38. 최종 Mental Model

```text
문제가 있다
↓
Prompt로 해결 가능한가?
↓
RAG가 필요한가?
↓
그래도 반복되는 Model 행동 문제가 남는가?
↓
Fine-tuning 검토
↓
Task 계약
↓
Baseline
↓
Dataset
↓
Split
↓
Parameter 전략
↓
Training
↓
Validation
↓
Artifact 저장
↓
Reload
↓
잠근 Test
↓
Base와 비교
↓
Regression 확인
↓
배포 / Rollback
```

Fine-tuning에서 가장 중요한 것은:

> **“학습을 돌렸다”가 아니라, 무엇을 개선하려 했고 실제로 개선됐다는 증거가 있는가?**

이다.

---

# 39. 자기 점검

다음 질문에 자료를 보지 않고 답해본다.

1. Fine-tuning과 RAG의 차이는 무엇인가?
2. Parameter는 Database와 어떻게 다른가?
3. Fine-tuning의 Training Loop를 설명할 수 있는가?
4. Full Fine-tuning과 Partial Freeze의 차이는 무엇인가?
5. LoRA는 어떤 Parameter를 학습하는가?
6. QLoRA는 LoRA와 무엇이 다른가?
7. SFT와 LoRA를 같은 분류로 보면 왜 안 되는가?
8. Fine-tuning이 기존 능력을 일부 저하시킬 수 있는 이유는 무엇인가?
9. Train / Validation / Test의 역할은 무엇인가?
10. Data Leakage가 왜 위험한가?
11. Training Loss가 낮아도 실패할 수 있는 이유는 무엇인가?
12. Adapter Reload Test를 왜 해야 하는가?
13. 최신 회사 규정에는 왜 RAG가 더 관리하기 쉬운가?
14. 어떤 경우 Fine-tuning을 검토할 수 있는가?
15. Fine-tuning Experiment에 남겨야 할 Artifact는 무엇인가?

---

# 40. 참고자료

아래 자료는 기술 세부사항을 확인할 때 우선 참고한다.

- Hugging Face PEFT — Parameter-Efficient Fine-Tuning
  - https://huggingface.co/docs/peft/
- Hugging Face PEFT LoRA
  - https://huggingface.co/docs/peft/en/package_reference/lora
- Hugging Face TRL SFTTrainer
  - https://huggingface.co/docs/trl/sft_trainer
- Google Gemma Fine-tuning
  - https://ai.google.dev/gemma/docs/tune
- Google Gemma LoRA Fine-tuning
  - https://ai.google.dev/gemma/docs/core/lora_tuning
- Google Gemma QLoRA + Hugging Face
  - https://ai.google.dev/gemma/docs/core/huggingface_text_finetune_qlora
- LoRA Paper
  - https://arxiv.org/abs/2106.09685
- QLoRA Paper
  - https://arxiv.org/abs/2305.14314

> 라이브러리 API, Model ID, 권장 Precision과 Package Version은 빠르게 바뀔 수 있으므로 실제 실습 직전에 공식 문서를 다시 확인한다.

---

# 41. 관련 Wiki Link

```text
[[대규모 언어 모델(LLM)]]
[[Transformer]]
[[Prompt Engineering]]
[[RAG]]
[[Fine-tuning]]
[[Supervised Fine-Tuning]]
[[Instruction Tuning]]
[[PEFT]]
[[LoRA]]
[[QLoRA]]
[[Catastrophic Forgetting]]
[[Evaluation]]
[[Gemma]]
```

---

# 42. Knowledge 저장 위치 제안

```text
Knowledge/
└── Phase2/
    └── Fine-tuning/
        ├── Fine-tuning.md
        ├── RAG vs Fine-tuning.md
        ├── SFT와 Instruction Tuning.md
        ├── Full Fine-tuning.md
        ├── PEFT.md
        ├── LoRA.md
        ├── QLoRA.md
        ├── Dataset Split과 Leakage.md
        └── Fine-tuning Evaluation.md
```
