# Day 1 - 6교시. 현대 AI 개발 생태계와 핵심 라이브러리

> **이번 교시의 핵심 질문**  
> NumPy, pandas, PyTorch, Transformers, OpenAI SDK, Ollama, FastAPI는 모두 AI 개발에서 볼 수 있는 이름입니다. 그런데 **같은 종류의 도구가 아닌 이들을 왜, 언제, 어떻게 선택해야 할까요?**

## 개요

앞선 교시에서는 AI 모델이 학습되는 방식, 현대 생성형 모델의 등장 배경과 출력의 특성을 살펴보았습니다. 특히 4교시에서는 PyTorch가 신경망 개발에 필요한 계산을 지원한다는 사실을, 5교시에서는 사전학습된 모델을 Cloud 또는 Local 환경에서 사용할 수 있다는 사실을 배웠습니다.

이번 시간에는 이 내용을 다시 자세히 설명하지 않습니다. 대신 **개발자가 실제 프로젝트에 필요한 소프트웨어를 고를 때** 판단해야 할 문제를 살펴봅니다. AI를 만드는 데 필요한 수치 계산 도구와 데이터를 다루는 도구, 사전학습 모델을 찾고 사용하는 도구, 모델 실행 환경, 외부 서비스를 호출하는 개발 도구, 그리고 결과를 사용자에게 제공하는 웹 개발 도구는 서로 역할이 다릅니다.

수업을 마치면 새 라이브러리 이름을 외우는 것에서 그치지 않고, *"우리 프로젝트에 지금 필요한 도구인가? 필요한 이유는 무엇인가? 어떤 도구와 연결되는가?"*를 설명할 수 있어야 합니다.

> **학습 범위:** 이번 시간은 **도구의 역할·선택·연결을 이해하는 이론과 작은 로컬 코드 확인**이 중심입니다. 7교시에는 OpenAI SDK를 설치하고 실제 Cloud AI API를 호출하며, 8교시에는 FastAPI·Pydantic으로 AI 결과를 웹 API에 연결합니다. Ollama 설치와 Local Model 실행, Hugging Face 모델 활용의 실제 명령은 뒤 교시에서 다룹니다.

---

## 1. 학습 목표

이번 교시가 끝나면 학생은 다음을 설명하거나 수행할 수 있어야 합니다.

1. **Model, Library, Framework, SDK, API, Runtime/Serving, Hub/Platform**의 역할을 구분한다.
2. **NumPy, pandas, scikit-learn**이 데이터 준비와 Machine Learning에서 담당하는 일을 예제로 구분한다.
3. **PyTorch**가 Model 자체가 아니라 모델을 구성·학습·실행하는 Framework인 이유를 설명한다.
4. **Hugging Face Hub, Transformers, Tokenizers, Datasets, PEFT, Accelerate**의 주요 용도를 구분한다.
5. Model을 선택할 때 **Model Card의 용도·라이선스·한계·실행 조건**을 확인해야 하는 이유를 설명한다.
6. **OpenAI API, OpenAI SDK, httpx**의 차이를 구분하고 Cloud AI 요청 경로에 배치한다.
7. **Ollama와 Gemma**, **Transformers와 Ollama**의 관계를 설명한다.
8. **LangChain과 LlamaIndex**, **FastAPI와 Pydantic**, **React**를 실제 AI 서비스 안의 역할에 맞게 배치한다.
9. 동일한 요구사항에도 **직접 구현과 Library/Framework 도입** 중 적절한 선택을 제안한다.

---

## 2. 먼저, 무슨 문제를 해결하려는지 생각하자

AI 관련 도구가 많아 보이는 이유는 모든 도구가 한 가지 문제를 해결하는 것이 아니기 때문입니다. 예를 들어 개발자가 다음과 같은 일을 한다고 생각해 봅시다.

- CSV 파일에 저장된 데이터를 읽고 필요한 행만 남긴다.
- 이미 준비한 데이터로 예측 모델을 학습한다.
- 다른 개발자가 공개한 사전학습 모델을 찾는다.
- 자신의 컴퓨터에서 모델을 실행해 추론한다.
- 회사에서 제공하는 AI API로 요청을 보내고 응답을 받는다.
- AI가 만든 결과를 검사해 웹사이트에 표시한다.

이 일들은 모두 AI 프로젝트에서 발생할 수 있지만 필요한 도구는 서로 다릅니다. **데이터를 표로 정리하는 프로그램**과 **모델을 실제로 실행하는 프로그램**을 같은 것으로 생각하면 설치부터 설계까지 혼란스러워집니다.

따라서 오늘은 기술 이름을 다음 세 가지 질문에 연결합니다.

1. **무슨 일을 하는가?** 데이터를 준비하는가, 모델을 학습시키는가, 실행하는가, 사용자에게 제공하는가?
2. **무엇을 제공하는가?** 모델 자체인가, 코드 라이브러리인가, 서비스 인터페이스인가, 실행 환경인가?
3. **현재 작업에서 필요한가?** 직접 구현하거나 이미 있는 SDK로 충분한지, 다른 Framework가 추가로 필요한지 판단할 수 있는가?

### 개발 작업을 기준으로 보는 큰 지도

```text
[데이터를 준비하는 작업]
  ├─ NumPy            : 수치 배열과 계산
  ├─ pandas           : 표 형식 데이터 처리
  └─ Datasets         : ML Dataset 로딩·가공

[모델을 학습하거나 직접 다루는 작업]
  ├─ scikit-learn     : 전통적인 ML 알고리즘·평가
  ├─ PyTorch          : Tensor·신경망·자동 미분
  └─ Transformers     : 사전학습 Transformer 모델 활용

[모델을 찾고 배포하는 작업]
  └─ Hugging Face Hub: 모델·Dataset 등의 저장·공유

[추론을 요청하는 작업]
  ├─ OpenAI SDK/API   : 외부 Cloud AI 서비스 접근
  └─ Ollama           : Local Model 실행·Serving

[사용자 서비스를 만드는 작업]
  ├─ FastAPI          : Backend Web API
  ├─ Pydantic         : 데이터 구조·타입 검증
  ├─ httpx            : HTTP 요청을 보내는 Client
  ├─ React            : 사용자 화면
  └─ LangChain / LlamaIndex: 복합 LLM 처리 흐름 구성 시 검토
```

