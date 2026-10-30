
같은 맥락에서 등장하지만, **Feature와 Dataset은 같은 개념은 아닙니다.**  
관계를 잡자면 **Dataset을 구성하는 각각의 데이터에서 모델이 입력으로 사용하는 특성들이 Feature**라고 이해하면 좋습니다.

예를 들어 고객 이탈을 예측한다고 해보겠습니다.

|고객|나이|가입 기간|월 사용금액|접속 횟수|이탈 여부|
|---|--:|--:|--:|--:|---|
|A|25|3개월|30,000|5|이탈|
|B|40|24개월|80,000|30|유지|
|C|31|12개월|50,000|15|유지|

이 표 전체가 **Dataset**입니다.

여기서 모델이 고객 이탈을 예측하기 위해 사용하는:

```text
나이
가입 기간
월 사용금액
접속 횟수
```

같은 값들이 **Feature(특징)**입니다.

그리고

```text
이탈 여부
```

는 지도학습에서는 모델이 맞혀야 하는 **Target 또는 Label**이 됩니다.

따라서 관계를 그리면:

```text
Dataset
│
├── Input
│    ├── Feature 1: 나이
│    ├── Feature 2: 가입 기간
│    ├── Feature 3: 월 사용금액
│    └── Feature 4: 접속 횟수
│
└── Label
     └── 이탈 여부
```

### 그런데 Deep Learning에서는 조금 더 주의해야 합니다

앞에서 이야기한 **Representation Learning**과 연결하면 Feature라는 말이 두 가지 맥락에서 사용될 수 있습니다.

전통적인 Machine Learning에서는 사람이 Feature를 준비하거나 설계하는 경우가 많습니다.

```text
Raw Data
↓
사람이 Feature 선택/추출
↓
Feature
↓
Machine Learning Model
```

반면 Deep Learning에서는 원본에 가까운 데이터를 입력하고, 신경망이 학습 과정에서 **유용한 내부 Representation(특징 표현)을 학습**할 수 있습니다.

```text
Raw Data
↓
Deep Neural Network
↓
Feature / Representation 학습
↓
Prediction
```

예를 들어 이미지 Dataset이라면 **이미지들이 Dataset**이고, 신경망이 이미지에서 학습하는 선·형태·패턴 등의 내부 표현은 **학습된 Feature/Representation**이라고 볼 수 있습니다.

그래서 학생들에게는 우선 이렇게 정리해주면 충분합니다.

> **Dataset은 학습에 사용하는 데이터의 집합이고, Feature는 그 데이터에서 모델이 문제를 해결하기 위해 사용하는 특징이다.**

즉, **Dataset = Feature가 아니라, Dataset 안의 데이터를 설명하거나 그로부터 학습되는 특성이 Feature**라고 구분하는 것이 정확합니다.