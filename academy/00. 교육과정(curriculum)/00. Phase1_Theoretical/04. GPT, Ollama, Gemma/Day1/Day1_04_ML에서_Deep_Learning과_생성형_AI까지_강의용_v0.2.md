# Day 1 - 4교시. Machine Learning에서 Deep Learning과 생성형 AI까지

> **이번 교시의 핵심 질문**  
> 데이터를 학습하는 Machine Learning이 이미 있었는데, **Deep Learning은 무엇을 다르게 했고**, 그 변화는 **Transformer와 현대 생성형 AI**로 어떻게 이어졌을까요?

## 개요

3교시에서는 명시적인 규칙 기반 프로그램과 Machine Learning의 차이를 확인하고, `Dataset·Feature·Label → Training → Model → Inference`를 작은 Python 예제로 연결했습니다. 여기서 다시 같은 용어를 길게 정의하거나 선형 회귀 코드를 반복하지는 않겠습니다.

이번 교시의 초점은 **모델이 무엇을 학습하도록 발전했는가**에 있습니다. 특히 이미지, 언어, 음성처럼 구조가 복잡한 데이터를 다룰 때, 사람이 유용한 특징을 직접 설계하는 방식에서 모델이 여러 수준의 표현을 학습하는 방식으로 발전한 이유를 설명합니다.

이어서 **CNN, RNN, LSTM, Attention, Transformer**가 어떤 문제를 다루기 위해 등장했는지 살펴보고, 대규모 **Pre-training**이 어떻게 범용적인 모델 활용으로 이어졌는지 연결합니다. 마지막에는 Deep Learning을 실제 코드로 구현할 때 사용하는 **Tensor와 PyTorch**의 역할을 작은 예제로 확인합니다.

> **범위 안내:** 이 교시는 기술 발전의 이유와 각 구조의 역할을 이해하는 시간입니다. 신경망의 미분 수학, Self-Attention의 행렬 계산, Token 생성 원리, Foundation Model의 세부 활용 방법은 이후 교시와 Phase 2에서 다룹니다.

## 1. 학습 목표

이번 교시를 마치면 학생은 다음을 설명하거나 수행할 수 있어야 합니다.

1. **Feature Engineering**과 **Representation Learning**의 차이를 실제 데이터 처리 관점에서 설명한다.
2. **Neural Network**가 여러 층에서 입력을 처리하는 구조와 **Deep Learning**의 관계를 설명한다.
3. 대규모 데이터, 계산 자원, 학습 방법, Framework가 Deep Learning 발전에 기여한 이유를 설명한다.
4. 이미지에 대한 **CNN**, 순서 데이터에 대한 **RNN·LSTM**의 대표적인 역할을 구분한다.
5. **Attention**과 **Transformer**가 현대 언어 모델 발전의 중요한 전환점이 된 이유를 말한다.
6. **Pre-training**, **Pre-trained Model**, **Foundation Model**을 기술 발전 흐름 안에서 구분한다.
7. **NumPy Array**와 **PyTorch Tensor**를 간단한 코드로 생성하고 Shape를 확인한다.
8. **PyTorch·Transformers·Ollama**가 서로 다른 문제를 해결하는 도구임을 설명한다.

---

## 2. Feature Engineering에서 Representation Learning으로

### 2-1. 3교시의 Feature를 이번에는 다른 관점에서 보기

3교시에서 `Feature`는 모델이 예측을 위해 입력으로 사용하는 정보라고 배웠습니다. 4교시에서는 **그 입력을 어떻게 준비할 것인가**가 새로운 질문입니다.

고양이와 개를 구별하는 이미지 문제를 생각해 봅시다. 컴퓨터에 입력되는 사진은 결국 수치 데이터로 표현됩니다.

```text
사진(Image)
    ↓
픽셀(Pixel) 값
    ↓
많은 수치 정보
```

수치 데이터를 그대로 받아 처리할 수도 있지만, 많은 전통적인 Machine Learning 접근에서는 사람이 먼저 문제에 유용한 특징을 설계하거나 추출했습니다. 이미지라면 경계선, 형태, 질감, 색 등의 정보를 처리할 수 있습니다.

```text
이미지
  ↓
사람이 특징을 선택하거나 추출하는 절차 설계
  ├─ Edge(경계선)
  ├─ Shape(형태)
  ├─ Texture(질감)
  └─ Color(색상)
  ↓
Feature
  ↓
Machine Learning Model
  ↓
분류 결과
```

이처럼 **문제를 해결하는 데 도움이 되도록 입력 특징을 설계·가공·추출하는 작업**이 **Feature Engineering(특성 공학)**입니다. 모든 전통적인 머신러닝이 반드시 수작업 특징만 사용한다는 뜻은 아니지만, 좋은 특징을 고르는 작업이 중요했던 분야가 많았습니다.

### 2-2. Feature Engineering은 과거의 낡은 기술일까?

그렇지 않습니다. 현재도 정형 데이터를 다루는 문제에서는 사람이 도메인 지식을 바탕으로 Feature를 구성하는 일이 중요할 수 있습니다.

예시로 **고객 이탈 예측** 사례를 봅시다.

| 원래 가지고 있는 정보 | 가공해서 사용할 수 있는 Feature | 이런 특징이 필요한 이유 |
|---|---|---|
| 접속 기록 | 최근 로그인 횟수 | 최근 서비스 이용의 활발함을 나타내기 위해 |
| 구매 기록 | 마지막 구매 이후 경과일 | 구매 활동이 얼마나 오래 중단됐는지 보기 위해 |
| 거래 내역 | 월평균 구매 금액 | 이용 규모를 파악하기 위해 |
| 가입일 | 가입 기간 | 장기·신규 이용자의 차이를 나타내기 위해 |
| 문의 기록 | 문의 횟수 | 고객이 서비스와 상호작용하는 빈도를 나타내기 위해 |

예를 들어 **마지막 구매 이후 경과일**은 구매 기록과 기준 날짜를 이용해 새롭게 계산한 Feature일 수 있습니다. 이 값이 실제 이탈 예측에 유용한지는 데이터를 통해 검증해야 하며, **표에 적혔다고 자동으로 좋은 Feature가 되는 것은 아닙니다.**

