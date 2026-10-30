# Day 2 - 5교시. Transformers로 Pre-trained Model 직접 실행하기

## 개요 — 선택한 모델을 Python에서 처음으로 실행한다

4교시에서는 Hugging Face Hub의 Model Repository를 읽고, Task·License·Language·실행 환경을 기준으로 사용할 모델 후보를 판단했습니다. 이번에는 그 결과로 선정한 **Text Generation용 Pre-trained Model**을 Python에서 불러와 직접 실행합니다.

앞에서 각각 다뤘던 Tokenizer, Tensor, Model Parameter, Inference의 **정의를 다시 설명하지 않습니다.** 실제 코드의 입출력을 따라가며 이 요소들이 어디에서 만나고 어떤 값을 주고받는지 확인합니다.

```text
선정한 Model ID
    ├── AutoTokenizer.from_pretrained() → Tokenizer 객체
    └── AutoModelForCausalLM.from_pretrained() → Model 객체

입력 문자열
    ↓ Tokenizer 실행
input_ids / attention_mask 등 (PyTorch Tensor)
    ↓ model.generate()
입력과 생성 결과를 포함하는 Token ID Tensor
    ↓ 새로 생성된 ID 구간 분리
Tokenizer.decode()
    ↓
생성된 Text
```

이번 수업의 핵심 질문은 다음 세 가지입니다.

1. `from_pretrained()`로 생성되는 객체는 무엇이며, **다운로드와 메모리 로드**는 어떻게 구별되는가?
2. `model.generate()`에 넣는 데이터와 반환받는 데이터는 어떤 형태인가?
3. 반환된 Token ID에서 **사용자가 제공한 입력과 새로 생성된 부분**을 어떻게 나누는가?

> **이번 교시의 범위:** 하나의 Python 프로그램 안에서 모델을 직접 로드하고 생성 결과를 확인합니다. 별도 Model Server, Runtime, Serving 구조, Ollama 실행 및 HTTP API 연동은 다음 교시들에서 다룹니다.

---

# 1. 학습 목표와 완료 기준

학생은 다음 작업을 수행할 수 있어야 합니다.

1. 4교시에서 선정한 **실제 Model ID**와 사용 환경을 준비한다.
2. `AutoTokenizer.from_pretrained()`로 호환되는 Tokenizer를 로드한다.
3. `AutoModelForCausalLM.from_pretrained()`로 사전학습된 Text Generation Model을 로드한다.
4. `tokenizer(text, return_tensors="pt")`의 반환값에서 `input_ids`와 필요시 `attention_mask`를 확인한다.
5. Model과 Input Tensor가 동일한 계산 Device에 있는지 확인한다.
6. `model.eval()`과 `torch.inference_mode()`를 사용해 Inference를 수행한다.
7. `generate()`가 반환하는 **Token ID Tensor**와 이를 Decode한 문자열을 구분한다.
8. 전체 Sequence와 새로 생성된 부분을 별도로 출력한다.
9. `max_new_tokens`, `do_sample` 설정 변경에 따른 관찰 결과를 기록한다.
10. 다운로드·캐시·메모리 로드 및 주요 오류를 실제 실행 단계와 연결해 설명한다.

**실습 완료 판정:** 모델을 실행한 뒤 *Input IDs / Input Shape / Output IDs / New Token IDs / Generated Text*를 출력하고, 각 값이 무엇을 뜻하는지 설명합니다. 단순히 문장 한 줄이 출력되었다는 것만으로 완료하지 않습니다.

---

# 2. 수업 시작 전에 확인할 것 — 4교시 결과 활용

이번 실습은 모델 탐색을 다시 시작하지 않습니다. **4교시에서 선정한 후보**가 있다는 전제에서 출발합니다. Model Card를 다시 처음부터 읽는 대신 실행과 직접 관련 있는 내용을 확인합니다.

| 확인 항목 | 이번 코드에 미치는 영향 | 미확정 시 처리 |
|---|---|---|
| 정확한 Model ID | Tokenizer와 Model을 같은 저장소에서 로드 | 강사가 확정하기 전 실행하지 않음 |
| Task: Text Generation | `AutoModelForCausalLM`과의 적합성 | 다른 Task Model은 이 실습에서 제외 |
| Transformers 사용 가능 여부 | `from_pretrained()` 지원 여부 | 공식 사용 예제가 다르면 모델 또는 코드 재검토 |
| 공개·접근 조건 | 다운로드 및 인증 가능 여부 | Gated/Private 조건 확인 |
| 라이선스 | 교육 및 이후 사용 가능 범위 | 라이선스 확인 전 배포하지 않음 |
| 모델 크기·필요 메모리 | 실제 RAM/VRAM에서 로드 가능 여부 | 작은 검증 모델로 변경하거나 환경 준비 |
| Tokenizer 및 Prompt 안내 | 입력 문자열 및 Chat Template 형식 | 해당 모델의 사용 예제를 우선 확인 |

실습에 필요한 조건은 **크기가 작고, Model Card와 사용 예제가 있으며, 일반 Python/Transformers 환경에서 Text Generation을 할 수 있는 모델**입니다. CPU에서도 실행 가능한 수준으로 선택하면 실습실 하드웨어 차이를 줄일 수 있습니다.

원문에서 모델을 특정 ID로 고정하지 않은 이유도 여기에 있습니다. 교육장 환경이나 모델 접근 조건을 확인하지 않고 특정 모델을 강제로 정하면 다운로드 실패, 메모리 부족, 잘못된 Task 선택이 발생할 수 있습니다.

이번 파일도 **검증되지 않은 모델 ID를 임의로 확정하지 않습니다.** 실행 코드에서는 강사가 선택한 ID를 환경 변수 `CLASS_MODEL_ID`로 전달합니다. 이 값이 비어 있으면 잘못된 ID로 다운로드를 시도하는 대신 명확한 안내를 출력합니다.

> **강사 준비 사항:** 4교시 선정 기록에서 실습 모델 ID·Revision·실행 가능 환경을 확정하고, 실습 전에 최소 1회 다운로드와 생성 결과를 실제로 검증해야 합니다. 이 검증 전에는 모델 실행 성공을 보장할 수 없습니다.

---

# 3. 실습 환경과 파일 구조

권장 준비 사항:

```text
Python과 Virtual Environment
PyTorch (torch)
Hugging Face Transformers (transformers)
모델 최초 다운로드가 가능한 Internet Connection
저장 공간 및 모델 실행에 충분한 RAM
강사가 확인한 Model ID / Model Card
```

이 교시는 CPU에서 실행 가능한 작은 모델을 기본 대상으로 설계합니다. GPU 활용을 필수로 하지 않습니다. 하드웨어에 따른 별도 설치 명령이나 최적화는 강사가 실제 환경에서 검증한 결과를 사용합니다.

프로젝트 예:

```text
day2_transformers/
├── .venv/
├── basic_generation.py
├── compare_prompts.py
└── requirements.txt
```

이미 가상환경이 있다면 활성화하고, 필요한 라이브러리를 설치합니다.

```bash
python -m pip install torch transformers
```

버전 확인:

```bash
python -m pip show torch
python -m pip show transformers
```

수업용 `requirements.txt`에는 **교육장 실습에서 실제 확인한 버전**을 기록합니다. 다음은 양식 예시일 뿐, 그대로 설치할 수 있는 버전 지정이 아닙니다.

```text
torch==<검증한 버전>
transformers==<검증한 버전>
```

실행 환경별로 PyTorch 설치 방식이 달라질 수 있고, Transformers의 지원 Model Class 및 API도 버전에 따라 달라질 수 있습니다. 따라서 강사는 검증된 환경을 배포해야 합니다.

**Model ID 설정 — macOS/Linux 터미널:**

```bash
export CLASS_MODEL_ID="강사가_검증한_실제_Model_ID"
```

**Model ID 설정 — Windows PowerShell:**

```powershell
$env:CLASS_MODEL_ID="강사가_검증한_실제_Model_ID"
```

위 문자열은 **자리표시자**입니다. 문자 그대로 실행하면 실습이 성공하지 않습니다. 정확한 Repository ID를 강사가 대입해야 합니다.

학생이 모델 이름을 바꿔 실습할 경우에도 같은 Task와 실행 환경 조건을 충족하는지 먼저 확인합니다. **이 교시에서는 모델을 비교 선정하는 활동을 다시 하지 않습니다.**

---

# 4. Python에서 Tokenizer와 Model 객체 준비하기

## 4.1 `AutoTokenizer` — 직접 클래스 이름을 고르지 않는다

원문의 첫 번째 로딩 단계는 다음과 같습니다.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
```

`AutoTokenizer`는 주어진 Model ID나 로컬 경로의 설정을 참고해 적절한 Tokenizer Class를 선택하는 인터페이스입니다. 1교시에서 Tokenizer의 내부 역할은 이미 공부했으므로, 여기서는 **객체를 실제 프로그램에서 어떻게 확보하는가**를 확인합니다.

학생은 다음 사항을 관찰합니다.

- `MODEL_ID`는 앞 교시에서 확인한 Repository를 식별한다.
- `from_pretrained()`가 필요한 파일을 찾아 Tokenizer 객체를 준비한다.
- `type(tokenizer)`를 출력하면 실제 선택된 Class가 나타날 수 있다.
- 모델마다 Tokenizer Class나 입력 필드는 다를 수 있다.

## 4.2 `AutoModelForCausalLM` — Text Generation에 맞는 Model Class

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
```

`AutoModel` 계열에는 여러 목적의 Class가 있습니다. 이번에는 **앞선 문자열에 이어질 Token을 생성하는 Causal Language Model**이므로 `AutoModelForCausalLM`을 사용합니다.

여기서 별도의 분류 모델이나 Embedding 모델을 함께 로드하지 않습니다. 해당 모델은 Task가 다르기 때문입니다.

```text
AutoTokenizer.from_pretrained(ID)
→ Text를 Model Input으로 만들 Tokenizer 객체

AutoModelForCausalLM.from_pretrained(ID)
→ Text Generation을 수행할 Model 객체
```

`type(model)` 또는 `print(model)`로 로드된 객체를 확인할 수 있습니다. 다만 `print(model)`은 매우 긴 Layer 정보를 출력할 수 있으므로, 강사는 **전체 Layer를 강의 중 모두 해석하지 않습니다.** 이번 학습의 목적은 Model 내부 설계 분석이 아니라 *직접 실행*입니다.

### `from_pretrained()`에서 오해하기 쉬운 점

이 메서드의 역할은 이미 저장된 Tokenizer나 Model 자원을 찾아 **불러오는 것**입니다. 이름에 `pretrained`가 들어 있어도 함수 호출만으로 Training이 시작되는 것은 아닙니다.

처음 실행할 때는 다음 두 작업이 연속해서 일어날 수 있습니다.

```text
저장소에서 필요한 파일 확보 (Download / Cache)
    ↓
해당 파일로 Python 객체를 구성하고 메모리에 로드 (Load)
```

두 작업은 같지 않습니다. 다운로드한 파일이 로컬 Storage에 남아 있어도 Python 실행을 종료하면 메모리에 로드된 객체는 유지되지 않을 수 있습니다. 이후 실행에서는 조건이 맞으면 Cache를 재사용하여 파일 다운로드 없이 **메모리 로드**부터 진행할 수 있습니다.

---

# 5. 입력 문자열을 Model Input으로 만들기

원문의 실습 입력 문자열을 그대로 사용합니다.

```python
text = "Artificial intelligence is useful."
```

```python
inputs = tokenizer(text, return_tensors="pt")
```

`return_tensors="pt"`의 `pt`는 PyTorch를 뜻합니다. Tokenizer가 Model에 전달할 입력을 PyTorch Tensor 형태로 준비하도록 요청하는 것입니다.

이번에는 Token을 어떻게 나누는지 다시 강의하는 대신, **메서드를 실행한 뒤 반환된 자료 구조**를 확인합니다.

```python
print("Tokenizer:", type(tokenizer))
print("Tokens:", tokenizer.tokenize(text))
print("Input keys:", list(inputs.keys()))
print("Input IDs:", inputs["input_ids"])
print("Input shape:", inputs["input_ids"].shape)
```

대표적인 입력 필드:

| 필드 | 이번 실습에서 확인하는 내용 |
|---|---|
| `input_ids` | Model에 전달할 Token ID Tensor |
| `attention_mask` | 제공되는 경우 실제 입력·Padding 위치 구분에 사용되는 정보 |