이 지도는 **어떤 프로젝트든 위 도구를 전부 설치해야 한다**는 목록이 아닙니다. 필요에 따라 일부만 선택하며, 기능이 겹치거나 여러 역할에 활용되는 도구도 있습니다. 특히 **모델 개발 경로**와 **이미 만들어진 모델을 사용해 애플리케이션을 만드는 경로**는 서로 다른 선택지입니다.

---

## 3. 이름이 아니라 소프트웨어의 종류를 구분하자

처음 나오는 용어를 정확히 짚고 넘어가겠습니다.

| 용어 | 쉬운 설명 | 이번 강의에서의 예 |
|---|---|---|
| **Model(모델)** | 입력에 대해 학습된 계산을 수행하는 대상 | GPT 계열, Gemma 계열의 실제 모델 |
| **Library(라이브러리)** | 프로그램에서 불러다 쓰는 재사용 가능한 기능 | NumPy, pandas, httpx |
| **Framework(프레임워크)** | 모델이나 애플리케이션을 구성하는 데 필요한 기능·구조를 폭넓게 제공 | PyTorch, FastAPI |
| **SDK(Software Development Kit)** | 특정 서비스·플랫폼 기능을 코드에서 이용하기 편리하게 제공하는 개발 도구 모음 | OpenAI Python SDK |
| **API(Application Programming Interface)** | 다른 소프트웨어에 기능을 요청하거나 사용하기 위해 공개한 인터페이스 | Cloud AI가 제공하는 HTTP API |
| **Runtime / Serving** | 모델을 실제로 실행하고 추론 요청을 처리할 수 있게 하는 환경·기능 | Ollama |
| **Hub / Platform** | 모델·Dataset 등 자산을 모아 검색·공유·배포하는 곳 | Hugging Face Hub |

이 용어들은 같은 층에 놓인 경쟁 제품 이름이 아닙니다. 예를 들어 **Gemma 모델**을 **Ollama 실행 환경**에서 사용할 수 있고, 개발자는 **FastAPI로 만든 서버**에서 그 모델에 요청을 보낼 수 있습니다. 이 세 가지의 관계는 `모델 / 실행 환경 / 웹 서버`이지 `세 개의 AI 모델`이 아닙니다.

또한 Library와 Framework의 경계는 실제 사용 맥락에 따라 유연하게 표현되기도 합니다. 중요한 것은 사전에 적힌 분류를 암기하는 것이 아니라 **해당 도구가 제공하는 기능과 맡길 책임을 파악하는 것**입니다.

**강사 질문:** “OpenAI SDK를 설치하면 내 컴퓨터에 GPT 모델이 설치되나요?”  
**예상 답변:** 아닙니다. SDK는 Cloud AI 서비스가 제공하는 API를 **호출하기 위한 개발 도구**입니다. 모델을 로컬에 설치하는 동작과 다릅니다.

---

## 4. NumPy — 수치 배열을 계산하는 도구

AI 모델은 내부적으로 수치 계산을 다룹니다. 데이터의 특징이 숫자로 표현되어 있다면 숫자들을 한꺼번에 저장하고 계산할 방법이 필요합니다. 이때 자주 사용하는 Python 라이브러리가 **NumPy**입니다.

Python의 `list`로도 숫자를 저장할 수 있지만, NumPy의 `ndarray`는 같은 종류의 수치 데이터를 배열로 다루고 계산하는 데 필요한 기능을 제공합니다. `ndarray`는 NumPy가 제공하는 **다차원 배열 자료 구조**입니다.

### 4-1. 원본 강의의 점수 예제

```python
import numpy as np

scores = np.array([80, 90, 70, 100])

print(scores)
print(scores.mean())
print(scores.shape)
```

`np.array(...)`는 입력한 숫자를 NumPy 배열로 만듭니다. `scores.mean()`은 그 값들의 평균을 계산합니다. `.shape`는 배열이 어떤 크기로 구성되어 있는지 보여줍니다.

**예상 출력**

```text
[ 80  90  70 100]
85.0
(4,)
```

여기서 `(4,)`는 숫자 4개가 들어 있는 **1차원 배열의 크기**를 뜻합니다. 새로운 AI 모델을 학습한 것은 아니며, **모델의 입력이나 계산에 사용할 수치 데이터를 다루는 도구**를 확인한 것입니다.

### 4-2. AI 개발에서 왜 필요할까?

수치 배열이 한 줄에 4개가 아니라 수천 개의 행과 수백 개의 Feature로 늘어날 수 있습니다. NumPy는 이런 데이터를 수치 연산으로 다루는 Python 생태계의 중요한 기반입니다. 대표적으로 배열 연산, 선형대수, 통계 계산, 모양 변경(reshape) 등의 기능을 제공합니다.

다만 **NumPy가 곧 Machine Learning Model은 아닙니다.** 배열을 계산하는 기능과 그 계산을 이용해 학습하는 알고리즘은 구분해야 합니다.

---

## 5. pandas — 표 형태의 데이터가 필요할 때

**pandas**는 행과 열로 이루어진 데이터를 정리하고 분석할 때 사용합니다. 핵심 자료 구조로는 `Series`와 `DataFrame`이 있습니다. 처음에는 `DataFrame`을 **열마다 이름이 있는 표 형태의 데이터**라고 생각하면 됩니다.

원본의 문서 정보 예제를 그대로 살펴보겠습니다.

```python
import pandas as pd

df = pd.DataFrame(
    {
        "document": ["a.pdf", "b.pdf", "c.pdf"],
        "pages": [10, 20, 5],
        "category": ["report", "manual", "report"],
    }
)

print(df)
print(df["pages"].mean())
```

**예상 출력**

```text
  document  pages category
0    a.pdf     10   report
1    b.pdf     20   manual
2    c.pdf      5   report
11.666666666666666
```

`document`, `pages`, `category`는 **열 이름**입니다. 한 행은 문서 하나의 정보를 나타냅니다. `df["pages"]`는 `pages` 열을 선택하며, 이어서 평균을 계산할 수 있습니다.

이 작업은 모델의 정답을 예측하는 작업이 아닙니다. **모델을 사용하기 전 데이터를 점검·정리하는 작업**과 더 가깝습니다.

### 5-1. NumPy와 pandas의 차이를 실제 질문으로 구분하기

