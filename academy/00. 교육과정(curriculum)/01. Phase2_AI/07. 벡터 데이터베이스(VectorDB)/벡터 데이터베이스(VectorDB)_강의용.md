
# Phase 2 — 07. 벡터 데이터베이스(Vector DB)

> 과목 단위 안내. 아래에는 기존 Unit별 상세 강의를 보존한다. 실행하지 않은 예제는 검증 완료로 표시하지 않는다.

## 개요

벡터 생성 모델과 저장·색인·검색 시스템의 책임을 구분한다.

## 학습 목표

Exact/ANN, HNSW/IVF, Hybrid Search, Metadata·권한 Filtering을 설명한다.

## Why

빠른 후보 검색만으로 정답 근거나 문서 접근 권한이 보장되지 않는다.

## Concept

Embedding Model은 벡터를 만들고 DB는 저장·색인·후보 검색을 맡는다.

## Architecture

벡터·Metadata 색인→후보 검색→권한 Filter→필요 시 Reranking의 경계를 그린다.

## Example

규정 번호가 빠지고 타 부서 문서가 섞일 때 검색 방식과 권한을 따로 고친다.

## Practice

작은 후보 표에서 Exact/ANN와 권한 조건 적용 전후를 비교한다.

## Summary

검색 Top-k는 후보 수이며 생성 모델의 Top-k/Top-p와 다르다.

## 실무 팁

Index·Embedding 버전과 권한 Filter 위치를 기록한다.

## 주의사항

유사도가 높다는 이유만으로 비공개 문서를 모델 Context에 넣지 않는다.

## 참고자료

- [본문의 공식·원문 참고자료](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) — Exact/ANN, HNSW, IVF 계열의 인덱스 개념을 확인한다.

## 관련 Wiki Link

- `[[임베딩(Embedding)]]`는 기존 강의의 Wiki 제안 표기다. 실제 Wiki 경로는 아직 확인되지 않았다.

## 전체 학습 지도

이 과목에서는 Vector DB 제품 사용법보다 먼저 **검색 시스템 안에서 각 구성 요소가 무엇을 책임지는지**를 이해합니다.

```text
문서
  ↓
Parsing / Chunking
  ↓
Embedding Model
  ↓
Vector
  ↓
Vector 저장 + Metadata
  ↓
Index
  ├─ Exact Search
  └─ ANN
      ├─ HNSW
      └─ IVF
  ↓
Query Vector
  ↓
Candidate Retrieval
  ↓
Metadata / Permission Filter
  ↓
필요 시 Hybrid Search / Reranking
  ↓
Top-k Chunk
  ↓
RAG Context
```

이 흐름에서 반드시 구분해야 할 책임은 다음과 같습니다.

```text
Embedding Model
→ Vector를 만든다.

Vector DB / Vector Search Engine
→ Vector와 Metadata를 저장하고 검색한다.

Index
→ 많은 Vector 중 검색 범위를 빠르게 좁힌다.

Reranker
→ 검색된 후보를 질문과 함께 다시 비교하여 순서를 조정한다.

LLM
→ 최종 Context를 이용하여 답변을 생성한다.
```

---

# [학습] 벡터 데이터베이스(Vector DB) (Unit 1 - 왜 일반 데이터베이스로는 AI 검색을 할 수 없는가?)

> **기술 확인일: 2026-09-24 (KST).** 제목의 질문은 검색 구조를 비교하기 위한 것입니다. 관계형 DB도 제품과 설정에 따라 벡터 저장·검색 기능을 제공할 수 있으며, VectorDB만이 AI 검색의 유일한 구현은 아닙니다.

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
> ⑥ Embedding ✅
> 
> **⑦ Vector DB** ← 현재 학습
> 
> ⑧ RAG
> 
> ...

---

## 이번 학습 목표

이번 Unit이 끝나면 다음 질문에 답할 수 있어야 합니다.

- Vector DB는 왜 등장했는가?
    
- 일반 DB(SQL)와 무엇이 다른가?
    
- Embedding과 Vector DB는 어떤 관계인가?
    
- AI는 문서를 어떻게 검색하는가?
    
- RAG 검색에서 Vector Search는 언제 유용하고 언제 다른 검색 방식이 필요한가?
    

---

## ① 문제 이해 (Why)

### AI는 검색을 어떻게 할까?

먼저 질문을 하나 해보겠습니다.

회사 규정 문서에 아래와 같이 적혀 있습니다.

```text
반품 및 환급 정책
```

사용자가 질문합니다.

```text
환불 규정을 알려줘.
```

여러분은

이 문서를 찾을 수 있을까요?

당연히 찾을 수 있습니다.

왜냐하면

여러분은

```text
환불 = 환급

규정 = 정책
```

이라는 것을 알기 때문입니다.

---

그런데 단순한 문자열 조건만 사용한 검색은 어떨까요?

```text
환불

≠

환급
```

문자가 다릅니다.

따라서 `환불`이라는 문자열만 찾도록 작성한 Query는 `환급` 문서를 놓칠 수 있습니다.

---

### SQL은 검색 방식이 아니라 데이터 질의 언어다

예를 들어

```sql
SELECT *

FROM document

WHERE title LIKE '%환불%'
```

그러면

문서에

```text
환급
```

이라고 적혀 있으면

찾지 못합니다.

---

여기서 “SQL은 문자를 찾고 Vector DB는 의미를 찾는다”고 결론 내리면 안 됩니다. SQL은 관계형 데이터베이스를 질의하는 언어이며, PostgreSQL 같은 데이터베이스는 Exact Match, `LIKE`, Full-text Search와 확장 기능을 통한 Vector Search까지 수행할 수 있습니다.

