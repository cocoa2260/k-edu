# Day 2 - 3교시. AI Model과 Parameter — Training과 Inference

## 개요 — 이번에는 학습 전후에 **무엇이 달라지는지** 확인한다

앞 교시에서는 수치 데이터를 `Tensor`에 담고, `shape`·`dtype`·`device`를 확인했습니다. 이미 Day 1에서는 `Training`과 `Inference`의 의미도 배웠습니다. 이번 시간에는 그 정의를 다시 외우지 않고, **PyTorch Model의 Parameter를 직접 관찰**하여 학습 과정의 차이를 실증합니다.

오늘 사용할 예제는 다음 관계를 학습하는 작은 선형 모델입니다.

```text
입력 x : 1, 2, 3, 4
목표 y : 2, 4, 6, 8

                 학습 전                    학습 후
               ┌─────────┐              ┌─────────┐
입력 x ────────→│  Model  │              │  Model  │←── 새 입력 5
               │ w, b ?  │── Training ─→│ w≈2,b≈0│
               └─────────┘              └────┬────┘
                                             ↓
                                         출력 약 10
```

강의의 중심 질문은 세 가지입니다.

1. 같은 모델 코드라도 `weight`와 `bias`가 다르면 왜 결과가 달라질까?
2. `loss.backward()`와 `optimizer.step()` 중 **실제로 Parameter를 바꾸는 것은 어느 단계**일까?
3. Training을 마친 뒤 새로운 입력을 처리할 때 Parameter는 그대로 유지될까?

오늘은 이 질문에 답할 수 있도록 하나의 실습을 점진적으로 완성합니다. 외부 Model을 내려받거나 Hugging Face Hub를 탐색하는 과정은 다음 교시에서 다룹니다.

---

# 1. 학습 목표

이번 교시가 끝나면 학생은 다음을 할 수 있어야 합니다.

1. Model의 **구조(Architecture)**와 학습되는 **Parameter**를 구별한다.
2. 간단한 선형 모델 `y = wx + b`에서 Weight와 Bias의 역할을 설명한다.
3. `nn.Linear(1, 1)`을 생성하고 `named_parameters()`로 Parameter를 확인한다.
4. Prediction과 Target의 차이가 `Loss`로 표현되는 이유를 설명한다.
5. `Gradient`, `Optimizer`, `Learning Rate`가 각각 맡은 일을 구별한다.
6. `zero_grad → forward → loss → backward → step` 순서를 코드와 연결한다.
7. Training 이전과 이후의 Weight·Bias·Loss를 비교한다.
8. `model.train()`, `model.eval()`, `torch.no_grad()`의 목적을 혼동하지 않는다.
9. 새로운 입력으로 Inference를 수행하면서 Parameter가 변경되지 않음을 확인한다.

**실습 성공 기준:** 프로그램이 오류 없이 끝나는 것만으로는 부족합니다. 학생이 **어떤 값이 달라졌고, 어느 코드가 그 변화를 일으켰는지** 설명해야 합니다.

---

# 2. 앞 교시에서 가져오는 지식과 오늘 새롭게 다룰 지식

| 이미 배운 내용 | 이번 교시에서 새로 확인할 것 |
|---|---|
| Tensor는 수치 데이터를 담는다 | Model의 `weight`와 `bias`도 Tensor로 확인할 수 있다 |
| `shape`는 각 축의 크기다 | Input Tensor가 Model의 입출력 구조와 맞아야 한다 |
| Training은 Parameter를 학습한다 | 어느 코드가 Gradient를 계산하고 Parameter를 갱신하는지 확인한다 |
| Inference는 학습된 Model을 사용한다 | 실행 전후 Parameter를 비교하여 갱신이 없는지 확인한다 |

이번 교시에서는 다음 식 하나를 계속 사용합니다.

```text
y = wx + b
```

여러 종류의 문제를 번갈아 제시하는 대신 **하나의 작은 모델에서 값이 어떻게 변화하는지** 끝까지 추적합니다.

---

# 3. Model의 구조와 Parameter를 구분하자

## 3.1 Model은 소스코드와 학습값 중 어느 하나만 의미할까?

다음 식은 **계산 구조**를 나타냅니다.

```text
y = wx + b
```

- `x`: 입력값
- `w`(Weight): 입력에 곱하는 학습값
- `b`(Bias): 계산 결과에 더하는 학습값
- `y`: 모델의 출력값

`w`와 `b`가 이 모델에서 조정할 **Parameter**입니다. 식이 똑같더라도 값에 따라 결과는 달라집니다.

## 3.2 같은 입력이라도 Parameter가 다르면 출력이 달라진다

입력 `x = 2`를 넣겠습니다.

| 구분 | Weight (`w`) | Bias (`b`) | 계산 | 출력 |
|---|---:|---:|---|---:|
| Model A | 1 | 0 | `1 × 2 + 0` | 2 |
| Model B | 3 | 1 | `3 × 2 + 1` | 7 |

