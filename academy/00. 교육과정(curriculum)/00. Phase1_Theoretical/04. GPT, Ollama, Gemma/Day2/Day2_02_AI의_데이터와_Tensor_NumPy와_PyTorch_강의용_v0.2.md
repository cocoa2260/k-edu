# Day 2 - 2교시. AI의 데이터와 Tensor — NumPy와 PyTorch

## 개요 — 오늘은 숫자가 담긴 데이터의 **모양**을 살펴본다

앞 교시에서는 텍스트를 Token ID로 변환하는 과정을 확인했습니다. 이번에는 **숫자로 변환된 데이터가 어떤 구조로 저장되고, 그 구조에 따라 어떤 계산을 할 수 있는지** 살펴봅니다. Tokenizer를 다시 구현하거나 Token 분할 방식을 설명하지 않습니다.

예를 들어 다음 두 숫자 묶음을 보세요.

```text
A = [1, 2, 3]
B = [[1, 2, 3],
     [4, 5, 6]]
```

모두 숫자지만 A는 값이 한 줄로, B는 행과 열로 배치되어 있습니다. 숫자가 어떤 순서와 구조로 놓여 있는지는 AI 코드에서 매우 중요합니다. **모양(Shape)이 맞지 않으면 계산 자체가 불가능할 수 있기 때문**입니다.

이번 교시에서는 크게 세 가지를 연결합니다.

```text
숫자 데이터의 구조를 읽는다
        ↓
NumPy 배열로 수치 연산을 수행한다
        ↓
PyTorch Tensor의 Shape·dtype·Device를 확인한다
```

오늘은 모델을 학습시키지 않습니다. 다음 교시에서 다룰 Model, Parameter, Loss, Gradient의 작동 원리는 미리 설명하지 않고, **모델에 전달할 숫자 데이터의 형태를 다루는 능력**에 집중합니다.

---

# 1. 학습 목표

이번 교시를 마치면 학생은 다음을 할 수 있어야 합니다.

1. Scalar, Vector, Matrix와 다차원 Tensor의 관계를 숫자 예시로 설명한다.
2. `Dimension(차원 수)`와 `Shape(각 축의 크기)`를 구분한다.
3. 숫자로 표현된 이미지, 여러 입력의 묶음(Batch)이 어떤 Shape를 갖는지 읽는다.
4. NumPy에서 `ndarray`를 생성하고 `shape`, `ndim`, `dtype`을 확인한다.
5. NumPy에서 배열 단위 연산과 행렬 곱셈을 실행한다.
6. PyTorch의 Tensor를 만들고 `shape`, `ndim`, `dtype`, `device`를 확인한다.
7. NumPy Array와 PyTorch Tensor를 서로 변환하는 기본 방법을 사용한다.
8. CPU와 CUDA GPU의 차이를 입문 수준에서 설명하고, 사용 가능한 Device를 안전하게 선택한다.
9. Shape·dtype·Device가 맞지 않을 때 어디부터 점검할지 판단한다.

**오늘의 완료 기준:** 학생이 임의의 2차원 숫자 데이터를 보고 `(행 수, 열 수)`를 예측한 후, 실제 코드 출력과 비교하고 왜 그렇게 나오는지 말로 설명할 수 있어야 합니다.

---

# 2. AI가 계산할 때 왜 데이터의 구조가 중요한가?

사람은 사진, 음성, 텍스트, 표를 서로 다른 형태로 봅니다. AI 계산에 사용되는 데이터는 이러한 정보를 숫자로 나타낸 결과입니다.

| 원래 데이터 | 수치 표현의 예 | 이번 교시에서 확인할 부분 |
|---|---|---|
| 이미지 | Pixel(픽셀) 값의 배열 | 높이·너비·색상 채널의 크기 |
| 음성 | 시간에 따른 수치 데이터 | 숫자들이 놓인 축과 길이 |
| 표 데이터 | 행과 열의 숫자 | 몇 행·몇 열인지 |
| Token ID | 정수 ID들의 배열 | ID를 담은 자료 구조의 Shape |

여기서 다시 Token의 의미나 Text Encoding을 설명하지 않습니다. **이미 숫자가 준비되어 있다고 가정하고 그 숫자를 담는 모양과 연산**을 배웁니다.

강사 질문: "숫자 6개만 있다면 컴퓨터가 자동으로 2행 3열인지, 3행 2열인지 알까요?" 숫자의 **개수**만으로는 배치를 결정할 수 없습니다. 코드에 배열의 구조가 주어져야 합니다.

---

# 3. Scalar·Vector·Matrix·Tensor를 구분하자

## 3.1 Scalar — 숫자 한 개

```text
5
```

Scalar(스칼라)는 하나의 수치 값입니다. 예를 들어 온도 `25.3`, 확률 `0.91`처럼 값 하나만 필요한 경우를 생각하면 됩니다.

