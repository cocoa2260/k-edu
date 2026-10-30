# Phase 2 — 06. 임베딩(Embedding)

> **과목 목적**  
> Transformer와 LLM에서 배운 벡터 표현을 실제 검색 시스템까지 연결한다. 이 과목의 목표는 "Embedding = 의미를 숫자로 바꾸는 것"이라는 한 문장을 외우는 것이 아니라, **어떤 단위를 어떤 모델로 벡터화하고, 어떤 방식으로 비교하며, 검색 품질을 어떻게 검증해야 하는지** 설명할 수 있게 하는 것이다.

---

## 과목 개요

앞 과목까지 우리는 다음 흐름을 배웠다.

```text
Token
  ↓
Embedding
  ↓
Transformer
  ↓
Contextual Representation
  ↓
LLM
```

이번 과목에서는 같은 "Embedding"이라는 단어가 실제 AI 시스템에서 서로 다른 역할로 사용된다는 점부터 구분한다.

```text
[LLM 내부]
Token ID
  ↓
Token Embedding
  ↓
Transformer Layer
  ↓
Contextual Representation

[검색 시스템]
질문 / 문장 / 문서 Chunk
  ↓
Retrieval Embedding Model
  ↓
Sentence / Document Vector
  ↓
Similarity Search
```

이 두 흐름은 관련되어 있지만 **같은 벡터를 같은 목적으로 쓰는 것은 아니다.**

---

## 전체 학습 지도

```text
Why
왜 문자열 ID만으로는 의미 검색이 어려운가?
        ↓
Concept 1
Vector / Embedding / Vector Space
        ↓
Concept 2
Token Embedding
vs
Contextual Representation
vs
Sentence·Document Embedding
        ↓
Concept 3
Dense
vs
Sparse / Lexical
        ↓
Concept 4
Cosine / Dot Product / Normalization
        ↓
Architecture
Bi-encoder Retrieval
→ Hybrid Retrieval
→ Reranking
        ↓
Operation
Model / Dimension / Similarity / Index Version 관리
        ↓
Evaluation
Recall / Ranking / 실제 업무 질문 Dataset
        ↓
다음 과목
Vector DB
```

---

## 학습 목표

이 과목을 마치면 다음 질문에 자신의 말로 답할 수 있어야 한다.

1. Token ID와 Embedding Vector는 무엇이 다른가?
2. Token Embedding과 Sentence·Document Embedding은 왜 같은 것이 아닌가?
3. Dense Search와 Sparse/Lexical Search는 각각 무엇을 잘 찾는가?
4. BM25의 Vocabulary와 Neural Network Parameter는 어떻게 다른가?
5. Cosine Similarity와 Dot Product는 언제 같은 결과를 낼 수 있는가?
6. Bi-encoder와 Cross-encoder를 왜 함께 사용하는가?
7. Embedding Model을 바꾸면 왜 기존 문서를 다시 Embedding해야 하는가?
8. `dimensions`, 검색 `top-k`, 생성의 `top-k/top-p`를 어떻게 구분하는가?
9. Hybrid Search는 하나의 특정 Model 이름인가, 검색 설계인가?
10. 좋은 Embedding Model을 Benchmark 점수만 보고 선택하면 왜 안 되는가?

---

## 과목에서 계속 사용할 예제

교육 과정 전체에서 같은 사례를 반복해 사용한다.

```text
사용자 질문
"법인카드로 해외 ATM에서 현금을 인출할 수 있나요?"

회사 문서 A
"해외 출장비 정산 기준"

회사 문서 B
"법인카드 국외 현금서비스 및 ATM 인출 제한 규정"

회사 문서 C
"법인카드 분실 신고 절차"

회사 문서 D
"CARD-ATM-2026 예외 승인 절차"
```

이 사례를 통해 다음을 비교한다.

```text
의미가 비슷한 표현을 찾는 힘
        → Dense

ATM / CARD-ATM-2026 같은 정확한 문자열
        → Sparse / Lexical

두 결과를 합침
        → Hybrid

최종 후보를 질문과 직접 다시 비교
        → Reranker / Cross-encoder
```

---
# Unit 1 — AI는 텍스트를 어떻게 벡터로 표현하는가?



> **커리큘럼 위치**
> 
> ① AI 최신 동향 및 전체 지도 ✅
> 
> ② AI / 머신러닝 / 딥러닝 개요 ✅
> 
> ③ Transformer ✅
> 
> ④ LLM ✅
> 
> ⑤ Prompt Engineering ✅
> 
> **⑥ Embedding** ← 현재 학습
> 
> ⑦ Vector DB
> 
> ...

---

## 이번 학습 목표

이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Embedding은 무엇인가?
    
- Token과 Embedding은 무엇이 다른가?
    
- 왜 숫자로 변환해야 하는가?
    
- Embedding은 왜 AI의 '의미 이해'의 시작인가?
    
- RAG와 Vector DB에서 왜 Embedding이 중요한가?
    

---

결론부터 이야기하면,

AI가 사람처럼 의미를 이해하는 것은 아닙니다.

Embedding은 단어와 문장의 의미적 관계를 숫자 공간에서 표현하는 방식입니다.

## ① 문제 이해 (Why)

### 컴퓨터는 글자를 이해할 수 있을까?

사람에게

```text
사과
```

를 보여주면

즉시 떠오르는 것이 있습니다.

- 과일
    
- 빨간색
    
- 먹는다
    
- 과수원
    

즉,

**의미(Meaning)** 를 이해합니다.

---

하지만 컴퓨터는?

```text
사과
```

는 그냥

```text
사

과
```

라는 문자입니다.

의미를 모릅니다.

---

### 그럼 숫자로 바꾸면 될까?

예를 들어

```text
사과 = 1

바나나 = 2

자동차 = 3
```

이렇게 번호를 붙여봅시다.