두 모델은 모두 같은 `y = wx + b` 구조입니다. 그러나 **Model A의 Parameter와 Model B의 Parameter가 다르므로 결과도 다릅니다.**

> 강사 질문: Python 파일에서 `y = wx + b`라는 계산식을 바꾸지 않고 Model A의 출력을 Model B처럼 바꾸려면 무엇이 달라져야 할까요?
>
> 예상 답: `w`와 `b`의 값이 달라져야 합니다.

이제 사람이 `w`, `b`를 손으로 정하는 대신, 학습 데이터로부터 값을 조정하는 과정을 구현합니다.

---

# 4. 학습할 데이터와 목표 관계

다음은 원본 강의에서 사용하는 아주 작은 지도학습 데이터입니다.

| 입력 `x` | 목표값 `y` |
|---:|---:|
| 1 | 2 |
| 2 | 4 |
| 3 | 6 |
| 4 | 8 |

사람이 보면 `y = 2x`라는 규칙을 쉽게 찾습니다. 하지만 `nn.Linear` Model은 생성 직후부터 `w=2`, `b=0`으로 설정되어 있지 않습니다. 처음에는 주어진 초기값으로 계산하고, 학습을 통해 목표 관계에 가까워지도록 조정합니다.

```text
Training Data
  ├── x: 모델에 넣을 입력
  └── y: 모델이 맞혀야 할 Target
               ↓
             Model
               ↓
         Prediction 출력
               ↓
       Target과 차이 확인
               ↓
       Weight·Bias 조정
```

이번 예제의 Tensor는 다음과 같습니다.

```python
import torch

x = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
y = torch.tensor([[2.0], [4.0], [6.0], [8.0]])

print(x.shape)  # torch.Size([4, 1])
print(y.shape)  # torch.Size([4, 1])
```

`[4, 1]`은 **데이터 4개에 각 데이터당 입력값 하나**가 있다는 뜻입니다. Shape와 차원의 자세한 정의는 앞 교시에서 다루었으므로 여기에서는 Model 입력 구조와 연결하는 데만 사용합니다.

---

# 5. Loss — 지금 예측이 얼마나 목표에서 벗어났을까?

Model은 현재 Parameter로 결과를 계산합니다. 이를 **Forward(순전파) 계산**이라고 합니다.

현재 계산 결과가 `3`인데 목표값이 `4`라면 두 값은 일치하지 않습니다.

```text
Prediction = 3
Target     = 4
         ↓
       오차 존재
```

학습하려면 이 차이를 하나의 값으로 측정해야 합니다. 그때 사용하는 것이 **Loss(손실)**이며, Loss를 계산하는 방법이 **Loss Function(손실 함수)**입니다.

이 예제에는 `MSELoss`(Mean Squared Error, 평균제곱오차)를 사용합니다.

```text
각 Prediction과 Target의 차이를 구한다
         ↓
차이를 제곱한다
         ↓
여러 데이터의 제곱 오차를 평균낸다
         ↓
Loss
```

한 개의 값만 있다면 `Prediction=3`, `Target=4`의 제곱 오차는 `(3 - 4)² = 1`입니다. 전체 Dataset의 MSE는 **각 입력에 대한 제곱 오차의 평균**입니다.

```python
from torch import nn

loss_function = nn.MSELoss()
```

Loss 자체가 Model을 수정하지는 않습니다. **현재 상태가 목표와 얼마나 다른지 계산한 결과**이기 때문입니다. 실제 Parameter를 바꾸려면 다음 단계가 필요합니다.

> 주의: 학습 데이터에서 Loss가 작다고 해서 처음 보는 모든 데이터에서도 반드시 잘 동작한다는 뜻은 아닙니다. 데이터 분리·일반화 성능의 자세한 평가는 이후의 Machine Learning 이론 과정에서 학습합니다.

---

# 6. Gradient와 Optimizer — 방향 계산과 실제 변경은 다르다

## 6.1 Gradient는 어떤 역할을 할까?

Loss가 크다는 사실만으로는 Weight를 늘릴지 줄일지 결정하기 어렵습니다.

**Gradient(기울기)**는 Parameter를 조금 바꿀 때 Loss가 어떤 방향으로 변하는지를 계산하는 데 사용됩니다. PyTorch는 자동 미분(Automatic Differentiation)을 통해 이 계산을 지원합니다.

```text
Model의 Prediction
       ↓
Target과 비교하여 Loss 계산
       ↓
loss.backward()
       ↓
각 Parameter의 Gradient 계산
```

중요한 점은 **`loss.backward()`만 실행한다고 Weight·Bias의 값이 곧바로 갱신되지는 않는다**는 것입니다.

## 6.2 Optimizer는 무엇을 할까?

**Optimizer(최적화 도구)**는 Gradient와 설정된 갱신 규칙을 사용해 Parameter를 실제로 조정합니다. 이번 예제는 PyTorch의 `SGD`를 사용합니다.