위 예제가 `환급`을 찾지 못한 이유는 **SQL을 사용했기 때문이 아니라 `LIKE '%환불%'`이라는 문자열 조건만 사용했기 때문**입니다.

---

### 사람이 하는 검색

사람은

```text
환불

↓

환급

↓

반품

↓

교환
```

이

비슷한 의미라는 것을 압니다.

즉,

사람은

**의미(Semantics)** 로 검색합니다.

---

의미가 비슷한 표현을 벡터로 비교하려면 많은 Embedding을 저장하고 가까운 후보를 제한된 시간 안에 찾는 기능이 필요합니다. 전용 Vector Database, 검색 엔진의 Vector 기능, PostgreSQL의 Vector Extension처럼 여러 구현이 이 문제를 해결합니다.

---

## ② 개념 이해 (Concept)

### Vector DB란?

한 문장으로 정의하면

> **고차원 벡터와 관련 Metadata를 저장하고, 거리 또는 유사도 기준의 Nearest Neighbor Search를 효율적으로 수행하도록 설계된 데이터 시스템**

입니다.

Vector DB는 검색의 기준이 되는 Embedding 벡터를 중심으로 저장합니다.

실제 서비스에서는 벡터와 함께 원문 또는 원문 위치, 문서 ID, Metadata를 연결합니다. 원문을 같은 시스템에 저장할지 별도 Object Storage나 Database에서 가져올지는 제품과 아키텍처에 따라 다릅니다.

검색은 벡터를 기준으로 이루어지고,
검색된 후에는 원문을 함께 가져옵니다.

---

### 다시 흐름을 보면

우리는

지난 Unit에서

```text
문장

↓

Embedding

↓

Vector
```

를 배웠습니다.

예를 들어

```text
환불 규정
```

↓

```text
[0.34, -0.12, ...]
```

입니다.

Vector DB는

이 벡터를 저장합니다.

---

### 비유

도서관을 생각해봅시다.

기존 도서관은

책 제목 순으로 정렬합니다.

```text
A

B

C

...
```

입니다.

---

Vector 검색 시스템은 각 벡터를 좌표처럼 비교하고, Index를 이용해 가까운 후보를 찾습니다.

```text
환불

환급

반품

교환
```

적절한 Embedding 모델에서는 이 표현들이 가까운 벡터가 될 수 있습니다.

---

즉,

책을 물리적으로 의미 순서로 꽂아 두는 것보다는, **질문과 가까울 가능성이 높은 책으로 빠르게 이동할 수 있는 색인 지도**를 만든 도서관에 가깝습니다. HNSW와 IVF 같은 Index의 실제 저장 구조와 탐색 방식은 서로 다릅니다.

---

## ③ 원리 이해 (Principle)

### Vector DB에는 무엇이 저장될까?

예를 들어

문서가 있습니다.

```text
문서1

환불 정책
```

↓

Embedding

↓

```text
[0.32, 0.84, ...]
```

---

문서2

```text
배송 안내
```

↓

```text
[-0.82, 0.12, ...]
```

---

문서3

```text
교환 정책
```

↓

```text
[0.28, 0.81, ...]
```

---

Vector DB에는

실제로

이런 벡터들이

저장됩니다.

---

## 사용자가 질문한다.

예를 들어

```text
환불은 어떻게 하나요?
```

---

먼저

Embedding합니다.

```text
질문

↓

Embedding

↓

[0.31, 0.80, ...]
```

---

그 다음

Vector DB에서

가장 가까운 벡터를 찾습니다.

```text
질문 벡터

↓

거리 계산

↓

가장 가까운 문서
```

```
Vector DB는
가장 비슷한 문서를 하나만 찾는 것이 아닙니다.

보통

Top-3

Top-5

Top-10

처럼

가장 유사한 여러 문서를 함께 반환합니다.

이것을 Top-K Search라고 합니다.
```

---

### 왜 가까운 것이 중요한가?

Embedding에서는

비슷한 의미가

가까운 위치에 있습니다.

예를 들어

```text
질문

↓

환불
```

문서

```text
환급 정책
```

벡터가

가깝습니다.

그러므로

찾을 수 있습니다.

---

## Similarity Search

이것이

Vector DB의 핵심입니다.

역할을 먼저 나누면 **Embedding Model이 텍스트를 Vector로 만들고, Vector DB 또는 Search Engine이 Vector와 문서 ID·Metadata를 저장하며, Index/Search 방식이 가까운 후보를 찾습니다.** 검색 결과의 문서가 질문에 실제로 맞는지와 사용자가 볼 권한이 있는지는 별도의 검증입니다.

Similarity

=

유사도

입니다.

즉,

```text
질문

↓

유사한 벡터 찾기

↓

문서 반환
```

입니다.

---

### 거리(Distance)

벡터는

거리를 계산할 수 있습니다.

예를 들어

```text
사과

↓

●
```

```text
바나나

↓

●
```

가깝습니다.

반면

```text
자동차

↓

●
```

는

멀리 있습니다.

즉,

선택한 Embedding 모델과 Distance Metric에서 거리가 가까울수록 **모델이 학습한 기준상 관련성이 높다고 해석할 수 있습니다.** 이것이 실제 업무의 관련성과 일치하는지는 평가가 필요합니다.

---

### 코사인 유사도(Cosine Similarity)

널리 사용되는 방법 중 하나입니다.

복잡한 수식은