문제가 있을까요?

엄청난 문제가 있습니다.

컴퓨터는

```text
2 - 1 = 1
```

이라고 계산합니다.

그런데

바나나가

사과보다

1만큼 크다는 뜻일까요?

아닙니다.

번호(ID)는

의미를 담지 못합니다.

---

### 결국 필요한 것은?

모델은 Token ID 자체가 아니라, 학습 과정에서 조정할 수 있는 연속적인 숫자 표현이 필요합니다.

바로 이것이

Embedding입니다.

---

## ② 개념 이해 (Concept)

### Embedding이란?

한 문장으로 정의하면

> **텍스트·이미지 같은 대상을 모델이 계산하고 비교할 수 있는 숫자 벡터(Vector)로 표현하는 방법**

입니다.

Embedding은 원본의 모든 정보를 보존하는 압축 파일이 아닙니다. 어떤 관계가 벡터에 잘 나타나는지는 학습 데이터, 학습 목표, 모델과 사용 목적에 따라 달라집니다.

---

### Token과 Embedding의 차이

많은 사람들이 헷갈립니다.

```
문장

↓

Token

↓

Embedding
```

Token은

문장을

조각내는 것입니다.

예를 들어

```
나는

오늘

학교에

갔다
```

입니다.

---

입력 Embedding은 각 Token ID를 학습 가능한 벡터로 바꿉니다.

```
학교

↓

[-0.21, 0.83, ...]
```

---

즉,

```
Token

=

언어 단위

Embedding

=

의미를 가진 숫자
```

입니다.

---

### 비유

여권을 생각해봅시다.

여권 번호는

```
A12345678
```

입니다.

번호만으로는

아무것도 모릅니다.

하지만

사람의

- 나이
    
- 국적
    
- 직업
    
- 언어
    

등을 함께 보면

그 사람의 특징을 알 수 있습니다.

Embedding도 같습니다.

숫자 자체보다

그 숫자가 표현하는 **특징**이 중요합니다.

---

## ③ 원리 이해 (Principle)

### Embedding은 벡터(Vector)이다.

먼저

벡터가 무엇인지 알아봅시다.

벡터는

여러 개의 숫자로 이루어진 하나의 점입니다.

예를 들어

```
사과

↓

[0.32, -0.41, 0.87]
```

입니다.

실제 모델은

768개,

1024개,

3072개 이상의 숫자를 사용하는 경우가 많습니다.

---

### 왜 여러 개의 숫자가 필요할까?

사람도

사물을

하나의 특징으로 설명하지 않습니다.

예를 들어

사과는

- 색
    
- 맛
    
- 과일
    
- 먹는 것
    
- 둥글다
    

등

수많은 특징을 가지고 있습니다.

Embedding도 여러 차원을 함께 사용해 학습 목표에 유용한 패턴을 분산해서 표현합니다. 위의 `색`, `맛`, `과일`은 직관을 위한 비유일 뿐, 실제 벡터의 한 차원이 사람이 이름 붙인 특징 하나와 정확히 대응하는 경우는 드뭅니다.

---

### 중요한 성질

비슷한 의미는

가까운 위치에 있습니다.

예를 들어

```
사과

      바나나

           포도
```

는

가깝습니다.

하지만

```
자동차
```

는

멀리 있습니다.

즉,

검색용 Embedding은 학습 목표가 관련하다고 판단한 입력들이 선택한 Similarity Metric에서 가깝도록 학습됩니다. 일상적인 의미가 비슷해도 모델의 언어·도메인·학습 방식이 맞지 않으면 멀어질 수 있고, 반대로 글자만 비슷한 표현이 잘못 가까워질 수도 있습니다.

---

#### 이것이 가장 중요한 개념입니다.

Embedding은

```
문자

↓

의미 공간(Semantic Space)
```

으로

보내는 기술입니다.

---

## 벡터 공간(Vector Space)

이제

Embedding의 핵심을 배워봅시다.

예를 들어

2차원이라면

```
            과일

              ↑

      사과

          바나나

────────────────────→

             자동차
```

비슷한 것끼리

가까이 있습니다.

실제 AI에서는

2차원이 아니라

수백~수천 차원입니다.

---

### 어떻게 이런 위치를 결정할까?

여기가 가장 중요한 질문입니다.

Embedding을 만드는 사람이

직접

```
사과는 여기

바나나는 여기
```

놓는 것이 아닙니다.

---

LLM은 학습 과정에서

다음 Token을 예측하려고 합니다.

이 과정에서

비슷한 문맥에서

자주 등장하는 단어들이

자연스럽게

가까운 벡터를 가지게 됩니다.

예를 들어

```
사과를 먹었다.

바나나를 먹었다.

포도를 먹었다.
```

처럼

비슷한 문맥에서

등장합니다.

그러다 보니

벡터도

가까워집니다.

---

### 그래서 Embedding은

사람이 직접 좌표를 지정하는 것이 아니라, 학습 과정에서 형성됩니다. 

다만 실제 서비스에서는 

이미 학습된 Embedding 모델을 가져와 사용하는 경우가 많습니다.

이것이 매우 중요합니다.

---

## Embedding은 무엇을 보존할까?

Embedding은 원문을 그대로 보존하는 것이 아니라, 학습 목적에 유용한 관계를 벡터 공간에 표현합니다.

예를 들어

```
자동차

Car
```

언어는 다르지만

의미는 같습니다.

좋은 Embedding 모델은

이 둘을

가까운 벡터로

표현할 수 있습니다.

(모델에 따라 다르며, 다국어 임베딩 모델은 여러 언어를 같은 의미 공간에 매핑하도록 학습됩니다.)

---

## ④ 관계 이해 (Relation)

이제

전체 AI 구조에서

Embedding의 위치를 보겠습니다.