모든 모델이 동일한 키를 반드시 반환하는 것은 아닙니다. `attention_mask`를 확인할 때는 다음처럼 작성할 수 있습니다.

```python
mask = inputs.get("attention_mask")
print("Attention mask:", mask)
```

개념적인 `input_ids` 출력은 다음과 같은 모습입니다.

```text
tensor([[..., ..., ..., ...]])
```

예를 들어 Shape가 `torch.Size([1, 7])`이라면 1개의 입력 Sequence가 7개의 Token ID로 표현되었다는 뜻입니다. **`7`은 예시 값**이며 실제 Token 수는 선택한 Tokenizer와 입력 내용에 따라 달라집니다.

이미 1교시에서 Token과 ID의 차이, 2교시에서 Tensor Shape를 배웠습니다. 따라서 이번 질문은 **“Token이 무엇인가?”**가 아니라 **“Tokenizer 결과 중 어느 값을 `generate()`에 전달해야 하는가?”**입니다.

---

# 6. Model과 입력 Tensor가 같은 Device에 있어야 한다

2교시에서 Tensor의 `device`를 확인했습니다. 이제 그 개념을 실제 Model 호출에 적용합니다.

CPU 실습 환경에서는 다음처럼 계산 Device를 명시할 수 있습니다.

```python
import torch

device = torch.device("cpu")
model = model.to(device)
inputs = {
    key: value.to(device)
    for key, value in inputs.items()
}
```

GPU 실습을 사용한다면 실제 하드웨어 및 Model 지원 여부가 검증된 환경에서 다음과 같이 선택할 수 있습니다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
```

이 코드만으로 모든 GPU 환경이나 큰 모델 실행을 보장하는 것은 아닙니다. 지금은 다음 원칙만 기억합니다.

> **Model의 Parameter Tensor와 `input_ids` 등의 Input Tensor는 호환되는 계산 Device에 있어야 합니다.**

확인 코드:

```python
print("Model device:", next(model.parameters()).device)
print("Input device:", inputs["input_ids"].device)
```

입문용 작은 모델을 기준으로 작성한 예제입니다. 하나의 GPU에 들어가지 않는 대형 모델, 여러 Device에 나누어 로드되는 모델, 특수한 양자화·오프로딩 설정 등은 이 교시에서 구현하지 않습니다.

### Model Parameter 수 확인 — 이미 배운 개념을 실제 Model에 적용

3교시에서는 `nn.Linear(1, 1)`의 `weight`와 `bias`를 보았습니다. 여기서는 실제로 불러온 Pre-trained Model의 Parameter 수를 **출력으로 확인만** 합니다.

```python
parameter_count = sum(
    parameter.numel() for parameter in model.parameters()
)
print("Parameter count:", f"{parameter_count:,}")
```

`numel()`은 Tensor 원소 수를 반환합니다. 실제 숫자는 선택한 모델에 따라 달라집니다. 이 결과를 모델 카드의 표기와 비교할 수 있지만, 표기·Counting 기준이 다를 가능성도 있으므로 **숫자가 조금 다르다는 이유만으로 바로 오류라고 단정하지 않습니다.**

이번 교시에서 Weight·Bias를 직접 업데이트하거나 학습시키지는 않습니다.

---

# 7. 생성 전 설정 — `eval()`과 `inference_mode()`

이미 Day2 3교시에서 `model.train()`, `model.eval()`, `torch.no_grad()`를 구분했습니다. 이번에는 해당 원리를 다시 길게 설명하지 않고, 실제 생성 코드에 적용합니다.

```python
model.eval()

with torch.inference_mode():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=30,
        do_sample=False,
    )
```

여기에는 세 가지 중요한 부분이 있습니다.

1. **`model.eval()`** — 일부 Layer가 Evaluation 상황에 맞게 동작하도록 Mode를 변경합니다.
2. **`torch.inference_mode()`** — 이번처럼 Gradient 기반 학습이 필요 없는 추론에서 사용할 수 있는 Context입니다.
3. **`model.generate(...)`** — 입력 Sequence를 바탕으로 새 Token ID들을 생성합니다.

`eval()` 호출만으로 Gradient 추적이 자동으로 완전히 꺼지는 것은 아닙니다. 또한 `inference_mode()`를 사용했다고 해서 Model의 학습된 Parameter를 새로 만드는 것은 아닙니다.

## 7.1 `**inputs`는 무엇인가?

Tokenizer 결과는 Dictionary처럼 Key와 Value를 가진 자료 구조입니다. 예를 들어 다음과 같을 수 있습니다.

```python
{
    "input_ids": ...,
    "attention_mask": ...,
}
```

`model.generate(**inputs)`는 Dictionary에 들어 있는 Key/Value들을 같은 이름의 Keyword Argument로 풀어 전달합니다. 이는 대략 다음 호출과 대응됩니다.

```python
model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_new_tokens=30,
)
```

다만 두 번째 예시는 실제로 `attention_mask`가 존재하는 경우의 설명입니다. 공통 실행 코드에서는 해당 키가 없는 모델도 고려하여 `**inputs` 형태를 사용합니다.

## 7.2 `max_new_tokens=30`

새로 생성할 Token 수의 상한을 지정합니다. **30글자 또는 30단어를 뜻하지 않습니다.** 입력 토큰 수와는 별도로 관리합니다. 모델이 종료를 나타내는 Token을 먼저 생성하면 지정한 수보다 적은 Token을 반환할 수도 있습니다.

## 7.3 `do_sample=False`

Sampling을 사용하지 않는 생성 설정입니다. 이번 첫 실습에서는 결과를 관찰하기 쉽게 하기 위해 사용합니다. 같은 설정이라도 실행 환경과 라이브러리 차이에 따라 완전한 재현성이 무조건 보장되는 것은 아니므로, 학생에게 동일한 문자열이 반드시 출력된다고 안내하지 않습니다.

Sampling·Temperature·Top-k·Top-p의 상세 동작 및 비교 실험은 이번 실습 목표가 아닙니다. 이 교시에서는 **설정이 Model의 생성 동작에 영향을 준다**는 범위에서만 확인합니다.

---

# 8. `generate()`의 반환값은 문자열이 아니다

생성 결과를 먼저 출력합니다.

```python
print("Output IDs:", output_ids)
print("Output shape:", output_ids.shape)
```

현재와 같은 **Causal Language Model의 일반적인 기본 호출**에서는 `generate()`가 Sequence를 담은 Token ID Tensor를 반환할 수 있습니다. 선택한 옵션에 따라 다른 반환 구조를 사용할 수도 있지만, 여기서는 원문의 기본 예제를 사용합니다.

```text
입력한 문자열
    ↓ Tokenizer
