# Day 3 - 3교시. Model Size, Parameter와 Quantization (v0.2)

## 개요 — 모델 이름의 숫자를 실제 저장 용량으로 연결하기

Day3 1교시에는 하나의 Model Family 안에도 여러 크기의 Variant가 있음을 확인했고, 2교시에는 Base/Pre-trained와 Instruction-tuned Variant가 **무엇을 위해 조정되었는지** 비교했습니다. 이제 다른 질문을 다룹니다.

> 같은 계열의 모델이라도, **Parameter를 어떤 표현 방식으로 저장하느냐에 따라 Weight가 차지하는 크기는 얼마나 달라질까?**

이번 교시는 이미 알고 있는 `Parameter`, `Tensor`, `dtype`을 처음부터 다시 설명하지 않습니다. 이 세 개념을 **Model Weight의 저장 크기 계산**에 이용합니다. 이때 Quantization(양자화)이 왜 등장하는지, 계산 결과의 어느 부분까지 믿을 수 있는지 확인합니다.

수업의 범위는 다음과 같습니다.

| 구분 | 이번 시간에 배울 것 | 다른 교시에서 배울 것 |
|---|---|---|
| 이전 학습 활용 | Parameter Count, `dtype`, Model Variant | Parameter 업데이트·Tensor 기초 재설명은 하지 않음 |
| **이번 시간의 새 학습** | bit/byte 계산, FP32·FP16/BF16·8-bit·4-bit 크기 비교, Quantization, 크기 추정의 한계 | — |
| 다음 Day3 4교시 | 저장한 Weight를 실제 하드웨어에서 실행할 수 있는지 | CPU·GPU·RAM·VRAM의 구체적인 역할과 Device 운용 |
| 다음 Day3 5교시 | 프로젝트에 사용할 모델의 최종 선택 | Model Card 기반 후보 평가·실측 비교·운영 의사결정 |
| 이후 별도 학습 | 학습 및 최적화 심화 | PEFT·LoRA·QLoRA 구현·정량적 학습 기법 |

**오늘의 성공 기준:** 학생이 4B Model의 **32-bit 이론상 Weight 16 GB**, **16-bit 8 GB**, **8-bit 4 GB**, **4-bit 2 GB**를 계산할 수 있고, 이 숫자를 **실제 다운로드 크기 또는 필요한 RAM/VRAM으로 단정하지 않아야** 합니다.

---

# 1. 학습 목표

교시가 끝나면 다음을 할 수 있어야 합니다.

1. `1B`, `4B`, `12B` 등의 Parameter 규모 표기를 저장 용량과 구분한다.
2. Parameter 수, 표현 bit 수, byte 수를 이용해 **이론적인 Weight 저장량**을 계산한다.
3. FP32·FP16·BF16·8-bit·4-bit의 저장 크기 관계를 비교한다.
4. **낮은 bit로 저장하는 것**과 **Quantization을 수행하는 것**을 구분한다.
5. Quantization의 목적과 품질·호환성 측면의 Trade-off를 설명한다.
6. Quantization과 Pruning, GGUF 파일 형식을 혼동하지 않는다.
7. 추정 Weight 용량과 Model File Size, 실행 중 Memory 사용량의 차이를 설명한다.
8. Python 계산 결과와 PyTorch Tensor에서 확인한 실제 Byte 수를 구분해 기록한다.
9. 크기 정보만으로 Local Model 실행 가능 여부를 확정하지 않는다.

---

# 2. 출발 질문 — `4B Model`은 4GB 파일이라는 뜻일까?

앞 교시에서 `B`가 일반적으로 *Billion*, 즉 10억 단위의 Parameter 수를 표현한다고 배웠습니다. 따라서 `4B`는 대략 40억 개의 Parameter를 가진 **모델 규모 표기**입니다.

그런데 다음 두 모델이 있다고 가정해 봅시다.

- 모델 A: 약 4B Parameter를 **32-bit**로 표현
- 모델 B: 같은 약 4B Parameter를 **16-bit**로 표현

두 모델은 Parameter 수를 기준으로 하면 비슷한 규모지만, 저장해야 하는 **숫자 한 개당 bit 수**가 다릅니다. 그러므로 Weight 크기도 달라집니다.

여기에서 필요한 질문은 두 가지입니다.

1. **숫자를 몇 개 저장하는가?** → Parameter Count
2. **숫자 하나를 몇 bit로 표현하는가?** → Representation Precision / Bit Width

이번 교시에서는 이 두 질문의 **곱셈**을 먼저 이해합니다. 어떤 모델이 실제로 더 좋은 답변을 내는지는 이 곱셈만으로 결론 내릴 수 없습니다.

---

# 3. 크기 계산에 사용할 세 가지 단위

수치 계산에 들어가기 전에 단위를 통일합니다.

| 표기 | 이 교시에서의 의미 | 예 |
|---|---|---|
| `B`(모델 이름에서) | Billion, 약 10억 개 Parameter | `4B` ≈ 4,000,000,000개 |
| `bit` | 숫자 표현에 사용하는 정보의 단위 | FP32 = 32 bit |
| `byte` | 8 bit | 32 bit = 4 byte |
| `GB` | 십진 기준 1,000,000,000 byte | 약 4 GB |
| `GiB` | 이진 기준 1,073,741,824 byte | 약 3.73 GiB = 4 GB |

**주의:** Model 이름의 `4B`에서 `B`는 **Billion**이지 **Byte**가 아닙니다. 반면 `4 GB`의 `B`는 Byte입니다. 같은 글자를 사용하므로 문맥을 확인해야 합니다.

이번 원본 강의의 계산 예제는 이해하기 쉽게 **십진 GB**를 사용합니다. 실제 운영체제나 도구는 GiB로 표시할 수 있으므로, 표시 숫자가 다르다고 반드시 계산 오류인 것은 아닙니다.