```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
```

이 코드는 완전한 예제의 `model`이 만들어진 뒤에 실행합니다.

- `model.parameters()`: 어느 Parameter를 갱신할지 Optimizer에 전달합니다.
- `lr=0.01`: Parameter 갱신 크기에 영향을 주는 **Learning Rate(학습률)**입니다.
- `optimizer.step()`: Gradient를 바탕으로 실제 Parameter 갱신을 수행합니다.

| 구분 | 역할 | Parameter 값 변경 여부 |
|---|---|---|
| `loss_function(prediction, y)` | 현재 오차를 Loss로 계산 | 변경하지 않음 |
| `loss.backward()` | Gradient 계산 | 변경하지 않음 |
| `optimizer.step()` | Optimizer 규칙에 따라 Parameter 갱신 | **변경할 수 있음** |

Gradient가 없거나 0이라면 `step()`을 실행해도 기대한 변화가 없을 수 있습니다. 따라서 **코드 호출 사실과 실제 값의 변화는 구분해 확인**해야 합니다.

---

# 7. Parameter와 Hyperparameter는 다르다

오늘의 학습에서는 두 종류의 값을 혼동하기 쉽습니다.

| 종류 | 예 | 누가 또는 무엇이 정하는가? |
|---|---|---|
| Parameter | `weight`, `bias` | Training 과정에서 모델이 학습 |
| Hyperparameter | `lr=0.01`, `epochs=1000`, Batch Size | 실습 또는 학습 설정에서 지정 |

Learning Rate를 너무 크게 하면 갱신 폭이 커져 안정적으로 학습하기 어려울 수 있고, 너무 작으면 변화가 느려질 수 있습니다. 이번 교시는 **좋은 Learning Rate를 찾는 최적화 실험**이 아닙니다. `0.01`을 사용하는 이유는 작은 모델의 Parameter 갱신 과정을 관찰하기 위해서입니다.

강사가 학생에게 물어볼 질문은 다음과 같습니다.

> `1000`번 반복하고 `lr=0.01`을 지정했을 때, 학습을 통해 자동으로 수정되는 값은 무엇인가요?
>
> **정답:** `weight`와 `bias`입니다. `1000`과 `0.01`은 이번 코드에서 정한 학습 설정입니다.

---

# 8. Epoch·Batch·Training Step을 실제 예제에 연결하기

앞 교시의 Batch는 여러 데이터를 묶어 처리하는 방법이었습니다. 여기서는 **Training Loop의 횟수**와 연결해 봅니다.

- **Epoch:** Training Dataset 전체를 한 번 학습에 사용하는 단위
- **Batch:** 한 번의 계산에 사용하도록 묶은 데이터
- **Training Step:** 보통 Batch를 이용하여 Forward·Loss·Backward·Parameter Update를 수행하는 한 번의 갱신 과정

현재 Dataset은 4개이고, **매 Epoch에 4개를 모두 하나의 Batch로 사용**합니다.

```text
Dataset 4개
     ↓
Epoch 1: 전체 4개로 1번 학습·갱신
     ↓
Epoch 2: 전체 4개로 1번 학습·갱신
     ↓
...
     ↓
Epoch 1000
```

따라서 이 예제에서는 **1000 Epoch ≈ 1000회의 Optimizer Step**입니다. 일반적으로 Batch 크기를 줄이면 한 Epoch에 여러 Step이 생길 수 있습니다. 현재는 이 차이만 이해하면 충분합니다.

---

# 9. PyTorch에서 Model과 Parameter를 직접 만들기

## 9.1 `nn.Linear(1, 1)`의 의미

PyTorch의 `nn.Linear`는 입력을 선형 변환하는 Layer입니다.

```python
import torch
from torch import nn

model = nn.Linear(in_features=1, out_features=1)
print(model)
```

첫 번째 `1`은 입력 Feature 개수, 두 번째 `1`은 출력 Feature 개수입니다. 이번에는 숫자 하나를 입력받아 숫자 하나를 출력하기 때문에 `1, 1`을 사용합니다.

## 9.2 `named_parameters()`로 확인하기

```python
for name, parameter in model.named_parameters():
    print(name, parameter.detach())
```

학생이 관찰할 출력은 다음과 비슷한 형태입니다.

```text
weight tensor([[...]])
bias   tensor([...])
```

초기 숫자는 실행 조건에 따라 달라질 수 있습니다. `named_parameters()`는 **이름과 실제 Parameter Tensor를 함께 조회**합니다. `detach()`는 여기에서 학습 계산과 분리된 값을 읽는 용도로 사용합니다.

`torch.manual_seed(42)`를 Model 생성 전에 지정하면 같은 환경에서 초기값을 비교하기 편리합니다. 숫자 `42` 자체에 특별한 학습 의미가 있는 것은 아닙니다.