Input IDs Tensor
    ↓ Model.generate()
Output IDs Tensor
    ↓ Tokenizer.decode()
Text
```

반환값을 텍스트처럼 `print(output_ids)`했을 때 숫자로 보인다는 사실이 중요합니다. 사람에게 보여줄 문장을 얻으려면 Decode가 필요합니다.

```python
generated_text = tokenizer.decode(
    output_ids[0],
    skip_special_tokens=True,
)
print("Full generated text:", generated_text)
```

`skip_special_tokens=True`는 지원되는 특수 Token을 디코딩 결과에서 표시하지 않도록 처리합니다. 정확한 결과는 Model/Tokenizer별로 달라질 수 있습니다.

여기까지 실행하면 결과가 나옵니다. 그러나 교육 관점에서는 한 가지가 더 남았습니다. **이 문자열에서 학생이 넣은 입력과 모델이 새로 생성한 부분을 어떻게 구분할까요?**

---

# 9. 입력 Prompt와 새로 생성된 Token 구간 분리

이번 교시에서 가장 중요한 코드 해석 부분입니다.

Causal Language Model의 기본 `generate()` 결과에는 입력 Token ID 뒤에 새로 생성된 ID들이 이어지는 형태가 나타날 수 있습니다.

```text
Input IDs       : [10, 20, 30]
New Token IDs   : [40, 50]
Output IDs      : [10, 20, 30, 40, 50]
```

위 숫자는 설명을 위한 가상 값입니다. 이를 그대로 Decode하면 **입력 Prompt까지 함께 출력**될 수 있습니다.

따라서 다음 순서로 구분합니다.

```python
input_length = inputs["input_ids"].shape[1]
new_token_ids = output_ids[0][input_length:]

generated_only = tokenizer.decode(
    new_token_ids,
    skip_special_tokens=True,
)

print("New token IDs:", new_token_ids)
print("Generated only:", generated_only)
```

`shape[1]`은 이 예제처럼 `[Batch, Sequence Length]` 구조에서 현재 입력 Sequence의 길이입니다. `output_ids[0]`는 첫 번째 입력에 대한 반환 Sequence이고, `[input_length:]`는 입력 이후의 새 Token ID 부분만 가져옵니다.

학생에게 다음을 구분해서 설명하게 합니다.

| 값 | 무엇을 담는가? | 사람에게 바로 보여줄 문장인가? |
|---|---|---|
| `inputs["input_ids"]` | 사용자가 입력한 문자열의 Token ID | 아니요 |
| `output_ids[0]` | 입력과 생성 결과를 포함한 ID Sequence | 아니요 |
| `new_token_ids` | 모델이 새로 생성한 부분의 ID | 아니요 |
| `generated_text` | 전체 Sequence를 Decode한 Text | 상황에 따라 Prompt 포함 |
| `generated_only` | 새로 생성된 부분만 Decode한 Text | 생성 결과만 보여줄 때 사용 |

이 구분은 단순 출력 문법이 아니라 **Model의 입력과 출력이 어떻게 연결되는지**를 이해하는 핵심입니다.

---

# 10. 완전한 실행 코드 — `basic_generation.py`

앞서 나눠 확인한 코드를 하나의 파일로 합칩니다. 원본의 전체 실행 흐름을 유지하되, 실습 환경에 지정된 모델 ID를 받고, 각 단계의 결과를 한 번에 비교할 수 있도록 보강했습니다.

```python
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    model_id = os.environ.get("CLASS_MODEL_ID", "").strip()
    if not model_id or model_id == "강사가_검증한_실제_Model_ID":
        raise RuntimeError(
            "실행할 실제 Model ID가 없습니다. "
            "강사가 확인한 CLASS_MODEL_ID를 설정하세요."
        )

    print("[1. Model ID]")
    print(model_id)

    print("\n[2. Load Tokenizer]")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    print(type(tokenizer))

    print("\n[3. Load Model]")
    model = AutoModelForCausalLM.from_pretrained(model_id)
    device = torch.device("cpu")
    model = model.to(device)
    model.eval()
    print(type(model))
    print("Model device:", next(model.parameters()).device)

    parameter_count = sum(p.numel() for p in model.parameters())
    print("Parameters:", f"{parameter_count:,}")

    print("\n[4. Prepare Input]")
    text = "Artificial intelligence is useful."
    inputs = tokenizer(text, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    print("Input text:", text)
    print("Tokens:", tokenizer.tokenize(text))
    print("Input keys:", list(inputs.keys()))
    print("Input IDs:", inputs["input_ids"])
    print("Input Shape:", inputs["input_ids"].shape)
    print("Attention Mask:", inputs.get("attention_mask"))

    print("\n[5. Generate]")
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=False,
        )

    print("Output IDs:", output_ids)
    print("Output Shape:", output_ids.shape)

    print("\n[6. Decode]")
    full_text = tokenizer.decode(
        output_ids[0],
        skip_special_tokens=True,
    )
    input_length = inputs["input_ids"].shape[1]
    new_token_ids = output_ids[0][input_length:]
    generated_only = tokenizer.decode(
        new_token_ids,
        skip_special_tokens=True,
    )

    print("New token IDs:", new_token_ids)
    print("Full text:", full_text)
    print("Generated only:", generated_only)


if __name__ == "__main__":
    main()
```

실행:

```bash
python basic_generation.py
```

**주의:** 원문의 `MODEL_ID = "수업에서_검증한_Model_ID"`와 마찬가지로, 이 코드도 강사가 실제 Model ID를 지정하고 호환 모델을 준비해야 완료됩니다. `CLASS_MODEL_ID` 환경 변수만 설정한다고 다운로드와 모델 호환성이 보장되는 것은 아닙니다.

## 10.1 실행하며 관찰할 순서

1. **Model ID**가 교육장 공통 값인지 확인합니다.
2. Tokenizer와 Model **Class 이름**이 실제로 출력되는지 확인합니다.
3. Input IDs의 Shape가 `[1, Sequence Length]`인지 살펴봅니다.
4. `generate()` 반환값이 **숫자 ID Tensor**인지 확인합니다.
5. `Full text`에는 입력 문자열도 포함될 수 있다는 것을 확인합니다.
6. `Generated only`가 새로 생성된 부분임을 확인합니다.

### 예시 출력 형식

```text
[1. Model ID]
(강사가 지정한 실제 모델 ID)