## 3.2 Vector — 숫자가 한 축으로 나열된 구조

```text
[32, 12, 45000]
```

한 고객의 나이·구매 횟수·평균 구매 금액을 숫자로 표현한 예시입니다. 값 세 개가 하나의 축을 따라 놓여 있으므로 입문 수준에서는 **1차원 Vector(벡터)**로 이해합니다. 값의 단위가 서로 다르더라도, 지금은 배열에 몇 개의 숫자가 들어 있는지에만 주목합니다.

## 3.3 Matrix — 숫자를 행과 열로 배치한 구조

```text
[
  [32, 12, 45000],
  [25,  3, 18000],
  [41, 20, 72000]
]
```

세 고객의 값을 각각 한 행에 놓으면 **3행 3열 Matrix(행렬)**가 됩니다. 첫 번째 행은 첫 고객, 두 번째 행은 두 번째 고객의 값입니다. 행과 열은 구분된 두 축입니다.

## 3.4 Tensor — 여러 차원의 수치 데이터를 다루는 구조

PyTorch에서 Tensor는 숫자를 여러 차원으로 담고 연산할 수 있는 핵심 자료 구조입니다. 입문 단계에서는 다음처럼 구분하면 충분합니다.

| 수치 데이터의 모습 | 차원 수 | 예 |
|---|---:|---|
| Scalar | 0 | `5` |
| Vector | 1 | `[1, 2, 3]` |
| Matrix | 2 | `[[1, 2], [3, 4]]` |
| 더 높은 차원의 배열 | 3 이상 | `2 × 2 × 2` 크기의 수치 배열 |

**헷갈리기 쉬운 점:** Tensor가 반드시 3차원 이상이어야 하는 것은 아닙니다. PyTorch에서는 숫자 하나를 담은 0차원 Tensor도, 벡터에 해당하는 1차원 Tensor도 만들 수 있습니다. 또한 Tensor를 새로운 학습 알고리즘이나 특정 AI 모델의 이름으로 생각하면 안 됩니다.

---

# 4. Dimension과 Shape — 축의 개수와 각 축의 길이

이름이 비슷하지만 서로 다른 질문에 답합니다.

- **Dimension(차원 수, `ndim`)**: 축이 몇 개인가?
- **Shape(형상, `shape`)**: 각 축에는 값이 몇 개씩 배치되어 있는가?

다음 예시를 비교해 봅시다.

```text
A = 5
B = [1, 2, 3]
C = [[1, 2, 3],
     [4, 5, 6]]
D = [
      [[1, 2], [3, 4]],
      [[5, 6], [7, 8]]
    ]
```

| 데이터 | 차원 수 | Shape | Shape 읽기 |
|---|---:|---|---|
| A | 0 | `()` | 축이 없는 값 하나 |
| B | 1 | `(3,)` | 길이 3인 축 하나 |
| C | 2 | `(2, 3)` | 행 2개, 각 행의 값 3개 |
| D | 3 | `(2, 2, 2)` | 크기 2인 축이 세 개 |

특히 `B`의 `(3,)`은 **값이 세 개이지만 차원은 1개**라는 뜻입니다. 반대로 `C`의 `(2, 3)`에 숫자 두 개가 적혀 있는 것은 차원 수가 2개이기 때문입니다.

강사 시연: 종이에 `[[1, 2, 3], [4, 5, 6]]`을 쓰고 바깥쪽 목록의 길이를 먼저 세게 합니다. 바깥쪽에 행이 2개 있고, 각 행에 값이 3개 있으므로 `(2, 3)`입니다. 출력한 값 6개를 보면서 `(6,)`이라고 답하는 학생이 있다면 **값의 총개수와 데이터의 Shape는 다르다**는 점을 확인시킵니다.

---

# 5. 이미지와 Tensor의 모양

이미지도 계산에 사용하는 순간 수치 데이터의 배치 문제가 생깁니다. 색상 이미지 한 장을 간단히 생각하면 다음 세 축을 사용해 표현할 수 있습니다.

```text
Height × Width × Channels
```

원본 강의의 예시처럼 높이와 너비가 각각 224이고 색상 채널이 3개라면, 다음 Shape로 나타낼 수 있습니다.

```text
(224, 224, 3)
```

다만 모든 소프트웨어가 축의 순서를 동일하게 쓰지는 않습니다. 같은 크기의 이미지라도 다음처럼 채널을 먼저 놓는 형태가 가능합니다.

```text
(3, 224, 224)
```

두 배열은 숫자의 종류가 같더라도 **축의 순서가 다릅니다.** 모델이나 함수가 기대하는 Shape를 확인하지 않은 채 넣으면 계산 오류가 발생하거나 잘못된 축을 기준으로 처리할 수 있습니다.