```python
torch.manual_seed(42)
model = nn.Linear(1, 1)
```

> **주의:** 두 코드 블록은 단계 설명입니다. 실제 실행은 아래 **11절의 완전한 코드**를 기준으로 진행합니다. 이미 실행 중인 Model에 Seed를 나중에 지정해도 기존 Weight·Bias가 과거로 돌아가지는 않습니다.

---

# 10. Training Loop의 다섯 동작

학습 코드의 순서를 먼저 말로 설명할 수 있어야 합니다.

```text
① optimizer.zero_grad()             이전 Gradient 초기화
                  ↓
② prediction = model(x)             Forward로 Prediction 계산
                  ↓
③ loss = loss_function(prediction,y) Prediction과 Target 비교
                  ↓
④ loss.backward()                   Gradient 계산
                  ↓
⑤ optimizer.step()                   Parameter 갱신
                  ↓
            다음 Epoch에서 반복
```

코드로 바꾸면 다음과 같습니다.

```python
for epoch in range(1000):
    optimizer.zero_grad()
    prediction = model(x)
    loss = loss_function(prediction, y)
    loss.backward()
    optimizer.step()
```

여기서 `zero_grad()`가 왜 필요할까요? PyTorch에서는 Gradient가 누적될 수 있으므로, **현재 Step에서 계산할 Gradient가 이전 Step의 값과 의도치 않게 섞이지 않도록** 초기화합니다.

**실수하기 쉬운 차이**를 학생이 직접 말할 수 있어야 합니다.

- `model.train()`은 Model을 Training에 적합한 동작 모드로 바꿉니다. **학습 반복을 대신 실행하지 않습니다.**
- `loss.backward()`는 Gradient를 계산합니다. **Parameter를 갱신하지 않습니다.**
- `optimizer.step()`이 Optimizer의 규칙에 따라 **Parameter를 갱신**합니다.

---

# 11. 통합 실습 — Training 전후의 Parameter를 비교하기

이 교시의 **중심 실습**입니다. 앞부분의 조각 코드를 따로 이어 붙이지 말고, 다음 파일 하나로 실행합니다.

## 11.1 실습 목표와 준비

파일명: `train_linear_model.py`

준비 조건:

- Python과 PyTorch를 사용할 수 있는 실습 환경
- CPU만 있는 환경에서도 실행 가능
- 별도의 AI Model 다운로드 또는 Cloud API Key는 필요하지 않음

PyTorch 설치가 되지 않은 경우, 교육장 OS 및 Python 버전에 맞는 설치 환경을 먼저 준비해야 합니다. 이번 코드의 실행에 필요한 외부 AI 서비스는 없습니다.

## 11.2 완전한 실행 코드

```python
import torch
from torch import nn


def snapshot_parameters(model: nn.Module) -> dict[str, torch.Tensor]:
    """현재 Parameter를 독립된 값으로 복사해 둡니다."""
    return {
        name: parameter.detach().clone()
        for name, parameter in model.named_parameters()
    }


def main() -> None:
    torch.manual_seed(42)

    # 1. 이번 교시의 작은 Dataset: y = 2x
    x = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
    y = torch.tensor([[2.0], [4.0], [6.0], [8.0]])

    # 2. 학습할 Model, Loss Function, Optimizer
    model = nn.Linear(1, 1)
    loss_function = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    # 3. 학습 이전의 Parameter와 Loss를 별도로 기록
    before = snapshot_parameters(model)
    with torch.no_grad():
        initial_loss = loss_function(model(x), y).item()

    print("[Before Training]")
    print("weight:", before["weight"].item())
    print("bias  :", before["bias"].item())
    print("loss  :", initial_loss)

    # 4. Training
    model.train()
    for epoch in range(1000):
        optimizer.zero_grad()
        prediction = model(x)
        loss = loss_function(prediction, y)
        loss.backward()
        optimizer.step()

    # 5. Training 이후의 Parameter와 Loss를 확인
    after = snapshot_parameters(model)
    model.eval()
    with torch.no_grad():
        final_loss = loss_function(model(x), y).item()

    print("\n[After Training]")
    print("weight:", after["weight"].item())
    print("bias  :", after["bias"].item())
    print("loss  :", final_loss)
    print("loss decreased:", final_loss < initial_loss)

    # 6. 새로운 입력으로 Inference
    parameter_before_inference = snapshot_parameters(model)
    test_input = torch.tensor([[5.0]])
    with torch.no_grad():
        inference_result = model(test_input).item()
    parameter_after_inference = snapshot_parameters(model)

    unchanged = all(
        torch.equal(
            parameter_before_inference[name],
            parameter_after_inference[name],
        )
        for name in parameter_before_inference
    )

    print("\n[Inference]")
    print("input:", test_input.item())
    print("prediction:", inference_result)
    print("parameters unchanged:", unchanged)


if __name__ == "__main__":
    main()
```

실행:

```bash
python train_linear_model.py
```