[4. Prepare Input]
Input text: Artificial intelligence is useful.
Input IDs: tensor([[..., ..., ...]])
Input Shape: torch.Size([1, ...])

[5. Generate]
Output IDs: tensor([[..., ..., ..., ...]])
Output Shape: torch.Size([1, ...])

[6. Decode]
New token IDs: tensor([...])
Full text: (입력 문자열과 생성 부분을 포함할 수 있는 Text)
Generated only: (새로 생성된 Text)
```

이 출력은 **형태 설명을 위한 예시**입니다. 실제 모델 실행 결과를 기록한 로그가 아닙니다. 정확한 Token ID·Shape·생성 문장은 선택한 모델과 환경에서 확인해야 합니다.

---

# 11. 코드를 읽는 순서 — 데이터가 바뀌는 지점 표시하기

학생은 전체 프로그램을 다음과 같이 설명할 수 있어야 합니다.

| 코드 | 데이터 또는 상태의 변화 | 주의할 점 |
|---|---|---|
| `AutoTokenizer.from_pretrained(model_id)` | Tokenizer 객체 준비 | 모델 설정과 호환되어야 함 |
| `AutoModelForCausalLM.from_pretrained(model_id)` | 학습된 Model 객체 준비 | Training이 아님 |
| `model.to(device)` | Model을 계산 Device로 이동 | 충분한 메모리 필요 |
| `tokenizer(text, return_tensors="pt")` | 문자열에서 Tensor 입력 생성 | `input_ids` 포함 여부 확인 |
| `model.eval()` | Evaluation 동작 Mode 설정 | Gradient 추적 제어와 다름 |
| `with torch.inference_mode()` | 추론을 위한 계산 Context 적용 | Parameter 학습 과정이 아님 |
| `model.generate(**inputs, ...)` | 생성된 Token ID Sequence 얻음 | 문자열을 곧바로 반환하는 예제가 아님 |
| `output_ids[0][input_length:]` | 새로 생성된 ID만 분리 | 입력 부분을 함께 출력하지 않기 위함 |
| `tokenizer.decode(...)` | ID Sequence를 Text로 변환 | 특수 Token 표시 방식은 설정에 영향 받음 |

**강사 질문:** `full_text`와 `generated_only`가 다른 이유는 무엇입니까?

**답변:** Causal Language Model의 기본 생성 결과에는 입력 Sequence가 이어 붙어 있을 수 있기 때문입니다. 따라서 입력 길이를 기준으로 새로 생성된 부분을 분리하면 결과만 확인할 수 있습니다.

**강사 질문:** `from_pretrained()`를 두 번 호출하는 이유는 무엇입니까?

**답변:** 각각 Tokenizer 객체와 Model 객체를 준비하기 때문입니다. **같은 Model ID를 사용해 호환되는 구성**을 불러오는 것이 핵심입니다.

---

# 12. 생성 조건 하나씩 바꿔서 실험하기

실습에서는 모델을 다시 학습시키지 않고 **기존 Model에 전달하는 Input 및 Generation 설정**만 변경합니다. 가능한 한 같은 모델을 메모리에 로드한 상태에서 반복 실행하면 모델 다운로드·로드 시간을 반복할 필요가 없습니다.

## 12.1 Input 변경

원문에서 제시한 세 입력을 순서대로 사용합니다.

```text
Artificial intelligence is
Machine learning is
A language model is
```

각 입력을 Tokenizer에 넣어 `Input Shape`와 `Generated only`를 기록합니다. 같은 Model을 사용해도 **입력 Sequence가 달라지므로 생성 결과가 달라질 수 있음**을 확인합니다.

| Input | Input Token 수 | New Token 수 | 생성된 문장 특징 |
|---|---|---|---|
| Artificial intelligence is | 실습 후 기록 | 실습 후 기록 | 실습 후 기록 |
| Machine learning is | 실습 후 기록 | 실습 후 기록 | 실습 후 기록 |
| A language model is | 실습 후 기록 | 실습 후 기록 | 실습 후 기록 |

여기서는 Token이 무엇인지 다시 토론하는 것이 아니라, **입력 길이가 달라지는 모습을 실행 결과로 확인**하는 활동입니다.

## 12.2 생성 길이 상한 변경

같은 입력을 유지하면서 `max_new_tokens`를 변경합니다.

```python
max_new_tokens=10
```

```python
max_new_tokens=30
```

```python
max_new_tokens=50
```

관찰할 항목:

- 실제 생성된 ID 길이가 설정값보다 작을 수 있는가?
- `max_new_tokens`를 키워도 반드시 해당 개수만큼 생성되는가?
- 출력된 문자열 길이가 Token 수와 일치하는가?

**해설:** 이 값은 새로 생성할 Token의 상한입니다. EOS 등 종료 조건에 따라 일찍 끝날 수도 있습니다. 글자 수와 Token 수는 동일하지 않습니다.

## 12.3 결정적 생성 설정 관찰

```python
with torch.inference_mode():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=30,
        do_sample=False,
    )