여기서는 색상 채널의 세부 처리 방식이나 이미지 모델 내부 구조를 배우지 않습니다. 지금 필요한 판단은 "데이터가 같은 이미지라고 해서 배열의 Shape까지 항상 같은가?"라는 질문에 **아니라고 답할 수 있는 것**입니다.

---

# 6. Batch — 여러 입력을 하나의 데이터 묶음으로 만들기

**Batch(배치)**는 여러 개의 데이터 항목을 한 번에 처리하도록 묶은 것입니다. 모델이 처리할 입력 한 개를 `Sample(샘플)`이라고 부를 때, Sample 두 개를 하나로 묶으면 Batch Size는 2입니다.

다음은 각 Sample이 `2 × 3`의 모양을 갖는 간단한 숫자 데이터입니다.

```text
Sample A             Sample B
[ [1, 2, 3],         [ [7, 8, 9],
  [4, 5, 6] ]           [10, 11, 12] ]
```

이 두 Sample을 하나로 묶으면:

```text
[
  [[1, 2, 3], [4, 5, 6]],
  [[7, 8, 9], [10, 11, 12]]
]
```

Shape는 `(2, 2, 3)`입니다. 첫 번째 `2`는 Sample이 2개라는 뜻이고, 뒤의 `(2, 3)`은 각 Sample의 구조입니다.

```text
(2, 2, 3)
 ↑  └──┬──┘
Batch   Sample 하나의 Shape
```

**중요:** Batch는 곧바로 학습(Training)을 의미하지 않습니다. 여러 입력을 묶어서 처리하는 데이터 구성 방법입니다. 학습 과정에서 Batch를 어떻게 반복해서 사용하는지는 이후 교시에서 다룹니다.

---

# 7. NumPy — 숫자 배열을 직접 만들어 보자

NumPy는 Python에서 다차원 수치 배열과 수치 계산을 다루기 위한 라이브러리입니다. 핵심 자료 구조의 이름은 `ndarray`입니다. Day1에서 NumPy가 어떤 도구인지 배웠다면, **이번에는 배열의 Shape·차원·자료형을 실제 값으로 확인하는 것**이 새로운 학습입니다.

가상환경을 활성화한 뒤 NumPy를 설치합니다.

```bash
python -m pip install numpy
```

첫 실행은 다음과 같습니다.

```python
import numpy as np

readings = np.array([
    [1, 2, 3],
    [4, 5, 6],
])

print("배열:")
print(readings)
print("자료 구조:", type(readings))
print("Shape:", readings.shape)
print("Dimension:", readings.ndim)
print("원소 수:", readings.size)
```

예상 핵심 결과:

```text
Shape: (2, 3)
Dimension: 2
원소 수: 6
```

여기서 꼭 구분해야 할 값은 다음과 같습니다.

| 확인 방법 | 확인하는 것 | 위 예제 결과 |
|---|---|---|
| `readings.shape` | 각 축의 크기 | `(2, 3)` |
| `readings.ndim` | 축의 개수 | `2` |
| `readings.size` | 전체 원소 개수 | `6` |

`size == 6`이라고 해서 Shape가 `(6,)`이라는 뜻은 아닙니다. 이 점을 실제 코드 출력과 연결해서 확인합니다.

---

# 8. dtype — 숫자에도 자료형이 있다

숫자로 이루어진 배열이라고 해서 모두 같은 방식으로 저장되는 것은 아닙니다. **`dtype`(data type)**은 배열의 원소가 어떤 수치 자료형으로 표현되는지 알려줍니다.

다음 두 NumPy 배열을 비교해 봅시다.

```python
import numpy as np

integers = np.array([1, 2, 3], dtype=np.int32)
floats = np.array([1.0, 2.0, 3.0], dtype=np.float32)

print("정수:", integers.dtype)
print("실수:", floats.dtype)
print("정수 Shape:", integers.shape)
print("실수 Shape:", floats.shape)
```

둘 다 Shape는 `(3,)`입니다. 하지만 정수와 실수를 표현하는 자료형은 다릅니다. **Shape는 모양, dtype은 저장되는 숫자의 종류**를 말합니다.

원본 강의에서 dtype과 메모리의 관계도 소개했습니다. 다음 코드는 같은 값 개수를 서로 다른 부동소수점 자료형으로 저장할 때 배열의 크기가 어떻게 달라지는지 직접 확인합니다.

```python
import numpy as np

small = np.array([1.0, 2.0, 3.0], dtype=np.float32)
large = np.array([1.0, 2.0, 3.0], dtype=np.float64)

print("float32 bytes:", small.nbytes)
print("float64 bytes:", large.nbytes)
```

예상 결과:

```text
float32 bytes: 12
float64 bytes: 24
```