지금은 몰라도 됩니다.

핵심만 기억합시다.

> **두 벡터가 같은 방향을 향할수록 Cosine Similarity가 높다. 그 값이 의미 관계를 잘 반영하는지는 Embedding Model의 학습 방식에 달려 있다.**

즉,

```text
질문

↗
```

문서

```text
↗
```

이면

매우 유사합니다.

반대로

```text
질문

↗
```

문서

```text
↘
```

이면

관련성이 낮습니다.

> 실제 시스템에서는 코사인 유사도 외에도 **내적(Dot Product)**, **유클리드 거리(Euclidean Distance)** 등을 사용하는 경우가 있습니다. 어떤 방식을 사용하는지는 Embedding 모델과 Vector DB의 설계에 따라 달라집니다.

---

## 그런데 문제가 하나 있다.

문서가

100억 개라면?

모든 벡터를

하나씩 비교할까요?

```text
질문

↓

문서1

문서2

...

문서100억
```

불가능합니다.

너무 느립니다.

---

그래서

Vector DB는

특수한 검색 알고리즘을 사용합니다.

대표적으로

```text
ANN

Approximate Nearest Neighbor
```

입니다.

---

### ANN이란?

쉽게 말하면

> **정답에 매우 가까운 벡터를 아주 빠르게 찾는 알고리즘**

입니다.

왜 "Approximate(근사)"일까요?

100억 개를 모두 비교하면 가장 정확하지만 시간이 너무 오래 걸립니다.

대신 ANN은

조금의 정확도를 양보하는 대신

엄청난 속도를 얻습니다.

예를 들어,

- 모든 집을 직접 방문하는 대신,
    
- 먼저 동네를 좁힌 후,
    
- 그 안에서 가장 가까운 집을 찾는 것과 비슷합니다.
    

현대 RAG 시스템은 대부분 ANN 기반 검색을 사용합니다.

```
대표적인 ANN 알고리즘과 Index 구성 방식으로는

HNSW

IVF / IVFFlat

PQ 계열

등이 있습니다.

여기서는 HNSW와 IVF를 **제품 이름이 아니라 ANN Index/Search 방식**으로 이해합니다.
```

---

# [보강] HNSW와 IVF를 실제 탐색 지도처럼 이해하기

Vector Index는 문서를 의미 순서대로 한 줄로 정렬해 두는 기능이 아닙니다.

문서의 Embedding은 실제로 수백~수천 차원의 좌표입니다.

```text
문서 A → [0.12, -0.38, 0.72, ...]
문서 B → [0.04,  0.55, 0.11, ...]
질문   → [0.10, -0.35, 0.75, ...]
```

문서가 100만 개라면 질문이 들어올 때마다 모든 문서와 거리를 계산하는 방식은 데이터가 커질수록 비용이 커집니다.

```text
Exact Search

질문 Vector
→ 모든 Document Vector와 비교
→ 실제로 가장 가까운 Vector 선택
```

ANN Index는 대신 다음 질문에 답하기 위한 **탐색 지름길**을 만듭니다.

> "가까운 문서가 있을 가능성이 높은 영역을 먼저 찾아가면, 전체를 다 보지 않고도 좋은 후보를 찾을 수 있지 않을까?"

이 때문에 ANN은 속도를 얻는 대신 Exact Search의 결과 일부를 놓칠 수 있습니다. 이를 검색 품질 측면에서는 흔히 **Recall Trade-off**로 봅니다.

## HNSW — 가까운 점을 연결한 여러 층의 Graph

HNSW는 `Hierarchical Navigable Small World`의 약자입니다.

핵심 아이디어는 Vector를 점으로 보고, 가까운 점 사이에 연결을 만드는 것입니다.

```text
A ───── B ───── C
│       │
D ───── E ───── F
```

하지만 모든 점을 같은 밀도로 연결하면 탐색 비용이 커집니다. 그래서 여러 층을 둡니다.

```text
상위 Layer
A ───────────── F
     │
중간 Layer
A ─── C ─── F
│     │
하위 Layer
A-B-C-D-E-F-G-H-I ...
```

검색은 대략 다음과 같이 생각할 수 있습니다.

```text
Query Vector
   ↓
상위 Layer에서 먼 거리를 빠르게 이동
   ↓
가까운 지역 발견
   ↓
한 층씩 내려감
   ↓
더 많은 이웃을 비교
   ↓
Top-k Candidate 반환
```

도서관 비유로 보면 HNSW는 **관련 책끼리 연결된 통로를 따라 큰 구역에서 세부 구역으로 이동하는 지도**에 가깝습니다.

### HNSW에서 자주 보는 설정

제품마다 이름과 허용 범위는 다를 수 있지만 대표적으로 다음 개념을 접합니다.

```text
M
→ 한 Node가 연결할 이웃의 최대 폭과 관련
→ 크게 잡으면 탐색 품질이 좋아질 수 있지만 Index Memory와 Build 비용 증가

ef_construction
→ Index를 만들 때 고려하는 Candidate 폭
→ 크게 잡으면 Build 품질이 좋아질 수 있지만 생성 시간이 증가

ef_search / efSearch
→ 검색할 때 탐색하는 Candidate 폭
→ 크게 잡으면 Recall이 좋아질 수 있지만 Latency 증가
```

예를 들어 pgvector의 HNSW는 `m`, `ef_construction`, `hnsw.ef_search` 같은 설정을 제공합니다. Faiss도 HNSW 계열에서 `M`, `efSearch`와 같은 개념을 사용합니다.