```

`do_sample=False`는 Sampling 없이 생성하도록 요청하는 설정입니다. 같은 Model·Input·환경에서 관찰한 결과를 비교해봅니다. 반복해서 동일 문자열이 나오더라도 이를 모든 Model과 모든 Hardware에서 완전한 결정성이 보장된다는 뜻으로 설명하지 않습니다.

Sampling을 켜는 실습은 강사가 Model Card와 호환 가능한 Generation 설정을 확인한 경우에만 **선택 활동**으로 수행합니다. Temperature, Top-k, Top-p의 수학적 의미나 최적화 기법은 여기에서 강의하지 않습니다.

---

# 13. Chat Model을 사용할 때의 입력 형식 주의

위의 기본 실습은 단일 Text Prompt를 처리하는 **Causal Language Model**을 기준으로 합니다. 하지만 모델이 Instruction/Chat 용도로 추가 학습되었다면 권장 입력 형식이 다를 수 있습니다.

원문에 있는 다음 구조를 생각해봅시다.

```python
messages = [
    {
        "role": "user",
        "content": "AI가 무엇인지 설명해줘.",
    }
]
```

Chat Model의 경우 Model Card에 제시된 **Chat Template**을 통해 이 대화 구조를 모델이 기대하는 형식으로 변환해야 할 수 있습니다. 지원되는 Tokenizer에서는 다음과 같은 인터페이스를 만날 수 있습니다.

```python
formatted = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)
```

여기서 `tokenize=False`는 문자열 형태로 형식화된 결과를 요청하는 예이고, 실제 모델 입력은 그 후 별도로 Tokenize해야 할 수 있습니다. Tokenizer가 Chat Template을 지원하는지, 어떤 역할 이름과 종료 Token을 쓰는지는 **모델별 안내**에 따라 달라집니다.

이번 시간에 모든 Chat Model의 Template을 직접 구현하지는 않습니다. 학생이 알아야 하는 것은 두 가지입니다.

1. **단순 문자열 입력과 Chat 메시지 형식은 항상 교환 가능한 것이 아니다.**
2. **실제 선택한 Model Card의 공식 사용 예제가 우선이다.**

`apply_chat_template()`가 제공되지 않는 모델에서 강제로 호출하면 안 됩니다. 강사가 이번 실습에 Text Generation용 Model을 선택했다면 본문의 `basic_generation.py`를 먼저 완료한 뒤 이 부분을 보충 설명합니다.

---

# 14. `pipeline`은 왜 이번 핵심 실습에서 사용하지 않는가?

Transformers에는 Tokenization, Model 실행, 후처리를 편리하게 묶어 사용할 수 있는 `pipeline` 인터페이스가 있습니다.

```python
from transformers import pipeline
```

하지만 이번 교시의 학습 목표는 **`Tokenizer → Tensor → Generate → Decode`가 어디서 실행되는지 확인하는 것**입니다. 처음부터 하나의 고수준 함수만 사용하면 학생이 중간 결과를 직접 관찰하기 어렵습니다.

```text
직접 작성하는 실습
입력 → Tokenizer → Input Tensor → Model.generate() → Output Tensor → Decode

고수준 편의 인터페이스
입력 → pipeline(...) → 출력
```

따라서 먼저 단계별 코드를 익히고, 실행 흐름을 이해한 뒤에 편의 인터페이스의 존재를 알면 충분합니다. `pipeline`의 모든 설정과 Task별 사용 예제를 별도 강의로 확장하지 않습니다.

---

# 15. Download, Cache, Memory Load를 실제로 관찰하기

4교시에서 Repository 파일의 종류를 읽었으므로, 이번에는 실행할 때 해당 파일이 **어떤 단계에서 사용되는지** 살펴봅니다.

```text
처음 실행
Model ID 확인
    ↓
필요한 파일 다운로드(기존 Cache가 없을 때)
    ↓
Local Cache / Storage
    ↓
Python Model·Tokenizer 객체 생성 및 Memory Load
    ↓
Generation
```

다음 실행에서는 동일한 파일이 Cache에 있고 사용 가능한 상태라면 **다운로드 없이 로드**할 수 있습니다.

```text
재실행
Local Cache 확인
    ↓
Tokenizer·Model 객체 다시 로드
    ↓