### 왜 GiB를 잠깐 언급할까?

예를 들어 정확히 4,000,000,000 byte를 다른 단위로 표현하면 다음과 같습니다.

```text
4,000,000,000 byte
= 4.00 GB
≈ 3.73 GiB
```

**내용의 양이 달라진 것이 아니라 단위가 달라진 것**입니다. 단위 변환을 배우는 목적은 뒤에서 파일 크기나 시스템 표시값과 대조할 때 생기는 혼동을 막기 위해서입니다.

---

# 4. 이론적 Weight 크기를 구하는 공식

오늘 계속 사용할 공식은 하나입니다.

\[
\text{Weight bytes (이론값)}
= \frac{\text{Parameter 개수}\times\text{Parameter당 bit 수}}{8}
\]

십진 GB로 바꾸면:

\[
\text{Weight GB (이론값)}
= \frac{\text{Parameter 개수}\times\text{bit 수}}{8\times10^9}
\]

위 공식은 **모든 Parameter가 같은 bit 폭으로 저장된다고 가정**한 계산입니다. 이 조건이 무너지면 각 Parameter 그룹의 표현 크기를 따로 더해야 할 수 있습니다.

그림 대신 구체적인 값을 대입해 봅니다.

```text
약 4B Parameters
= 4,000,000,000개

Parameter마다 32 bit 사용
= 32 / 8
= 4 byte

4,000,000,000 × 4 byte
= 16,000,000,000 byte
≈ 16 GB
```

여기까지 계산했을 때 아직 알 수 없는 것은 **실제 모델 파일의 정확한 용량**과 **실행에 필요한 전체 메모리**입니다. 이론값은 어디까지나 Weight 표현량의 첫 추정치입니다.

---

# 5. FP32·FP16·BF16은 무엇을 비교하는가?

Day2 2교시에서 `tensor.dtype`을 읽는 방법은 이미 실습했습니다. 이번에는 `dtype`을 **표현하는 숫자의 저장 공간** 관점에서만 사용합니다.

| 형식 | 기본 bit 폭 | 한 원소의 기본 저장 크기 | 이번 시간에 강조할 점 |
|---|---:|---:|---|
| FP32 (`float32`) | 32 bit | 4 byte | 높은 정밀도의 부동소수점 표현 |
| FP16 (`float16`) | 16 bit | 2 byte | FP32보다 적은 byte로 표현 |
| BF16 (`bfloat16`) | 16 bit | 2 byte | FP16과 byte 수는 같지만 표현 특성은 다름 |

### 5.1 FP32와 FP16의 차이는 여기서 무엇일까?

오늘 필요한 사실은 저장 공간의 차이입니다. 같은 4B Parameter라면 모든 원소를 FP32로 저장하는 이론값은 **16 GB**, FP16으로 저장하면 **8 GB**입니다.

`FP16`과 `BF16`을 모두 16-bit라고 부르더라도 완전히 같은 자료형은 아닙니다. 표현 가능한 숫자의 범위와 세부 정밀도 특성이 다릅니다. 하지만 이 교시의 **순수 용량 계산**에는 둘 다 Parameter당 2 byte를 적용할 수 있습니다.

**주의:** 16-bit 값으로 저장한다고 해서 그 모델이 언제나 FP32 버전과 똑같은 출력이나 품질을 보이는 것은 아닙니다. 이 교시의 표는 **메모리 계산표**이며 품질 비교표가 아닙니다.

---

# 6. 같은 4B Model의 표현 bit 수만 바꿔 비교하기

같은 Parameter 수를 고정하고 표현 bit 수만 바꿉니다.

| 가정한 표현 | Parameter당 이론값 | 4B의 Weight 크기(십진 GB) | 4B의 Weight 크기(약 GiB) |
|---|---:|---:|---:|
| FP32 / 32-bit | 4 byte | 16 GB | 14.90 GiB |
| FP16·BF16 / 16-bit | 2 byte | 8 GB | 7.45 GiB |
| 8-bit | 1 byte | 4 GB | 3.73 GiB |
| 4-bit | 0.5 byte | 2 GB | 1.86 GiB |

**표를 읽는 법**

- 위 네 행은 Parameter 수가 모두 **약 4B**라는 동일한 가정입니다.
- `4-bit = 0.5 byte`는 **전체 Weight의 bit 수를 평균 낸 이론값**입니다. 하나의 Python 숫자 객체가 실제로 0.5 byte를 차지한다는 뜻이 아닙니다.
- 실제 4-bit Weight 저장에는 여러 값을 함께 포장(Packing)하는 방식이 쓰일 수 있습니다. 또한 Quantization 부가 정보가 추가될 수 있습니다.
- 표의 크기는 **모델 전체 실행 메모리 요구량이나 실제 파일 크기를 보장하는 값이 아닙니다.**

### 계산 결과에서 답해야 할 질문

`4B FP32`와 `4B 4-bit`를 비교할 때 **Parameter가 1/8로 사라진 것일까요?** 아닙니다. 표현에 필요한 bit 수의 이론값이 `32 → 4`로 바뀌었기 때문에 저장량이 약 1/8 수준으로 내려간 것입니다.

---

# 7. 1B와 4B를 교차 비교하면 무엇이 보일까?

Parameter 수와 bit 폭은 **서로 다른 축**입니다. 둘 중 하나만 보면 크기를 추정할 수 없습니다.

| 사례 | 계산 | 이론적 Weight 크기 |
|---|---|---:|
| 1B, FP32 | 1 × 10억 × 4 byte | 4 GB |
| 1B, FP16 | 1 × 10억 × 2 byte | 2 GB |
| 4B, 8-bit | 4 × 10억 × 1 byte | 4 GB |
| 4B, 4-bit | 4 × 10억 × 0.5 byte | 2 GB |