같은 숫자 세 개도 자료형에 따라 저장 공간이 다릅니다. 다만 **메모리를 적게 사용한다는 이유만으로 특정 dtype이 항상 더 좋다고 말할 수는 없습니다.** 필요한 정밀도와 실행 환경도 고려해야 합니다. 대규모 모델의 Parameter 메모리나 Quantization을 계산하는 내용은 이번 교시에서 미리 배우지 않습니다.

---

# 9. Vectorized Operation — 배열을 하나씩 반복하지 않고 계산하기

NumPy는 배열의 각 원소에 연산을 적용할 수 있습니다. 이것을 **Vectorized Operation(배열 단위 연산)**이라고 합니다.

일반 Python 목록에 있는 값을 각각 두 배로 만들려면 다음처럼 반복문을 사용할 수 있습니다.

```python
numbers = [1, 2, 3]
result = []

for number in numbers:
    result.append(number * 2)

print(result)
```

결과는 `[2, 4, 6]`입니다. 같은 계산을 NumPy에서는 다음처럼 표현할 수 있습니다.

```python
import numpy as np

numbers = np.array([1, 2, 3])
result = numbers * 2

print(result)
```

출력은 `[2 4 6]` 형태입니다. 여기서 NumPy가 특별한 판단을 하는 것이 아닙니다. **`* 2`라는 명확한 연산을 배열의 값들에 적용하는 것**입니다.

이제 새로운 실습으로 확장합니다. 앞에서 사용한 **2행 3열 배열** 전체에 10을 더해 보세요.

```python
import numpy as np

readings = np.array([
    [1, 2, 3],
    [4, 5, 6],
])

adjusted = readings + 10

print(adjusted)
print("원본 Shape:", readings.shape)
print("결과 Shape:", adjusted.shape)
```

예상 출력:

```text
[[11 12 13]
 [14 15 16]]
원본 Shape: (2, 3)
결과 Shape: (2, 3)
```

배열의 **값**은 바뀌었지만 배열의 **모양**은 그대로라는 점을 확인합니다. 학생에게 "`readings + 10`은 Shape를 바꾸는 코드인가?"라고 물으면 이번 교시의 핵심과 연결됩니다.

---

# 10. Matrix Multiplication — Shape가 계산 가능성을 결정한다

숫자 배열에서는 원소별 계산 외에 행렬 곱셈을 수행할 수 있습니다. NumPy에서 `@` 기호는 행렬 곱셈에 사용할 수 있습니다.

```python
import numpy as np

a = np.array([
    [1, 2],
    [3, 4],
])

b = np.array([
    [5, 6],
    [7, 8],
])

result = a @ b

print(result)
print("Shape:", result.shape)
```

실행 결과:

```text
[[19 22]
 [43 50]]
Shape: (2, 2)
```

행렬 곱셈에서는 첫 행렬의 **열 크기**와 두 번째 행렬의 **행 크기**가 맞아야 합니다. 이번 시간에는 곱셈 공식을 전개해 암기하지 않고 **계산에 필요한 Shape 조건**만 확인합니다.

```text
가능한 예: (2, 3) @ (3, 2) → (2, 2)

불가능한 예: (2, 3) @ (2, 2) → 축 크기가 맞지 않음
```

같은 숫자 배열이라도 모양이 다르면 기대했던 계산을 할 수 없다는 점이 중요합니다. 실제로 오류가 발생하면 뒤의 디버깅 활동에서 Shape를 비교해 원인을 찾습니다.

---

# 11. PyTorch — Tensor를 만들고 정보를 확인하기

PyTorch는 NumPy처럼 숫자 데이터를 다룰 수 있지만, Deep Learning에 필요한 다른 기능도 제공하는 Framework입니다. Day1에서는 이 **도구의 위치**를 배웠습니다. 이번에는 **Tensor를 생성하고 실제 값을 검사**합니다.

PyTorch 설치는 운영체제와 CPU/GPU 환경에 따라 달라질 수 있습니다. 이 문서에서는 특정 설치 명령이 모든 교육장 환경에서 동일하게 동작한다고 단정하지 않습니다. 강사가 교육장 환경에서 검증한 PyTorch 설치 방법을 제공한 다음 진행합니다.

```python
import torch

readings = torch.tensor([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
])

print("Tensor:")
print(readings)
print("자료 구조:", type(readings))
print("Shape:", readings.shape)
print("Dimension:", readings.ndim)
print("dtype:", readings.dtype)
print("Device:", readings.device)
```

CPU의 기본 실행 환경에서 예상하는 핵심 결과:

```text
Shape: torch.Size([2, 3])
Dimension: 2
dtype: torch.float32
Device: cpu
```

여기서 `torch.Size([2, 3])`과 NumPy의 `(2, 3)`은 **같은 축 크기**를 표현합니다. `ndim`은 둘 다 `2`입니다.