### HNSW의 일반적인 장단점

```text
장점
- 높은 Recall과 낮은 Query Latency의 균형을 얻기 쉬움
- IVF처럼 별도 군집 학습 단계를 요구하지 않는 구현이 있음
- 데이터가 추가되는 환경에서 비교적 유연하게 사용할 수 있는 구현이 많음

주의점
- Graph 연결 정보를 저장하므로 Memory 사용량이 커질 수 있음
- Index Build가 느릴 수 있음
- Filter와 결합했을 때 실제 Candidate 수가 줄어드는 방식은 제품별로 다름
```

---

## IVF — Vector 공간을 여러 구역으로 나누고 일부 구역만 검색

IVF는 `Inverted File` 계열 Index입니다.

먼저 Vector 공간을 여러 Cluster/List로 나눕니다.

```text
전체 Vector

┌────────────┬────────────┬────────────┐
│ Cluster 1  │ Cluster 2  │ Cluster 3  │
│  • • •     │ • • • •    │  • •       │
│   •        │    •       │ • • •      │
└────────────┴────────────┴────────────┘
```

중요한 점은 이 Cluster가 사람이 붙인 `인사`, `출장`, `계약` 같은 업무 분류가 아니라는 것입니다.

실제 Cluster는 **Vector 위치를 기준으로 계산된 공간 분할**입니다.

검색할 때는 모든 Cluster를 보지 않고 Query Vector와 가까운 Cluster 몇 개만 확인합니다.

```text
Query Vector
   ↓
가까운 Cluster 찾기
   ↓
선택된 Cluster 내부의 Vector 비교
   ↓
Top-k Candidate 반환
```

도서관 비유로 하면 IVF는 **먼저 어느 서가 구역을 찾아볼지 결정한 뒤, 그 구역 안에서 책을 찾는 방식**입니다.

### IVF에서 자주 보는 설정

```text
nlist / lists
→ 전체 Vector 공간을 나눌 List 또는 Cluster 수

nprobe / probes
→ Query 때 실제로 검색할 List 수
```

`nprobe`를 늘리면 더 많은 구역을 보기 때문에 Recall이 높아질 수 있지만 검색 비용도 증가합니다.

pgvector의 IVFFlat은 Index를 만들기 전에 데이터가 어느 정도 존재해야 하며, Index 구성 과정에서 k-means 기반 Cluster 구성 단계가 있습니다.

### IVF의 일반적인 장단점

```text
장점
- 탐색할 데이터 범위를 크게 줄일 수 있음
- HNSW보다 Build가 빠르고 Memory 부담이 낮을 수 있는 구현이 있음

주의점
- 가까운 Cluster를 잘못 선택하면 실제 관련 Vector를 놓칠 수 있음
- Cluster 수와 Query 때 탐색할 Cluster 수의 설정이 Recall/Latency에 큰 영향을 줌
- 데이터 분포가 크게 바뀌면 Index 재구성을 검토해야 함
```

---

## HNSW와 IVF를 한눈에 비교

| 구분 | HNSW | IVF / IVFFlat |
|---|---|---|
| 핵심 구조 | Multi-layer Graph | Cluster/List 분할 |
| 탐색 | Graph 연결을 따라 이동 | 가까운 List 선택 후 내부 검색 |
| 별도 학습 단계 | 일반적으로 없음 | Cluster 구성 단계 필요 |
| Build | 상대적으로 무거울 수 있음 | 상대적으로 빠를 수 있음 |
| Memory | Graph 때문에 커질 수 있음 | 상대적으로 낮을 수 있음 |
| Recall/Latency 조절 | `ef_search` 등 | `nprobe`/`probes` 등 |
| 대표 확인 항목 | Recall@K, Latency, Memory | Recall@K, Latency, List/Probe 설정 |

여기서 가장 중요한 결론은 다음입니다.

> **HNSW가 항상 최고이거나 IVF가 항상 대규모에 정답인 것은 아닙니다. 실제 Dataset, Update 패턴, Memory, Latency 목표, Filter 방식으로 평가해야 합니다.**

---

## Exact Search와 ANN은 무엇을 기준으로 선택할까?

데이터가 작다면 ANN이 필요하지 않을 수도 있습니다.

```text
작은 Dataset
→ Exact Search로도 충분히 빠름
→ 결과를 정확히 재현하기 쉬움

큰 Dataset / 낮은 Latency 요구
→ ANN 검토
→ Recall과 Latency 측정
```

따라서 실무 질문은

```text
"Vector DB를 쓰는가?"
```

보다

```text
"우리 데이터 규모와 지연시간 목표에서
Exact와 ANN 중 어떤 검색 구조가 적절한가?"
```

에 더 가깝습니다.

---

## ④ 관계 이해 (Relation)

지금까지 배운 내용을 연결해봅시다.

```text
문서

↓

Embedding

↓

Vector

↓

Vector DB 저장

↓

사용자 질문

↓

Embedding

↓

Similarity Search

↓

가장 가까운 문서
```

이것이

Vector Search입니다.

---

그리고

다음 커리큘럼과 연결하면

```text
Embedding

↓

Vector DB

↓

RAG

↓

LLM

↓

답변 생성
```

즉,

Vector DB는

RAG의

검색 엔진입니다.

---

## 관계형 DB와 Vector 검색 기능을 어떻게 선택할까?

`SQL DB`와 `Vector DB`는 완전히 반대되는 종류가 아닙니다. 관계형 데이터베이스가 Vector Type과 ANN Index를 제공할 수도 있고, 전용 Vector Database가 Metadata Filter와 Keyword Search를 제공할 수도 있습니다. 비교해야 할 것은 이름보다 **필요한 검색·운영 기능**입니다.