**관찰할 점:** `1B FP32`와 `4B 8-bit`는 이론적 Weight 크기가 둘 다 약 **4 GB**입니다. **동일한 저장량이 동일한 Parameter 수, 계산 속도, 정확도 또는 출력 품질을 뜻하지는 않습니다.**

학생에게 묻습니다.

> 같은 약 2 GB인 `1B FP16`과 `4B 4-bit` 중 어느 쪽의 한국어 문서 요약 품질이 더 좋은가요?

오늘 배운 크기 계산만으로는 **판단할 수 없습니다.** 그 이유가 바로 다음에 배울 Quantization의 Trade-off와 연결됩니다. 실제 모델 후보의 최종 평가는 Day3 5교시에 맡깁니다.

---

# 8. Quantization — 같은 값을 더 적은 bit로 표현하려면

일반적인 Model Quantization은 Weight 또는 Activation 등의 수치 표현을 **더 낮은 정밀도의 방식으로 변환**하여 저장량 또는 연산 부담을 줄이는 기술 범주입니다. Local LLM에서 가장 쉽게 관찰할 수 있는 효과는 **Weight를 저장하는 데 필요한 공간을 줄일 수 있다는 것**입니다.

예를 들어 원래 Weight의 수치가 다음과 같이 세밀하게 저장되었다고 생각합니다.

```text
0.12345678
-0.73482910
0.00410983
...
```

낮은 정밀도 표현에서는 원래 값과 완전히 똑같은 숫자 표현을 유지하지 못할 수 있습니다. 변환 방법에 따라 값의 근삿값을 사용하고, 복원에 필요한 별도의 정보를 함께 저장할 수 있습니다.

따라서 다음 두 문장을 구분합니다.

- **맞는 설명:** Weight 값을 더 적은 bit로 근사 표현할 수 있고, 이를 통해 저장량을 줄일 수 있다.
- **틀린 설명:** 원래 값과 항상 완전히 같으면서 파일만 작아지므로 출력 품질은 절대 달라지지 않는다.

이 절의 목적은 Quantization 알고리즘 내부의 수식을 구현하는 것이 아닙니다. **왜 낮은 bit의 모델 배포본이 가능한가**를 이해하는 것입니다.

---

# 9. ‘8-bit 자료형’과 ‘Quantization’은 동의어인가?

두 표현은 연관되지만 같은 말로 사용하지 않습니다.

`int8`은 컴퓨터가 숫자를 나타내는 **자료형**입니다. 반면 Quantization은 기존 수치 표현을 더 제한된 수의 값으로 **변환하는 방법**과 관련됩니다.

예를 들어 단순히 실수 `0.7`을 정수 `int(0.7)`로 바꾸면 결과는 `0`입니다. 이것은 Python 형 변환의 예이지, 모델 Weight를 적절한 범위와 척도로 근사해 저장하는 양자화 기법의 작동 원리를 충분히 설명하는 예제가 아닙니다.

실제 Quantization에서는 방식에 따라 변환에 필요한 **Scale, Zero Point, Group별 정보** 등 추가적인 값이 사용될 수 있습니다. 그래서 앞에서 계산한 `4B × 4-bit = 2 GB`가 **실제 Quantized File의 정확한 크기**가 되는 것은 아닙니다.

이번 교시에서 자세히 다루지 않을 내용은 Quantization을 위한 수치 변환 알고리즘별 공식과 Kernel 구현입니다. 학생은 먼저 **bit 수만으로 모든 조건이 결정되지 않는다**는 점을 기억하면 됩니다.

---

# 10. Quantization은 Parameter를 줄이는 것일까?

가장 중요한 오해 중 하나입니다.

```text
약 4B Parameter Model
   ↓ 4-bit Quantization
여전히 약 4B Parameter 규모의 Model
(일반적인 Weight Quantization 기준)
```

일반적인 Weight Quantization의 목표는 **Parameter 개수 자체를 삭제하는 것**이 아니라 각 Weight를 표현하는 정밀도를 바꾸는 것입니다.

반면 원본 강의에서 함께 언급한 **Pruning**은 중요도가 낮은 Weight나 일부 구조를 제거하거나 희소화하는 접근입니다. 두 기술은 모두 모델 압축과 연관될 수 있지만 **같은 기술이 아닙니다.**

| 구분 | 주로 바꾸는 것 | 이 교시에서 기억할 것 |
|---|---|---|
| Quantization | 수치의 표현 방식·정밀도 | 같은 Parameter 수라도 Weight 크기가 줄 수 있다 |
| Pruning | 일부 Weight 또는 구조의 제거·희소화 | ‘표현 bit 수만 낮추는 것’과 다르다 |

여기서는 두 개념을 **구분**하는 데서 멈춥니다. Pruning 방법을 구현하거나 모델 구조를 변경하는 실습은 하지 않습니다.

---

# 11. Quantization의 장점과 Trade-off

Quantization을 도입할 이유는 단순히 ‘파일이 작아 보인다’는 것 이상입니다. 원본 강의에서 제시한 효과를 **가능성**과 **보장되지 않는 부분**으로 나눕니다.

| 기대할 수 있는 점 | 반드시 확인할 조건 |
|---|---|
| Weight 저장 크기 감소 가능 | 부가 Metadata를 포함한 실제 배포 파일 크기 |
| 실행 시 Weight Memory 감소 가능 | Runtime에서 실제로 어느 표현으로 Load하는지 |
| Memory Bandwidth 부담 감소 가능 | Hardware와 연산 구현이 해당 형식을 효율적으로 지원하는지 |
| 일부 환경에서 더 작은 모델 실행 부담 | 추가 Buffer·Activation·Cache를 포함한 실제 요구량 |
| 일부 환경에서 속도 개선 가능 | Quantization 처리 방식·연산 Kernel·Runtime의 지원 |

그리고 **품질** 문제를 따로 봅니다.