```
문장

↓

Tokenization

↓

Embedding

↓

Transformer

↓

Attention

↓

LLM
```

입력 Embedding은 Token ID를 연속적인 벡터 표현으로 바꾸는 초기 단계입니다. 이후 Transformer Layer를 지나며 문맥 정보가 반영됩니다.

---

그리고

앞으로 배울 내용과 연결하면

```
Embedding

↓

Vector DB

↓

Similarity Search

↓

RAG

↓

Agent
```

즉,

Embedding은

RAG의 출발점입니다.

---

## ⑤ 활용 이해 (Application)

Embedding은 단순히 LLM 내부에서만 사용하는 기술이 아닙니다.

대표적인 활용 사례는 다음과 같습니다.

|활용|Embedding의 역할|
|---|---|
|의미 검색(Semantic Search)|의미가 비슷한 문서 찾기|
|추천 시스템|비슷한 상품·콘텐츠 추천|
|문서 군집화|비슷한 문서를 자동으로 그룹화|
|RAG|질문과 관련된 문서를 검색|
|중복 문서 탐지|의미가 거의 같은 문서 찾기|

예를 들어 사용자가

> "환불 규정을 알려줘."

라고 질문했을 때,

문서에

> "반품 및 환급 정책"

이라고 쓰여 있어도,

적절한 검색용 Embedding 모델은 두 표현이 같은 업무 의도를 가리킨다는 관계를 학습했을 수 있으므로 관련 문서를 찾는 데 도움이 됩니다. 실제로 잘 찾는지는 회사 질문과 문서로 Retrieval 평가를 해야 합니다.

Embedding에는 크게 두 가지 관점이 있습니다.

1. 입력 Token Embedding
- Token ID를 모델의 첫 입력 벡터로 바꿉니다.

2. Contextual Representation
- Transformer Layer를 지나며 같은 Token도 앞뒤 문맥에 따라 다른 Hidden Representation을 갖습니다.

3. 검색용 Embedding
- 문장이나 문서를 벡터로 바꾸어 의미 검색에 사용하는 표현입니다.

모두 벡터 표현이지만 학습 목표와 사용 목적이 다릅니다. LLM의 임의 Hidden State를 그대로 검색용 Embedding으로 사용한다고 좋은 검색 품질이 자동으로 보장되지는 않습니다.

---

## ⑥ 핵심 정리 (Summary)

이번 Unit에서 반드시 기억해야 할 핵심은 다음과 같습니다.

1. **Embedding은 데이터를 모델이 계산하고 비교할 수 있는 숫자 벡터로 표현하는 방법**입니다.
    
2. Token은 언어를 나누는 과정이고, Embedding은 Token을 의미 공간으로 변환하는 과정입니다.
    
3. 검색용 Embedding은 학습 목표상 관련된 입력이 **선택한 Similarity Metric에서 가까워지도록** 학습됩니다.
    
4. Embedding 벡터는 사람이 직접 만드는 것이 아니라 **학습 과정에서 자동으로 형성**됩니다.
    
5. Embedding은 LLM뿐 아니라 **Vector DB와 RAG의 핵심 기반 기술**입니다.
    

---

## ⑦ 이해도 확인 (Check)

다음 질문에 자신의 언어로 답해보세요.

1. Token과 Embedding은 어떤 차이가 있나요?
    
2. 단순히 단어에 번호(ID)를 붙이는 것으로는 왜 충분하지 않을까요?
    
3. Embedding이 "의미를 보존한다"는 것은 무슨 뜻인가요?
    
4. 비슷한 의미를 가진 단어들이 왜 벡터 공간에서 가까워질까요?
    
5. Embedding이 RAG의 핵심 기술인 이유는 무엇인가요?
    

---

## Knowledge 연결

### 저장 위치

```text
Knowledge/
└── AI/
    └── Embedding/
        ├── Embedding 개요.md
        ├── Token과 Embedding.md
        ├── Semantic Space.md
        └── Embedding의 원리.md
```

### 관련 Wiki Link

```text
[[대규모 언어 모델(LLM)]]
[[트랜스포머(Transformer)]]
[[벡터 데이터베이스(VectorDB)]]
[[검색 증강 생성(RAG)]]
`Semantic Search`
```


# Unit 2 — 검색용 Embedding은 LLM 내부 Embedding과 무엇이 다른가?

## 1. 먼저 세 가지를 분리한다

"Embedding"이라는 단어가 하나의 기술만 뜻한다고 생각하면 이후 Vector DB와 RAG에서 계속 헷갈린다.

### 1-1. Token Embedding

Tokenizer가 만든 Token ID를 모델이 계산할 수 있는 벡터로 바꾸는 입력 표현이다.

```text
"학교"
  ↓ Tokenizer
Token ID 4821
  ↓ Embedding Table
[0.12, -0.31, 0.77, ...]
```

여기서 중요한 것은 `4821`이라는 정수 자체에는 거리나 의미가 없다는 점이다.

```text
Token ID 4821
Token ID 4822
```

두 ID가 1 차이 난다고 두 Token의 의미가 비슷하다는 뜻이 아니다.

---

### 1-2. Contextual Representation

Transformer Layer를 통과하면 같은 Token도 문맥에 따라 다른 표현을 가질 수 있다.

```text
"은행에 돈을 맡겼다"
          ↓
       은행

"강가의 은행나무를 보았다"
          ↓
       은행
```

입력 Token이 같더라도 주변 Token과 Attention을 수행한 뒤의 Hidden Representation은 달라질 수 있다.

따라서 다음을 구분한다.

```text
초기 Token Embedding
= Token ID를 처음 벡터로 바꾼 값

Contextual Representation
= Transformer를 지나며 문맥이 반영된 표현
```

---

### 1-3. Sentence / Document Embedding

검색에서는 보통 질문 하나와 문서 Chunk 하나를 서로 비교해야 한다.