| 개발자가 하려는 일 | 먼저 검토할 도구 | 이유 |
|---|---|---|
| 숫자 목록의 평균과 배열 크기 계산 | NumPy | 수치 배열 연산에 적합 |
| 문서별 페이지 수·종류를 표로 정리 | pandas | 열 이름이 있는 표를 다루기 편리 |
| CSV 파일을 읽어 필요한 열만 선택 | pandas | 표 데이터의 입출력·선택·가공을 지원 |
| 정리한 수치 데이터를 ML 알고리즘에 전달 | pandas·NumPy·ML 라이브러리 등 | 데이터 형태와 사용하는 모델에 따라 연결 방식 선택 |

NumPy와 pandas는 반드시 둘 중 하나만 골라야 하는 경쟁 관계가 아닙니다. 하나의 데이터 처리 과정에서 함께 활용할 수 있습니다.

**학생 확인:** 문서의 `category` 열을 기준으로 문서 종류를 확인하려는 개발자에게 PyTorch부터 설치하라고 할 필요가 있을까요?  
**예상 답변:** 없습니다. 지금 해결할 문제는 **표 데이터를 확인하는 것**이므로 pandas 같은 도구부터 검토할 수 있습니다.

---

## 6. scikit-learn — 학습 알고리즘과 평가가 필요할 때

**scikit-learn**은 Python에서 Machine Learning 모델을 학습·평가하는 데 널리 사용하는 라이브러리입니다. 분류(Classification), 회귀(Regression), 군집화(Clustering), 전처리(Preprocessing), 학습·평가용 데이터 분할, 성능 평가 지표(Metrics), Pipeline 등의 기능을 제공합니다.

3교시에서는 이미 `LinearRegression` 예제를 사용해 **`fit()`은 Training**, **`predict()`는 Inference**라는 차이를 확인했습니다. 이 코드를 다시 실행하거나 같은 숫자를 바꿔 반복하지 않겠습니다. 이번에는 **도구가 개발 과정에서 어디를 담당하는지**를 살펴봅니다.

```text
학습에 사용할 데이터
       ↓
필요한 전처리·데이터 분할
       ↓
scikit-learn의 ML 알고리즘 선택
       ↓
fit() — 모델 학습
       ↓
모델 평가·새 입력에 predict()
```

여기서 중요한 것은 도구를 설치했다고 모든 과정이 자동으로 안전하게 수행되는 것이 아니라는 점입니다. 개발자는 **학습할 문제**, **사용할 입력 정보**, **결과를 판단할 평가 기준**을 결정해야 합니다. 모델의 일반화 능력과 데이터 분할의 상세한 원리는 Phase 2에서 학습합니다.

### 6-1. scikit-learn과 PyTorch 중 어느 것을 사용할까?

원본에는 `Linear Regression`, `Decision Tree`, `Random Forest`, `SVM`, `Clustering` 등이 scikit-learn과 연결되는 작업으로 제시되어 있습니다. 이런 알고리즘과 평가 기능을 편리하게 사용하려면 scikit-learn을 고려할 수 있습니다.

반대로 **Tensor 연산과 신경망의 층을 직접 구성하고 Gradient를 계산**하는 개발 작업이라면 PyTorch 같은 Framework가 중요합니다. 어느 도구가 항상 더 우수하다는 관계가 아니라 **해결하려는 문제와 구현 방식의 차이**입니다.

---

## 7. PyTorch — 신경망을 만드는 계산 기능

4교시에서는 Neural Network의 내부 계산과 `Tensor`를 이미 살펴보았습니다. 여기서 Tensor의 정의와 배열 생성 코드를 처음부터 반복할 필요는 없습니다. 6교시에서는 **개발자가 PyTorch를 선택하는 이유**만 명확히 연결합니다.

신경망을 직접 개발하려면 다음 작업을 처리해야 할 수 있습니다.

- Tensor 형태의 데이터와 Parameter를 관리한다.
- 신경망의 층(Layer)을 구성하고 입력에 대해 계산한다.
- 예측값과 정답 사이의 차이 등을 이용해 손실(Loss)을 계산한다.
- 자동 미분(Automatic Differentiation)을 사용해 Gradient를 계산한다.
- Optimizer를 통해 Parameter를 조정한다.
- 필요하면 CPU 또는 GPU 등 지원되는 실행 환경을 활용한다.
- 학습한 Model을 저장하거나 불러온다.

PyTorch는 위와 같은 기능을 제공하는 Machine Learning / Deep Learning Framework입니다. 신경망의 계산을 바닥부터 전부 구현해야 하는 부담을 줄일 수 있습니다.

| 구분 | PyTorch | GPT·Gemma 계열의 모델 |
|---|---|---|
| 무엇인가? | Framework | Model / Model Family |
| 무엇을 제공하는가? | Tensor 연산, 신경망 구성, 학습·실행에 필요한 기능 | 이미 학습되었거나 학습 대상으로 사용할 계산 구조·가중치 등 |
| 개발자의 관심 | 어떻게 계산하고 학습·실행할 것인가 | 어떤 모델이 어떤 작업에 적합한가 |

**PyTorch를 설치했다고 GPT나 Gemma 모델이 자동으로 준비되는 것은 아닙니다.** Framework와 학습된 모델의 자산은 별도로 구분해야 합니다.

---

## 8. Hugging Face — 하나의 라이브러리가 아닌 생태계

지금까지는 직접 숫자와 표를 계산하거나 모델을 학습하는 도구를 살펴보았습니다. 하지만 이미 학습된 모델을 사용하려면 **그 모델을 어디에서 찾고 어떻게 불러올지**도 중요합니다.

`Hugging Face`는 이 과정에서 자주 만나게 되는 이름입니다. 중요한 점은 이것이 **Python 라이브러리 하나의 이름으로만 끝나지 않는다**는 것입니다.

| 이름 | 담당하는 문제 | 수업에서 기억할 구분 |
|---|---|---|
| **Hugging Face Hub** | Model·Dataset 등의 자산 저장, 검색, 공유·배포 | 모델을 **찾는 플랫폼** |
| **Transformers** | 다양한 사전학습 Transformer 모델과 Tokenizer를 코드에서 활용 | 모델을 **불러와 활용하는 Library** |
| **Tokenizers** | 텍스트를 Token으로 나누고 필요한 ID 표현으로 변환하는 처리 | 텍스트 **입력 처리 도구** |
| **Datasets** | Dataset 로딩, 변환·가공 | **학습·평가 데이터** 처리 |
| **PEFT** | 효율적인 Parameter 조정 기반의 Fine-tuning 지원 | 모델 **적응·미세조정** 지원 |
| **Accelerate** | 하드웨어와 분산 환경의 학습·실행 코드 처리 지원 | **실행 환경** 지원 |