- 낮은 정밀도에서는 원래 Weight 수치를 근사하게 되므로 출력이 달라질 수 있습니다.
- 변경의 영향은 Model, Task, Quantization 방식에 따라 다릅니다.
- 더 낮은 bit가 항상 더 빠르거나 더 좋은 답을 내는 것은 아닙니다.

따라서 `4-bit`와 `8-bit` 중 하나를 **이론적 저장량만으로 최종 결정하지 않습니다.** 이번에는 그 이유까지만 학습하고, 실제 모델 후보 평가와 운영 판단은 Day3 5교시로 남깁니다.

---

# 12. 같은 ‘4-bit’라도 왜 배포본이 다를까?

원본에서 언급한 용어를 역할에 따라 정리합니다.

| 이름 | 이번 교시에서의 위치 | 주의사항 |
|---|---|---|
| 8-bit / 4-bit | 사용되는 표현 정밀도를 나타내는 말 | 구체적인 변환 방식이 하나로 고정되지 않음 |
| GPTQ / AWQ | Quantization 방법의 이름 | 내부 알고리즘은 이 수업 범위가 아님 |
| bitsandbytes | 저정밀도 연산·Quantization 관련 Library | 모든 OS·Hardware에서 동일하게 지원된다고 단정하지 않음 |
| GGUF | Model Data를 저장·배포하기 위한 파일 형식 | **GGUF 자체가 Quantization 알고리즘은 아님** |

### 12.1 GGUF 파일은 왜 자주 언급될까?

Local LLM 생태계에서는 GGUF 형식의 모델 파일을 만날 수 있습니다. 이 파일이 Quantized Weight를 담는 경우가 있지만, `GGUF`라는 이름 자체는 **파일 형식**을 가리킵니다.

```text
Quantization  → Weight의 숫자 표현 방식과 관련
GGUF          → Model 정보를 저장·배포하는 파일 형식
```

따라서 `GGUF면 모두 같은 정밀도다`라는 설명도 틀립니다. 어떤 **Variant**인지 함께 확인해야 합니다.

### 12.2 Ollama와 Transformers에서는?

앞에서 사용했던 Ollama 또는 Transformers를 통해 낮은 정밀도의 모델 배포본을 만나거나 관련 Library와 조합할 수 있습니다. 그러나 **어떤 형식이 실제로 지원되는지**는 선택한 모델, 도구 버전, 실행 환경에 따라 다릅니다. 이번 교시에서는 설치 명령어나 변환 코드를 추가하지 않고, **이름만으로 실제 정밀도와 호환성을 확정하지 않는 방법**을 배웁니다.

---

# 13. Weight 이론값과 실제 Model File은 왜 다를까?

예를 들어 앞의 계산표에서 **4B 4-bit = 약 2 GB**라는 숫자가 나왔습니다. 그런데 실제 Repository의 파일 크기는 정확히 2 GB가 아닐 수 있습니다.

단순 공식에서 생략된 정보에는 다음과 같은 것이 있습니다.

| 계산에서 빠진 요소 | 왜 차이가 날 수 있는가? |
|---|---|
| Quantization Scale·Zero Point·Group 정보 | 원래 Weight 값을 근사 표현·해석하는 데 필요한 추가 정보가 저장될 수 있음 |
| 일부 Tensor의 다른 dtype | 모든 Weight가 꼭 4-bit로 저장되는 것은 아닐 수 있음 |
| Model Configuration·Metadata | Weight 외의 설명·설정 정보가 함께 저장될 수 있음 |
| 여러 파일로 분할된 Weight | 실제 배포본에서 Weight가 나뉘어 있을 수 있음 |
| File Format 차이 | Container·Index·관리 정보의 구성 방식이 다를 수 있음 |

따라서 모델의 규모를 말할 때는 최소한 **무슨 값을 적었는지** 명확히 구분합니다.

```text
“4B, 4-bit → 이론적 Weight 크기 약 2 GB”
“이 저장소에서 다운로드한 파일 크기 ○○ GB”
```

첫 번째는 **가정에 기반한 계산**, 두 번째는 **특정 파일의 확인값**입니다. 이번 교시에서 실제 파일을 다운로드하지 않았다면, 두 번째 값은 **미확인**이라고 기록합니다.

---

# 14. Storage와 Runtime Memory를 같은 값으로 보면 안 된다

다음 가정을 검토합니다.

> 모델 파일이 4GB이므로, 메모리가 정확히 4GB인 컴퓨터에서 실행할 수 있다.

**이 정보만으로는 판단할 수 없습니다.** 모델을 저장하는 공간과 실행 중 필요한 자원은 다른 문제이기 때문입니다.

원본 강의가 열거한 실행 중 메모리 항목을 **이름과 의미** 수준에서 정리하면 다음과 같습니다.

| 항목 | 이번 교시에서 알아둘 의미 |
|---|---|
| Model Weights | 계산에 사용하는 학습된 Parameter 값 |
| Activation | 모델 계산 중 만들어질 수 있는 중간 값 |
| KV Cache | 생성 중 이전 Token 관련 계산 정보를 재사용하기 위한 저장 영역 |
| Input / Output Tensor | 처리할 입력과 계산 결과를 담는 수치 데이터 |
| Runtime / Library / Process Overhead | 모델 실행 소프트웨어가 사용하는 부가 메모리 |

이 표가 `실행 중 메모리는 항상 위 항목을 모두 단순 합산하면 정확히 나온다`는 뜻은 아닙니다. 구현과 설정에 따라 항목의 종류, 규모, 배치 방법이 달라질 수 있습니다.

**이번 교시의 결론:** 단순 Weight 크기는 **실행 메모리 요구량의 일부를 이해하는 계산값**이지, 실행 가능 여부의 최종 판정값이 아닙니다.

실제 CPU·GPU·RAM·VRAM 배치와 장치별 동작은 **바로 다음 4교시**에서 배웁니다.

---

# 15. Context와 Batch도 실행 중 메모리에 영향을 줄까?