| 요구사항 | 적합한 기능 예 |
|---|---|
| 주문 번호·문서 ID의 정확한 조회 | B-tree/Hash Index, SQL 조건 |
| 단어·구문 검색과 형태소 기반 검색 | Full-text·Keyword·Sparse Search |
| 표현이 달라도 관련된 후보 검색 | Dense Vector Search |
| 부서·권한·작성일 조건 | Metadata/Relational Filter |
| 의미와 정확한 용어를 함께 반영 | Hybrid Search |
| 매우 큰 벡터 집합의 낮은 지연시간 | HNSW·IVF 같은 ANN Index 검토 |
| Transaction과 복잡한 관계 무결성 | 관계형 Database 기능 |

소규모 프로젝트라면 PostgreSQL과 Vector Extension 하나로 Transaction, Metadata, Vector Search를 함께 운영하는 것이 단순할 수 있습니다. 데이터 규모와 처리량, 다중 Tenant, 검색 기능이 커지면 전용 검색·Vector 시스템을 분리할 수 있습니다. 제품 선택은 실제 Dataset의 Recall, Latency, 운영 복잡도와 비용으로 결정합니다.

### Vector Library, Vector 기능, Vector Database는 같은 말이 아니다

학생들이 자주 헷갈리는 부분입니다.

```text
Faiss
→ Vector 검색 Library

PostgreSQL + pgvector
→ 관계형 Database 안에 Vector Type/Search 기능 추가

전용 Vector Database / Search Service
→ Vector 저장·Index·검색·Metadata·분산 운영 등을 제품 수준으로 제공
```

따라서 `HNSW를 쓴다`는 사실만으로 어떤 제품을 사용하는지는 알 수 없습니다. 여러 제품과 Library가 HNSW 또는 IVF 계열 Index를 구현할 수 있습니다.

### Metadata는 Vector가 아니다

문서 하나를 저장할 때 보통 Vector만 저장하지 않습니다.

```text
{
  "chunk_id": "DOC-001-C03",
  "document_id": "DOC-001",
  "text": "출장비는 ...",
  "embedding": [0.12, -0.44, ...],
  "department": "finance",
  "status": "active",
  "security_level": 2,
  "effective_date": "2026-08-01"
}
```

여기에서

```text
embedding
→ 의미 검색용 Vector

metadata
→ Filter, 권한, 최신성, 추적에 사용하는 구조화 정보
```

입니다.

### Filter를 나중에만 하면 왜 위험할까?

예를 들어 사용자가 일반 직원인데, ANN이 먼저 임원 전용 문서를 Top-5 Candidate로 가져왔다고 가정해봅시다.

```text
ANN Search
↓
임원 전용 문서 포함
↓
LLM Context에 삽입
↓
출력 단계에서만 권한 검사
```

이 구조는 이미 비밀 문서가 Model Context에 들어갔기 때문에 위험합니다.

목표 구조는 다음에 가깝습니다.

```text
사용자 인증 / 권한
↓
검색 가능한 범위 결정
↓
Vector / Hybrid Search
↓
최종 Candidate 권한 재검증
↓
허용된 Chunk만 LLM Context에 삽입
```

다만 ANN Index와 Metadata Filter가 내부적으로 결합되는 방식은 제품마다 다릅니다. 어떤 시스템은 Filter를 먼저 적용하고, 어떤 시스템은 탐색 중에 적용하며, 어떤 조건에서는 후보 검색 뒤 추가 Filter가 일어날 수 있습니다. 그래서 **최종 Context 직전 권한 재검증**을 별도로 두는 것이 안전합니다.

---

## ⑤ 활용 이해 (Application)

Vector DB는 다양한 AI 서비스에서 사용됩니다.

|활용|Vector DB의 역할|
|---|---|
|RAG|질문과 관련된 문서 검색|
|AI 챗봇|회사 문서 검색|
|추천 시스템|비슷한 상품·콘텐츠 찾기|
|의미 검색|키워드가 달라도 관련 문서 검색|
|중복 탐지|의미가 거의 같은 문서 찾기|

예를 들어

- "연차 규정"
    
- "휴가 정책"
    
- "휴가 사용 기준"
    

처럼 표현이 달라도 의미가 비슷한 문서를 찾아주는 것이 Vector DB의 강점입니다.

---

## ⑥ 핵심 정리 (Summary)

이번 Unit에서 반드시 기억해야 할 핵심은 다음과 같습니다.

1. SQL은 질의 언어이며 관계형 Database도 Full-text·Vector Search를 지원할 수 있습니다. 중요한 것은 제품 이름이 아니라 사용하는 Index와 검색 방식입니다.
    
2. Vector DB는 문서 자체보다 **Embedding 벡터**를 저장하고 검색합니다.
    
3. 질문도 Embedding으로 변환한 뒤, 가장 가까운 벡터를 검색합니다.
    
4. Similarity Search는 벡터 간의 유사도를 계산하여 관련 문서를 찾는 방식입니다.
    
5. 대규모 데이터에서는 ANN 알고리즘을 사용해 빠르게 유사한 벡터를 찾습니다.
    
6. Vector Search는 RAG의 대표적인 검색 방식이지만 필수 조건은 아닙니다. Keyword, SQL, Search Engine, Graph, API 검색과 결합하거나 대체할 수 있습니다.
    

---

## ⑦ 이해도 확인 (Check)