## 11.3 실행 결과에서 꼭 볼 네 가지

1. **Before Training:** 초기 Weight·Bias와 Loss를 읽습니다.
2. **After Training:** Weight·Bias가 바뀌었고 Loss가 작아졌는지 확인합니다.
3. **Inference:** 처음 학습 데이터에 없던 `x=5`를 넣어 약 `10`에 가까운 값이 나오는지 관찰합니다.
4. **Parameter 비교:** Inference 이전과 이후의 `parameters unchanged`가 `True`인지 확인합니다.

예상되는 **결과의 의미**는 다음과 같습니다. 정확한 숫자까지 외우게 하지 않습니다.

```text
Before Training
  weight·bias: 초기값
  loss: 상대적으로 큰 값

After Training
  weight: 2에 가까워짐
  bias: 0에 가까워짐
  loss: 초기값보다 작아짐
  loss decreased: True

Inference
  input: 5
  prediction: 약 10
  parameters unchanged: True
```

수치 결과는 실행 환경에 따라 다소 달라질 수 있습니다.

**실제 실행 참고값:** 수정본 검수 환경의 PyTorch `2.10.0+cpu`에서 위 코드를 실행했을 때 `weight: 1.98099`, `bias: 0.05588`, 학습 후 Loss 약 `0.00052`, `x=5`의 Prediction 약 `9.96085`, `parameters unchanged: True`를 확인했습니다. 이는 해당 환경에서 얻은 검수 결과이지 **모든 교육장 환경의 출력값을 보장하는 정답표는 아닙니다.**

## 11.4 원본 예제에서 한 가지 개선한 점

`loss`는 Training Loop 중 **해당 Step의 Parameter 갱신 전**에 계산됩니다. 따라서 마지막 `optimizer.step()`을 실행한 **직후의 최종 Loss**를 확인하려면, 업데이트된 Model로 Loss를 다시 계산해야 합니다.

```python
model.eval()
with torch.no_grad():
    final_loss = loss_function(model(x), y).item()
```

또한 `before = model.weight`처럼 단순 참조만 저장하면 Training과 함께 값이 변하는 객체를 보게 될 수 있습니다. 따라서 위 통합 코드에서는 `detach().clone()`으로 **학습 전 Parameter의 별도 복사본**을 보존합니다.

---

# 12. Training 코드의 각 줄을 실제 변화와 연결하기

학생에게 실행 코드를 다시 보여준 뒤 아래 표를 채워 보도록 합니다.

| 코드 | 학생이 확인할 질문 | 역할 |
|---|---|---|
| `torch.manual_seed(42)` | 왜 실행할 때 초기값을 일정하게 만들까? | 난수 초기값 재현에 도움 |
| `nn.Linear(1, 1)` | 어떤 Parameter가 만들어질까? | Weight·Bias를 가진 Model 생성 |
| `nn.MSELoss()` | 무엇을 비교할까? | Prediction과 Target의 오차 측정 |
| `model.parameters()` | Optimizer는 무엇을 갱신할까? | 갱신 대상 Parameter 전달 |
| `optimizer.zero_grad()` | 왜 이전 값이 남지 않게 할까? | Gradient 초기화 |
| `model(x)` | 이 줄에서 정답을 알아냈을까? | 현재 Parameter로 Prediction 계산 |
| `loss_function(...)` | 현재 오차가 얼마인가? | Loss 계산 |
| `loss.backward()` | 이 줄에서 Weight가 변할까? | Gradient 계산 |
| `optimizer.step()` | 언제 Weight·Bias가 갱신될까? | Parameter 갱신 |
| `parameter.detach().clone()` | 초기값을 나중에도 비교할 수 있을까? | Parameter 복사본 보관 |

이 표를 처음부터 외우게 하기보다 **코드 실행 결과를 한 번 확인한 뒤에** 연결하면 됩니다.

---

# 13. `model.train()`·`model.eval()`·`torch.no_grad()` 구분

이 세 기능은 이름이 비슷하게 느껴져도 책임이 다릅니다.

| 코드 | 무엇을 바꾸는가? | 무엇을 하지 않는가? |
|---|---|---|
| `model.train()` | Model을 Training 동작 모드로 설정 | Training Loop를 자동 실행하지 않음 |
| `model.eval()` | Model을 Evaluation 동작 모드로 설정 | Inference를 자동 실행하지 않음 |
| `torch.no_grad()` | 해당 범위에서 Gradient 추적을 비활성화 | Model Mode 자체를 변경하지 않음 |

## 13.1 왜 Model Mode가 있을까?

모든 Layer가 Training과 Evaluation에서 똑같이 동작하는 것은 아닙니다. 원본 보충 설명에 등장하는 **Dropout**은 두 모드의 차이를 이해하기 위한 대표적인 사례입니다.