여기서 학생들에게 질문해 봅시다.

> **질문:** Deep Learning이 널리 쓰인다고 해서 고객의 가입 기간이나 최근 구매일 같은 입력 Feature를 더 이상 준비할 필요가 없을까요?
>
> **예상 답변:** 아닙니다. 어떤 데이터를 모으고 어떻게 사용할지는 문제와 모델에 따라 여전히 중요합니다.

### 2-3. 사람이 중간 특징까지 일일이 설계하기 어려운 경우

이미지에는 픽셀 수가 많고, 같은 물체도 조명·각도·배경·자세에 따라 달라 보입니다. 사람에게는 쉽게 보이는 모양도, 모든 가능한 변형에 대해 적절한 특징 추출 규칙을 직접 만드는 것은 어렵습니다.

이때 중요한 아이디어가 **Representation Learning(표현 학습)**입니다. 이것은 데이터에서 문제에 유용한 **내부 표현(Representation)**을 모델이 학습하도록 하는 접근입니다.

```text
Raw Data
   ↓
모델이 학습하는 초기 표현
   ↓
여러 표현을 결합한 더 복잡한 표현
   ↓
Task Output(분류·인식 등)
```

이미지 인식을 단순화하면 아래처럼 생각할 수 있습니다.

```text
Pixel → Edge → Simple Shape → Complex Pattern → Object
```

이 그림은 **모든 모델의 내부가 반드시 이 순서대로 구성된다**는 뜻이 아닙니다. 학습된 표현이 단순한 형태에서 더 복잡한 특징으로 발전할 수 있다는 점을 직관적으로 보여주는 개념도입니다.

| 비교 관점 | Feature Engineering이 강조되는 접근 | Deep Learning에서의 표현 학습 |
|---|---|---|
| 중간 표현을 만드는 사람 | 개발자가 유용한 특징을 설계·추출하는 비중이 클 수 있음 | 모델이 데이터에서 유용한 내부 표현을 학습할 수 있음 |
| 이미지 예시 | 경계선·질감 등을 추출한 값을 입력으로 사용 | 여러 층이 입력으로부터 표현을 단계적으로 계산 |
| 핵심 장점 | 도메인 지식을 직접 반영할 수 있음 | 복잡한 데이터의 특징을 자동으로 학습할 수 있음 |
| 주의점 | 특징 설계에 사람의 전문성과 시간이 많이 들 수 있음 | 학습 데이터·계산 자원·검증이 필요하며 언제나 더 우수한 것은 아님 |

**강사 포인트:** “옛 방식은 사람이 모두 하고 새 방식은 기계가 전부 한다”가 아닙니다. 개발자는 여전히 문제를 정하고 데이터와 목표를 준비합니다. 달라진 것은 **모델이 학습할 수 있는 표현의 범위**입니다.

---

## 3. Neural Network와 Deep Learning

### 3-1. Neural Network는 어떤 구조일까?

**Neural Network(신경망)**는 계산 단위와 연결을 이용해 입력을 출력으로 변환하는 모델 구조입니다. 여러 **Layer(층)**를 통해 수치 데이터를 차례로 계산한다고 생각할 수 있습니다.

```text
Input Layer
    ↓
Hidden Layer 1
    ↓
Hidden Layer 2
    ↓
Output Layer
```

- **Input Layer(입력층)**: 이미지의 수치 값이나 다른 입력 정보를 받습니다.
- **Hidden Layer(은닉층)**: 입력을 변환하고 다음 단계에 전달하며, 모델이 유용한 내부 표현을 형성하는 데 기여합니다.
- **Output Layer(출력층)**: 분류 점수 등 최종 작업에 필요한 형태의 결과를 계산합니다.

여기서 `Layer`는 단순한 문서의 목차가 아니라, **입력에 수학적 연산을 적용해 다음 단계에 전달하는 계산 구조**를 의미합니다. 각 층과 연결에는 학습 가능한 Parameter가 있을 수 있습니다.

3교시에서 Parameter를 학습으로 조정되는 모델 내부 값이라고 배웠습니다. 여기서는 그 값들이 **많은 층에 걸쳐 작용하며 입력 표현을 바꾼다**는 점이 새 학습 내용입니다. Parameter 업데이트의 상세 수식은 지금 외울 필요가 없습니다.

### 3-2. 층이 많다는 것만으로 설명이 끝날까?

**Deep Learning**은 여러 층을 가진 신경망을 중심으로 발전한 Machine Learning 접근입니다. 하지만 “깊다(Deep) = 층의 개수만 많다”로 끝내면 왜 중요한지를 설명하지 못합니다.

서로 다른 층을 거치면서 모델이 단순한 패턴을 조합해 더 복잡한 표현을 만들 수 있고, **그 표현을 데이터로부터 학습**할 수 있다는 점이 중요합니다.

이미지 분류를 다시 생각해 봅시다.

```text
이미지의 수치 입력
       ↓
비교적 단순한 국소 패턴 처리
       ↓
패턴을 결합한 중간 표현
       ↓
분류에 유용한 복합 표현
       ↓
최종 분류 결과
```

이 그림 역시 특정 신경망의 층 수나 연산을 엄밀히 재현한 것이 아닙니다. **입력에서 결과까지 정보를 변환하는 과정**과 **그 과정의 표현을 학습할 수 있다**는 점을 보여줍니다.

> **확인 질문:** Deep Learning의 중요성을 “신경망 층이 많아서”라는 한 문장으로만 설명하면 빠지는 것은 무엇일까요?  
> **예상 답변:** 층을 거치며 문제에 유용한 **복잡한 표현을 데이터에서 학습한다**는 점입니다.

### 3-3. Neural Network와 Deep Learning은 완전히 같은 말일까?

동일하게 취급하지 않습니다. Neural Network는 모델의 **구조**를 가리키는 말이고, Deep Learning은 **다층 신경망을 활용해 표현을 학습하는 접근**이라는 말입니다. 신경망을 이용한 모든 실험이 같은 규모나 학습 방식을 가지는 것도 아닙니다.