**코드 해설:** `torch.tensor(...)`로 Tensor를 만들고, `.shape`·`.ndim`·`.dtype`·`.device`로 서로 다른 정보를 읽습니다. 단순히 화면에 숫자를 출력하는 것과 **AI 계산에 사용할 데이터의 조건을 점검하는 것**은 다른 작업입니다.

---

# 12. NumPy ndarray와 PyTorch Tensor를 비교하자

두 도구는 같은 숫자를 다룰 수 있지만, 서로 다른 라이브러리의 자료 구조입니다.

| 비교 | NumPy | PyTorch |
|---|---|---|
| 대표 자료 구조 | `ndarray` | `Tensor` |
| Shape 확인 | `.shape` | `.shape` |
| 차원 수 확인 | `.ndim` | `.ndim` 또는 `.dim()` |
| 자료형 확인 | `.dtype` | `.dtype` |
| Device 확인 | 이번 NumPy 실습의 핵심 대상 아님 | `.device` |
| 수업의 핵심 기능 | 범용 수치 계산·배열 연산 | Tensor 처리 및 계산 장치 연결 |

중요한 차이는 **라이브러리 이름이 다르다**는 사실 자체가 아닙니다. 같은 숫자 배열을 만들더라도 어떤 기능을 활용하고 어떤 형식으로 주고받는지 확인해야 한다는 것입니다.

예를 들어 다음 코드는 동일한 수치 데이터를 NumPy와 PyTorch에서 각각 생성해 비교합니다.

```python
import numpy as np
import torch

values = [
    [1.0, 2.0],
    [3.0, 4.0],
]

array = np.array(values)
tensor = torch.tensor(values)

print("NumPy:", array.shape, array.dtype)
print("PyTorch:", tensor.shape, tensor.dtype, tensor.device)
```

기본 환경에서는 NumPy가 `float64`, PyTorch가 `float32`로 출력될 수 있습니다. **같은 값을 넣었다고 기본 dtype까지 반드시 같지는 않다는 것**을 확인하는 것이 목적입니다. 실제 차이를 비교할 때는 라이브러리의 기본값과 별도 dtype 지정 여부를 함께 살펴봅니다.

---

# 13. NumPy와 PyTorch 사이에서 데이터 변환하기

원본 강의의 중요한 실습 중 하나는 NumPy Array를 PyTorch Tensor로, 다시 Tensor를 NumPy Array로 바꾸는 과정입니다.

```python
import numpy as np
import torch

array = np.array([1.0, 2.0, 3.0])
tensor = torch.from_numpy(array)
restored = tensor.numpy()

print("원본 타입:", type(array))
print("Tensor 타입:", type(tensor))
print("되돌린 타입:", type(restored))
print("Shape:", array.shape, tensor.shape, restored.shape)
```

예상하는 관찰 결과는 다음과 같습니다.

```text
원본 타입: <class 'numpy.ndarray'>
Tensor 타입: <class 'torch.Tensor'>
되돌린 타입: <class 'numpy.ndarray'>
Shape: (3,) torch.Size([3]) (3,)
```

변환을 했다는 이유만으로 값의 배열이 자동으로 바뀌는 것은 아닙니다. 위 코드에서는 **자료 구조의 종류를 바꾸면서도 원소 세 개의 배열 모양을 유지**합니다.

여기서 `tensor.numpy()`는 **CPU Tensor**를 대상으로 사용합니다. GPU 등 다른 Device에 있는 Tensor는 CPU 쪽으로 옮기는 절차가 필요할 수 있습니다. 복잡한 Model Parameter를 변환하거나 Gradient를 관리하는 방법까지 이번 교시에서 진행하지는 않습니다.

---

# 14. Device — Tensor는 어디에서 계산되는가?

PyTorch의 Tensor에는 `device`라는 속성이 있습니다. **Device(계산 장치)**는 Tensor가 어느 장치에 놓여 계산되는지 나타냅니다.

이번 원문에 등장하는 대표 장치는 다음 둘입니다.

- **CPU:** 컴퓨터의 범용 계산 장치입니다. 작은 수치 실습은 CPU에서도 할 수 있습니다.
- **CUDA GPU:** 지원되는 NVIDIA GPU 환경에서 사용하는 계산 장치입니다. 많은 병렬 수치 연산을 처리하는 데 강점이 있습니다.

모든 학생의 컴퓨터가 CUDA GPU를 사용할 수 있는 것은 아닙니다. 따라서 **GPU가 없는 학생도 실패 없이 따라 할 수 있게** Device를 선택합니다.

```python
import torch

selected = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

values = torch.tensor([1.0, 2.0, 3.0], device=selected)

print("CUDA 사용 가능:", torch.cuda.is_available())
print("선택한 Device:", selected)
print("Tensor Device:", values.device)
```