```text
질문
"해외 ATM 인출 한도는?"
        ↓
[질문 전체를 대표하는 하나의 Vector]

문서 Chunk
"법인카드 해외 현금 인출은 1일 ..."
        ↓
[Chunk 전체를 대표하는 하나의 Vector]
```

검색용 모델은 이런 비교가 잘 되도록 별도 학습되는 경우가 많다.

즉,

```text
Token Embedding
≠
검색용 Sentence Embedding
```

이다.

### 자주 하는 오해

> LLM의 Token Vector를 평균 내면 검색용 Embedding이 되는 것 아닌가요?

수학적으로 평균을 낼 수는 있다. 그러나 **검색 품질이 좋다는 보장은 없다.**

검색용 Embedding Model은 흔히 다음 목표를 학습한다.

```text
관련 Query ↔ 관련 Document
          가까이

관련 없는 Query ↔ Document
          멀리
```

따라서 "벡터를 만들 수 있다"와 "검색에 적합한 벡터다"는 다른 문제다.

---

## 2. Query와 Document가 같은 형태라고 가정하지 않는다

검색 Model에 따라 Query와 Document에 서로 다른 Instruction 또는 Encoding 함수를 사용하기도 한다.

```text
Query
"법인카드 해외 인출 가능?"

Document
"해외 ATM 현금서비스 제한 정책 ..."
```

둘의 역할이 다르기 때문이다.

```text
Query
→ 사용자의 정보 요구

Document
→ 답을 포함할 수 있는 후보 정보
```

따라서 실제 Model을 사용할 때는 공식 문서에서 다음을 확인한다.

```text
encode_query가 따로 있는가?
encode_document가 따로 있는가?
Query Prefix가 필요한가?
Document Prefix가 필요한가?
Normalization이 필요한가?
```

---

# Unit 3 — Dense Embedding과 Sparse Retrieval

## 1. Dense란 무엇인가?

Dense Vector는 대부분의 차원에 실수 값이 들어 있는 비교적 짧은 벡터다.

```text
[0.12, -0.43, 0.08, 0.91, ...]
```

사람이 각 차원의 뜻을 직접 읽기는 어렵지만, 학습 과정에서 검색에 유용한 패턴이 분산되어 표현된다.

Dense Retrieval의 강점은 **표현이 달라도 의미가 비슷한 경우**를 찾는 것이다.

```text
Query
"회사카드 해외 현금 인출"

Document
"법인카드 국외 ATM 현금서비스"
```

정확한 단어가 모두 같지 않아도 의미가 가깝다면 후보가 될 수 있다.

---

## 2. Sparse란 무엇인가?

Sparse Representation은 매우 큰 가능한 Feature 공간에서 일부 위치만 값이 존재하는 표현이다.

교육용으로 Vocabulary를 다음처럼 단순화해 보자.

```text
[법인카드, 해외, ATM, 인출, 환불, 출장비]
```

"법인카드 해외 ATM 인출"은 개념적으로 다음처럼 생각할 수 있다.

```text
[1, 1, 1, 1, 0, 0]
```

실제 검색 시스템이 반드시 이런 0/1 배열 전체를 저장한다는 뜻은 아니다. 대규모 Lexical Search는 보통 Inverted Index 같은 효율적인 구조를 사용한다.

---

## 3. BM25의 '전체 단어 사전'은 Model Parameter인가?

일반적인 BM25 문맥에서는 **아니다.**

문서 집합을 분석해서 얻은 검색 용어 목록과 Inverted Index는 신경망 Model의 학습 Parameter와 다르다.

예를 들어 문서가 다음과 같다고 하자.

```text
문서 1: 법인카드 해외 ATM 인출 제한
문서 2: 해외 출장비 정산 기준
문서 3: 법인카드 사용 내역 제출
```

검색 엔진은 개념적으로 다음 정보를 만든다.

```text
Vocabulary
법인카드
해외
ATM
인출
제한
출장비
정산
기준
사용
내역
제출
```

그리고 역색인을 만든다.

```text
ATM      → 문서 1
해외     → 문서 1, 문서 2
법인카드 → 문서 1, 문서 3
```

이것은 문서를 검색하기 위한 Index 구조이지, Backpropagation으로 학습된 Neural Network Weight가 아니다.

### Neural Sparse Model은 다르다

SPLADE나 ELSER처럼 학습된 Sparse Retrieval Model도 있다.

```text
BM25
→ Corpus 통계와 Lexical Matching 중심

Neural Sparse Model
→ 학습된 Model이 Sparse Weight를 생성
```

따라서

```text
Sparse = 모두 BM25
```

가 아니다.

---

## 4. BM25는 무엇을 높게 평가하는가?

BM25는 대표적으로 다음 신호를 사용한다.

```text
Query Term이 Document에 존재하는가?
        ↓
해당 Term이 Document에 얼마나 나타나는가?
        ↓
전체 Document 중 그 Term이 얼마나 흔한가?
        ↓
Document 길이를 어떻게 보정할 것인가?
```

여기서 "드문 단어"는 **현재 입력 문장 안에서 드문 단어**가 아니다.

정확하게는:

> 전체 문서 집합에서 적은 문서에 등장하는 Query Term은 문서를 구별하는 신호가 더 클 수 있다.

예를 들어:

```text
전체 10,000개 문서

"규정"
→ 7,500개 문서 등장

"CARD-ATM-2026"
→ 3개 문서 등장
```

사용자가 `CARD-ATM-2026`을 검색했다면 이 문자열은 특정 문서를 구별하는 힘이 크다.

하지만 여기서 중요한 한계가 있다.

```text
드물다
≠
업무상 중요하다
```

오탈자, 임시 코드, 무의미한 식별자도 드물 수 있다.