모델 Weight 크기가 같더라도 실행 조건이 다르면 Memory 사용량은 달라질 수 있습니다.

### 15.1 Context Length

Language Model이 긴 입력을 처리하거나 더 많은 생성 기록을 유지하면, **KV Cache 등 추가 Memory가 늘어날 수 있습니다.** 이번에는 KV Cache의 내부 Attention 수식을 다루지 않습니다.

### 15.2 Batch Size

여러 입력을 함께 처리할 때는 **동시에 처리하는 데이터량**이 달라집니다. Model과 Runtime에 따라 추가 Memory가 늘어날 수 있습니다.

### 같은 모델, 다른 조건

| 조건 | 달라지지 않는 것 | 달라질 수 있는 것 |
|---|---|---|
| 짧은 Context → 긴 Context | 모델의 Parameter Count | Cache·중간 계산 등에 필요한 Memory |
| Batch Size 1 → 더 큰 Batch | 모델의 Parameter Count | 동시에 처리하는 데이터의 Memory |

핵심은 **`Model Size = 유일한 실행 메모리 결정 요인`이 아니라는 것**입니다. 얼마만큼 증가하는지 계산하거나 동시에 몇 요청을 처리할지 설계하는 내용은 이번 교시의 범위가 아닙니다.

---

# 16. Training과 Inference의 Memory 요구가 왜 다를 수 있을까?

Day2 3교시에서 Training Loop와 Gradient·Optimizer를 직접 확인했습니다. 여기서는 그 코드를 반복하지 않고 메모리 관점만 연결합니다.

- Inference는 모델의 Parameter로 결과를 계산하기 위한 Memory를 사용합니다.
- Training은 여기에 더해 **Gradient, Optimizer State, 학습 과정의 중간 계산값**을 보관해야 할 수 있습니다.
- 따라서 같은 모델이라도 일반적으로 **Training의 Memory 요구가 Inference보다 클 수 있습니다.**

원본에서 언급한 `PEFT`, `LoRA`, `QLoRA`는 이런 부담과 연관된 추가 학습 접근입니다. 이름만 연결하고 **학습 알고리즘이나 구현을 앞당겨 설명하지 않습니다.**

특히 **Quantization과 QLoRA는 같은 말이 아닙니다.** Quantization은 저정밀도 표현의 기술 범주이고, QLoRA는 Quantized 기반 모델과 LoRA Adapter 등을 이용하는 추가 학습 접근입니다. 현재는 서로 같은 개념이 아니라는 정도만 구분합니다.

---

# 17. Python 실습 1 — 가정한 Weight의 이론적 크기 계산

이번 시간의 핵심 계산을 Python으로 검증합니다. 이 코드는 **표준 Python만 사용**하며 모델 다운로드나 GPU가 필요하지 않습니다.

`weight_size_estimator.py`

```python
BILLION = 1_000_000_000
BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024 ** 3


def estimate_weight_size(
    parameter_billions: float,
    bits_per_parameter: int,
) -> tuple[float, float]:
    """모든 Parameter의 bit 폭이 같다는 가정하의 Weight 이론값."""
    if parameter_billions <= 0:
        raise ValueError("Parameter 규모는 0보다 커야 합니다.")
    if bits_per_parameter <= 0:
        raise ValueError("bit 수는 0보다 커야 합니다.")

    parameter_count = parameter_billions * BILLION
    total_bytes = parameter_count * bits_per_parameter / 8
    return total_bytes / BYTES_PER_GB, total_bytes / BYTES_PER_GIB


def main() -> None:
    for bits in (32, 16, 8, 4):
        gb, gib = estimate_weight_size(4, bits)
        print(f"4B / {bits:>2}-bit: {gb:>5.2f} GB ({gib:.2f} GiB)")


if __name__ == "__main__":
    main()
```

실행:

```bash
python weight_size_estimator.py
```

예상 출력(소수 둘째 자리 반올림):

```text
4B / 32-bit: 16.00 GB (14.90 GiB)
4B / 16-bit:  8.00 GB (7.45 GiB)
4B /  8-bit:  4.00 GB (3.73 GiB)
4B /  4-bit:  2.00 GB (1.86 GiB)
```

**코드를 읽을 때 세 가지를 확인합니다.**

1. `parameter_billions * BILLION`: **B 단위 → 개수** 변환
2. `* bits_per_parameter / 8`: **전체 bit → byte** 변환
3. `GB`와 `GiB`: **같은 byte 총량의 서로 다른 단위 표현**

이 계산기의 `bits_per_parameter=4`는 **이론적 평균 bit 폭을 입력한 값**입니다. 이 코드가 실제 Weight를 Quantization하거나 Model의 성능·실행 가능 메모리를 측정하는 것은 아닙니다.

---

# 18. 계산기를 바꿔 보자 — 어떤 숫자를 비교할 것인가?

### 활동 A. Parameter 규모만 바꾸기

다음 코드를 `main()`의 출력 부분에 추가합니다.

```python
for billions in (1, 4, 12):
    gb, _ = estimate_weight_size(billions, 16)
    print(f"{billions}B / 16-bit: {gb:.2f} GB")
```

예상 출력:

```text
1B / 16-bit: 2.00 GB
4B / 16-bit: 8.00 GB
12B / 16-bit: 24.00 GB
```

**확인:** bit 폭을 16으로 고정하면 Parameter 수가 커질수록 이론 Weight가 비례해 증가합니다.

### 활동 B. 표현 bit만 바꾸기

이번에는 Parameter를 **4B**로 고정하고 bit 폭만 바꿉니다. 앞에서 작성한 기본 `main()`이 바로 이 실험입니다.

**확인:** Parameter 수를 바꾸지 않고 bit 폭을 변경해도 이론 Weight 크기는 달라집니다.

### 활동 C. 예상 출력과 실제 파일 크기 구분하기