CPU 환경이라면 다음과 비슷하게 출력됩니다.

```text
CUDA 사용 가능: False
선택한 Device: cpu
Tensor Device: cpu
```

**학생 확인 질문:** "GPU를 선택하지 못하면 Tensor를 생성할 수 없을까요?" 아닙니다. 이 예제는 CPU에서도 실행됩니다. 다만 실제로 어떤 장치를 선택할지는 **수치 연산의 크기, 장치 지원, 데이터 이동과 메모리 조건** 등을 고려해야 합니다. GPU라고 모든 연산이 자동으로 더 빨라지는 것은 아닙니다.

---

# 15. RAM·VRAM과 dtype을 연결해 보자

수치 데이터는 저장 공간을 사용합니다. 원본 강의에서 소개한 메모리 용어를 간단히 구분해 봅니다.

| 용어 | 입문 수준의 의미 |
|---|---|
| RAM | CPU 중심 실행에서 사용되는 시스템 메모리 |
| VRAM | GPU가 사용하는 메모리 |
| dtype | 숫자 한 개를 어떤 형태로 저장하는지 결정하는 정보 |

배열이 커지거나 더 많은 숫자를 저장하면 필요한 메모리도 커질 수 있습니다. 또한 동일한 원소 개수라도 `float32`와 `float64`처럼 자료형이 다르면 저장하는 바이트 수가 달라집니다.

오늘은 **어느 장치에 데이터가 있고, 어떤 자료형인지** 확인하는 데까지만 배웁니다. 몇십억 개 Parameter를 가진 모델의 메모리를 추정하거나 Quantization을 적용하는 방법은 이후 교시에서 학습합니다.

또한 CPU와 GPU에서의 실행 속도는 연산 규모·데이터 이동·하드웨어 특성에 따라 달라집니다. 이번에는 벤치마크로 속도 우열을 결론 내리지 않습니다.

---

# 16. Shape 오류를 통해 디버깅 순서 익히기

**Debugging(디버깅)**은 프로그램이 예상대로 작동하지 않는 원인을 찾는 과정입니다. Tensor를 사용하는 코드에서는 숫자 값보다 **Shape, dtype, device**를 먼저 확인하면 원인 파악에 도움이 되는 경우가 많습니다.

다음 배열 두 개를 보세요.

```python
import numpy as np

a = np.array([
    [1, 2, 3],
    [4, 5, 6],
])

b = np.array([
    [7, 8],
    [9, 10],
])

print("a:", a.shape)
print("b:", b.shape)

try:
    print(a @ b)
except ValueError:
    print("행렬 곱셈 불가: 서로 맞물리는 축의 크기가 다릅니다.")
```

`a.shape`는 `(2, 3)`, `b.shape`는 `(2, 2)`입니다. 행렬 곱셈에서 가운데 축의 크기가 `3`과 `2`로 일치하지 않아 오류가 납니다.

**확인 순서**는 다음처럼 정리할 수 있습니다.

1. **Shape 확인:** 몇 차원이며 각 축의 크기가 얼마인가?
2. **dtype 확인:** 이 연산에 사용할 수 있는 숫자 자료형인가?
3. **Device 확인:** PyTorch Tensor를 사용할 경우 예상한 장치에 있는가?

PyTorch에서도 다음 세 줄은 기본적인 점검 방법입니다.

```python
print(tensor.shape)
print(tensor.dtype)
print(tensor.device)
```

이 코드는 기존에 생성한 `tensor` 변수를 대상으로 실행해야 합니다. **독립 파일에 세 줄만 복사하면 `tensor` 변수가 없어 실행되지 않는다는 점**을 강사가 알려 줍니다. 다음 통합 예제에는 변수 생성과 출력 코드를 함께 넣었습니다.

---

# 17. 통합 실습 A — `tensor_basics.py`

여기서는 2차원 Tensor를 만들고 핵심 정보를 한 번에 출력합니다. 아래 코드 전체를 `tensor_basics.py`로 저장한 뒤 실행합니다.

```python
import torch


def main() -> None:
    tensor = torch.tensor([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
    ])

    print("Tensor:")
    print(tensor)
    print("Shape:", tensor.shape)
    print("Dimension:", tensor.ndim)
    print("dtype:", tensor.dtype)
    print("Device:", tensor.device)


if __name__ == "__main__":
    main()
```

```bash
python tensor_basics.py
```

예상 핵심 출력:

```text
Shape: torch.Size([2, 3])
Dimension: 2
dtype: torch.float32
Device: cpu
```

예상 출력의 `cpu`는 **CPU에서 실행했을 때**의 예시입니다. GPU에서 실행하도록 직접 Device를 설정했다면 달라질 수 있습니다.