따라서 BM25의 희귀성은 **의미 중요도**가 아니라 **검색 구별력에 대한 통계적 신호**다.

---

## 5. Dense와 Sparse는 무엇을 각각 잘 찾는가?

| 상황 | Dense | Sparse/Lexical |
|---|---:|---:|
| 표현은 다르지만 의미가 비슷함 | 강점 | 상대적으로 약함 |
| 제품 코드·규정 번호 정확 일치 | 놓칠 수 있음 | 강점 |
| 동의어·의역 | 강점 | 사전 설정 없으면 약함 |
| 사람 이름·기관명 정확 검색 | 모델에 따라 다름 | 강점 |
| 문맥적 관련성 | 강점 | 제한적 |

예를 들어:

```text
Query
"해외에서 회사카드로 현금을 뽑을 수 있나요?"
```

Dense는 다음 문서를 찾는 데 도움이 될 수 있다.

```text
"법인카드 국외 현금서비스 제한"
```

반면 사용자가 다음처럼 질문하면:

```text
"CARD-ATM-2026 규정"
```

Sparse/Lexical Search가 매우 강할 수 있다.

---

# Unit 4 — Hybrid Search

## 1. Hybrid는 '세 번째 Model 이름'이 아니다

Hybrid Search는 서로 다른 검색 신호를 결합하는 **Architecture Pattern**이다.

대표적인 형태는:

```text
사용자 Query
   ├─ Dense Embedding → Vector Search
   │
   └─ Lexical/Sparse → BM25 또는 Sparse Search
                    ↓
               결과 결합
                    ↓
                Reranking
                    ↓
              최종 Chunk
```

따라서 다음 구성이 모두 가능하다.

```text
Dense Model + BM25
Dense Model + Neural Sparse Model
Dense/Sparse를 모두 출력하는 하나의 Model
```

---

## 2. Dense와 Sparse를 '한 Index에 넣는다'는 말

제품마다 저장 방식은 다르다.

핵심은 이것이다.

> Dense Vector와 Sparse Vector의 원소를 억지로 이어 붙이거나 더해서 하나의 보통 Dense Vector로 만든다는 뜻은 아니다.

가능한 구현은 다음처럼 나뉜다.

```text
방식 A
한 Record
├─ Dense Vector
├─ Sparse Vector
└─ Metadata

방식 B
Dense Index
+
Sparse / Lexical Index
↓
검색 후 결과 결합
```

제품의 API와 Index 구조를 확인해야 한다.

---

## 3. 점수를 그냥 더하면 안 되는 이유

예를 들어:

```text
Dense Similarity
0.82

BM25 Score
17.4
```

두 숫자는 같은 척도가 아니다.

따라서:

```text
0.82 + 17.4
```

를 그대로 의미 있는 통합 점수라고 볼 수 없다.

실무에서는 다음과 같은 방법을 사용한다.

```text
Score Normalization
Weighted Combination
Rank-based Fusion
RRF(Reciprocal Rank Fusion)
```

RRF의 장점은 서로 다른 검색기의 점수 범위보다 **순위**를 기반으로 결과를 합칠 수 있다는 점이다.

---

# Unit 5 — Bi-encoder와 Cross-encoder

## 1. Bi-encoder: 빠른 후보 검색

Bi-encoder는 Query와 Document를 독립적으로 Encoding한다.

```text
Query
  ↓ Encoder
Query Vector

Document
  ↓ Encoder
Document Vector
```

Document Vector는 미리 만들어 저장할 수 있다.

```text
[Offline]
Document
→ Embedding
→ Vector Index 저장

[Online]
Query
→ Embedding
→ 가까운 Document 검색
```

이 구조는 문서가 매우 많아도 검색하기 좋다.

---

## 2. Cross-encoder: 후보 정밀 비교

Cross-encoder는 Query와 Document를 함께 입력한다.

```text
[Query] 해외 ATM 인출 한도는?
[Document] 법인카드 국외 ATM 현금서비스는 ...
        ↓
Cross-encoder
        ↓
Relevance Score
```

Query와 Document Token이 모델 안에서 직접 상호작용할 수 있으므로 세밀한 관련성 판단에 유리할 수 있다.

하지만 전체 문서가 100,000개라면 Query와 100,000개 문서를 각각 함께 넣어야 하므로 비싸고 느리다.

그래서 대표적인 구조는 다음과 같다.

```text
1단계 Retrieval
Bi-encoder / Hybrid Search
→ Top 50 후보

2단계 Reranking
Cross-encoder
→ 후보 50개 정밀 비교

3단계 Final Selection
→ Top 5 Chunk

4단계 Generation
→ LLM Context에 전달
```

`50`, `5`는 예시다. 실제 값은 평가와 Latency Budget으로 정한다.

---

## 3. Cross-encoder가 항상 더 좋다는 뜻은 아니다

다음까지 같이 봐야 한다.

```text
Retrieval Recall
Reranking Quality
Latency
Model Cost
GPU/CPU 자원
Document 길이
언어·도메인 적합성
```

Reranker 자체가 도메인에 맞지 않으면 오히려 좋은 후보의 순서를 망칠 수도 있다.

---

# Unit 6 — Similarity와 Normalization

## 1. Cosine Similarity

Cosine Similarity는 두 벡터의 **각도**, 즉 방향이 얼마나 비슷한지를 본다.

```text
cos(A, B)
=
(A · B) / (|A||B|)
```

개념적으로:

```text
같은 방향
→ 1에 가까움

직교
→ 0 부근

반대 방향
→ -1에 가까움
```

실제 검색 Model의 Score 해석 범위는 Model과 구현에 따라 확인해야 한다.

---

## 2. Dot Product

Dot Product는:

```text
A · B
```

이며 방향뿐 아니라 벡터 크기의 영향을 받을 수 있다.

다음 예를 보자.