```text
Training Mode
  → Dropout Layer는 학습을 위해 일부 출력에 확률적 처리를 적용

Evaluation Mode
  → Dropout Layer는 해당 확률적 제거 동작을 적용하지 않음
```

이번 교시에서는 Dropout의 수학이나 정규화 기법을 배우지 않습니다. **왜 두 모드가 분리되어 있는지** 이해하면 충분합니다.

## 13.2 그럼 `eval()`만 호출하면 안전한 Inference일까?

아닙니다. `model.eval()`은 Gradient 추적을 자동으로 끄지 않습니다. 따라서 일반적인 Inference에서는 다음을 함께 사용합니다.

```python
model.eval()

with torch.no_grad():
    prediction = model(test_input)
```

또한 PyTorch에는 추론을 위한 `torch.inference_mode()`도 있습니다. 이번 교시의 실습에서는 차이를 비교하는 대신 **`torch.no_grad()`만 사용**합니다.

> **학생 확인 질문:** `model.train()`을 호출해 놓고 Training Loop를 한 번도 실행하지 않았다면 Parameter는 자동으로 학습되었을까요?
>
> **정답:** 아닙니다. Mode만 변경한 것입니다.

---

# 14. Inference에서 실제로 무엇이 변하지 않을까?

통합 실습은 `x=5`로 추론하기 전과 후에 Parameter를 복사하여 비교합니다.

```text
[Training 완료]
       ↓
Before Inference: Weight·Bias 저장
       ↓
model.eval()
       ↓
with torch.no_grad():
    model([[5.0]])
       ↓
After Inference: Weight·Bias 다시 확인
       ↓
두 복사본 비교
```

이때 **새로운 입력에 대한 Prediction은 생성**되지만, 일반적인 추론에서는 **Weight와 Bias를 다시 학습하지 않습니다.**

다음 두 표현은 서로 다릅니다.

- `Prediction이 만들어졌다`: Model이 입력을 처리했다.
- `Parameter가 갱신되었다`: Model의 학습값이 수정되었다.

이번 예제에서 Prediction이 약 `10`으로 나온다는 사실만큼 중요한 것은, **Prediction을 만드는 동안 Weight·Bias를 다시 조정하지 않았음**을 확인하는 것입니다.

---

# 15. 실습 결과가 예상과 다를 때 확인할 것

학생이 단순히 오류 메시지를 넘기지 않고, 어떤 단계의 문제인지 구분하도록 합니다.

| 관찰된 현상 | 확인할 지점 | 강사 설명 포인트 |
|---|---|---|
| `ModuleNotFoundError: torch` | PyTorch 설치 여부 | 학습 코드 실행 이전 환경 문제 |
| Shape 관련 오류 | `x.shape`, `y.shape`, `nn.Linear(1, 1)` | Tensor의 입출력 크기 불일치 가능성 |
| Training해도 값이 거의 안 바뀜 | `backward()`, `step()`, Learning Rate | Gradient 계산·갱신 단계가 존재하는지 확인 |
| Loss가 이전보다 줄지 않음 | Dataset, Loss, 학습 반복, Learning Rate | 숫자만 보지 말고 학습 과정 전체 점검 |
| 같은 코드를 재실행할 때 초기값이 달라짐 | Seed를 Model 생성 **이전**에 지정했는지 | 난수 초기화와 재현성의 관계 |
| `parameters unchanged`가 `False` | Inference 사이에 갱신 코드가 실행되었는지 | Mode 전환과 Parameter 변경은 별개의 문제 |

### 가장 먼저 볼 출력 세 가지

```text
Before Training의 weight·bias
After Training의 weight·bias
Before/After Loss
```

앞 교시의 `shape`·`dtype`·`device` 확인은 **실제로 오류가 발생했을 때 필요한 만큼만** 연결합니다. 다시 별도의 Tensor 강의를 시작하지 않습니다.

---

# 16. 학생 활동 A — 학습 단계의 순서 맞히기

다음 코드를 순서 없이 제공합니다.

```text
optimizer.step()
loss.backward()
prediction = model(x)
optimizer.zero_grad()
loss = loss_function(prediction, y)
```

학생이 올바른 순서로 배치한 다음 각 줄의 책임을 설명합니다.

**정답:**

```python
optimizer.zero_grad()
prediction = model(x)
loss = loss_function(prediction, y)
loss.backward()
optimizer.step()
```

강사 추가 질문:

> Gradient를 계산하는 줄과 실제 Parameter를 바꾸는 줄을 서로 바꾸면 올바른 학습이 될까요?
>
> 정상적인 갱신을 기대할 수 없습니다. 이번 Step의 Gradient를 계산한 뒤에 그 결과를 이용해 갱신해야 합니다.

---

# 17. 학생 활동 B — 코드 변경 전후 결과 예측하기

통합 실습의 Training Loop에서 **한 가지 줄만 변경한 뒤**, 실행 결과를 예상합니다.