**수업에서 확인할 질문:** `Dimension`이 2이기 때문에 Shape의 숫자가 `(2, 3)`인 것일까요? 두 값의 관계는 단순히 "둘 다 2가 들어 있다"가 아닙니다. **Shape에 기록된 축이 두 개**이기 때문에 Dimension이 2입니다.

---

# 18. 통합 실습 B — `numpy_vs_torch.py`

두 번째 실습에서는 동일한 수치 데이터를 서로 다른 라이브러리로 생성합니다.

```python
import numpy as np
import torch


def main() -> None:
    values = [
        [1.0, 2.0],
        [3.0, 4.0],
    ]

    array = np.array(values)
    tensor = torch.tensor(values)

    print("[NumPy]")
    print(array)
    print("Shape:", array.shape)
    print("dtype:", array.dtype)

    print()

    print("[PyTorch]")
    print(tensor)
    print("Shape:", tensor.shape)
    print("dtype:", tensor.dtype)
    print("Device:", tensor.device)


if __name__ == "__main__":
    main()
```

```bash
python numpy_vs_torch.py
```

실행 전에 학생이 먼저 표를 채우게 합니다.

| 질문 | 예상할 것 |
|---|---|
| 두 자료 구조의 전체 원소 개수는? | 각각 4개 |
| NumPy Shape는? | `(2, 2)` |
| PyTorch Shape는? | `torch.Size([2, 2])` |
| NumPy와 PyTorch의 dtype 표시도 반드시 같은가? | 아니요. 기본 dtype이 다를 수 있습니다. |

실행 후 예상과 실제 출력이 같았는지 확인하고, **값의 개수·Shape·자료형은 각각 다른 속성**이라는 점을 말하게 합니다.

---

# 19. 학생 활동 — 값을 보기 전에 Shape를 먼저 예측하기

## 활동 A. Shape와 Dimension 맞히기

다음 세 코드가 어떤 Shape를 만드는지 실행 전에 예상합니다.

```python
import torch

a = torch.tensor([1, 2, 3])
b = torch.tensor([[1, 2, 3], [4, 5, 6]])
c = torch.zeros(4, 10, 768)

print("A:", a.shape, a.ndim)
print("B:", b.shape, b.ndim)
print("C:", c.shape, c.ndim)
```

예상 답:

| 변수 | Shape | Dimension |
|---|---|---:|
| `a` | `(3,)` | 1 |
| `b` | `(2, 3)` | 2 |
| `c` | `(4, 10, 768)` | 3 |

`c`의 세 축은 서로 다른 크기를 가진다는 사실만 확인합니다. 이 숫자들을 Model의 Hidden Size나 Transformer 내부 차원과 연결해 자세히 설명하는 것은 이번 교시의 범위를 벗어납니다.

## 활동 B. dtype 바꾸기

다음 코드를 실행한 뒤 자료형만 바꿔 다시 실행합니다.

```python
import torch

values = torch.tensor([1, 2, 3], dtype=torch.float32)
print(values)
print(values.dtype)

changed = values.to(dtype=torch.float64)
print(changed)
print(changed.dtype)
```

두 Tensor는 같은 개수의 값을 가지고 있습니다. **Shape가 바뀌었는가, dtype이 바뀌었는가?** 답은 dtype만 바뀌었다는 것입니다.

## 활동 C. Device 확인하기

14절의 Device 선택 코드를 직접 실행합니다. CUDA를 사용할 수 없으면 `cpu`가 출력되는 것이 정상입니다. 이를 실습 실패로 취급하지 않습니다.

## 활동 D. Shape가 맞지 않는 이유 설명하기

16절의 행렬 곱셈 코드를 실행하고, 다음 중 왜 오류가 발생하는지 설명합니다.

- 숫자 값이 너무 커서 발생했는가?
- 행렬의 Shape가 서로 맞지 않아서 발생했는가?
- GPU가 없기 때문에 발생했는가?

**답:** `(2, 3) @ (2, 2)`에서 가운데 축의 크기가 서로 다르기 때문입니다. 오류를 해결하려면 기대하는 입력 배열의 구조를 먼저 확인해야 합니다.

---

# 20. 수업 확인 질문과 자주 발생하는 오해

**Q1. Tensor는 무조건 3차원 이상의 데이터인가요?**  
아닙니다. PyTorch에서는 0차원부터 여러 차원의 Tensor를 다룰 수 있습니다.

**Q2. `(2, 3)`과 `(3, 2)`는 값이 모두 6개이니 같은 Shape인가요?**  
아닙니다. 원소 수는 같아도 행과 열의 배치가 다릅니다.

**Q3. `shape`, `ndim`, `dtype`은 모두 모양을 뜻하나요?**  
아닙니다. 순서대로 각 축의 크기, 축의 개수, 원소의 숫자 자료형입니다.

