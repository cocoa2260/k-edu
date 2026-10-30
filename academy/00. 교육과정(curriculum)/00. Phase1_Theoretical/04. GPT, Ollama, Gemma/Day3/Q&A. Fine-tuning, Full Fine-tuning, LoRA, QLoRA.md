# Q. 
Instruction Tuning이라고 하는 행위가 결국은 Base Model에서 이미 학습된 parameter를 변경하는 행위라면, Base Model은 기존에 학습되어 있던 지식을 잃어버린다고 이해해도 되는건가?

# A.

네, **앞부분은 맞습니다.** 

다만 **“그러면 기존 지식을 잃어버린다”라고 바로 연결하면 조금 부정확합니다.**

Instruction Tuning은 Training이므로

`Loss → Gradient → Parameter Update`를 통해

일반적으로 Parameter에 변화가 생긴다고 설명하고 있습니다.

### 1. Instruction Tuning에서는 Parameter가 바뀐다

기본 흐름은 맞습니다.

```text
Pre-training
↓
Base Model
↓
이미 학습된 Parameter 존재

        +

Instruction Dataset
↓
추가 Training
↓
Parameter Update
↓
Instruction-tuned Model
```

예를 들어 Base Model이 이미 학습을 통해

```text
언어 패턴
문법
단어 관계
여러 지식 패턴
코드 패턴
...
```

등을 Parameter에 반영하고 있다고 합시다.

Instruction Tuning은 **이 Base Model에서 출발해서 추가 학습을 하는 것**입니다.

따라서 Full Fine-tuning 방식이라면 기존 Parameter들이 실제로 업데이트될 수 있습니다.

---

### 2. 그런데 Parameter가 바뀐다 ≠ 기존 지식을 모두 잃는다

여기가 중요합니다.

Instruction Tuning의 목적은 보통:

```text
Base Model이 가진 능력
        +
Instruction을 따르는 행동 강화
```

입니다.

즉 기존 능력을 전부 지우고 새롭게 학습시키는 것이 아닙니다.

개념적으로는:

```text
Base Model

"많은 Text Pattern과 지식을 학습했어."
"그런데 사용자의 명령을 Assistant처럼
 잘 따르도록 특별히 훈련된 것은 아니야."

        ↓ Instruction Tuning

Instruction-tuned Model

"기존 Language Modeling 능력을 바탕으로
 사용자의 요청에 적절하게 응답하는 행동을
 더 잘하도록 조정됐어."
```

Instruction-tuned Model의 `Text Continuation` 능력을 

**"기반 능력 유지"**라고 표현한 방향이 맞습니다.

### 3. 그렇다고 기존 지식 손실이 절대 없다는 것도 아니다

추가 Training 과정에서 Parameter를 변경하기 때문에 **기존에 가지고 있던 능력이나 지식의 일부가 저하될 가능성은 있습니다.**

대표적으로 연결되는 개념이 **Catastrophic Forgetting(파국적 망각)**입니다.

```text
기존 Training
↓
기존 능력 A, B, C를 학습

추가 Training
↓
특정 데이터에 지나치게 맞춰 Parameter 변경

결과
↓
새로운 능력 D는 좋아졌는데
기존 능력 A의 성능이 떨어질 수 있음
```

예를 들어 극단적으로:

```text
Base Model
→ 한국어 잘함
→ 영어 잘함
→ 코드 잘함
→ 일반 지식 잘함

        ↓

아주 편향된 특정 Dataset으로
강하게 Fine-tuning

        ↓

Fine-tuned Model
→ 특정 Task는 매우 잘함
→ 하지만 일부 기존 능력이 저하될 수도 있음
```

따라서 정확한 표현은:

> **Instruction Tuning에서는 Base Model의 기존 Parameter를 기반으로 추가 학습하며, 학습 방식에 따라 Parameter가 변경됩니다. 기존 지식을 의도적으로 지우는 과정은 아니지만, Parameter 변경으로 인해 기존 능력이나 지식이 일부 저하되는 현상이 발생할 가능성은 있습니다.**

그리고 이것 때문에 Fine-tuning에서도 **Evaluation이 중요합니다.**

```text
Base Model
↓
Instruction Tuning
↓
Instruction Following ↑

그런데...

기존 능력은 유지됐나?
한국어 성능은?
코드 능력은?
일반 지식은?
↓
Evaluation 필요
```