| 변경 | 학생의 예상 | 확인할 결과 |
|---|---|---|
| `optimizer.step()`을 실행하지 않음 | Gradient는 계산될 수 있으나 Parameter 갱신은 수행되지 않을 것 | 학습 전후 Weight·Bias 비교 |
| `loss.backward()`를 실행하지 않음 | 필요한 Gradient가 계산되지 않아 기대한 갱신이 이루어지지 않을 것 | Parameter 변화와 Loss 확인 |
| `for epoch in range(1000)`을 `range(1)`로 변경 | 학습 기회가 줄어 충분히 맞추지 못할 수 있음 | Before/After Loss 비교 |
| Inference 부분만 두 번 실행 | 입력이 같고 Model이 변하지 않으면 이번 선형 모델의 출력도 같을 것 | 출력 및 Parameter 비교 |

주의: 코드를 바꾸어 테스트할 때는 **매번 스크립트를 처음부터 실행**합니다. 이미 학습된 Model을 그대로 사용하면 앞 실험의 영향이 남습니다.

활동의 목표는 정답 문자열을 맞히는 것이 아니라 **학습 알고리즘의 어느 단계가 빠졌는지 근거를 들어 설명하는 것**입니다.

---

# 18. 학생 활동 C — Parameter 변화 기록표

학생이 실제 실행 출력을 읽고 다음 표를 작성합니다. 비어 있는 칸에는 실행 결과를 입력합니다.

| 확인 값 | Training 전 | Training 후 | 학생 해석 |
|---|---|---|---|
| Weight | 직접 기록 | 직접 기록 | 목표값 `2`에 가까워졌는가? |
| Bias | 직접 기록 | 직접 기록 | 목표값 `0`에 가까워졌는가? |
| Loss | 직접 기록 | 직접 기록 | 감소했는가? |
| `x=5` Prediction | — | 직접 기록 | 약 `10`인가? |
| Inference 전후 Parameter | — | 변화 여부 기록 | 일반적인 추론에서 갱신이 없었는가? |

> 강사 질문: Training 전후 Python 파일 내용은 그대로인데 출력이 바뀌었다면, 실제로 달라진 것은 무엇일까요?
>
> **예상 답:** Model 내부의 학습된 Weight와 Bias입니다.

---

# 19. 수업 확인 질문과 오해 바로잡기

### Q1. Model은 Python 소스코드 한 파일과 같은 뜻인가요?

아닙니다. 이번 예제에서는 `nn.Linear`가 계산 구조를 정하고, 학습된 Weight·Bias가 그 구조에서 사용할 값을 결정합니다. **Model 구조와 Parameter를 함께 이해**해야 합니다.

### Q2. Parameter와 Hyperparameter는 무엇이 다른가요?

`weight`·`bias`는 Training을 통해 조정하는 Parameter입니다. `lr=0.01`·`epochs=1000`은 이번 실습에서 미리 지정한 학습 설정입니다.

### Q3. Loss가 줄면 Weight와 Bias가 자동으로 수정된다는 뜻인가요?

그렇지는 않습니다. Loss 계산과 Parameter 갱신은 다른 과정입니다. `backward()`로 Gradient를 계산하고 `optimizer.step()`으로 갱신해야 합니다.

### Q4. `loss.backward()`와 `optimizer.step()`은 같은 기능인가요?

아닙니다. 전자는 Gradient를 계산하고, 후자는 계산된 Gradient 등을 이용하여 Parameter를 갱신합니다.

### Q5. `model.train()`을 호출하면 1000 Epoch가 자동으로 실행되나요?

아닙니다. Model의 동작 모드만 바뀝니다. 실제 반복은 `for epoch in range(1000)`과 Training Loop가 수행합니다.

### Q6. `model.eval()`을 호출하면 Gradient 계산도 자동으로 중지되나요?

아닙니다. Model 동작 모드와 Gradient 추적 설정은 서로 다릅니다. 이번 실습에서는 `model.eval()`과 `torch.no_grad()`를 함께 사용합니다.

### Q7. Loss가 0이면 모든 새로운 데이터에서도 완벽할까요?

아닙니다. 이번처럼 단순한 관계에서는 잘 맞을 수 있지만, 실제 문제에서는 학습 데이터와 새로운 데이터의 차이를 별도로 확인해야 합니다. 이 수업은 학습 과정 관찰에 집중합니다.

### Q8. Parameter 수가 더 많으면 언제나 더 좋은 Model인가요?

아닙니다. Parameter 수는 모델 규모와 관계되지만, 모든 업무의 성능이 Parameter 개수만으로 결정되지는 않습니다. 이번 교시에서는 **Parameter가 실제로 무엇인지** 확인하는 데 집중합니다.

### Q9. Inference를 실행할 때마다 Weight와 Bias가 갱신되나요?

일반적인 Inference에서는 갱신하지 않습니다. 이번 예제에서는 추론 전후의 복사본을 직접 비교하여 확인합니다.