**Q4. NumPy와 PyTorch는 같은 라이브러리인가요?**  
아닙니다. NumPy의 대표 자료 구조는 `ndarray`, PyTorch의 대표 자료 구조는 `Tensor`입니다. 두 도구에서 숫자 배열을 만들고 변환할 수 있지만 각각의 역할이 다릅니다.

**Q5. CPU만 있으면 이번 Tensor 실습이 불가능한가요?**  
아닙니다. 제시한 기본 Tensor 생성·Shape·dtype 실습은 CPU에서 실행할 수 있습니다.

**Q6. Model에 숫자를 넣기 전에 어떤 정보를 확인하면 좋나요?**  
먼저 Shape·dtype·Device를 확인해야 합니다. 특히 Model이 기대하는 배열 구조와 실제 값의 Shape가 다르면 문제가 발생할 수 있습니다.

### 강사 확인 활동

학생에게 아래 숫자를 보여 줍니다.

```text
[[1, 2, 3],
 [4, 5, 6]]
```

질문은 세 개만 합니다. "총 숫자는 몇 개일까요?", "축은 몇 개일까요?", "Shape는 무엇일까요?" 답은 각각 **6개**, **2개**, **`(2, 3)`**입니다. 세 답이 서로 다른 정보임을 설명할 수 있으면 이번 교시의 핵심 목표를 달성한 것입니다.

---

# 21. 이번 교시 핵심 정리

오늘은 모델의 내부 구조를 배운 것이 아니라, **모델이 사용할 수치 데이터의 형태를 실제 Python 코드로 확인**했습니다.

```text
숫자 데이터
    ↓
Scalar / Vector / Matrix / 다차원 Tensor
    ↓
Shape와 Dimension으로 구조 확인
    ↓
NumPy ndarray / PyTorch Tensor
    ↓
dtype·Device 확인
    ↓
필요한 수치 연산에 사용
```

꼭 기억할 사항은 다음 네 가지입니다.

1. **Shape는 숫자 배열의 각 축 크기를 나타냅니다.** 데이터의 총개수만 알아서는 Shape를 알 수 없습니다.
2. **dtype은 숫자 자료형을, Device는 계산 장치를 나타냅니다.** 둘 다 Shape와는 다릅니다.
3. **NumPy와 PyTorch는 모두 수치 데이터를 다룰 수 있지만, 자료 구조와 사용 목적은 다릅니다.**
4. **AI 코드에서 계산이 실패하면 Shape·dtype·Device를 먼저 살펴보는 습관이 중요합니다.**

### 오늘의 최종 점검

- [ ] Scalar·Vector·Matrix를 차원 수로 구분할 수 있다.
- [ ] 2차원과 3차원 배열의 Shape를 직접 예상할 수 있다.
- [ ] NumPy의 `shape`, `ndim`, `dtype`을 읽을 수 있다.
- [ ] PyTorch의 `shape`, `dtype`, `device`를 읽을 수 있다.
- [ ] 배열 단위 연산과 행렬 곱셈을 실행했다.
- [ ] NumPy Array와 PyTorch Tensor의 변환을 확인했다.
- [ ] CPU 환경에서 Tensor 예제가 정상 실행되는지 확인했다.
- [ ] Shape 불일치가 어떤 오류를 만드는지 설명할 수 있다.

---

# 22. 다음 교시 연결 — Tensor 다음에는 무엇을 배울까?

앞 교시에서는 **텍스트를 숫자로 바꾸는 입구**를 배웠습니다. 이번 교시에서는 **숫자를 담고 계산하는 자료 구조**를 살펴봤습니다.

```text
Day 2 — 1교시: Text → Token IDs
                 ↓
Day 2 — 2교시: 숫자 배열의 Shape·dtype·Device
                 ↓
Day 2 — 3교시: 이러한 데이터를 처리하는 Model과 학습·추론의 작동
```

다음 시간의 핵심 질문은 다음과 같습니다.

> **숫자 데이터를 사용하는 Model은 무엇으로 구성되어 있으며, 학습 과정에서 무엇이 달라질까요?**

Parameter·Loss·Gradient·Optimizer의 동작과 학습 코드는 **다음 교시에서 처음부터 자세히 학습**합니다. 오늘 강의의 실습에는 해당 계산을 포함하지 않았습니다.

---

# 참고자료 — 단일 원본 강의에 포함된 목록

- NumPy 공식 문서
- PyTorch 공식 문서
- PyTorch Tutorials — Tensors
- PyTorch Tutorials — Automatic Differentiation (후속 교시 관련)
- Hugging Face Transformers 공식 문서 (앞 교시·후속 연결용)

> 이 목록은 원본 교육과정 강의에 기재된 참고자료 이름을 보존한 것입니다. 이번 편집에서 외부 문서나 다른 ZIP 내용을 교육자료 수정의 추가 근거로 사용하지 않았습니다.