앞선 시간의 `AI ⊃ Machine Learning ⊃ Deep Learning` 도식을 다시 여러 번 그리기보다, 이번 교시에서는 **신경망이 어떻게 입력을 가공하는가**라는 새로운 측면을 기억하면 됩니다.

---

## 4. Deep Learning은 왜 크게 발전할 수 있었을까?

Neural Network의 아이디어 하나만으로 오늘날의 대규모 학습이 가능해진 것은 아닙니다. 발전 조건을 **각각의 역할**로 구분해 봅시다.

| 발전 조건 | 실제로 기여한 점 |
|---|---|
| 더 많은 Data | 모델이 학습할 수 있는 다양한 사례를 제공 |
| 학습 알고리즘과 방법의 발전 | Parameter를 조정하는 과정을 더 효과적으로 구성 |
| 신경망 Architecture의 발전 | 이미지·순서 데이터 등 서로 다른 문제에 맞는 계산 구조 제공 |
| GPU 등 계산 하드웨어의 발전 | 많은 수치 연산을 병렬적으로 처리할 수 있는 기반 제공 |
| Software Framework의 발전 | Tensor 연산과 미분, 모델 구성 등을 코드로 다루기 쉽게 지원 |

이 요소들은 서로 영향을 주었습니다. 복잡한 모델을 만들 수 있어도 데이터를 처리하거나 실제로 학습시킬 계산 자원이 부족하다면 활용이 제한될 수 있습니다. 반대로 하드웨어가 빨라져도 적합한 학습 방법과 데이터가 없다면 좋은 모델을 자동으로 얻을 수는 없습니다.

### 4-1. 왜 GPU가 자주 등장할까?

Deep Learning 학습과 추론에는 **행렬(Matrix)**과 **Tensor**를 이용한 대량의 수치 연산이 많이 등장합니다. GPU는 이런 연산 중 병렬 처리에 적합한 계산을 효율적으로 수행할 수 있어 Deep Learning 발전에 중요한 역할을 했습니다.

```text
학습 데이터 / 모델 내부 값
           ↓
행렬·Tensor를 이용한 대량 계산
           ↓
CPU 또는 GPU 등 계산 자원
           ↓
모델 학습 / 추론
```

**CPU를 사용하면 AI가 불가능하다는 뜻은 아닙니다.** 데이터 크기, 모델 구조, 환경에 따라 CPU도 활용할 수 있습니다. GPU는 특정 대규모 병렬 연산에서 유리하다는 의미입니다.

Day 2에서 Local Model을 다룰 때는 `RAM`, `VRAM`, `Model Size`, `Quantization` 등이 등장합니다. 이들은 여기서 상세히 정의하지 않고, **모델 실행이 하드웨어 자원과 연결된다**는 맥락만 기억합니다.

---

## 5. 이미지 처리의 발전: CNN

### 5-1. 이미지 데이터는 무엇이 특별한가?

이미지에서는 **어느 위치에 어떤 픽셀이 놓여 있는가**, 가까운 부분에 어떤 모양이 함께 나타나는가가 중요합니다. 단순히 픽셀값의 목록만 보는 것보다, 공간적으로 이웃한 정보 사이의 관계를 활용하는 것이 도움이 됩니다.

이런 특성을 다루기 위해 널리 발전한 구조가 **CNN(Convolutional Neural Network, 합성곱 신경망)**입니다.

```text
Image
  ↓
Local Visual Patterns(주변의 시각 패턴)
  ↓
Higher-level Features(더 복합적인 표현)
  ↓
Classification / Detection / Recognition
```

여기서 `Local`은 **이미지의 가까운 영역**을 의미합니다. CNN은 이미지의 국소적인 패턴을 처리하고 그것들을 조합하는 데 적합한 구조로 널리 활용됐습니다.

### 5-2. CNN은 무엇을 바꾸었을까?

Feature Engineering의 관점에서 보면, CNN의 중요한 의의는 이미지에 유용한 특징을 처리하는 과정을 **신경망 구조와 학습 과정 안으로 가져왔다**는 것입니다. 모든 경계선과 형태를 별도의 수작업 규칙으로 지정하지 않아도, 학습을 통해 유용한 시각적 표현을 얻을 수 있습니다.

CNN 관련 활용 영역은 다음과 같습니다.

- **Image Classification**: 이미지가 어느 범주에 해당하는지 분류
- **Object Detection**: 이미지 안의 물체를 찾아 식별
- **Face Recognition**: 얼굴과 관련된 인식 작업
- **Medical Imaging**: 의료 영상 분석

이 작업들이 모두 **똑같은 CNN 하나로 해결된다**는 뜻은 아닙니다. CNN이 이러한 Computer Vision 문제에서 중요한 기술적 기반이 됐다는 의미입니다.

> **이번 교시 범위:** Convolution Filter의 수식이나 Filter 값을 실제로 계산하지 않습니다. 지금은 **왜 이미지에 특화된 구조가 필요했는가**를 이해합니다.

---

## 6. 순서가 중요한 데이터를 위한 RNN과 LSTM

### 6-1. 이미지와 문장은 무엇이 다를까?

이미지는 주변 픽셀의 공간적 관계가 중요하다면, 문장이나 음성 등은 **정보가 나타나는 순서**가 중요한 경우가 많습니다.

두 문장을 보겠습니다.

```text
나는 학교에 간다.
학교에 나는 간다.
```

비슷한 단어를 사용하더라도 순서가 달라지면 문장의 표현과 해석이 달라질 수 있습니다. 또한 뒤에 나온 단어를 이해할 때 앞에서 읽은 내용이 필요할 수 있습니다.

이처럼 순서가 있는 데이터를 **Sequence Data(순서 데이터)**라고 부르며, 텍스트와 음성 등이 대표적 예입니다.

### 6-2. RNN은 이전 정보를 어떻게 활용했을까?

**RNN(Recurrent Neural Network, 순환 신경망)**은 순서대로 입력을 처리하면서 이전 단계의 정보를 다음 계산에 활용하도록 고안된 구조입니다.