강사가 교육장에 제공한 Model Repository 또는 Local 파일이 있다면 학생은 **실제 파일에 표시된 Size**를 따로 기록합니다. 이 파일이 없다면 `실제 파일 크기: 미확인`이라고 작성합니다.

| 비교 항목 | 학생 기록 |
|---|---|
| 가정한 Parameter 규모 |  |
| 가정한 bit 폭 |  |
| 이론 Weight (GB) |  |
| 실제 Model 파일·배포본 크기 | 확인값 또는 미확인 |
| 두 값의 차이가 날 수 있는 이유 |  |

파일이 크거나 네트워크 환경이 불안정하면 다운로드를 새로 수행하지 않습니다. **목적은 크기를 구분해서 기록하는 것**입니다.

---

# 19. Python 실습 2 — 실제 PyTorch Tensor의 Byte 수 확인

앞 실습은 **가정한 Weight 총량** 계산이었습니다. 이번에는 **현재 메모리에 만들어진 Tensor 하나의 수치 데이터 크기**를 직접 확인합니다.

Day2에서 배운 `numel()`·`element_size()`의 사용법을 처음부터 반복하지 않고 둘을 곱합니다.

`inspect_tensor_bytes.py`

```python
import torch


def tensor_data_bytes(tensor: torch.Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def main() -> None:
    values = [1.0, 2.0, 3.0, 4.0]

    for dtype in (torch.float32, torch.float16, torch.bfloat16):
        tensor = torch.tensor(values, dtype=dtype)
        print(
            f"{str(dtype):<15} "
            f"numel={tensor.numel()}, "
            f"element_size={tensor.element_size()}, "
            f"data_bytes={tensor_data_bytes(tensor)}"
        )


if __name__ == "__main__":
    main()
```

가상환경에 PyTorch가 설치된 경우 실행합니다.

```bash
python inspect_tensor_bytes.py
```

예상되는 핵심 수치:

| dtype | 원소 수 | 한 원소 byte | 총 수치 데이터 byte |
|---|---:|---:|---:|
| `torch.float32` | 4 | 4 | 16 |
| `torch.float16` | 4 | 2 | 8 |
| `torch.bfloat16` | 4 | 2 | 8 |

**중요한 차이:** 앞 계산기의 `4B`는 **수십억 개 Parameter의 가정값**이었고, 이 실습의 `4개`는 **지금 실제로 만든 Tensor의 원소 수**입니다. 둘 다 `원소 수 × 원소당 byte`라는 같은 사고방식을 사용하지만, 한쪽은 가정한 값이고 다른 한쪽은 생성한 Tensor의 실제 데이터 byte를 계산합니다.

이 계산은 Tensor 객체 및 Python 실행 환경의 **전체 Memory 사용량 측정**이 아닙니다.

---

# 20. 실제 Model Parameter의 dtype을 확인한다면?

Day2 5교시에서 이미 Pre-trained Model을 직접 로드하는 코드를 배웠습니다. 그 코드를 여기서 다시 작성하지 않습니다. **이전에 로드한 `model` 객체가 실행 중일 때에만** 다음과 같은 점검을 할 수 있습니다.

```python
# 전제: 앞 교시에서 model 객체를 이미 로드한 상태
first_parameter = next(model.parameters())

print(first_parameter.dtype)
print(first_parameter.device)
print(first_parameter.element_size())
```

여기에서 확인할 수 있는 것은 **첫 번째 Parameter Tensor의 dtype·Device·원소당 Byte**입니다.

**이것만으로 Model 전체가 동일한 dtype이라고 결론 내리면 안 됩니다.** Model의 각 Tensor가 서로 다른 dtype을 사용할 수도 있고, 일부 Quantization 표현은 일반 PyTorch Tensor의 `element_size()`와 같은 방식만으로 전체 저장량을 설명하기 어렵습니다.

따라서 이 코드는 **앞서 배운 `dtype`과 실제 Parameter Tensor를 연결하는 선택 활동**이지, **Quantized Model의 전체 크기를 정확히 계산하는 코드가 아닙니다.** 로드한 모델이 없는 학생은 이 단계를 건너뛰어도 오늘의 계산 목표를 달성할 수 있습니다.

---

# 21. 학생 활동 — 네 가지 주장을 판별하기

학생은 각 문장에 `맞음 / 틀림 / 주어진 정보로는 판단 불가`를 표시하고, **배운 숫자 또는 기준을 근거로 한 문장**씩 설명합니다.

| 문장 | 학생 판단 | 근거에 포함할 내용 |
|---|---|---|
| A. `4B`는 파일 크기가 4 GB라는 뜻이다. |  | 4B의 B가 무엇을 뜻하는지 |
| B. 같은 4B Model을 32-bit 대신 16-bit로 표현하면 이론 Weight는 약 절반이 된다. |  | 숫자 하나당 byte 수 |
| C. 4B를 4-bit로 만들면 Parameter 수가 0.5B로 줄어든다. |  | 개수와 표현 bit의 구분 |
| D. Model File이 6 GB라면 RAM 8 GB PC에서 무조건 실행 가능하다. |  | 파일 용량과 전체 실행 Memory의 구분 |
| E. 4-bit 모델은 8-bit 모델보다 모든 작업에서 반드시 품질이 나쁘다. |  | 모델·Task·Quantization Method 의존성 |
| F. GGUF는 4-bit Quantization 알고리즘의 정확한 이름이다. |  | File Format과 방법의 차이 |
| G. FP16과 BF16은 각각 16-bit이므로 저장 크기 계산에선 같은 byte 수를 사용한다. |  | bit 수와 표현 특성의 차이 |
| H. `ollama ls`에 보이는 Model Size는 모델 실행 중 필요한 전체 Memory와 반드시 같다. |  | 저장 공간과 실행 메모리 차이 |

### 강사용 해설