하나의 작업에서 이 도구들 중 여러 개를 함께 쓸 수 있지만, 모든 프로젝트에서 전부 필요한 것은 아닙니다.

### 8-1. Hub와 Transformers는 어떻게 연결될까?

```text
Hugging Face Hub
    └─ 모델 저장소·파일·설명 문서
                ↓ 필요한 모델 선택
       Transformers 등의 도구
                ↓ 모델과 Tokenizer 활용
           Python 프로그램
                ↓
               추론
```

Hub는 모델 자체를 실행하는 Python Framework와 같지 않습니다. **모델 자산을 제공하는 장소**와 **모델을 사용하는 코드** 사이의 차이를 기억하면 됩니다.

한편 `Transformer`는 4교시에서 배운 **신경망 구조(Architecture)**이고, `Transformers`는 이 이름을 사용하는 **Hugging Face 라이브러리**입니다. 이름이 비슷해도 같은 개념이 아닙니다.

### 8-2. Tokenizers와 Datasets는 언제 중요할까?

5교시에서 Token이 무엇인지 배웠습니다. 여기서는 Token의 정의를 반복하기보다 프로그램에서 어떤 처리 도구가 필요한지 봅니다.

```text
사용자가 입력한 Text
        ↓
Tokenizer로 Token·ID 표현 처리
        ↓
모델에 전달
```

반면 학습용 Dataset을 파일이나 저장소에서 읽어 필요한 형태로 가공하려는 경우에는 `Datasets` 라이브러리를 검토할 수 있습니다. **텍스트를 모델 입력 단위로 바꾸는 일**과 **학습할 데이터 묶음을 관리하는 일**은 서로 다릅니다.

### 8-3. PEFT와 Accelerate를 구분하기

`PEFT`는 **Parameter-Efficient Fine-Tuning**에 관련된 기능을 제공합니다. 예를 들어 이후 Fine-tuning 수업에서 만나게 되는 `LoRA` 같은 접근을 지원합니다. 모든 Parameter를 같은 방식으로 업데이트하는 대신 효율적으로 모델을 적응시키는 방법들과 연결됩니다.

`Accelerate`는 다양한 하드웨어·분산 환경에서 학습이나 실행 코드를 다루는 일을 돕습니다. 따라서 다음처럼 구분할 수 있습니다.

- **PEFT:** 모델을 **어떻게 효율적으로 적응시킬 것인가**의 문제
- **Accelerate:** 학습·실행 코드를 **어떤 하드웨어 환경에서 수행할 것인가**의 문제

이번 시간에 두 라이브러리의 API나 LoRA 계산을 외울 필요는 없습니다. 필요한 상황이 올 때 이름을 다시 찾을 수 있으면 충분합니다.

---

## 9. Hugging Face Hub에서 Model Card를 읽는 이유

**Model Card**는 모델의 용도·특징·제약 등을 설명하는 문서입니다. 다운로드할 수 있는 모델이 있다고 해서 내 프로젝트에 적합하거나 아무 제약 없이 사용할 수 있다는 뜻은 아닙니다.

원본 강의에서 제시한 항목을 질문으로 바꾸어 보겠습니다.

| 확인할 항목 | 실제 선택 전에 던질 질문 |
|---|---|
| 용도·Task | 이 모델은 분류용인가, 대화형 생성용인가, 다른 작업용인가? |
| 작성자·출처 | 누가 만들고 배포했는가? |
| License | 우리 프로젝트의 사용 목적에 허용되는 라이선스인가? |
| 입력·출력 | 텍스트만 받는가, 이미지도 받는가? 어떤 결과를 반환하는가? |
| 크기·하드웨어 | 사용하려는 장치의 메모리·계산 자원으로 실행할 수 있는가? |
| 언어·구성 | 필요한 언어를 지원하는가? 사용 방법은 무엇인가? |
| 한계·주의사항 | 모델이 잘하지 못하거나 사용에 주의해야 할 조건은 무엇인가? |

5교시에서 Model Family와 Model Variant가 서로 다른 범위임을 배웠습니다. 따라서 **Family 이름이 같다고 모델의 크기·입력 유형·대화 적합성·라이선스까지 같다고 생각하면 안 됩니다.**

### 강사 활동 — 문서 종류를 자동으로 분류하는 모델을 고른다면?

5절의 `DataFrame`에는 `a.pdf`, `b.pdf`, `c.pdf`라는 파일명과 `report`, `manual`이라는 문서 종류가 있었습니다. 이번에는 단순히 표를 보는 수준을 넘어, **새로 들어오는 문서의 종류를 자동으로 분류**하는 기능을 만든다고 생각해 봅시다.

> “문서가 들어왔을 때 `report`인지 `manual`인지 예측하려고 합니다. Model Hub에서 눈에 띄는 모델을 바로 다운로드하면 될까요?”

학생들에게 모델을 찾기 전에 무엇부터 정해야 하는지 물어봅니다.

**예상 접근:** 먼저 모델에 줄 **입력 데이터**가 무엇인지 정해야 합니다. 파일명만 사용할 것인지, 문서의 실제 텍스트를 추출해 사용할 것인지에 따라 필요한 모델과 데이터 처리 흐름이 달라집니다. 분류할 **범주와 기대 출력**도 명확히 정해야 합니다. 그다음 Model Card에서 모델의 Task, 지원 입력, 사용 방법, License, 필요한 Hardware와 한계를 확인합니다.

**강사 포인트:** `DataFrame`은 문서 정보를 정리하는 도구이고, Hub는 모델 후보를 찾는 곳입니다. 문서 종류를 예측하는 Model과 실제 서비스에서 문서를 읽고 요청을 보내는 코드가 추가로 필요할 수도 있습니다. **자료를 표로 저장하는 일과 그 자료를 학습·추론에 사용하기 적합하게 준비하는 일은 동일하지 않습니다.**

여기서 모델 하나를 실제로 선정하거나 분류 정확도를 단정하지는 않습니다. 이 원본 자료에는 구체적인 모델 후보별 최신 성능·라이선스·요구 메모리가 제시되어 있지 않으므로, 실제 선택과 실행 검증은 별도 단계입니다.