```text
Q = [1, 0]
A = [0.8, 0.6]
B = [0.7, 0.0]
```

Cosine은:

```text
cos(Q, A) = 0.8
cos(Q, B) = 1.0

→ B가 더 같은 방향
```

Dot Product는:

```text
Q·A = 0.8
Q·B = 0.7

→ A가 더 큼
```

따라서 정규화되지 않은 벡터에서는 검색 순위가 다를 수 있다.

---

## 3. Normalization

L2 Normalization은 벡터 길이를 1로 맞춘다.

```text
v_normalized
=
v / |v|
```

모든 비교 벡터의 길이가 1이면:

```text
Cosine Similarity
=
Dot Product
```

가 된다.

그래서 어떤 Model은 정규화된 Embedding과 Dot Product를 사용하고, 어떤 Model은 Cosine을 권장한다.

중요한 원칙은:

> 아무 Metric이나 선택하는 것이 아니라 Embedding Model의 학습 방식과 권장 검색 설정에 맞춘다.

---

## 4. Euclidean Distance는 어디에 있는가?

또 다른 대표 방식은 Euclidean Distance(L2 Distance)다.

```text
두 점 사이의 직선 거리
```

Vector DB에 따라 다음 중 하나 이상을 지원한다.

```text
Cosine Similarity
Dot Product / Inner Product
Euclidean / L2 Distance
```

"Score가 높을수록 좋은가" 또는 "Distance가 낮을수록 좋은가"도 제품 API마다 확인해야 한다.

---

# Unit 7 — Embedding Dimension은 무엇인가?

## 1. Dimension

Embedding이 다음처럼 생겼다면:

```text
[0.12, -0.32, 0.91, ...]
```

숫자 개수가 Dimension이다.

예:

```text
1536 dimensions
3072 dimensions
```

Dimension이 크다고 무조건 검색 품질이 높다고 단정할 수는 없다.

같이 봐야 할 것은:

```text
Model 학습 품질
언어 적합성
도메인 적합성
Input Length
Dimension
Index 방식
Latency
Memory / Storage
실제 Retrieval 평가
```

---

## 2. Dimension을 줄이는 것과 Top-k는 완전히 다르다

다음 세 개를 구분한다.

```text
Embedding dimensions
→ Vector 한 개의 숫자 개수

Retrieval top-k
→ 검색 결과로 몇 개의 후보를 가져올 것인가

Generation top-k / top-p
→ 다음 Token 생성 후보를 어떻게 제한할 것인가
```

즉:

```text
dimensions = 1024
```

는 "더 많은 문서를 대충 검색한다"는 뜻이 아니다.

단지 생성되는 Vector의 길이를 1024로 정한다는 뜻이다.

검색에서:

```text
top_k = 20
```

은 상위 20개 후보를 반환한다는 뜻이다.

LLM Decoding의 `top-k`, `top-p`는 또 다른 계층이다.

---

## 3. OpenAI Embedding 예시

2026년 9월 공식 문서 기준 OpenAI는 `text-embedding-3-small`, `text-embedding-3-large`를 Embedding Model로 안내하고 있으며 기본 Dimension은 각각 1536, 3072이다. `dimensions` Parameter로 출력 Vector 길이를 줄일 수 있다.

이 사례에서 배워야 할 것은 Model 이름 암기가 아니라 다음 원칙이다.

```text
Embedding Model
        ↓
Output Dimension
        ↓
Vector Index Dimension과 일치
        ↓
Query와 Document가 동일한 좌표계 사용
```

---

# Unit 8 — BM25는 '학습'하지 않는가?

## 1. 일반적인 BM25

BM25 자체는 Neural Network처럼 Weight를 Backpropagation으로 학습하는 Model이 아니다.

문서가 추가되면 하는 일은:

```text
새 Document 분석
        ↓
Token / Term 추출
        ↓
Inverted Index 갱신
        ↓
Document Frequency 등 Corpus 통계 갱신
```

이다.

이를 Neural Network의 Fine-tuning과 같은 의미의 "학습"이라고 부르지 않는 것이 좋다.

---

## 2. 그래도 조정할 것은 있다

BM25 기반 검색도 운영 설정이 필요하다.

```text
Tokenizer / Analyzer
형태소 분석
Stopword
Synonym
k1
b
Field Boost
Query 설계
```

특히 한국어에서는 단순 공백 분리만으로 검색 품질이 충분하지 않을 수 있다.

따라서:

```text
학습 안 함
≠
설정할 것이 없음
```

이다.

---

# Unit 9 — Embedding Model 선택

## 1. 공개 Benchmark만 보면 안 되는 이유

회사 문서 검색에서는 실제 질문이 다음처럼 나타날 수 있다.

```text
CARD-ATM-2026
ATM 출금
현금서비스
회사카드
법인카드
공공기관 고유 사업명
한국어 약어
영문 제품명
```

일반 Benchmark에서 높은 Model이 반드시 회사 데이터에서도 가장 좋은 것은 아니다.

---

## 2. 최소 평가 Dataset을 만든다

예를 들어:

| Query | 찾아야 할 정답 문서 |
|---|---|
| 해외 ATM에서 법인카드 사용 가능? | 국외 현금서비스 제한 규정 |
| CARD-ATM-2026 | CARD-ATM-2026 예외 승인 절차 |
| 출장 항공권 취소 비용 | 출장비 및 항공권 환불 규정 |

이 Dataset으로 각 Model을 비교한다.

---

## 3. 무엇을 측정할까?

초기 Retrieval에서는 특히 **정답 문서를 후보 안에 넣는 능력**이 중요하다.

예:

```text
Recall@5
Recall@10
Recall@20
```

그리고 Ranking 품질을 볼 때는:

```text
MRR
NDCG
```

같은 Metric을 사용할 수 있다.

강의에서는 수식보다 역할을 먼저 이해한다.