- **A — 틀림:** B는 Billion으로, Parameter 규모를 뜻합니다.
- **B — 맞음:** FP32의 4 byte와 FP16의 2 byte를 같은 개수에 적용하면 이론값이 절반입니다.
- **C — 틀림:** 일반적인 Quantization은 개수보다 각 Weight의 표현 정밀도를 바꾸는 것입니다.
- **D — 틀림:** 추가 Runtime Memory가 필요하므로 그 정보만으로 실행 가능하다고 결론 내릴 수 없습니다.
- **E — 틀림:** 품질 변화는 발생할 수 있지만 모든 Task의 결과를 bit 수 하나로 단정할 수 없습니다.
- **F — 틀림:** GGUF는 파일 형식입니다.
- **G — 맞음:** Byte 수는 같지만 부동소수점 표현 특성은 동일하지 않습니다.
- **H — 틀림:** 저장된 크기와 실행 중 메모리 요구량은 서로 다른 값입니다.

여기에서 학생이 **계산으로 알 수 있는 사실**과 **실행·평가해야만 알 수 있는 결과**를 구별하는지 확인합니다.

---

# 22. 학생 활동 — 계산은 맞지만 결론은 틀린 상황

아래는 **가상의 수업용 조건**입니다. 실제 Gemma 모델의 성능·다운로드 크기·실행 가능성을 주장하는 자료가 아닙니다.

```text
후보 A: 4B / FP16 가정
후보 B: 4B / 4-bit 가정
```

1. 각 후보의 이론 Weight 크기를 계산합니다.
2. 더 작은 이론값을 가진 후보를 찾습니다.
3. 다음 결론 가운데 **계산만으로는 말할 수 없는 것**을 고릅니다.

- `B는 Weight 저장의 이론값이 A보다 작다.`
- `B가 모든 컴퓨터에서 A보다 빠르게 실행된다.`
- `B는 언제나 A와 정확히 같은 답을 생성한다.`
- `B라면 반드시 RAM 4 GB만으로 실행 가능하다.`

첫 문장은 주어진 가정에서 **맞습니다**. 나머지는 **알 수 없습니다**. 학생은 `추가 Metadata`, `Runtime Memory`, `품질`, `하드웨어 지원` 중 적절한 근거를 연결해 설명합니다.

**수업 포인트:** Weight 크기 비교는 중요한 정보이지만, 그 자체가 **최종 모델 선정표**는 아닙니다. 정식 선정·평가는 Day3 5교시에서 다룹니다.

---

# 23. 교실에서 관찰할 수 있는 실제 크기와 상태

Day2 7교시에서 Ollama 실습을 완료했다면 강사가 승인한 기존 모델에 한해 다음 명령을 **관찰용**으로 사용할 수 있습니다.

```bash
ollama ls
ollama ps
```

이번 시간에 명령어 사용법을 새로 가르치는 것은 아닙니다. 이전 실습에서 얻었던 출력값을 다음 표에 기록합니다.

| 관찰 항목 | 학생 기록 | 이번 교시에서 의미하는 것 |
|---|---|---|
| `ollama ls`의 Size |  | 다운로드된 Model에 대한 저장 용량 정보 |
| 해당 모델의 Parameter 규모 | 확인값 또는 미확인 | 이름/공식 설명에서 확인한 개수 규모 |
| 해당 배포본의 표현 정밀도 | 확인값 또는 미확인 | 4-bit 등 수치 표현 관련 정보 |
| 이론 Weight 크기 | 계산값 | Parameter × bit 수로 얻은 근삿값 |
| `ollama ps`에 표시된 실행 상태 |  | 실행·메모리 적재 상태에 대한 관찰 정보 |

**확인하지 않은 bit 폭을 파일 크기만 보고 역산해 확정하지 않습니다.** 또한 `ollama ps`의 모델 표시와 운영체제 전체 Memory 사용량은 구분해야 합니다.

현재 실습 환경에서 Ollama가 없다면 이 표의 실제 관찰값은 `미검증`으로 남깁니다. 오늘의 Python 계산 실습은 Ollama 없이 완료할 수 있습니다.

---

# 24. 수업 확인 질문과 자주 발생하는 오해

### Q1. 4B Model의 Parameter는 몇 개인가요?

일반적으로 약 40억 개 규모를 뜻합니다. 정확한 개수는 Model 문서를 확인해야 합니다. **4 GB 파일이라는 뜻이 아닙니다.**

### Q2. 4B Weight를 FP32로 저장하면 이론상 얼마나 될까요?

약 40억 × 4 byte = 약 **16 GB**입니다. 이론적 Weight 용량이지 실행에 필요한 전체 Memory가 아닙니다.

### Q3. BF16이 FP16보다 항상 절반의 공간을 사용하나요?

아닙니다. 둘 다 16-bit 표현이므로 같은 원소 수에서는 기본 저장 Byte 수가 같습니다. 두 Format의 **수치 표현 특성은 다를 수 있습니다.**

### Q4. Quantization으로 Parameter 수를 줄이나요?

일반적인 Weight Quantization은 Parameter 수를 줄이기보다 표현 정밀도를 낮춥니다. 일부 Weight·구조를 제거하는 **Pruning**과 구분합니다.

### Q5. 4-bit가 더 작으니 모든 상황에서 더 좋은가요?

아닙니다. 저장량 이외에 출력 품질, Runtime의 지원, 실제 연산 성능 등을 확인해야 합니다.

### Q6. GGUF와 Quantization은 같은 말인가요?

GGUF는 모델 데이터 저장·배포 형식이고 Quantization은 수치 표현을 바꾸는 최적화 기술 범주입니다.

### Q7. Model 파일이 2 GB라면 RAM 2 GB로 꼭 실행되나요?

그 정보만으로는 판단할 수 없습니다. Weight 외에도 Runtime과 계산 중 필요한 메모리가 있을 수 있습니다.

### Q8. `numel() * element_size()`가 정확한 GPU 메모리 사용량인가요?