다음 질문에 자신의 언어로 답해보세요.

1. `SQL=문자 검색`, `Vector DB=의미 검색`이라고 단순히 나누면 안 되는 이유는 무엇인가요?
    
2. Vector Similarity Search에 Embedding 또는 다른 Vector Feature가 필요한 이유는 무엇인가요?
    
3. Similarity Search는 어떤 원리로 동작하나요?
    
4. ANN 알고리즘이 필요한 이유는 무엇인가요?
    
5. Vector DB 없이도 RAG를 만들 수 있는 검색 방법 두 가지를 설명해보세요.
    

---

## AIKOS Knowledge 제안

### 저장 위치

```text
Knowledge/
└── AI/
    └── Vector DB/
        ├── Vector DB 개요.md
        ├── Similarity Search.md
        ├── ANN (Approximate Nearest Neighbor).md
        └── SQL DB vs Vector DB.md
```

### 관련 Wiki Link

```text
[[임베딩(Embedding)]]
[[검색 증강 생성(RAG)]]
[[대규모 언어 모델(LLM)]]
`Semantic Search`
`ANN`
```

---

---

# [보강 학습] 빠르게 찾는 것과 올바르게 찾는 것은 다르다

VectorDB의 목적은 벡터를 보관하는 데 그치지 않습니다. 많은 문서에서 제한된 시간 안에 관련 후보를 찾고, 권한과 최신성을 지키며, 실제로 정답 문서를 찾았는지 측정해야 합니다.

## 1. Exact Search와 ANN

Exact Search는 질문 벡터를 모든 문서 벡터와 비교하므로 가장 가까운 결과를 정확히 찾을 수 있지만 문서가 커질수록 비교량이 증가합니다. ANN(Approximate Nearest Neighbor)은 미리 만든 Index를 이용해 가능성이 높은 영역을 탐색합니다. 일부 정답 후보를 놓칠 수 있는 대신 훨씬 빠른 검색을 목표로 합니다.

```text
Embedding Model → 질문·문서 Vector 생성
Vector DB / Search Engine → Vector·문서 ID·Metadata 저장 및 검색
  └─ Index/Search 방식 → Flat(전체 비교), HNSW(그래프), IVF(군집) 등
```

앞에서 본 HNSW와 IVF는 **Vector DB의 제품명이 아니라 ANN Index/Search 방식**입니다. 이 보강에서는 내부 구조를 다시 외우기보다 실제 운영에서 조정값과 평가 지표가 어떻게 연결되는지 확인합니다.

**원본 수업 질문의 조정값을 Faiss 예로 구분합니다.** HNSW의 `M`은 그래프의 이웃 연결 수로, 늘리면 탐색 품질이 좋아질 수 있지만 메모리 사용량도 커진다. `efSearch`는 질의할 때 살피는 후보의 폭을 조절한다. IVF의 `nlist`는 Index를 만들 때 나누는 군집 수, `nprobe`는 질의할 때 살피는 군집 수다. `efSearch`나 `nprobe`를 키우면 정답을 찾을 가능성이 높아질 수 있지만 지연·계산량이 늘어난다. 이 이름과 허용 범위는 제품마다 다르므로 Faiss 설정을 다른 VectorDB에 그대로 복사하지 않는다.

| 방식 | 탐색 그림 | 먼저 측정할 것 |
|---|---|---|
| HNSW | 여러 층의 그래프 연결을 따라 가까운 점으로 이동 | Recall@K, 지연, 그래프 메모리, 갱신·삭제 제약 |
| IVF | 가까운 군집을 고르고 그 안의 후보를 비교 | Recall@K, 지연, 군집 학습·재구성 비용, 메모리 |

```text
더 넓게 탐색 → Recall 증가 가능, 지연시간·계산량 증가
더 좁게 탐색 → 검색 속도 향상, 정답 누락 가능
```

여기서 Vector Search의 **top-k**는 검색 결과로 돌려받을 후보 개수 `k`입니다. LLM Decoding의 **top-k**는 다음 토큰을 뽑을 때 고려하는 후보 토큰 개수이며 **top-p**는 누적 확률 질량 기준입니다. 이름이 같아도 적용 위치와 단위가 다릅니다.

| 용어 | 적용 단계 | 예 |
|---|---|---|
| Vector Search top-k | 저장된 문서/Chunk 검색 | 관련 Chunk 5개 반환 |
| LLM Decoding top-k | 다음 토큰 선택 | 후보 토큰 40개 중 선택 |
| LLM Decoding top-p | 다음 토큰 선택 | 누적 확률 임계값의 후보군 사용 |

확인 활동: 같은 작은 문서 집합에서 Flat과 ANN의 상위 5개를 비교하고 정답 Chunk 포함 여부(`Recall@5`)와 지연을 기록합니다. ANN 설정을 바꾸면 속도와 검색 누락이 어떻게 변하는지 확인합니다. 수업 자료의 숫자는 측정 전까지 실제 성능 수치로 쓰지 않습니다.

## 2. Hybrid Search와 Reranking

의미는 비슷하지만 표현이 다른 질문은 Dense Vector Search가 잘 찾을 수 있습니다. 사번, 규정 번호, 제품 코드처럼 정확히 일치해야 하는 값은 Keyword·Sparse Search가 유리합니다.

```text
질문
├→ Dense 검색
└→ Keyword·Sparse 검색
     ↓
점수 또는 순위 결합
     ↓
후보 문서
     ↓
Reranker가 질문과 후보를 함께 읽고 재정렬
```