---

## 10. Cloud AI — OpenAI API와 SDK의 역할

이미 학습된 모델을 직접 다운로드하고 실행할 필요가 없는 프로젝트도 있습니다. 외부 AI Provider(서비스 제공자)가 모델을 실행하고 **API**를 제공하면 우리 애플리케이션이 그 기능을 사용할 수 있습니다.

이때 개발자가 알아야 할 차이는 **서비스가 제공하는 인터페이스**와 **그 인터페이스를 사용하는 개발 도구**입니다.

```text
우리 Python 코드
        ↓
OpenAI Python SDK  ← Python에서 호출을 쉽게 다루는 도구
        ↓
OpenAI API         ← 외부 서비스가 제공하는 인터페이스
        ↓
Cloud AI Service   ← 서버 측에서 모델 추론 수행
        ↓
Response           ← 결과를 받아 우리 프로그램에서 처리
```

SDK는 API 요청을 구성하고 인증 정보나 응답 객체를 다루는 작업을 편리하게 해줄 수 있습니다. **SDK를 사용하지 않고 HTTP API를 직접 호출할 수도 있습니다.** 따라서 `SDK = API`도 아니고 `SDK = Model`도 아닙니다.

### 10-1. SDK가 반드시 필요한가?

원본 강의는 `http_client.post(...)`와 같은 **HTTP 요청 개념 예시**를 보여 줍니다. HTTP Client Library를 이용해 요청을 직접 구성할 수도 있다는 뜻입니다. 하지만 실제 인증 방식과 요청 데이터 형식은 각 Provider의 API 계약에 따라 달라집니다.

여기서는 **'가능한 경로'**만 구분합니다.

```text
경로 A: Python 코드 → 공식 SDK → Provider API
경로 B: Python 코드 → HTTP Client → Provider API
```

둘 중 하나가 항상 정답은 아닙니다. 공식 SDK가 제공하는 기능, 필요한 요청 형태, 유지보수 부담을 고려해 선택합니다.

**7교시에서 할 일:** 실제 사용 가능한 API Key와 환경 변수를 준비하고 OpenAI SDK로 요청을 전송합니다. **이번 교시에서는 API Key를 만들거나 외부 서비스를 실행하지 않습니다.**

---

## 11. httpx는 AI 모델도, AI 전용 SDK도 아니다

`httpx`는 Python에서 HTTP 요청을 보내는 **HTTP Client Library**입니다. 외부 AI 서비스뿐 아니라 검색 API, OCR API, 내부 업무 서비스 등 다른 HTTP 기반 시스템과 통신할 때에도 사용할 수 있습니다.

```text
Python 프로그램
     ↓
httpx
     ↓
HTTP 요청
     ↓
외부 API 서버
```

API와 통신한다는 이유만으로 그 라이브러리가 AI를 학습하거나 추론하는 것은 아닙니다. **AI 프로젝트에서 자주 사용한다는 것**과 **AI 전용 도구라는 것**도 구별해야 합니다.

### 도구 선택 연습

- “공식 SDK가 제공하는 방식으로 Cloud AI를 호출하겠다” → **Provider SDK** 검토
- “사내 서비스가 공개한 일반 HTTP Endpoint를 요청하겠다” → **httpx 같은 HTTP Client** 검토

여기서는 실제 URL·인증 값·API 요청 코드를 작성하지 않습니다. 네트워크 호출과 예외 처리는 7교시의 실습과 연결합니다.

---

## 12. Local AI — Ollama는 무엇을 담당할까?

외부 Cloud 서비스 대신 직접 관리하는 환경에서 모델을 실행할 수도 있습니다. 이때 **Ollama** 같은 도구는 Local Model을 실행하고 추론 요청을 받을 수 있도록 하는 **Runtime/Serving 계층**을 담당합니다.

```text
우리 Application
       ↓
Ollama가 제공하는 실행·Serving 기능
       ↓
실행할 Local Model (예: Gemma 계열)
       ↓
CPU / GPU 등 계산 자원
```

이 그림에서는 역할이 세 가지로 나뉩니다.

- **Application:** 입력을 받고 모델 결과를 사용합니다.
- **Ollama:** 모델을 실행하고 요청을 처리하도록 돕습니다.
- **Gemma 계열 모델:** 실제로 입력을 처리해 출력에 관여하는 모델 자산입니다.

따라서 `Ollama = Gemma`가 아닙니다. 모델을 바꾸어도 실행 도구의 역할은 구분해서 생각할 수 있습니다. 실제로 어떤 모델이 설치·실행 가능한지는 사용하는 환경과 모델의 지원 조건을 확인해야 합니다.

### Transformers와 Ollama의 차이

| 구분 | Transformers를 활용하는 경우 | Ollama를 활용하는 경우 |
|---|---|---|
| 개발자의 주요 접점 | Python Library의 모델·Tokenizer 기능 | Model Runtime / Serving 기능 |
| 중심 관심 | 모델 구성 요소를 코드에서 직접 다루는 방식 | 로컬 실행·추론 요청을 다루는 방식 |
| 모델 자체인가? | 아님 | 아님 |
| 대표적으로 연결되는 대상 | 사전학습 모델·PyTorch 등 지원 Backend | Local Model·실행 하드웨어 |

두 방식은 모델을 활용하는 **접점과 책임**이 다릅니다. 어느 쪽이 무조건 빠르거나 쉬운지는 일반화하지 않습니다. Local Model 설치와 실제 추론은 이후 교시에서 다룹니다.

---

## 13. LangChain과 LlamaIndex — 복잡해진 작업을 연결하는 도구

간단한 애플리케이션이라면 요청을 한 번 보내고 결과를 받는 것만으로 충분할 수 있습니다. 이 경우에는 공식 SDK나 직접 작성한 서비스 코드로 시작할 수 있습니다.

하지만 다음과 같은 작업이 많아지면 코드의 책임이 복잡해질 수 있습니다.

- 사용자 질문과 지시문(Prompt)을 관리한다.
- 대화 상태나 처리 단계를 연결한다.
- 외부 Document에서 정보를 찾아 모델에 전달한다.
- 여러 Tool이나 외부 API 사용 단계를 조합한다.
- 결과를 다음 단계로 넘기기 위한 Workflow를 구성한다.

**LangChain**은 LLM을 활용하는 프로그램에서 Model·Prompt·Tool·Retrieval·Workflow 등의 구성 요소를 연결하는 기능을 제공하는 Framework 생태계입니다.