```text
Recall
→ 정답 후보를 놓치지 않았는가?

Ranking
→ 정답을 얼마나 위에 올렸는가?
```

---

# Unit 10 — Model을 바꾸면 왜 Re-indexing이 필요한가?

Embedding Model A와 Model B는 일반적으로 서로 다른 Vector Space를 만든다.

```text
Document
→ Model A
→ Vector A

Query
→ Model B
→ Vector B
```

이 두 Vector의 좌표값이 같은 의미 체계에 있다고 보장할 수 없다.

따라서 Model을 변경하면 보통:

```text
새 Model 선정
        ↓
기존 Document 전체 Re-embedding
        ↓
새 Index 생성
        ↓
동일 Evaluation Dataset 실행
        ↓
기존 Index와 비교
        ↓
Traffic 전환
        ↓
문제 시 Rollback
```

순서가 안전하다.

---

## 운영 Metadata

최소한 다음을 기록하는 것이 좋다.

```text
embedding_model
embedding_model_version
dimension
normalization
similarity_metric
chunking_version
index_version
created_at
```

Embedding만 바뀌는 것이 아니다. Chunking 방식이 바뀌어도 검색 결과가 달라질 수 있다.

---

# Unit 11 — 전체 Retrieval Architecture

지금까지 배운 내용을 실제 RAG 검색 Pipeline으로 연결한다.

## Offline Indexing

```text
원본 문서
  ↓
Parsing / OCR
  ↓
정제
  ↓
Chunking
  ↓
Metadata
  ↓
┌───────────────────┐
│ Dense Embedding   │
└───────────────────┘
  ↓
Vector Index

동시에 필요하면

Chunk Text
  ↓
Lexical Analyzer
  ↓
BM25 / Sparse Index
```

---

## Online Query

```text
사용자 질문
      ↓
Query 정제 / 권한 확인
      ↓
┌───────────────┬────────────────┐
│ Dense Search  │ Lexical Search │
└───────────────┴────────────────┘
      ↓
Hybrid Fusion
      ↓
Top Candidate
      ↓
Reranker
      ↓
Final Chunk
      ↓
LLM Context
      ↓
Grounded Answer
```

이 그림에서 Embedding은 전체 RAG 중 **Retrieval을 가능하게 하는 한 구성요소**다.

```text
Embedding
≠ Vector DB
≠ RAG
≠ LLM
```

각 역할을 분리해야 한다.

---

# Unit 12 — 실습

## Practice 1 — ID와 Embedding 구분

다음 표현을 보고 어떤 문제가 있는지 설명한다.

```text
사과 = 1
바나나 = 2
자동차 = 3
```

질문:

1. 왜 `2 - 1 = 1`이 의미 관계가 아닌가?
2. Token ID는 왜 검색 거리로 바로 사용할 수 없는가?
3. Embedding Vector에는 어떤 관계가 표현되기를 기대하는가?

---

## Practice 2 — Token vs Sentence Embedding

다음 문장을 사용한다.

```text
"법인카드 해외 ATM 인출 제한"
```

다음 두 관점을 각각 설명한다.

```text
A. 각 Token이 갖는 Representation
B. 문장 전체를 대표하는 검색 Vector
```

둘의 목적이 왜 다른지 적는다.

---

## Practice 3 — Dense vs Sparse

질문:

```text
"회사카드로 해외에서 현금 인출 가능?"
```

후보:

```text
A. 법인카드 국외 현금서비스 제한 규정
B. 해외 출장 숙박비 지급 기준
C. CARD-ATM-2026 예외 승인 절차
```

다음을 예측한다.

1. Dense가 잘 찾을 가능성이 높은 문서
2. Exact Keyword가 중요한 문서
3. Hybrid가 유리할 수 있는 이유

---

## Practice 4 — BM25 희귀 단어

다음 두 단어를 비교한다.

```text
규정
CARD-ATM-2026
```

질문:

1. 어떤 단어가 Corpus에서 더 구별력이 높을 가능성이 있는가?
2. 그 단어가 업무상 더 중요한 단어라는 뜻인가?
3. Query에 그 단어가 없더라도 자동으로 높은 점수를 주는가?

---

## Practice 5 — Similarity 직접 계산

```text
Q = [1, 0]
A = [0.8, 0.6]
B = [0.7, 0.0]
```

1. `Q·A`, `Q·B`를 계산한다.
2. Cosine Similarity를 계산한다.
3. 두 Metric에서 순위가 왜 달라지는지 설명한다.
4. A/B를 모두 L2 Normalize하면 무엇이 달라지는지 설명한다.

---

## Practice 6 — Bi-encoder와 Cross-encoder 배치

문서가 500,000개 있다고 가정한다.

다음 설계 중 더 현실적인 것을 선택하고 이유를 설명한다.

```text
A.
Query + 500,000개 문서
→ Cross-encoder 500,000회

B.
Bi-encoder / Vector Search
→ Top 100
→ Cross-encoder Reranking
→ Top 10
```

---

## Practice 7 — Dimension / top-k / top-p 구분

다음 설정을 분류한다.

```text
dimensions = 1024
retrieval top_k = 20
generation top_p = 0.9
```

각각 다음 중 어디에 해당하는가?

```text
Vector 표현 크기
검색 후보 수
LLM Token Decoding
```

---

## Practice 8 — Model Migration

현재:

```text
Model A
Dimension 768
Cosine
Index v1
```

새 Model:

```text
Model B
Dimension 1024
Normalized Dot Product
```

바로 Query만 Model B로 변경하면 안 되는 이유를 설명하고 안전한 전환 절차를 작성한다.

---

# 학생이 자주 헷갈리는 부분