검색 점수는 서로 다른 알고리즘에서 같은 의미를 갖지 않을 수 있으므로 단순히 더하기 전에 정규화나 순위 결합 방식을 정해야 합니다. Reranking은 후보 품질을 높일 수 있지만 추가 모델 호출과 지연시간이 발생합니다.

## 3. Metadata Filtering과 권한

문서 벡터와 함께 부서, 문서 유형, 작성일, 언어, 보안 등급, 소유자 같은 Metadata를 저장하면 검색 범위를 제한할 수 있습니다.

```text
사용자: 인사팀
질문: 최신 승진 규정

검색 조건
department = HR
effective_date <= today
status = active
사용자에게 허용된 security_level
```

보안 목표는 **권한 없는 문서가 모델 Context에 들어가지 않게 하는 것**입니다. 가능한 경우 검색 공간을 권한으로 먼저 제한하거나 권한을 인식하는 Filtered Search를 사용합니다. 검색 엔진 내부에서 Filter가 ANN 후보 생성 전·중·후 어느 단계에 적용되는지는 구현마다 다르므로, 최종 Context를 만들기 전에 모든 후보의 권한을 다시 검증해야 합니다. 출력 Filter만으로는 이미 Context에 들어간 비밀의 유출을 막을 수 없습니다.

## 4. 갱신, 삭제, 재색인

원본 문서가 바뀌면 Parsing 결과, Chunk, Embedding, Metadata, Index도 함께 바뀌어야 합니다. 삭제 요청도 VectorDB에서 실제 검색되지 않는지 확인해야 합니다. 모델이나 Chunking 전략을 변경하면 기존 벡터와 호환되지 않을 수 있으므로 새 Index를 구축하고 평가한 뒤 전환합니다.

```text
원본 Version
→ Parsing Version
→ Chunking Version
→ Embedding Model Version
→ Index Version
```

이 연결을 기록해야 잘못된 답변이 어느 단계의 오래된 데이터에서 시작되었는지 추적할 수 있습니다.

## 5. 검색 품질 평가

평가 Dataset은 질문과 찾아야 할 정답 문서의 쌍으로 만듭니다.

- **Recall@K:** 정답 문서가 상위 K개 안에 포함된 비율
- **Precision@K:** 상위 K개 중 실제 관련 문서의 비율
- **MRR:** 첫 번째 정답 문서가 얼마나 앞에 나타나는지 평가
- **nDCG:** 관련성 등급과 순서 모두 고려
- **Latency:** 검색 응답에 걸린 시간

RAG 답변이 틀렸을 때 먼저 정답 문서가 검색되었는지 확인해야 합니다. 검색되지 않았다면 LLM Prompt만 고쳐도 근본 문제가 해결되지 않습니다.

## 보강 핵심 정리

1. ANN은 속도·메모리 효율을 얻는 대신 Exact Nearest Neighbor 대비 일부 Recall을 양보할 수 있는 검색 방식이다.
2. Hybrid Search는 의미 검색과 정확한 용어 검색의 장점을 결합한다.
3. Reranking은 소수 후보를 더 정밀하게 재정렬한다.
4. 권한 없는 문서는 모델 Context에 넣지 않으며, 검색 Filter와 최종 후보 검증을 실제 인증 정보와 동기화한다.
5. 검색 품질은 Recall·순위·Latency를 실제 질문 Dataset으로 측정한다.

## 자신의 말로 답해 보기

1. 모든 벡터를 정확히 비교하지 않고 ANN을 사용하는 이유는 무엇인가요?
2. 사내 규정 번호 검색에 Hybrid Search가 유리한 이유는 무엇인가요?
3. 권한 검사를 검색 이후에만 수행하면 어떤 위험이 있나요?
4. RAG 답변이 틀렸을 때 Retrieval 평가부터 확인해야 하는 이유는 무엇인가요?

## Practice — 검색 구조를 단계별로 설계하기

### Practice 1. Exact와 ANN 구분

문서 100개 규모에서는 모든 Vector를 비교하는 Exact Search와 ANN Search의 결과를 같은 질문으로 비교해 보세요. 기록할 항목은 다음과 같습니다.

- 정답 문서가 Top-5에 들어왔는가?
- 두 방식의 순위가 같은가?
- 검색 시간은 얼마나 다른가?
- Metadata Filter를 적용했을 때 권한 없는 문서가 최종 후보에 남는가?

작은 데이터에서는 Exact Search가 충분히 빠를 수 있습니다. ANN을 사용한다는 사실 자체보다 실제 규모에서 Recall과 Latency가 목표를 만족하는지가 중요합니다.

### Practice 2. HNSW와 IVF 선택 이유 설명

다음 세 상황에서 어떤 항목을 먼저 비교할지 적어보세요. 정답은 특정 Index 이름 하나가 아니라 **비교 기준을 설명하는 것**입니다.

```text
상황 A
문서 5만 개 / 갱신 자주 발생 / 낮은 Latency 중요

상황 B
문서 수천만 개 / Memory 제약 큼 / Batch 재색인 가능

상황 C
문서 3천 개 / 하루 Query 100회
```

확인할 항목 예:

```text
Exact Search 가능 여부
Recall@K
P95 Latency
Index Memory
Build 시간
Update/Delete 특성
Metadata Filter 동작
```

### Practice 3. Metadata와 Vector 분리

다음 정보를 `Vector`, `Metadata`, `원문/본문`으로 나눠보세요.

```text
문서 제목
Chunk 본문
Embedding
부서
보안 등급
작성일
문서 Version
문서 ID
```