```text
입력 1 ──→ 상태 1
             ↓
입력 2 ──→ 상태 2
             ↓
입력 3 ──→ 상태 3 ──→ 출력
```

여기서 **State(상태)**는 이전 단계까지 처리한 정보가 다음 단계 계산에 반영되도록 전달되는 내부 표현이라고 이해하면 됩니다. 매 단계가 앞선 단계의 상태를 참고하므로, 순서를 가진 데이터를 다루는 데 적합한 방식이었습니다.

하지만 긴 문장을 처리할 때는 처음 등장한 중요한 정보가 뒤쪽 계산까지 유용하게 전달되지 못하는 등 **긴 거리의 관계(Long-range Dependency)**를 학습하기 어려운 문제가 생길 수 있습니다.

### 6-3. LSTM은 왜 필요했을까?

이 문제를 완화하려고 발전한 대표적인 구조가 **LSTM(Long Short-Term Memory)**이고, 관련 계열로 **GRU**도 있습니다.

```text
순서가 있는 데이터를 처리해야 함
             ↓
            RNN
             ↓
긴 구간의 정보를 학습·유지하기 어려움
             ↓
        LSTM / GRU
```

LSTM은 이전 정보를 무조건 모두 저장한다는 뜻이 아닙니다. **어떤 정보를 유지하고 어떤 정보를 갱신할지 다루는 구조**를 통해 순서 데이터의 긴 관계를 처리하는 능력을 개선하려는 접근입니다.

RNN과 LSTM은 역사적으로 자연어 처리, 음성, 시계열 데이터 등에 중요한 역할을 했습니다. 지금도 모든 문제가 Transformer 하나로 해결되는 것은 아니므로, **기존 구조가 완전히 사라졌다**고 이해해서는 안 됩니다.

> **확인 질문:** CNN과 RNN의 대표적인 출발 문제는 어떻게 다를까요?  
> **예상 답변:** CNN은 이미지의 **공간적 패턴**, RNN은 데이터의 **시간적·순서적 관계**를 다루는 데 중요한 구조였습니다.

---

## 7. 문맥 속 관계를 다루는 Attention

### 7-1. 단어를 순서대로 처리하는 것만으로 충분할까?

순서를 기억하는 것과 **어떤 표현이 서로 연결되는지 파악하는 것**은 다른 문제입니다.

```text
철수는 영희에게 책을 주었다.
그녀는 그것을 읽었다.
```

여기서 `그녀`와 `그것`이 가리키는 대상을 해석하려면 **같은 문장과 앞 문장의 관계**를 참고해야 합니다. 단어가 멀리 떨어져 있을수록 문맥의 관련 부분을 효과적으로 찾아내는 일이 중요해질 수 있습니다.

다른 예시도 살펴봅시다.

```text
The animal didn't cross the street because it was too tired.
```

`it`이 무엇을 가리키는지 생각할 때 문장 전체의 관련 정보를 참고해야 합니다. 이런 필요를 이해한 뒤 **Attention**을 살펴보면 자연스럽습니다.

### 7-2. Attention의 핵심 직관

Attention은 입력 요소들 사이의 **관련성을 계산해 현재 처리에 필요한 다른 정보를 참고하는 방식**입니다.

```text
현재 처리 중인 표현
        ↓
입력의 다른 부분 중 무엇이 관련 있는가?
        ↓
관련성을 반영하는 Attention 계산
        ↓
문맥 정보를 반영한 새로운 표현
```

단순히 “가장 중요한 단어 하나만 고른다”는 뜻은 아닙니다. 여러 입력 요소 사이의 관계를 계산하고, 그 결과를 현재 표현을 만드는 데 활용한다고 이해하면 됩니다.

여기서는 Attention의 직관까지만 다룹니다. **Self-Attention, Query/Key/Value, Multi-Head Attention** 등의 내부 계산은 Phase 2 Transformer 강의의 고유한 학습 내용으로 남겨 두겠습니다.

---

## 8. Transformer는 무엇을 바꾸었을까?

### 8-1. 2017년의 전환점

2017년에 제안된 **Transformer**는 Attention을 핵심으로 삼아 순서 데이터를 처리하는 신경망 Architecture입니다. 인용된 논문 제목은 **Attention Is All You Need**입니다.

RNN 계열의 핵심적인 특징은 이전 단계의 계산 결과를 다음 단계에 전달하며 순차적으로 처리한다는 데 있었습니다. Transformer는 **순환 구조에 의존하지 않고 Attention을 중심으로 관계를 계산하는 방식**을 제시했습니다.

이 변화는 이후 언어 모델의 대규모 학습과 발전에 중요한 영향을 주었습니다.

### 8-2. Transformer의 세 가지 핵심 역할

**첫째, 입력 요소 사이의 관계를 다룹니다.**  
Attention을 이용해 문장 안의 요소들이 서로 어떻게 관련되는지를 표현에 반영합니다.

**둘째, 순환 구조 없이 Sequence를 처리할 수 있습니다.**  
이런 구조는 학습 계산의 병렬화 측면에서 중요한 장점이 됐습니다. 다만 모든 상황에서 계산이 무조건 빠르거나 자원 사용이 적다는 뜻은 아닙니다.

**셋째, 현대 Language Model의 중요한 기반이 됐습니다.**  
GPT 계열을 포함해 많은 대규모 언어 모델이 Transformer 계열 Architecture를 바탕으로 발전했습니다.

### 8-3. 기술 발전을 한 줄로만 외우면 생기는 오해

`RNN → LSTM → Attention → Transformer` 흐름은 **문제 해결 방식이 발전한 역사적 맥락**입니다. 그 기술들이 하나의 모델 안에서 반드시 순서대로 실행된다는 뜻도, 새 구조가 나오면 옛 구조가 모두 폐기된다는 뜻도 아닙니다.