**LlamaIndex**는 문서 등 외부 데이터를 AI Application과 연결하고 검색·조회(Retrieval) 중심의 처리 흐름을 구성할 때 관련 기능을 제공하는 Framework입니다.

| 고민 중인 문제 | 살펴볼 도구·방식 | 주의할 점 |
|---|---|---|
| 모델에 한 번 질문하고 답을 받기 | SDK 또는 직접 HTTP 호출 | Framework를 추가하지 않아도 가능 |
| 여러 모델 호출이나 Tool을 연결하는 흐름 | 직접 코드 또는 LangChain 등 | 먼저 각 단계의 책임을 이해해야 함 |
| 문서를 준비하고 관련 정보를 찾아 LLM에 제공 | 직접 구현 또는 LlamaIndex 등 | Retrieval과 RAG의 원리를 대체하는 것은 아님 |

### Framework를 먼저 외우면 해결되는가?

아닙니다. `chain`, `retriever`, `agent` 같은 이름과 사용법만 외우면 왜 필요한지 판단하기 어렵습니다. **먼저 어떤 데이터를 어디서 받아 어느 모델에 제공하고, 무엇을 검증해야 하는지**를 설명할 수 있어야 합니다.

이후 Phase 2에서는 Retrieval·Embedding·RAG와 Agent의 원리를 공부하고, 그때 Framework가 무엇을 편리하게 해주는지 더 구체적으로 판단합니다. 여기서는 사용법과 API를 미리 배우지 않습니다.

---

## 14. FastAPI·Pydantic·React는 AI를 만들지 않는데 왜 필요할까?

AI 모델의 출력을 사용자가 이용하는 서비스로 만들려면 기존 소프트웨어 개발 도구가 필요할 수 있습니다. 이 도구들의 역할도 서로 다릅니다.

| 도구 | 맡는 역할 | AI 모델인가? |
|---|---|---|
| **FastAPI** | Python으로 HTTP Endpoint를 만들고 요청·응답을 처리하는 Backend Web Framework | 아니요 |
| **Pydantic** | 입력과 출력의 데이터 구조, 타입 등의 검증을 돕는 Library | 아니요 |
| **React** | 브라우저에서 사용자 인터페이스를 만드는 JavaScript Library | 아니요 |

### 14-1. Pydantic으로 무엇을 검사할 수 있을까?

원본 강의의 `SummaryResult` 예제를 확인하겠습니다.

```python
from pydantic import BaseModel

class SummaryResult(BaseModel):
    title: str
    summary: str
    keywords: list[str]
```

여기서 `SummaryResult`는 결과 데이터가 가져야 할 **형태에 관한 약속(Schema)**입니다.

- `title`: 문자열이어야 합니다.
- `summary`: 문자열이어야 합니다.
- `keywords`: 문자열 목록이어야 합니다.

이처럼 프로그램이 기대하는 데이터 구조를 정의하면 실제 AI 출력이 그 구조에 적합한지 검사하는 데 활용할 수 있습니다.

단, **Schema Validation을 통과했다는 것만으로 요약 내용이 사실에 맞는다는 뜻은 아닙니다.** 5교시에서 배운 출력 내용의 정확성 검토와 Pydantic의 구조 검증은 다른 책임입니다.

### 14-2. 웹 서비스와 모델 연결은 어디에서 일어날까?

React는 화면을 담당하고 FastAPI는 HTTP 요청과 서비스 처리를 담당합니다. AI 모델을 호출하거나 Ollama 같은 실행 환경과 통신하는 코드는 필요에 따라 Backend의 Service 영역에 둘 수 있습니다.

이번에는 이 구조를 자세히 구현하지 않습니다. **8교시에서 FastAPI Route와 AI Service 코드를 분리하고 Pydantic으로 결과를 검증하는 실습**을 진행합니다.

---

## 15. 도구가 많다고 좋은 구조는 아니다

새로운 라이브러리를 발견할 때마다 프로젝트에 설치한다고 해서 기능이 더 좋아지는 것은 아닙니다. 원본 강의에서 강조한 것처럼 Dependency(프로그램이 의존하는 외부 패키지)가 늘면 다음 사항을 고려해야 합니다.

| 고려 사항 | 개발 과정에서 생길 수 있는 일 |
|---|---|
| Learning Cost | 도구의 구조와 사용법을 추가로 학습해야 함 |
| Version Compatibility | 다른 라이브러리나 실행 환경과 버전이 맞아야 함 |
| Security Updates | 취약점 대응과 업데이트가 필요함 |
| Deployment Size | 설치 파일과 실행 환경이 커질 수 있음 |
| Debugging Complexity | 문제가 발생했을 때 원인 분석 경로가 늘어남 |
| Maintenance | 사용법 변경과 코드 유지보수 비용이 생길 수 있음 |

### 선택 순서

```text
현재 기능과 문제 정의
         ↓
직접 구현 또는 이미 사용 중인 도구로 해결 가능한가?
         ↓
새 Library/Framework를 추가하면 어떤 문제가 해결되는가?
         ↓
설치·운영·유지보수 비용을 감수할 가치가 있는가?
         ↓
필요한 도구만 선택
```

예를 들어 **Cloud AI에 텍스트를 한 번 전달하고 응답을 받는 기능**만 필요한데 복잡한 Workflow Framework부터 도입할 필요는 없습니다. 반대로 수많은 단계와 데이터 조회 흐름을 직접 반복 구현해야 한다면 적절한 Framework의 가치가 커질 수 있습니다.

**강사 질문:** “유명한 AI Framework를 사용하면 모델이 자동으로 정확해질까요?”  
**예상 답변:** 아닙니다. Framework가 해결하는 것은 주로 **연결·개발 방식의 문제**입니다. 모델 결과의 정확성은 작업 조건과 평가·검증에 따라 따로 판단해야 합니다.

---

## 16. 강사 시연 — 요구사항에서 필요한 도구만 고르기

원본에서 소개한 작업들을 **하나의 거대한 서비스 구조도**에 모두 억지로 넣지 않고, 요구사항별로 나누어 보겠습니다. 학생들이 각 도구를 구별하는 데 초점을 맞춘 시연입니다.

### 상황 A. 문서 목록을 표로 확인한다