### Q10. 오늘 만든 `nn.Linear` 모델이 대규모 언어 모델과 똑같은 구조인가요?

아닙니다. 구조와 규모는 매우 다릅니다. 이번 교시에서는 **작은 모델에서도 Training과 Inference의 Parameter 처리 원리가 관찰된다**는 점만 연결합니다. 대규모 모델의 종류와 파일 구성은 이번 실습 범위가 아닙니다.

---

# 20. 강사 시연 진행 순서

자료를 처음 보는 학생에게는 다음 순서로 진행하면 됩니다.

1. **출발 질문:** `y=wx+b`에서 `w`와 `b`가 바뀌면 `x=2`의 결과가 어떻게 달라지는가?
2. **첫 실행:** `train_linear_model.py`의 Before Training 값을 확인한다.
3. **코드 멈춤:** `loss.backward()`와 `optimizer.step()`의 위치를 학생이 찾는다.
4. **학습 후 비교:** Weight·Bias와 Loss가 어떻게 달라졌는지 설명한다.
5. **새로운 입력:** `x=5`를 넣고 Inference 결과를 읽는다.
6. **최종 판단:** Inference 전후 Parameter가 같은지 확인한다.
7. **활동 수행:** Training Loop에서 `optimizer.step()`을 제외하고 왜 결과가 달라지는지 실험한다.

학생이 막히면 먼저 “코드가 무엇을 **계산**하는지”와 “코드가 무엇을 **변경**하는지”를 구분해서 질문합니다.

---

# 21. 이번 교시 핵심 정리

하나의 그림으로 묶으면 다음과 같습니다.

```text
        Training Data (x, y)
                 ↓
         nn.Linear Model
           weight·bias
                 ↓
             Forward
                 ↓
          Prediction
                 ↓
        Target과 비교
                 ↓
              Loss
                 ↓
      backward() → Gradient 계산
                 ↓
      step()     → Parameter 갱신
                 ↓
         여러 Epoch 반복
                 ↓
         학습된 Model
                 ↓
    새로운 입력 x=5 → Inference
                 ↓
             약 10 출력
     (일반적 추론에서는 Parameter 유지)
```

오늘 반드시 기억해야 할 문장은 다음 세 가지입니다.

1. **Training에서 달라지는 것은 이 예제의 Weight와 Bias 같은 Model Parameter입니다.**
2. **`backward()`는 Gradient 계산, `step()`은 Parameter 갱신입니다.**
3. **Inference는 학습한 Parameter를 사용해 새로운 입력의 결과를 계산하며, 일반적으로 Parameter를 다시 학습하지 않습니다.**

### 실습 완료 체크

- [ ] PyTorch Model의 `weight`, `bias`를 직접 출력했다.
- [ ] 학습 전 값을 `detach().clone()`으로 별도 보관했다.
- [ ] Loss를 학습 전후에 각각 계산해 비교했다.
- [ ] `backward()`와 `step()`의 역할을 구분했다.
- [ ] 학습 후 새로운 입력으로 Inference를 했다.
- [ ] Inference 전후 Parameter 변화가 없음을 확인했다.
- [ ] `model.train()`과 `model.eval()`의 역할을 설명했다.

---

# 22. 다음 교시 연결 — 학습된 모델을 어디에서 가져올까?

오늘은 **작은 모델을 직접 만들고 학습**시켰습니다. 그러나 실제 응용 프로그램을 만들 때마다 큰 모델을 처음부터 학습해야 하는 것은 아닙니다.

다음 교시에서는 **이미 학습된 Model을 다른 개발자도 사용할 수 있도록 제공하는 생태계**를 살펴봅니다.

> **다음 질문:** 누군가 학습한 Model을 사용하려면 어디에서 찾고, 어떤 정보를 먼저 확인해야 할까요?

Hugging Face Hub를 비롯한 배포·탐색 체계와 Model Card 읽기는 **Day 2 - 4교시**에서 다룹니다. 이 교시에서는 설명하지 않습니다.

---

# 참고자료 — 단일 원본 교육과정 내부 문서

- `Day2_03_AI_Model과_Parameter_Training과_Inference_강의용.md` — 본 교시 원문
- `Q - Day2 3교시 33..md` — `train_linear_model.py`의 단계별 설명을 제공하는 원본 보충자료
- `Q - Day2 3교시 39..md` — `model.train()`/`model.eval()`과 Dropout의 역할을 설명하는 원본 보충자료
- `Day2_02_AI의_데이터와_Tensor_NumPy와_PyTorch_강의용.md` — 선수학습 경계 확인
- `Day2_04_Pretrained_Model_생태계와_Hugging_Face_Hub_강의용.md` — 다음 교시 범위 확인

> 이 수정본은 위의 교육과정 원문 및 동일 교육과정 내부 보충자료를 기준으로 구성했습니다. 실제 교육장 PyTorch 환경과 실행 결과는 별도로 확인해야 합니다.