```text
Deep Learning의 여러 Architecture
│
├── CNN: 이미지의 공간적 패턴에 중요한 역할
│
├── RNN / LSTM: 순서 데이터의 단계적 처리에 중요한 역할
│
└── Transformer: Attention 중심의 Sequence 처리에 큰 변화
                ↓
       현대 대규모 언어 모델의 발전에 기여
```

**강사 포인트:** “CNN을 통과한 뒤 RNN을 통과해야 Transformer가 된다”가 아닙니다. 각 구조의 **필요성과 설계 방향**을 구분하는 것이 이번 교시의 목표입니다.

### 8-4. 여기서 배우지 않을 내용

다음 용어는 이후에 자세하게 학습하므로 이름을 미리 외우지 않습니다.

`Tokenization`, `Embedding`, `Positional Information`, `Self-Attention`, `Query/Key/Value`, `Multi-Head Attention`, `Feed Forward Network`, `Residual Connection`, `Layer Normalization`, `Transformer Block`

지금은 **왜 Transformer가 필요했고 어떤 역할을 했는지**를 설명할 수 있으면 충분합니다.

---

## 9. 대규모 Pre-training과 Foundation Model로의 연결

### 9-1. 작업별 모델을 따로 만드는 접근

전통적으로는 문제에 따라 서로 다른 모델을 준비하는 방식이 널리 사용됐습니다. 예시는 다음과 같습니다.

```text
Spam Classification → Model A
Sentiment Analysis  → Model B
Translation         → Model C
```

이 접근이 잘못된 것은 아닙니다. 각 작업에 맞춘 모델이 유리할 수 있습니다. 여기에서 새로운 질문은 **하나의 사전학습 모델을 여러 작업의 출발점으로 활용할 수 없을까?** 입니다.

### 9-2. Pre-training은 무엇인가?

**Pre-training(사전학습)** 은 모델을 특정 응용에 활용하기 전에, 먼저 큰 규모의 데이터 등을 이용해 일반적으로 유용한 패턴이나 표현을 학습시키는 과정입니다.

```text
Large-scale Data
       ↓
   Pre-training
       ↓
 Pre-trained Model
       ↓
여러 후속 작업(Downstream Tasks)의 기반으로 활용
```

**Pre-trained Model(사전학습 모델)** 은 이 과정을 거친 모델입니다. 이후에는 목적에 따라 다른 학습·조정 단계를 거치거나, 이미 준비된 모델을 그대로 추론에 활용할 수 있습니다.

3교시의 배웠던 Training·Inference에 이어 **이미 학습된 모델(Pre-trained Model)이 후속 작업의 출발점이 될 수 있다**는 새로운 변화에 주목합니다.

### 9-3. Foundation Model의 정의와 등장배경

**Foundation Model(기반 모델)**은 대규모 데이터로 사전학습하여 다양한 작업의 기반으로 활용할 수 있도록 만든 AI 모델을 말합니다.

기존에는 번역, 분류, 요약 등 작업별로 모델을 따로 만드는 경우가 많았다면, Foundation Model은 하나의 사전학습된 모델을 여러 작업에 활용하거나 추가 학습하여 사용할 수 있다는 특징이 있습니다.

```text
특정 작업 중심                  공통 기반 모델 활용

Task A → Model A              ┌→ Task A
Task B → Model B    대비      │→ Task B
Task C → Model C          Pre-trained Model
                              │→ Task C
                              └→ Task D
```

두 방식 모두 실제로 사용될 수 있습니다. Foundation Model이라고 해서 **아무 추가 준비 없이 모든 문제를 완벽하게 해결한다**는 뜻은 아닙니다. 후속 작업의 요구에 따라 다른 구성 요소나 조정이 필요할 수 있습니다.

### 9-4. 생성형 AI와의 관계를 어디까지 설명할까?

대규모 사전학습과 Transformer 기반 모델의 발전은 현대 **텍스트 생성형 AI**의 확대와 밀접하게 연결됩니다. 생성형 AI는 이미지·오디오·비디오 등 다양한 모델도 포함되며, **모든 생성형 AI가 Transformer나 LLM 하나로 만들어지는 것은 아닙니다.**

이번에는 다음 구분을 기억하면 됩니다.

- **Transformer**: 모델의 Architecture(구조)에 관한 말
- **Pre-training**: 모델을 먼저 학습하는 과정에 관한 말
- **Pre-trained Model**: 사전학습을 거친 모델에 관한 말
- **Foundation Model**: 여러 작업의 기반으로 활용할 수 있는 모델의 성격에 관한 말
- **Generative AI**: 새로운 콘텐츠를 생성하는 기능과 모델·시스템의 범주에 관한 말

이들은 서로 다른 기준의 용어이므로 **하나의 필수 직선 단계**로 외우지 않습니다. 생성형 모델이 어떻게 문장을 만들고, Foundation Model을 실제로 어떻게 활용하는지는 바로 다음 **5교시**에서 새롭게 학습합니다.

---

## 10. 모델을 개발할 때 PyTorch가 필요한 이유

3교시에서는 NumPy·scikit-learn·PyTorch가 **서로 같은 종류의 도구가 아니다**라는 위치를 확인했습니다. 4교시에서는 그중 **PyTorch가 Deep Learning 계산을 실제 코드로 어떻게 지원하는가**를 살펴봅니다.

Deep Learning 모델을 학습하려면 입력 데이터와 Parameter를 수치 형태로 다루고, 여러 연산을 수행하고, 학습 과정에서 값을 조정해야 합니다. 이런 작업을 전부 처음부터 직접 구현하기는 어렵습니다.

PyTorch의 주요 역할은 다음과 같습니다.

| 기능 | 이번 교시에서 이해할 역할 |
|---|---|
| **Tensor** | 여러 차원의 수치 데이터를 표현하고 계산 |
| **Automatic Differentiation** | 학습 과정에 필요한 미분 값을 계산하도록 지원 |
| **Neural Network Components** | 모델의 층과 계산 구조를 구성하도록 지원 |
| **Optimizer** | 학습 과정의 Parameter 갱신을 지원 |
| **CPU / GPU Execution** | 지원되는 장치에서 계산 수행 |