> “문서 파일명, 페이지 수, 종류가 정리되어 있습니다. 페이지 수 평균을 계산하고 문서 목록을 확인해 주세요.”

**필요한 것:** pandas를 이용해 표를 읽고 확인할 수 있습니다. 수치 배열 중심 계산이 필요해지면 NumPy도 고려할 수 있습니다. 지금 요구사항만으로는 LLM API나 Ollama가 필요하지 않습니다.

**강사 설명:** `데이터 처리`라는 문제에 `모델 Serving` 도구를 선택하면 역할을 잘못 짝지은 것입니다.

### 상황 B. 이미 학습된 모델을 찾아 로컬에서 활용한다

> “사전학습된 모델을 찾아 필요한 환경에서 실행하고 싶습니다.”

**검토할 것:** Hugging Face Hub 등에서 모델과 Model Card를 확인합니다. Python에서 모델을 직접 다룰지, Ollama 같은 Runtime을 이용할지 선택합니다. 모델의 실제 지원 조건과 하드웨어 환경을 확인하기 전에는 실행할 수 있다고 확정하지 않습니다.

**강사 설명:** 모델을 **찾는 일**, 모델을 **선택하는 일**, 모델을 **실행하는 일**은 별도의 판단입니다.

### 상황 C. AI 기능을 웹에서 제공한다

> “사용자가 화면에서 요청하면 외부 AI 서비스를 사용해 결과를 보여주고 싶습니다.”

**검토할 것:** 화면이 필요하다면 React, Backend가 필요하다면 FastAPI를 사용할 수 있습니다. 외부 AI 기능은 Provider API와 SDK로 접근할 수 있으며, 응답 데이터의 구조 검증에는 Pydantic 등을 활용할 수 있습니다.

**강사 설명:** 이 상황에서 필요한 것은 모든 AI 라이브러리를 배우는 것이 아니라 **각 구성 요소가 무엇을 책임지는지** 정하는 것입니다. 실제 API 호출 코드는 7교시에서, Backend와 결과 검증 연결은 8교시에서 작성합니다.

---

## 17. 학생 활동 ① — 도구를 분류하고 근거를 말하기

학생들에게 다음 이름을 제시합니다.

```text
NumPy / PyTorch / Gemma / Transformers / Hugging Face Hub
OpenAI SDK / Ollama / FastAPI / Pydantic / LangChain
```

**활동 방법:** 단순히 명칭을 암기해 쓰는 대신 `어떤 종류인가?`, `어떤 문제를 해결하는가?`를 함께 말하도록 합니다.

| 항목 | 정답에 포함되어야 할 핵심 |
|---|---|
| NumPy | 수치 배열·계산 Library |
| PyTorch | 신경망 구성·학습·실행을 지원하는 Framework |
| Gemma | Model Family |
| Transformers | 사전학습 Transformer 모델 활용 Library |
| Hugging Face Hub | Model·Dataset을 저장·공유하는 Platform |
| OpenAI SDK | Provider API를 편리하게 사용하는 개발 도구 |
| Ollama | Local Model Runtime / Serving |
| FastAPI | Python Backend Web Framework |
| Pydantic | 데이터 구조·타입 검증 Library |
| LangChain | 복합 LLM Application 구성에 사용하는 Framework 생태계 |

**추가 질문:** “Transformers를 사용하면 반드시 Ollama를 설치해야 하나요?”  
**예상 답변:** 아닙니다. 목적과 실행 방식이 다르며, 하나를 사용하기 위해 다른 하나를 항상 설치해야 하는 관계는 아닙니다.

---

## 18. 학생 활동 ② — 개발 경로를 구별하기

다음 빈칸에 들어갈 도구의 **역할**부터 생각해 보게 합니다. 정답을 한 제품의 이름으로만 제한하지 않습니다.

### 문제 1. Cloud AI 서비스를 이용하는 Python 프로그램

```text
Python 프로그램
     ↓
[                  ]
     ↓
Cloud AI API
     ↓
외부 AI Service
```

**예상 답변:** 공식 **SDK** 또는 직접 작성한 **HTTP Client 호출 계층**. 예를 들어 OpenAI SDK를 사용할 수 있습니다.

### 문제 2. 자체 환경에서 모델을 실행하는 프로그램

```text
Application
     ↓
[                  ]
     ↓
Local Model
     ↓
Hardware
```

**예상 답변:** Local Model **Runtime / Serving**. 예로 Ollama를 고려할 수 있습니다.

### 문제 3. 모델 자산과 Python 코드 사이

```text
Hugging Face Hub의 모델 자산
     ↓
[                  ]
     ↓
Python에서 사전학습 모델 활용
```

**예상 답변:** **Transformers** 등 모델을 불러와 활용하는 Library가 들어갈 수 있습니다.

**강사 정리:** 세 문제 모두 AI와 관련되지만 서로 다른 도구를 요구합니다. 첫 번째는 *외부 서비스 접근*, 두 번째는 *로컬 실행*, 세 번째는 *모델 자산을 코드에 연결*하는 문제입니다.

---

## 19. 학생 활동 ③ — 꼭 추가해야 하는 라이브러리일까?

학생들에게 다음 상황을 제시하고, 새 Dependency를 추가할지 여부를 이유와 함께 설명하게 합니다.

| 상황 | 검토할 방향 | 학생이 답할 핵심 근거 |
|---|---|---|
| 단순한 AI API 호출 하나를 구현한다 | 기존 SDK로 충분한지 우선 확인 | 복잡한 Workflow Framework가 필수는 아님 |
| 문서 표의 평균과 범주를 확인한다 | pandas·NumPy 등의 데이터 도구 | 모델 학습이나 AI API가 필수는 아님 |
| 공개 모델로 추론하려 한다 | Model Card, 실행 방식, Runtime 검토 | 모델 자산과 실행 도구는 다름 |
| 여러 문서 검색·Tool 호출 단계를 연결해야 한다 | 직접 구현과 LangChain·LlamaIndex 등의 도입 비교 | 추상화의 이득과 의존성 비용을 함께 판단 |

**학생 활동의 성공 기준:** 특정 도구 이름을 말한 뒤 그 도구가 **어떤 책임을 맡고 어떤 도구는 필요 없는지**까지 설명할 수 있으면 됩니다.

---

## 20. 자주 혼동하는 관계를 짧게 점검하기