| 오해 | 정확한 설명 |
|---|---|
| Token ID 숫자가 가까우면 의미도 가깝다 | Token ID는 식별 번호다. |
| Embedding의 각 차원은 사람이 읽을 수 있는 한 가지 의미다 | 보통 특징이 여러 차원에 분산되어 있다. |
| LLM Token Embedding을 Vector DB에 넣으면 된다 | 검색용 Embedding은 목적과 학습 방식이 다를 수 있다. |
| Dense가 Sparse보다 무조건 최신이고 좋다 | 코드·고유명사·정확 문자열은 Lexical Search가 강할 수 있다. |
| Sparse = BM25 | BM25 외에도 Neural Sparse Retrieval이 있다. |
| BM25의 Vocabulary는 Neural Model Parameter다 | 일반 BM25에서는 Corpus의 검색 용어와 Index 정보다. |
| 드문 단어는 중요한 단어다 | 드물다는 것은 구별력 신호이지 업무 중요도 보증이 아니다. |
| Hybrid는 특정 Model 이름이다 | 서로 다른 Retrieval 신호를 결합하는 설계다. |
| Dense와 Sparse Vector를 그냥 원소별로 더한다 | 구현마다 별도 신호 저장·검색·Fusion을 사용한다. |
| Cross-encoder로 전체 문서를 검색하면 된다 | 계산량 때문에 보통 후보 Reranking에 쓴다. |
| Cosine이 항상 최고다 | Model의 권장 Metric과 실제 평가가 기준이다. |
| Vector Dimension을 줄이면 더 많은 후보를 검색한다 | Dimension과 Retrieval top-k는 별개다. |
| 검색 top-k와 생성 top-k는 같은 설정이다 | 이름만 같고 적용 계층이 다르다. |
| Model을 바꿔도 기존 Vector를 그대로 쓸 수 있다 | 다른 Vector Space가 되므로 보통 Re-embedding이 필요하다. |

---

# 전체 요약

이번 과목의 핵심을 한 장으로 정리하면 다음과 같다.

```text
텍스트
  ↓
Retrieval Embedding Model
  ↓
Dense Vector
  ↓
Vector Similarity Search
  ┐
  │
  ├─ 필요하면 Hybrid Fusion
  │
Lexical / Sparse Search
  ↓
Candidate
  ↓
Cross-encoder / Reranker
  ↓
Final Chunk
  ↓
RAG Context
```

그리고 반드시 기억한다.

```text
Token
≠ Embedding

Token Embedding
≠ Sentence / Document Embedding

Dense
≠ Sparse

Embedding Model
≠ Vector DB

Vector DB
≠ RAG

Retrieval top-k
≠ LLM Decoding top-k
```

---

## 실무 팁

1. Query와 Document는 **동일한 Embedding Model 계열과 호환되는 Encoding 정책**을 사용한다.
2. Model ID뿐 아니라 Version, Dimension, Normalization, Similarity Metric을 기록한다.
3. Model을 바꾸기 전에 실제 업무 Query–Relevant Document Dataset을 만든다.
4. Dense만으로 시작해도 되지만 코드·규정번호·기관명 검색 실패가 보이면 Hybrid를 검토한다.
5. Reranker를 추가할 때 Retrieval Recall과 Latency가 어떻게 변하는지 함께 측정한다.
6. Chunking 변경도 Embedding Model 변경처럼 검색 품질에 큰 영향을 줄 수 있다.
7. Vector Store 제품 기능과 Embedding Model 기능을 혼동하지 않는다.

---

## 주의사항

- "Semantic"이라는 표현이 사람과 같은 의미 이해를 보장하는 것은 아니다.
- 2차원 그림은 고차원 Vector Space를 이해하기 위한 비유다.
- Public Benchmark는 Model 선택의 출발점이지 최종 근거가 아니다.
- 동일한 Similarity Score라도 Model이 다르면 절대값을 직접 비교하기 어렵다.
- Retrieval Score가 높다는 사실만으로 문서 내용이 사실이라는 뜻은 아니다.
- Reranking을 사용해도 Grounding과 Citation 검증은 별도 문제다.

---

## 참고자료

- OpenAI, **Vector embeddings** — Embedding의 활용, `text-embedding-3-small`, `text-embedding-3-large`, `dimensions` Parameter 확인.
- Sentence Transformers, **Quickstart / Semantic Search / Retrieve & Re-Rank** — Bi-encoder와 Cross-encoder의 역할 확인.
- Elasticsearch, **How full-text search works / Similarity settings** — Inverted Index와 BM25의 Corpus 통계 기반 검색 확인.
- Elastic, **ELSER** — Neural Sparse Retrieval의 사례 확인.
- Pinecone, **Hybrid Search** — Dense/Sparse 신호를 결합하는 검색 Architecture 사례 확인.
- Reimers & Gurevych, **Sentence-BERT** — Sentence Embedding 기반 효율적 Semantic Similarity의 대표 연구.

---

## 관련 Wiki Link

```text
[[트랜스포머(Transformer)]]
[[대규모 언어 모델(LLM)]]
[[프롬프트 엔지니어링(Prompt Engineering)]]
[[벡터 데이터베이스(VectorDB)]]
[[검색 증강 생성(RAG)]]
[[Semantic Search]]
[[Hybrid Search]]
[[Reranking]]
[[BM25]]
```

---

## 저장 위치 제안

```text
Academy/
└── 00. 교육과정(curriculum)/
    └── 01. Phase2_AI/
        └── 06. 임베딩(Embedding)/
            └── 임베딩(Embedding)_강의용.md
```

Knowledge로 분리한다면:

```text
Knowledge/
└── AI/
    └── Embedding/
        ├── Embedding 개요.md
        ├── Token Embedding과 Retrieval Embedding.md
        ├── Dense와 Sparse Retrieval.md
        ├── Similarity와 Normalization.md
        ├── Bi-encoder와 Cross-encoder.md
        └── Embedding 운영과 Re-indexing.md
```