```text
개발자 코드
   ↓
PyTorch Framework
   ├── Tensor Operations
   ├── Automatic Differentiation
   ├── Neural Network Components
   └── Optimization
   ↓
CPU / GPU 등 실행 환경
```

여기서 중요한 차이가 있습니다. **PyTorch는 GPT API를 호출하기 위한 전용 라이브러리가 아니라, 신경망을 구성하고 계산·학습·실행하는 Framework**입니다.

### 10-1. Tensor란 무엇인가?

**Tensor(텐서)**는 입문 수준에서 **하나 이상의 차원을 가진 수치 데이터를 표현하는 자료 구조**라고 이해할 수 있습니다.

```text
Scalar(스칼라): 한 개의 값
5

Vector(벡터): 한 줄의 값
[1, 2, 3]

Matrix(행렬): 행과 열을 가진 값
[
  [1, 2],
  [3, 4]
]
```

더 높은 차원의 데이터도 Tensor로 표현할 수 있습니다. 입력 데이터뿐 아니라 신경망의 Parameter와 중간 계산 결과도 Tensor 형태로 처리할 수 있습니다.

> **강사 질문:** Tensor라는 이름을 쓰면 모두 AI 모델일까요?  
> **예상 답변:** 아닙니다. Tensor는 수치 데이터를 표현하고 계산하는 데 사용하는 구조이고, 모델은 그런 데이터를 이용해 특정 결과를 계산하는 구조입니다.

### 10-2. NumPy Array와 PyTorch Tensor 비교

두 코드를 나란히 살펴봅시다.

```python
import numpy as np

array = np.array([1.0, 2.0, 3.0])
print(array)
```

```python
import torch

tensor = torch.tensor([1.0, 2.0, 3.0])
print(tensor)
```

둘 다 수치 데이터를 다룬다는 점은 비슷해 보입니다. 그러나 PyTorch Tensor는 신경망 학습에 필요한 **자동 미분**, **Parameter 갱신**, **지원 장치에서의 연산** 등과 연결된다는 점이 핵심입니다.

이것이 “NumPy는 계산, PyTorch는 무조건 학습”이라는 뜻은 아닙니다. **NumPy도 다양한 수치 계산에 사용할 수 있고, PyTorch Tensor도 학습과 무관한 계산에 쓸 수 있습니다.** 두 도구가 제공하는 기능과 사용하는 목적을 구분하는 것이 중요합니다.

### 10-3. Automatic Differentiation은 왜 필요할까?

3교시에서 모델이 예측한 값과 정답을 비교해 Parameter를 갱신할 수 있다고 언급했었습니다. 신경망에서는 모델이 여러 층으로 이루어져 있으므로, **어떤 Parameter를 어떻게 조정할지 계산하는 과정**이 복잡해집니다.

```text
Input
  ↓
Model
  ↓
Prediction
  ↓
Loss
  ↓
Gradient
  ↓
Parameter Update
```

**Gradient(기울기)**는 Loss가 Parameter 변화에 어떻게 영향을 받는지 파악하는 데 사용하는 값입니다. **Automatic Differentiation(자동 미분)**은 계산 과정에 필요한 미분 값을 Framework가 계산하도록 지원하는 기능입니다.

이번 교시에서는 **“PyTorch Framework가 학습에 필요한 미분 계산을 도와준다”**까지만 이해하면 됩니다. Gradient를 구하는 수식, Backpropagation의 상세 과정, Optimizer의 갱신 공식은 이후 Phase 2에서 다룹니다.

---

## 11. 짧은 PyTorch 실습 — Tensor의 모양 확인하기

### 11-1. 실습의 목적과 준비

이 실습의 목적은 **Neural Network를 직접 Training하는 것**이 아니라, 이미지 등 복잡한 수치 데이터를 다루는 기반이 되는 **Tensor의 형태를 Python 코드에서 확인**하는 것입니다.

아래 예제는 **Python과 PyTorch가 설치된 환경**을 전제로 합니다. `import torch`가 실패한다면 PyTorch가 준비되지 않은 상태입니다. 설치 방법, 버전, GPU 구성은 실행 환경에 따라 확인해야 합니다.

### 11-2. Tensor 예제 실행하기

```python
import torch

x = torch.tensor([
    [1.0, 2.0],
    [3.0, 4.0],
])

print(x)
print(x.shape)
print(x.dtype)
```

이 코드는 **2행 2열**의 수치 데이터를 `Tensor`로 만듭니다.

- `torch.tensor(...)`: 제공된 데이터를 Tensor로 구성합니다.
- `x.shape`: 데이터의 크기를 차원별로 나타냅니다. 여기서는 **2 × 2**입니다.
- `x.dtype`: Tensor의 각 값이 어떤 수치 자료형으로 저장되는지 나타냅니다.
- `print(x)`: Tensor의 내부 값을 출력합니다.

다음은 별도 로컬 검증 환경에서 실제로 확인한 출력입니다. dtype의 경우 다른 환경에서도 동일하게 재현되는지는 따로 확인해야 합니다.

```text
tensor([[1., 2.],
        [3., 4.]])
torch.Size([2, 2])
torch.float32
```

여기서 `2 × 2`는 **행렬의 모양**입니다. `float32`는 **값의 자료형**입니다. 두 정보는 서로 다르며, 모델 입력을 준비할 때 모두 중요할 수 있습니다.

### 11-3. 실습 확인 질문

1. `x.shape`는 무엇을 알려 주나요? **→ 데이터의 차원별 크기**
2. `x.dtype`가 알려 주는 정보는 무엇인가요? **→ 값이 저장되는 수치 자료형**
3. Tensor를 출력했다고 해서 모델 학습이 일어난 것인가요? **→ 아닙니다. Tensor를 만들고 정보를 확인했을 뿐입니다.**
4. `np.array` 코드와 이번 코드의 공통점은 무엇인가요? **→ 수치 배열 데이터를 만든다는 점입니다.**
5. 어떤 점에서 PyTorch를 Deep Learning Framework라고 할 수 있나요? **→ Tensor 계산뿐 아니라 자동 미분·모델 층 구성·학습 과정 등을 지원하기 때문입니다.**