한 가지 더 중요한 점은 강의안에 적힌 것처럼 **항상 모든 기존 Parameter를 수정하는 것도 아닙니다.**

```text
Full Fine-tuning
→ 기존 Parameter의 많은/전체 부분을 직접 업데이트

PEFT / LoRA
→ Base Model의 Parameter 대부분은 고정하고
   추가적인 작은 Parameter를 학습
```

# Q.
어떤 방식으로 일부 parameter만 수정하는거지?
소스상에 일반적인 tuning, full file-tuning에 대한 method가 있는건가?

# A.

네. 여기서는 **개념과 실제 PyTorch/Transformers 코드가 어떻게 연결되는지** 같이 봐야 이해가 됩니다.

먼저 용어 하나를 정리하면, **“일반적인 tuning”이라는 별도의 표준 method가 있는 것은 아닙니다.** `Full Fine-tuning`, `LoRA`, `QLoRA` 등은 **어떤 Parameter를 어떤 방식으로 학습할 것인지에 대한 학습 전략**입니다. 현재 강의안에서도 “어떤 Parameter를 얼마나 업데이트하는지는 Training 방법에 따라 다를 수 있다”고 설명하고 있습니다.

## 1. Fine-tuning의 본질부터 보면

Pre-training이 끝난 Base Model에는 이미 수많은 Parameter가 있습니다.

아주 단순화하면:

```python
model.parameters()
```

안에 이런 Parameter들이 있다고 생각할 수 있습니다.

```text
Model
├── Parameter A
├── Parameter B
├── Parameter C
├── Parameter D
└── ...
```

Training의 핵심은 결국:

```text
Input
↓
Forward
↓
Loss 계산
↓
Backward
↓
Gradient 계산
↓
Optimizer
↓
Parameter Update
```

입니다.

PyTorch 수준에서는 대략 이런 구조입니다.

```python
optimizer.zero_grad()

output = model(input_ids)
loss = ...

loss.backward()

optimizer.step()
```

여기서 핵심이 `loss.backward()`와 `optimizer.step()`입니다.

```text
loss.backward()
→ 각 Parameter를 어느 방향으로 얼마나 바꿀지 Gradient 계산

optimizer.step()
→ Gradient를 이용해서 실제 Parameter 값 변경
```

즉 **Fine-tuning이라는 특별한 마법의 명령이 있는 게 아니라 결국 Training을 다시 수행하는 것**입니다.

---

# 2. Full Fine-tuning은 무엇인가?

Base Model의 기존 Parameter들을 학습 대상으로 두는 방식입니다.

개념적으로:

```text
Base Model

Parameter A  ← Update
Parameter B  ← Update
Parameter C  ← Update
Parameter D  ← Update
Parameter E  ← Update
...
```

PyTorch에서는 Parameter에 중요한 속성이 하나 있습니다.

```python
parameter.requires_grad
```

예를 들어:

```python
for param in model.parameters():
    print(param.requires_grad)
```

대부분이:

```text
True
True
True
...
```

라면 Gradient를 계산할 수 있는 Parameter라는 뜻입니다.

그리고 이 Parameter들을 Optimizer에 전달하면:

```python
optimizer = AdamW(
    model.parameters(),
    lr=...
)
```

학습 과정에서 업데이트할 수 있습니다.

따라서 개념적으로 Full Fine-tuning은:

```python
for param in model.parameters():
    param.requires_grad = True
```

와 같은 상태를 생각하면 됩니다.

물론 실제 Hugging Face 학습에서는 Trainer 등의 추상화 때문에 이런 코드를 직접 작성하지 않을 수도 있습니다.

---

# 3. 일부 Parameter만 학습하는 것도 가능하다

반대로 일부 Parameter를 고정할 수 있습니다.

PyTorch에서는:

```python
param.requires_grad = False
```

를 사용할 수 있습니다.

예를 들어 모델에 100개의 Parameter 그룹이 있다고 단순하게 가정하면:

```text
Parameter 1   → False
Parameter 2   → False
Parameter 3   → False
...
Parameter 99  → True
Parameter 100 → True
```

이렇게 할 수 있습니다.

즉:

```text
requires_grad = False
→ 학습하지 않음(Frozen)

requires_grad = True
→ 학습 가능(Trainable)
```

입니다.

실제로 일부 Layer를 Freeze하는 방식도 가능합니다.

개념적인 코드라면:

```python
for param in model.parameters():
    param.requires_grad = False

for param in model.some_layer.parameters():
    param.requires_grad = True
```

이러면:

```text
Base Model

Layer 1   🔒
Layer 2   🔒
Layer 3   🔒
Layer 4   🔒
Layer 5   ← Training
```

처럼 일부 Layer만 학습시킬 수 있습니다.

---

# 4. 그런데 LoRA는 이것과 조금 다르다

여기서 **PEFT / LoRA**가 중요합니다.

LoRA를 단순히:

> 기존 Parameter 중 일부만 골라서 수정한다.

라고 설명하면 **정확하지 않습니다.**

LoRA의 핵심은 기존 Weight를 대부분 **Freeze하고 별도의 작은 Trainable Parameter를 추가하는 것**입니다.

예를 들어 원래 Linear Layer의 Weight가 있다고 합시다.

```text
기존 Weight W
████████████████
████████████████
████████████████
████████████████

→ Freeze
```

LoRA에서는 이것을 직접 크게 수정하는 대신 작은 행렬을 추가합니다.

개념적으로:

```text
기존 Weight W
    ↓
Freeze

+

작은 Trainable Parameter
A × B
    ↓
Training
```

수식으로 보면 대략:

```text
W' = W + ΔW

ΔW = B × A
```

입니다.

여기서:

```text
W
→ Base Model의 기존 Weight
→ 고정

A, B
→ LoRA가 추가한 작은 Parameter
→ Training
```

그래서 학습해야 하는 Parameter 수를 크게 줄일 수 있습니다.

---

# 5. 실제 소스에서는 어떻게 하나?

Hugging Face 생태계에서는 보통 `transformers`와 함께 `peft` 같은 라이브러리를 사용합니다.

개념적으로는 다음과 같은 형태입니다.

```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
)

model = get_peft_model(
    model,
    lora_config,
)
```

여기서 중요한 것이:

```python
target_modules=["q_proj", "v_proj"]
```

같은 설정입니다.

쉽게 말하면:

> **Model의 어느 Module에 LoRA Adapter를 붙일 것인가?**

를 지정하는 것입니다.

그 결과 개념적으로:

```text
Transformer

Attention
├── q_proj
│    ├── 기존 Weight 🔒
│    └── LoRA A/B    ← Training
│
├── k_proj
│    └── 기존 Weight
│
├── v_proj
│    ├── 기존 Weight 🔒
│    └── LoRA A/B    ← Training
│
└── o_proj
     └── 기존 Weight
```

같은 구조가 만들어질 수 있습니다.

실제 Module 이름은 모델 Architecture마다 다르기 때문에 `q_proj`, `v_proj`를 모든 모델에 그대로 사용하면 안 됩니다.

---

# 6. 그래서 세 가지를 구분하면 된다

학생들에게는 우선 이렇게 구분시키는 게 좋습니다.

```text
① Full Fine-tuning

Base Model
├── 기존 Parameter ← Update
├── 기존 Parameter ← Update
├── 기존 Parameter ← Update
└── 기존 Parameter ← Update

→ 많은 Parameter 학습
→ 많은 Training Resource 필요
```

두 번째는:

```text
② 일부 기존 Layer Freeze

Base Model
├── 기존 Parameter 🔒
├── 기존 Parameter 🔒
├── 기존 Parameter ← Update
└── 기존 Parameter ← Update

→ 일부 기존 Parameter만 직접 변경
```

그리고 LoRA는:

```text
③ LoRA

Base Model
├── 기존 Parameter 🔒
├── 기존 Parameter 🔒
├── 기존 Parameter 🔒
└── 기존 Parameter 🔒

        +

LoRA Parameter
├── A ← Update
└── B ← Update

→ Base Weight 대부분 고정
→ 작은 추가 Parameter를 Training
```

**②와 ③은 다른 개념**이라는 게 중요합니다.

---

# 7. 그러면 `Trainer`는 뭘 해주는 건가?

Hugging Face를 사용하다 보면 실제 코드에서는:

```python
trainer.train()
```

처럼 보일 수 있습니다.