그리고 다음 질문에 답합니다.

> "부서=HR" 조건은 Embedding Model이 처리해야 할까요, 검색 Filter가 처리해야 할까요?

### Practice 4. Vector Search top-k와 LLM top-k 구분

```text
검색 결과 Chunk 10개 반환
→ Retrieval top-k = 10

다음 Token 후보를 40개로 제한
→ Generation top-k = 40
```

두 설정의 `k`가 같은 글자를 쓰더라도 **대상과 단계가 완전히 다르다**는 것을 설명해보세요.

### Practice 5. RAG 실패 원인 추적

질문:

```text
"해외 출장 시 법인카드 ATM 인출이 가능한가요?"
```

LLM의 답이 틀렸습니다. 다음 순서로 확인합니다.

```text
1. 정답 문서가 Index에 존재하는가?
2. 올바른 Embedding Version인가?
3. Metadata / Permission Filter가 잘못 제거하지 않았는가?
4. 정답 Chunk가 Retrieval Top-k 안에 들어왔는가?
5. Reranker가 정답 Chunk를 아래로 밀지 않았는가?
6. 정답 Chunk가 Context에 실제 삽입되었는가?
7. 그 다음에야 Prompt / LLM Generation을 확인
```

이 순서는 다음 RAG 과목에서 다시 사용합니다.

## 실무 팁

Index를 바꿀 때는 정답 문서가 상위 K개에 들어왔는지와 지연·메모리를 함께 기록합니다. 검색 자료의 버전, 권한 Metadata, 삭제 반영 여부까지 확인하면 잘못된 답의 원인을 찾기 쉽습니다.

## 주의사항

ANN은 속도와 정확 검색 대비 Recall의 교환이 있고, HNSW·IVF의 세부 제약은 제품별로 다릅니다. Vector Search top-k와 LLM Decoding top-k/top-p는 서로 다른 단계의 설정입니다.

## 참고자료 — 원문으로 확인하기

- [Faiss indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes), [Index selection](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index) — 2026-09-24 확인; Flat/HNSW/IVF가 각각 Index 방식임을 확인합니다.
- [Faiss indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes), [Faiss runtime parameter tuning](https://github.com/facebookresearch/faiss/wiki/Index-IO%2C-cloning-and-hyper-parameter-tuning) — 2026-09-25 확인; HNSW `M`/`efSearch`, IVF `nlist`/`nprobe`의 의미를 대조합니다.

- [pgvector 공식 저장소](https://github.com/pgvector/pgvector) — PostgreSQL 안에서 Exact·Approximate Vector Search와 HNSW·IVFFlat을 제공하며, HNSW의 `m`/`ef_construction`과 IVFFlat의 `lists`/`probes` 같은 조절값을 확인할 수 있습니다.
- [PostgreSQL Full Text Search](https://www.postgresql.org/docs/current/textsearch.html) — 관계형 Database가 Keyword·Full-text Search도 지원한다는 사실을 확인할 수 있습니다.
- [Faiss 공식 Wiki](https://github.com/facebookresearch/faiss/wiki) — Vector Index의 Exact·Approximate Search와 검색 시간·품질·메모리 Trade-off를 확인할 수 있습니다.
- [Efficient and Robust Approximate Nearest Neighbor Search Using HNSW](https://arxiv.org/abs/1603.09320) — HNSW의 계층형 Graph 탐색 원리를 확인할 수 있습니다.

## 더 깊이 공부하기

- [[07. 벡터 검색 아키텍처 심화학습(Vector Search Architecture Deep Dive)]]
- [[08. 고급 검색 증강 생성 심화학습(Advanced RAG Deep Dive)]]
- [[12. 운영 AI 아키텍처 심화학습(Production AI Architecture Deep Dive)]]

## 강사 관점 정리

이번 Unit에서 가장 중요한 깨달음은 다음 한 문장입니다.

> **Vector 검색은 문서에서 만든 Vector를 거리·유사도 기준으로 검색한다. 그 Vector가 업무상 의미를 잘 표현하는지는 Embedding Model과 평가 결과로 확인한다.**

이 차이가 현대 AI 검색의 핵심입니다.

전통적인 검색은 "같은 단어가 있는가?"를 묻습니다.

```
환불 → 환불
```

반면 Vector Search는

```
환불 ≈ 환급 ≈ 반품 정책 ≈ 교환 절차
```

처럼 **의미적 유사성(Semantic Similarity)** 을 기반으로 검색합니다.

이 방식은 RAG의 대표적인 Retrieval 구성입니다. 그러나 RAG는 Keyword Search, SQL Query, Search Engine, Graph, 외부 API처럼 질문에 필요한 정보를 가져올 수 있는 다른 Retrieval 방식으로도 만들 수 있습니다.

다음 Unit에서는 지금까지 배운 모든 내용을 하나로 연결하여,

```
RAG에서는

질문

↓

Retrieval 방식 선택
(Keyword·Vector·SQL·Graph·API 등)

↓

후보 문서와 데이터

↓

Prompt에 삽입

↓

LLM

↓

최종 답변

이라는 흐름으로 동작합니다.

다음 Unit에서는
이 전체 과정을 자세히 학습합니다.
```

이라는 **RAG(Retrieval-Augmented Generation)** 의 전체 구조와 동작 원리를 학습하게 됩니다. 이 시점부터 여러분은 현대 기업들이 AI 챗봇과 사내 지식 검색 시스템을 어떻게 구축하는지 전체 아키텍처를 이해할 수 있게 됩니다.