**실행 검증 기록:** 이번 수정 작업의 로컬 Python 환경에서 NumPy `2.3.5`, PyTorch `2.10.0+cpu`로 위 세 Python 예제의 출력을 실제 확인했습니다. 

---

## 12. 강사 시연 — 기술 발전의 흐름을 올바르게 배치하기

학생들에게 다음 단어를 보여 줍니다.

`Feature Engineering`, `Representation Learning`, `CNN`, `RNN`, `LSTM`, `Attention`, `Transformer`, `Pre-training`, `Foundation Model`

### 12-1. 먼저 같은 종류인지 구분해 보게 하기

강사가 질문합니다.

> “위 단어들은 모두 같은 종류의 알고리즘인가요? CNN 다음에 반드시 RNN을 거쳐야 Transformer가 되나요?”

**예상 답변:** 아닙니다. 서로 다른 역할과 종류를 가진 용어가 섞여 있고, CNN·RNN·Transformer가 반드시 직선으로 이어지는 단일 모델은 아닙니다.

다음 그림을 통해 문제와 기술의 관계를 설명합니다.

```text
Machine Learning
│
├── 사람이 유용한 입력 특징을 설계·가공할 수 있음
│     └── Feature Engineering
│
└── Deep Learning
      ├── 데이터를 통한 Representation Learning
      └── Neural Network Architecture의 발전
            ├── CNN        : 이미지의 공간적 패턴
            ├── RNN / LSTM : 순서 데이터와 이전 정보
            └── Transformer: Attention 중심의 관계 처리
                                   ↓
                   대규모 Pre-training에 활용되는 구조 중 하나
                                   ↓
                    여러 응용의 기반이 되는 Model 활용 확대
```

### 12-2. 강사가 설명해야 할 두 가지 구분

1. **Architecture**는 모델이 정보를 어떻게 계산하도록 구성됐는지에 관한 말입니다. CNN, RNN, LSTM, Transformer는 이 관점에서 비교합니다.
2. **Pre-training**은 모델을 학습시키는 단계에 관한 말이고, **Foundation Model**은 다양한 후속 작업의 기반으로 활용할 수 있는 모델의 성격을 말합니다.

Transformer가 나타났기 때문에 모든 CNN과 RNN이 없어졌다는 뜻도 아니고, Foundation Model이라는 말이 Transformer의 다른 이름이라는 뜻도 아닙니다.

> **강사 확인:** 학생이 “왜 이미지에는 CNN이, 순서 데이터에는 RNN이 중요했는지”와 “Transformer는 어떤 계산 방식을 새롭게 강조했는지”를 설명할 수 있는지 확인합니다.

---

## 13. 학생 활동 — 어떤 문제에 어떤 개념이 연결될까?

다음 활동에서는 **지난 교시의 정의를 다시 외우게 하는 대신**, 오늘 배운 기술의 등장 이유를 설명하게 합니다.

### 활동 A. 이미지 처리

> 고양이와 개가 포함된 이미지에서 유용한 특징을 학습하는 문제를 생각해 봅시다.

1. 사람이 경계선·질감 등 입력 특징을 직접 설계하는 접근은 무엇이라고 부를까요?
2. 여러 층에서 유용한 내부 표현을 학습하는 접근은 무엇인가요?
3. 이미지의 공간적 패턴을 처리하는 데 역사적으로 중요한 신경망 구조는 무엇인가요?

**예상 답변:** ① Feature Engineering ② Representation Learning/Deep Learning ③ CNN

### 활동 B. 순서 데이터

> 긴 문장에서 앞부분의 정보를 뒤쪽에서 참고해야 하는 문제를 생각해 봅시다.

1. 이전 단계의 상태를 다음 단계로 전달하는 구조는?
2. 긴 관계의 학습 어려움을 완화하기 위해 발전한 대표적인 구조는?
3. 입력의 다른 요소와 관련성을 계산해 참고하는 아이디어는?

**예상 답변:** ① RNN ② LSTM(또는 GRU) ③ Attention

### 활동 C. 기술의 역할 구분

| 항목 | 학생이 선택할 분류 | 예상 답변 |
|---|---|---|
| Deep Learning | 접근 방식 / Model Architecture / Framework | 접근 방식 |
| CNN | 접근 방식 / Model Architecture / Framework | Model Architecture |
| Transformer | 접근 방식 / Model Architecture / Framework | Model Architecture |
| PyTorch | Model Architecture / Framework / Runtime | Framework |
| NumPy | Model / 수치 계산 Library / Runtime | 수치 계산 Library |
| Ollama | Model Architecture / Framework / Runtime | Local Model Runtime/Serving |
| Generative AI | 생성 작업의 범주 / 모델 파일명 / Framework | 생성 작업의 범주 |

**강사 포인트:** 예상 답변을 바로 공개하기 전에 학생이 **왜 그렇게 분류했는지** 한 문장으로 설명하게 합니다.

---

## 14. 자주 발생하는 오해와 확인 질문

### 14-1. 개념을 혼동하는 경우

**오해 1. Deep Learning에서는 Feature가 없어졌다.**  
그렇지 않습니다. Deep Learning도 유용한 특징과 표현을 사용합니다. 달라진 점은 **데이터로부터 여러 수준의 내부 표현을 학습할 수 있다**는 것입니다.

**오해 2. CNN → RNN → Transformer는 하나의 모델 내부 실행 순서다.**  
아닙니다. 서로 다른 문제를 다루도록 발전한 신경망 구조들을 **역사적으로 비교한 것**입니다.

**오해 3. Transformer가 모든 Neural Network를 대체했다.**  
아닙니다. CNN이나 RNN 계열도 문제와 환경에 따라 사용될 수 있습니다.

**오해 4. PyTorch가 곧 AI Model이다.**  
아닙니다. PyTorch는 모델을 구성하고 수치 계산 및 학습을 지원하는 **Framework**입니다.

**오해 5. Pre-trained Model을 사용하려면 매번 처음부터 학습해야 한다.**  
아닙니다. 사전학습된 모델을 준비하여 Inference에 활용할 수 있습니다. 이 부분의 Training·Inference 차이는 3교시의 설명을 적용하면 됩니다.