그러면 학생 입장에서는:

> "`train()`이 Fine-tuning 해주는 특별한 함수인가?"

라고 생각할 수 있는데, 내부 개념은 결국 같습니다.

```text
trainer.train()
       ↓
Batch 가져오기
       ↓
Model Forward
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
       ↓
반복
```

즉 라이브러리가 **Training Loop를 추상화해준 것**입니다.

Full Fine-tuning 전용으로:

```python
model.full_fine_tuning()
```

같은 범용 표준 method가 있어서 Full Fine-tuning이 되는 것이 아닙니다.

**어떤 Parameter를 Trainable 상태로 만들고 Optimizer가 무엇을 업데이트하도록 구성했느냐**가 핵심입니다.

---

# 8. Instruction Tuning과 이것들을 연결하면

여기서 지금 수업의 **Instruction Tuning**과 `Full Fine-tuning / LoRA`를 분리해서 봐야 합니다.

두 개는 서로 다른 질문에 답합니다.

```text
Instruction Tuning
→ "무엇을 학습시키는가?"

Full Fine-tuning / LoRA
→ "Parameter를 어떤 방식으로 학습시키는가?"
```

예를 들어 Dataset이:

```text
Instruction:
"다음 문서를 요약하세요."

Input:
"긴 문서..."

Response:
"요약 결과..."
```

라면 **Instruction Following을 학습시키는 Dataset**입니다.

그런데 이 Dataset으로 학습할 때:

```text
방법 A
Instruction Dataset
↓
Full Fine-tuning
↓
기존 Parameter들을 직접 Update
```

할 수도 있고,

```text
방법 B
Instruction Dataset
↓
LoRA
↓
Base Weight Freeze
+
LoRA Parameter Update
```

할 수도 있습니다.

따라서:

```text
                Instruction Tuning
                       │
            ┌──────────┴──────────┐
            ↓                     ↓
    Full Fine-tuning             LoRA
            ↓                     ↓
기존 Weight 다수 변경       Base Weight 대부분 고정
                        + 작은 Adapter 학습
```

라고 이해하면 됩니다.

---

# 9. 이걸 알아야 SFT, PEFT도 정리된다

이후 Phase 2에서 나오는 용어들도 사실 **서로 같은 분류 기준이 아닙니다.**

예를 들어:

```text
SFT
Supervised Fine-Tuning
→ 어떤 학습 데이터와 목표를 이용해서 학습하는가

Full Fine-tuning
→ 기존 Parameter를 얼마나 직접 업데이트하는가

PEFT
→ 적은 Trainable Parameter로 Fine-tuning하는 접근

LoRA
→ 대표적인 PEFT 방법
```

그래서 실제 프로젝트에서는 조합될 수 있습니다.

```text
Base Model
↓
Instruction Dataset
↓
SFT
↓
LoRA 방식으로 학습
↓
Instruction-following Custom Model
```

이 표현이 가능합니다.

---

## 지금 단계에서 가장 중요한 그림

```text
                     Base Model
                         │
                이미 학습된 Parameter
                         │
            ┌────────────┴────────────┐
            │                         │
     Full Fine-tuning                LoRA
            │                         │
     기존 Parameter              기존 Parameter
      직접 Update                   Freeze
                                      │
                                 LoRA Parameter
                                      │
                                    Update
            │                         │
            └────────────┬────────────┘
                         ↓
                  Fine-tuned Model
```

그리고 **Instruction Tuning은 이 그림의 다른 축**입니다.

```text
무엇을 학습?
→ Instruction → Response 관계

어떻게 Parameter를 학습?
→ Full Fine-tuning?
→ 일부 Layer만?
→ PEFT / LoRA?
```

이렇게 분리해서 이해하면 지금 강의안의 **#9 Instruction Tuning → #15 Parameter는 바뀌는가? → #34 Fine-tuning과 연결**이 훨씬 명확해집니다.

현재 Day 3 강의에서는 여기까지 개념을 보여주고, **실제 `transformers + datasets + peft`로 Instruction Dataset을 만들어 LoRA 학습을 돌려보고, 학습 전/후 Parameter 수와 출력이 어떻게 달라지는지 확인하는 실습**을 뒤쪽 Fine-tuning 과정에 넣는 게 가장 자연스럽습니다.