Generation
```

**실습 방법:** 첫 번째 실행과 동일한 파일을 두 번째로 실행하며 다운로드 메시지, 실행까지의 시간, 모델 로드 과정을 비교합니다. 단, Cache가 이미 있는 환경에서는 첫 번째 실행 때도 다운로드가 나타나지 않을 수 있습니다.

확인 질문:

- 다운로드가 없었다면 **모델이 처음부터 Python 메모리에 올라가 있었다**는 뜻인가?
- Python 프로그램을 종료한 뒤 같은 모델을 다시 실행하면 **파일 다운로드**와 **메모리 로드** 중 어느 단계를 다시 수행하는가?
- 모델이 작은 파일이라도 실행 시 필요한 Memory가 파일 크기와 정확히 같다고 단정할 수 있는가?

정리: **Storage의 Cache와 실행 중인 Python 프로세스의 메모리는 다릅니다.** 모델 로딩 과정에서 추가 메모리가 사용될 수 있습니다. 여기서는 사실을 확인하는 데 집중하고, 별도 Server 프로세스에서 Model을 지속적으로 관리하는 개념은 다음 교시로 넘깁니다.

---

# 16. 실패했을 때 원인을 실행 단계별로 찾기

실습에서 오류가 발생하면 처음부터 모든 코드를 다시 작성하기보다 **실패한 단계**를 먼저 분류합니다.

| 오류가 생긴 단계 | 관찰할 현상 | 먼저 확인할 것 |
|---|---|---|
| Model ID / 저장소 | Repository를 찾을 수 없다는 메시지 | Model ID 철자, 저장소 존재, 접근 조건 |
| 다운로드 / Network | 연결 실패 또는 파일을 받지 못함 | Internet, 저장 공간, Cache 상태 |
| 인증 / Gated Model | 접근 권한 또는 인증 오류 | Model Card의 접근 조건, 승인·로그인 여부 |
| Tokenizer 로드 | Tokenizer Class·설정 관련 오류 | Model과 Tokenizer의 호환성, 문서의 사용 예제 |
| Model 로드 | Memory 부족, 지원되지 않는 Model Class | Task 적합성, 설치 버전, 메모리 요구량 |
| Device 준비 | CPU/GPU Device가 달라 발생하는 오류 | Model Parameter와 Input Tensor 위치 |
| Generation | 입력 Key, 생성 옵션, 길이 제약 관련 오류 | `inputs` 내용, `generate()` 옵션, Model 설정 |
| Decode | 예상과 다른 특수 Token·출력 형식 | `skip_special_tokens`, Model 안내, 결과 ID |

원문에서 지적한 주요 문제인 Model ID·Network·Authentication·Memory·Device·Tokenizer 오류를 실제 실행 순서에 대응시켰습니다.

예를 들어 `MODEL_ID` 철자가 틀렸다면 Tokenizer/Model 로딩에서 실패할 수 있습니다. 이 상황을 `generate()` 설정 문제로 해결하려고 하면 원인과 해결 방식이 맞지 않습니다.

또한 큰 모델이 GPU 메모리에 들어가지 않는 문제를 해결하기 위한 Quantization·Device Mapping·Multi-GPU 설정은 이 교시의 실습 범위가 아닙니다. 이 수업에서는 **검증된 작은 모델과 CPU 실행 경로**를 우선 사용합니다.

### 안전한 실습 운영

- Hugging Face 접근용 토큰이 필요하면 인증 정보는 Source Code에 기록하지 않습니다.
- Model Card에 안내된 사용 조건·권한을 확인한 저장소만 사용합니다.
- 알 수 없는 저장소의 임의 코드를 무조건 신뢰하여 실행하지 않습니다.
- 모델 파일이나 메모리가 부족하면 임의 옵션을 여러 개 붙이기보다 강사가 검증한 더 작은 모델로 변경합니다.

---

# 17. 학생 활동 — 관찰·예측·설명

## 활동 1. 각 출력의 의미 표시하기

`basic_generation.py`의 다음 출력을 캡처하거나 기록합니다.

```python
print(inputs["input_ids"])
print(inputs["input_ids"].shape)
print(output_ids)
print(new_token_ids)
print(generated_only)
```

각 줄 옆에 **Input Token IDs / Shape / Output Token IDs / New Token IDs / Decoded Text** 중 하나를 적습니다. 또한 Tokenizer 객체, Model 객체는 위 목록 중 어느 값과도 다른 **실행 객체**라는 점을 설명합니다.

## 활동 2. 입력별 결과 비교

세 문장을 한 모델에 넣어 Input Token 수와 새로 생성된 문장을 비교합니다.

```text
Artificial intelligence is
Machine learning is
A language model is
```

이번 활동의 정답은 특정 문장을 생성하는 것이 아닙니다. **같은 로드된 모델에서도 입력에 따라 생성 결과가 달라질 수 있고, 생성 결과가 Token ID 형태를 거쳐 Text로 변환된다는 사실**을 기록하면 됩니다.

## 활동 3. 출력 길이 설정 비교

`max_new_tokens=10`, `30`, `50`으로 변경하여 실제 생성된 Token ID 개수를 기록합니다.

```text
설정값: 10  → 실제 생성 수: ______
설정값: 30  → 실제 생성 수: ______
설정값: 50  → 실제 생성 수: ______
```

세 숫자가 항상 설정값과 같을 필요는 없습니다. Model이 먼저 종료했을 수 있기 때문입니다.

## 활동 4. Parameter 확인

로드한 모델에 대해 다음 코드를 실행합니다.

```python
parameter_count = sum(
    p.numel() for p in model.parameters()
)
print(f"{parameter_count:,}")
```

다음 질문에 답합니다. **이 모델의 Parameter를 세기 위해 다시 Training했는가?** 아닙니다. 이미 로드한 Model 객체의 Parameter Tensor 원소 수를 계산한 것입니다.

## 활동 5. Cache 관찰

같은 모델 ID로 두 번 실행합니다. 두 번째 실행에서 다운로드 메시지가 보이지 않을 수 있는 이유를 설명합니다. 다운로드한 Weight 파일의 존재와 Python 메모리에 로드된 Model 객체를 구분해야 합니다.

## 활동 6. 오류 진단

다음 사례의 **문제가 생긴 단계**를 고릅니다.

| 상황 | 학생 답안 |
|---|---|
| 없는 Model ID를 입력했다 | ______ |
| 메모리가 부족해 Model을 생성하지 못했다 | ______ |
| `input_ids`의 Device가 Model과 다르다 | ______ |
| `output_ids`를 출력했더니 숫자가 나타났다 | ______ |
| Chat용 Model의 응답 형식이 예상과 다르다 | ______ |

강사 해설: 앞 세 사례는 각각 모델 로딩·메모리 로딩·Device 문제입니다. 네 번째는 **오류가 아니라 Token ID 출력이라는 정상적인 중간 결과**입니다. 다섯 번째는 Model Card에 기재된 입력 형식과 Chat Template을 먼저 확인해야 합니다.

---

# 18. 수업 확인 질문 및 해설

**Q1. `from_pretrained()`를 호출하면 새 모델이 학습되나요?**

아니요. 저장된 Tokenizer 또는 Pre-trained Model의 구성과 파일을 찾아 로드합니다. 이번 수업에서는 Weight를 업데이트하지 않습니다.

**Q2. `AutoTokenizer`와 `AutoModelForCausalLM`을 같은 Model ID로 사용하는 이유는?**

선정한 Model에 맞는 입력 처리 도구와 생성용 Model 객체를 준비하려는 것입니다. 단, 실제 호환성은 Model Card와 지원 라이브러리 정보에 따라 검증해야 합니다.

**Q3. `return_tensors="pt"`의 결과로 바로 사람이 읽을 문장이 나오나요?**

아니요. 여기서는 Model에 전달할 수치 형태의 Tensor 입력이 준비됩니다. 사람이 읽을 문자열은 생성된 Token ID를 Decode한 다음 얻습니다.

**Q4. `model.eval()`과 `torch.inference_mode()`는 같은 기능인가요?**

아니요. Evaluation 동작 Mode를 설정하는 것과 추론에서 Gradient 추적을 제어하는 것은 다른 역할입니다. 상세 원리는 이미 3교시에서 배웠으므로 이번에는 사용 위치를 확인합니다.

**Q5. `generate()` 결과를 전부 Decode하면 입력 문자열도 보일 수 있나요?**

그럴 수 있습니다. 이번 Causal LM 실습의 기본 출력은 Prompt ID와 생성 ID가 이어진 Sequence일 수 있기 때문입니다. 따라서 입력 길이를 구해 새 ID 구간을 분리합니다.

**Q6. `max_new_tokens=30`이면 30글자가 반드시 나오나요?**

아닙니다. Token 기준 상한이며, 종료 조건에 따라 생성 개수도 달라질 수 있습니다.

**Q7. 같은 모델을 재실행할 때 다운로드가 없으면 Model을 메모리에 계속 보관한 건가요?**

아닙니다. 파일을 Cache에서 재사용할 수 있다는 의미일 수 있습니다. Python에서의 Model 객체 로드는 다시 수행할 수 있습니다.

**Q8. 왜 이번에는 `pipeline` 대신 직접 Tokenizer와 Model을 호출했나요?**

학생이 **어느 단계에서 문자열이 ID로 바뀌고, 어느 단계에서 새로운 ID가 생성되고, 어디서 Decode되는지**를 코드로 관찰하기 위해서입니다.

---

# 19. 강사용 시연 순서

학생에게 완성 코드를 처음부터 모두 보여주는 대신 단계별로 확인합니다. 한 번에 복잡한 내용을 나열하면 무엇이 새롭게 일어났는지 구분하기 어려울 수 있습니다.

1. 4교시의 **실제 선정 모델 ID**를 확인하고 `CLASS_MODEL_ID`로 설정합니다.
2. 가상환경·라이브러리를 확인한 후 Tokenizer와 Model을 로드합니다.
3. `type(tokenizer)`, `type(model)`, Parameter 수를 출력합니다.
4. 입력 문자열을 Tokenize하고 `input_ids` Shape를 확인합니다.
5. Device를 확인한 뒤 `model.eval()`과 `torch.inference_mode()`를 적용합니다.
6. `max_new_tokens=30`으로 `generate()`를 실행합니다.
7. `output_ids`와 전체 Decode 결과를 출력합니다.
8. `input_length`를 이용해 새로 생성된 ID만 분리합니다.
9. 한 입력과 한 설정만 바꾼 뒤 결과를 비교합니다.
10. Cache/Load 차이를 확인하고 오류 진단 활동을 진행합니다.

강사는 각 단계에서 **지금 출력이 문자열인지, Tensor인지, Python Model 객체인지**를 학생에게 묻습니다. 이 질문이 이번 교시의 일관된 확인 기준입니다.

---

# 20. 실습 완료 체크리스트

- [ ] 실제 Model ID가 정해져 있으며, 4교시 선정 근거를 확인했다.
- [ ] PyTorch와 Transformers가 실습 환경에 설치되었다.
- [ ] `AutoTokenizer.from_pretrained()`가 정상 수행되었다.
- [ ] `AutoModelForCausalLM.from_pretrained()`가 정상 수행되었다.
- [ ] Tokenizer와 Model Class를 출력했다.
- [ ] `input_ids`와 Shape를 확인했다.
- [ ] 입력 및 Model의 Device가 호환되는지 확인했다.
- [ ] `model.eval()`과 `torch.inference_mode()`로 생성했다.
- [ ] `output_ids`와 `output_ids.shape`를 확인했다.
- [ ] 전체 Decode 결과와 신규 생성 부분을 구분했다.
- [ ] `max_new_tokens`를 변경해 결과를 비교했다.
- [ ] Download/Cache와 Memory Load를 구분해 설명할 수 있다.
- [ ] 오류가 발생할 경우 실패한 단계를 분류할 수 있다.

이 체크리스트는 강사가 실제 Model ID와 교육장 환경을 검증하여 실습했을 때 채울 수 있습니다. **문서의 Python 문법 검사만으로 실습 수행 완료라고 표시하면 안 됩니다.**

---

# 21. 이번 교시 핵심 정리

이번 5교시의 핵심은 **개념을 하나 더 외우는 것**이 아니라, 지금까지 각각 배운 개념을 **실행 가능한 Python 코드의 흐름으로 연결**하는 것입니다.

```text
4교시에서 선정한 Model ID
    ↓