| 혼동하기 쉬운 표현 | 정확하게 구분할 점 |
|---|---|
| Hugging Face = Transformers | Hugging Face는 Hub와 여러 Library를 포함하는 생태계입니다. |
| Transformer = Transformers | 전자는 Architecture이고 후자는 Library입니다. |
| PyTorch = GPT·Gemma | 전자는 Framework, 후자는 Model 계열입니다. |
| Ollama = LLM | Ollama는 모델을 실행하는 Runtime/Serving 도구입니다. |
| OpenAI SDK = OpenAI API | SDK는 API를 코드에서 사용하도록 돕는 개발 도구입니다. |
| LangChain은 모든 AI Application에 필수 | 단순한 서비스에는 SDK 직접 사용으로도 충분할 수 있습니다. |
| FastAPI는 AI Model 개발 Framework | FastAPI는 Python Backend Web Framework입니다. |
| Pydantic을 통과하면 AI 내용도 사실로 검증됨 | 구조·타입 검증과 출력 내용의 사실 검증은 다릅니다. |

**수업 진행 팁:** 위 표를 처음부터 다시 장황하게 읽기보다, 학생이 틀린 구분을 말했을 때 관련 행을 찾아 근거를 설명하도록 합니다.

---

## 21. 수업 확인 질문

**Q1. NumPy와 pandas의 대표적인 차이는 무엇인가요?**  
**예상 답변:** NumPy는 수치 배열과 계산에, pandas는 행·열이 있는 표 데이터를 다루는 데 주로 사용합니다. 두 도구는 함께 사용할 수 있습니다.

**Q2. scikit-learn과 PyTorch는 둘 다 모델인가요?**  
**예상 답변:** 아닙니다. scikit-learn은 여러 ML 알고리즘과 데이터 처리·평가 도구를 제공하는 Library이고, PyTorch는 Tensor와 신경망의 구성·학습·실행을 지원하는 Framework입니다.

**Q3. Hugging Face Hub와 Transformers는 어떤 차이가 있나요?**  
**예상 답변:** Hub는 Model·Dataset 등의 자산을 찾고 공유하는 Platform이고, Transformers는 사전학습 Transformer 모델을 코드에서 활용하는 Library입니다.

**Q4. Gemma 모델을 Ollama에서 실행하면 Ollama도 Gemma 모델이 되나요?**  
**예상 답변:** 아닙니다. Gemma는 Model Family이고 Ollama는 Model Runtime / Serving 도구입니다.

**Q5. OpenAI API와 OpenAI SDK는 같은 의미인가요?**  
**예상 답변:** API는 외부 서비스가 제공하는 인터페이스이고 SDK는 개발자가 그 API를 편리하게 사용하도록 돕는 도구입니다.

**Q6. LangChain이나 LlamaIndex를 반드시 설치해야 AI 서비스를 만들 수 있나요?**  
**예상 답변:** 아닙니다. SDK나 직접 만든 코드로 충분한 경우도 있으며 복잡한 연결·검색 요구사항이 있을 때 필요성을 검토합니다.

**Q7. FastAPI와 Pydantic이 각각 맡는 일은 무엇인가요?**  
**예상 답변:** FastAPI는 Web API를 만들고 요청·응답을 처리하며, Pydantic은 입력·출력 데이터의 구조나 타입을 검증하는 데 사용합니다.

**Q8. 새 라이브러리를 고를 때 가장 먼저 해야 할 일은 무엇인가요?**  
**예상 답변:** 설치부터 하지 않고, 현재 해결하려는 문제와 도구가 담당할 책임을 먼저 확인합니다.

---

## 22. 이번 교시 핵심 정리

AI 개발 생태계는 하나의 라이브러리로 이루어지지 않습니다. **데이터 처리·모델 학습·모델 자산 공유·추론 실행·외부 서비스 접근·웹 애플리케이션 구성**에는 서로 다른 종류의 도구가 필요할 수 있습니다.

특히 이번 시간에는 세 가지 판단을 연습했습니다.

1. **모델과 도구를 구분한다.** Gemma는 Model Family이며, PyTorch·Transformers·Ollama는 그와 다른 역할을 하는 도구입니다.
2. **같은 결과를 얻는 여러 구현 경로를 구분한다.** 사전학습 모델을 코드에서 직접 다룰 수도 있고, Local Runtime을 이용할 수도 있고, Cloud API를 이용할 수도 있습니다.
3. **필요한 도구만 선택한다.** 사용 목적을 먼저 확인하고, 개발 편의성과 유지보수 비용을 함께 고려합니다.

오늘의 핵심 문장:

> **AI 개발에서 중요한 것은 라이브러리 이름을 많이 아는 것이 아니라, 해결할 문제에 맞춰 모델·데이터·실행 환경·서비스 코드를 올바르게 연결하는 능력입니다.**

---

## 23. 다음 교시 연결 — 실제 Cloud AI API 호출

지금까지는 도구가 어디에 쓰이는지 구분했습니다. 다음 7교시에서는 그중 **Cloud AI API와 SDK**를 실제로 사용합니다.

```text
Python 프로그램
     ↓
OpenAI SDK
     ↓
OpenAI API
     ↓
Cloud AI Service
     ↓
Response
```

이 과정에서 API Key를 안전하게 다루는 방법, 요청과 응답 객체의 구조, 오류를 어떻게 구분할지 확인합니다. 이어지는 8교시에서는 FastAPI와 Pydantic을 이용해 AI 기능을 웹 API로 제공하는 실습으로 확장합니다.

**다음 시간의 핵심 질문:** “도구의 위치를 알게 되었으니, 이제 Python 코드에서 실제 AI 서비스에 요청을 보내고 결과를 받을 수 있을까요?”

---

## 참고자료

아래는 원본 강의에 기재되어 있던 참고자료의 명칭입니다. **이번 개편 과정에서 외부 문서를 조회하거나 최신 버전·API 동작을 검증했다는 뜻은 아닙니다.** 실제 설치·API 사용 교시에서는 별도 검증이 필요합니다.

- NumPy Documentation
- pandas Documentation
- scikit-learn Documentation
- PyTorch Documentation
- Hugging Face Documentation / Hugging Face Transformers Documentation
- Hugging Face Datasets / PEFT / Accelerate Documentation
- OpenAI API / SDK Documentation
- Ollama Documentation
- LangChain Documentation
- LlamaIndex Documentation
- FastAPI Documentation
- Pydantic Documentation
- HTTPX Documentation