아닙니다. 주어진 Tensor의 수치 데이터 Byte 계산입니다. 객체·런타임·Cache 등 전체 사용량을 포함하지 않습니다.

### Q9. Training에 필요한 메모리를 4-bit Weight 크기만으로 계산할 수 있나요?

그럴 수 없습니다. Training에는 Gradient, Optimizer State 등 추가 Memory가 필요할 수 있습니다. Fine-tuning 관련 구현은 이후 과정에서 배웁니다.

### Q10. 모델을 비교할 때 오늘 반드시 기록할 것은 무엇인가요?

**가정한 Parameter 규모, bit 폭, 단위(GB/GiB), 이론 Weight 값**을 명시합니다. 실제 파일·Memory 값은 별도로 확인하거나 `미확인`으로 표시합니다.

---

# 25. 강사 진행 순서와 완료 기준

이번 교시는 수식만 보여주고 끝내지 않습니다. 학생이 **같은 수치를 다른 의미로 오해하는 순간**을 잡아내는 것이 중요합니다.

| 순서 | 진행 | 학생이 제출할 결과 |
|---|---|---|
| 도입 | `4B가 4GB인가?` 질문 | Parameter 수와 Byte의 차이 |
| 설명 | 계산 공식과 4B 32/16/8/4-bit 표 | 각 Weight 이론값과 단위 |
| 원리 | Quantization·Pruning·GGUF의 구분 | 세 개념의 차이 한 문장씩 |
| 실습 A | Python 계산기 실행 및 입력 수정 | 출력값·변경 전후 해석 |
| 실습 B | PyTorch Tensor 데이터 Byte 확인 | `numel × element_size` 기록 |
| 판별 활동 | 옳고 그른 주장 수정 | 틀린 주장과 근거 |
| 적용 | 이론 크기/실제 파일/실행 메모리 구분 | 확인/미확인 기록표 |

### 수업 완료로 볼 수 있는 상황

학생은 추가 설명 없이 다음 말을 할 수 있어야 합니다.

> **“4B는 모델의 Parameter 규모이며, 같은 4B여도 FP32와 4-bit로 표현하면 Weight의 이론적 저장 크기가 달라집니다. 하지만 그 계산만으로 실제 다운로드 용량, 전체 실행 메모리, 실행 속도, 모델 품질을 확정할 수는 없습니다.”**

계산값만 외우고 `4B = 4GB`라는 오해가 남아 있다면 **이번 교시의 핵심 목표를 달성한 것이 아닙니다.**

---

# 26. 이번 교시 정리 — 알 수 있는 값과 아직 알 수 없는 값

| 오늘 계산·설명할 수 있게 된 것 | 아직 이 정보만으로 결정할 수 없는 것 |
|---|---|
| Parameter Count × bit 폭으로 구한 Weight 이론값 | 실제 배포 파일의 정확한 크기 |
| FP32·FP16/BF16·8-bit·4-bit의 Byte 관계 | 실제 RAM·VRAM 전체 요구량 |
| Quantization과 Pruning의 개념적 차이 | 모든 작업에서의 품질 차이 |
| GGUF와 Quantization의 역할 차이 | 실제 Runtime·Hardware 호환성 |
| Context·Batch가 추가 Memory에 영향을 줄 수 있다는 점 | 특정 PC에서의 실행 속도와 동시 사용자 처리량 |

**이번 교시의 핵심:**

\[
\text{Parameter Count} \times \text{bit 폭}
\longrightarrow \text{이론적 Weight 저장량}
\]

하지만:

```text
이론적 Weight 저장량
≠ 정확한 다운로드 용량
≠ 전체 Runtime Memory
≠ 모델의 품질 점수
```

---

# 27. 다음 교시 연결 — 계산한 Weight는 실제 컴퓨터에서 어떻게 실행될까?

이번 시간에는 **Weight가 얼마나 큰지**를 계산했습니다. 이제 다음 질문이 남습니다.

> 같은 Weight 크기라도 컴퓨터의 구성에 따라 실행 조건이 왜 달라질까요?

다음 Day3 4교시에서는 **CPU·GPU·RAM·VRAM·Storage가 AI Model 실행 과정에서 각각 어떤 역할을 하는지** 살펴봅니다. 이번 교시에서 구한 Weight 이론값을 입력 정보로 사용하지만, **하드웨어의 실제 배치와 Device 이동**은 다음 시간에 배웁니다.

---

# 참고자료 — 교육과정 원본에 포함된 안내

- PyTorch 공식 Tensor 및 dtype 문서
- Hugging Face Transformers Quantization 문서
- Hugging Face bitsandbytes Quantization 문서
- Ollama 공식 문서
- llama.cpp / GGUF 관련 프로젝트 문서
- 각 Model Family의 공식 Model Card

> 이 목록은 **원본 교육과정에 적힌 참고자료 목록**입니다. 이번 개편에서 목록의 외부 링크, 최신 지원 버전, Quantization 호환성과 실제 모델 크기를 새로 검증한 것은 아닙니다.

# 관련 Wiki Link

- [[Parameter]] · [[Model Size]] · [[dtype]]
- [[FP32]] · [[FP16]] · [[BF16]] · [[INT8]]
- [[Quantization]] · [[Pruning]] · [[GGUF]] · [[bitsandbytes]]
- [[KV Cache]] · [[Context Window]]
- [[RAM]] · [[VRAM]] · [[GPU]]
- [[PyTorch]] · [[Transformers]] · [[Ollama]] · [[Gemma]]
- [[PEFT]] · [[QLoRA]]

# 저장 위치 제안

```text
Academy/
└── 00. 교육과정(curriculum)/
    └── 00. Phase1_Theoretical/
        └── 04. GPT, Ollama, Gemma/
            └── Day3_03교시_Model_Size_Parameter와_Quantization_강의용.md
```