AutoTokenizer.from_pretrained() + AutoModelForCausalLM.from_pretrained()
    ↓
Tokenizer 객체 + 학습된 Model 객체
    ↓
사용자 문자열 → input_ids / attention_mask 등 Tensor
    ↓
model.eval() + torch.inference_mode()
    ↓
model.generate()
    ↓
Output Token IDs
    ↓
입력 부분 / 신규 생성 부분 구분
    ↓
tokenizer.decode()
    ↓
사람이 읽을 수 있는 생성 결과
```

꼭 기억할 문장:

> **Transformers를 사용하여 Pre-trained Model을 직접 실행하면, Python 코드에서 Model과 Tokenizer를 로드하고, Tensor 입력을 전달하여 생성된 Token ID를 받은 뒤 Text로 변환하는 전 과정을 관찰할 수 있습니다.**

이번 교시에서는 모델을 **직접 실행**했습니다. Model 실행을 별도의 프로세스나 서버에서 제공하는 **Runtime·Serving 방식과 비교하는 것**은 다음 교시의 학습 목표입니다.

---

# 22. 다음 교시 연결

이번에는 Python 프로그램이 직접 Model 객체를 보유하고 `generate()`를 호출했습니다.

> 다음에는 **Model 실행을 하나의 프로그램 안에서 직접 처리하는 방식과 별도의 Runtime/Serving 계층을 사용하는 방식이 어떻게 다른가**를 공부합니다.

따라서 다음 교시의 시작 질문은 단순합니다.

**“모델을 직접 로드하지 않는 다른 애플리케이션도 이 모델의 결과를 사용할 수 있으려면 어떤 구조가 필요할까?”**

그 질문에 답하는 과정에서 Runtime, Serving, Transformers와 Ollama의 차이를 학습하게 됩니다. 이번 파일에서는 그 개념의 정의·비교표·서버 구성 코드를 미리 제시하지 않습니다.

---

# 참고자료

- Hugging Face Transformers 공식 문서
- Hugging Face Auto Classes 공식 문서
- Hugging Face Text Generation 공식 문서
- Hugging Face Chat Templates 공식 문서
- PyTorch 공식 문서

> Model ID·Model Card·Version·Chat Template 및 라이브러리 인터페이스는 실제 교육장 배포 시점에 다시 확인해야 합니다. 현재 문서의 예제만으로 특정 모델·버전에서의 실행 성공을 확정하지 않습니다.

# 관련 Wiki Link

- [[Transformers]]
- [[Hugging Face Hub]]
- [[Pre-trained Model]]
- [[AutoTokenizer]]
- [[AutoModelForCausalLM]]
- [[Tokenizer]]
- [[Token ID]]
- [[Tensor]]
- [[PyTorch]]
- [[Inference]]
- [[Generation]]
- [[Chat Template]]
- [[Model Cache]]