**오해 6. Foundation Model은 반드시 LLM과 같다.**  
동일한 개념이 아닙니다. Foundation Model은 다양한 작업의 기반으로 활용할 수 있는 모델의 성격을 말합니다. 그중 일부는 현대 언어 모델이며, 자세한 차이는 5교시에서 다룹니다.

### 14-2. 수업 확인 질문

| 확인 질문 | 수업에서 기대하는 핵심 답변 |
|---|---|
| Q1. Feature Engineering이 왜 중요했나요? | 입력에서 유용한 특징을 직접 설계·추출하는 과정이 모델의 성능과 연결될 수 있기 때문입니다. |
| Q2. Deep Learning은 이전 방식과 무엇이 다른가요? | 여러 층에서 복잡한 내부 표현을 데이터로부터 학습할 수 있다는 점이 중요합니다. |
| Q3. CNN은 어떤 분야에서 중요했나요? | 이미지 등 공간적 패턴을 다루는 Computer Vision입니다. |
| Q4. RNN과 LSTM이 다루는 핵심 문제는? | 순서 데이터의 이전 정보 활용과 긴 구간의 관계 학습입니다. |
| Q5. Transformer가 중요한 이유는? | Attention 중심으로 Sequence를 처리하고 대규모 언어 모델 발전에 영향을 주었기 때문입니다. |
| Q6. Tensor와 Neural Network는 같은가요? | 아닙니다. Tensor는 수치 자료 구조이고 Neural Network는 계산 구조입니다. |
| Q7. PyTorch와 Ollama는 무엇이 다른가요? | PyTorch는 학습·연산 Framework이고 Ollama는 로컬 모델 실행·Serving 도구입니다. |
| Q8. Pre-training과 Foundation Model은 같은 말인가요? | 아닙니다. 하나는 학습 과정이고 다른 하나는 여러 응용의 기반으로 활용할 수 있는 모델의 성격입니다. |

---

## 15. 이번 교시 핵심 정리

오늘 배운 기술을 **발전의 이유**에 따라 연결하면 다음과 같습니다.

```text
[새로운 문제]
이미지·언어·음성처럼 복잡한 데이터에서
모든 유용한 특징을 사람이 직접 지정하기 어렵다
                     ↓
[변화 1]
신경망의 여러 층에서 표현을 학습하는 Deep Learning
                     ↓
[변화 2]
데이터 특성에 맞는 Architecture의 발전
 ├─ 이미지 공간 정보: CNN
 ├─ 순서 데이터: RNN / LSTM
 └─ 요소 간 관계: Attention 중심 Transformer
                     ↓
[변화 3]
더 많은 데이터·GPU·Framework를 활용한 대규모 학습
                     ↓
[새로운 활용]
사전학습한 모델을 다양한 후속 작업의 기반으로 활용
                     ↓
[다음 교시]
현대 생성형 AI와 Foundation Model의 실제 특성·한계
```

오늘 반드시 기억해야 하는 것은 다음 네 가지입니다.

1. **Feature Engineering은 사라진 것이 아닙니다.** 다만 Deep Learning은 사람이 직접 만들기 어려운 복잡한 내부 표현을 학습할 수 있게 했습니다.
2. **CNN·RNN·LSTM·Transformer는 하나의 직선 단계가 아닙니다.** 서로 다른 데이터 특성과 문제를 해결하려고 발전한 Architecture입니다.
3. **Transformer와 대규모 Pre-training은 현대 언어 모델 발전의 중요한 요소**이지만, 생성형 AI 전체가 하나의 모델 구조만을 의미하지는 않습니다.
4. **PyTorch는 모델 자체가 아니라 학습과 계산을 지원하는 도구**입니다. Tensor, 자동 미분, 신경망 구성이라는 기능이 이런 역할을 뒷받침합니다.

---

## 16. 다음 교시 연결 — 생성형 AI와 Foundation Model

4교시에서는 **어떤 기술들이 어떤 문제를 해결하면서 발전했는지**를 배웠습니다. 이제 관심을 **그 결과 만들어진 현대 생성형 모델을 어떻게 이해하고 활용할 것인가**로 옮깁니다.

다음 5교시에서는 이 교시에서 일부러 상세히 다루지 않은 다음 질문을 학습합니다.

- 생성형 AI의 **생성**은 분류와 예측과 어떤 관계가 있을까요?
- Language Model과 LLM은 무엇이며, **Token**은 어떻게 사용될까요?
- **Foundation Model**은 여러 작업에 어떻게 활용되며, Base Model과 Instruction-tuned Model은 무엇이 다를까요?
- 텍스트뿐 아니라 이미지·음성 등 여러 **Modality**를 다루는 모델은 어떻게 이해할까요?
- 모델이 만든 결과의 **정확성, 한계, 검증 책임**은 어떻게 판단해야 할까요?

> **이번 교시에서의 연결 한 문장:** “Deep Learning이 **무엇을 학습할 수 있는지**와 모델 구조를 넓혔다면, 다음 교시에서는 사전학습된 생성형 모델이 **무엇을 만들어 내고 실제 서비스에서 어떻게 다뤄져야 하는지**를 배웁니다.”

---

## 참고자료 — 강의에 기재된 목록

다음은 **교육자료에 이미 적혀 있는 참고자료 명칭**입니다. 이번 개편에서 외부 자료를 새로 열거나 검증한 것은 아닙니다.

- Vaswani et al., *Attention Is All You Need*, 2017
- PyTorch Documentation
- NumPy Documentation
- Hugging Face Transformers Documentation
- Stanford CRFM, *On the Opportunities and Risks of Foundation Models*
- Ian Goodfellow, Yoshua Bengio, Aaron Courville, *Deep Learning*

**안내:** 교실에서 Tensor 실습을 진행하기 전에 Python·PyTorch 설치 상태를 확인해야 합니다. 모델·라이브러리 버전 및 장치별 실행 차이는 이 문서만으로 검증된 사항이 아닙니다.
