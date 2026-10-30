# Day 2 - 1교시. Language Model, LLM과 Token

> **강의 목적:** 사용자가 입력한 문자열이 언어 모델의 입력이 되기까지 어떤 변환을 거치는지 이해하고, 실제 Tokenizer를 사용해 Token·Token ID·Encode/Decode를 확인한다.
>
> **수업 범위:** Tokenizer와 입력 데이터의 표현까지. Tensor의 내부 연산, Model Parameter와 Training, 실제 Pre-trained Model의 생성 실행은 뒤 교시에서 다룬다.

## 개요 — 오늘은 모델의 ‘입구’를 살펴본다

Day 1에서는 Python 프로그램이 Cloud AI API에 질문을 보내고 응답을 받는 과정을 경험했다. API를 호출하는 개발자에게는 질문도 답변도 문자열로 보인다. 하지만 모델 내부는 문자열 자체가 아니라 수치 표현을 이용해 계산한다.

오늘 살펴볼 과정은 다음과 같다.

```text
사용자 입력 Text
       ↓
Tokenizer — 문자열을 처리 단위로 구분
       ↓
Token — 구분된 단위
       ↓
Vocabulary — 각 Token과 식별 번호의 대응
       ↓
Token IDs — 모델 입력에 사용할 정수들
       ↓
[다음 교시] Tensor / 수치 계산
       ↓
Language Model
       ↓
출력 Token IDs
       ↓
Tokenizer의 Decode
       ↓
사람이 읽는 Text
```

이 흐름에서 **오늘의 주인공은 `Tokenizer`, `Token`, `Token ID`, `Vocabulary`**다. Transformer가 어떻게 계산하는지, 모델이 어떻게 학습되는지는 여기서 다시 설명하지 않는다.

강사는 수업 시작에 이렇게 질문한다.

> Python 코드에서 `"AI를 공부합니다."`를 변수에 저장하면, 모델도 그 문자열을 사람처럼 그대로 읽을까요?

학생이 정확한 답을 모르더라도 괜찮다. 오늘 수업이 끝난 뒤에는 그 문자열이 어떤 단계를 거쳐 수치 입력으로 바뀌는지 직접 설명할 수 있으면 된다.

---

# 1. 학습 목표

수업이 끝나면 학생은 다음을 할 수 있어야 한다.

1. Language Model과 LLM의 관계를 **새 개념을 다시 암기하는 대신** 오늘 다룰 Token 처리 흐름과 연결해 설명한다.
2. Token이 반드시 하나의 단어나 한국어 어절과 같지 않은 이유를 설명한다.
3. Tokenizer, Vocabulary, Token ID의 역할을 서로 구분한다.
4. Encode와 Decode의 방향 및 입력·출력 형태를 설명한다.
5. Special Token, Padding, Attention Mask의 목적을 간단한 입력 사례로 설명한다.
6. 동일한 문자열이라도 Tokenizer에 따라 분할 결과와 개수가 달라질 수 있음을 이해한다.
7. Hugging Face `AutoTokenizer`를 사용해 Token 목록, ID, Decode 결과를 관찰한다.
8. Context Window와 Token 사용량이 API 비용과 입력 설계에 미치는 영향을 설명한다.

---

# 2. Day 1과 연결 — Language Model에서 새롭게 볼 부분

전날 생성형 AI 강의에서 이미 배운 사실 두 가지를 떠올려 보자.

- **Language Model**은 언어의 패턴을 모델링하는 모델이다.
- **LLM(Large Language Model)**은 대규모 데이터와 Parameter를 이용해 학습된 대규모 Language Model을 가리킨다.

Day 1에서는 다음 Token을 예측하며 문장을 이어 나가는 **생성의 직관**을 배웠다. 이번 교시에서 이 개념을 새롭게 다룰 지점은 다음과 같다.

```text
우리가 보는 것          모델의 처리 단위
─────────────────────────────────────────
"AI는 유용합니다"      →  Token과 Token ID의 Sequence
```

여기서 **Sequence**는 순서가 있는 값들의 나열이다. 문자열의 순서가 바뀌면 입력 의미도 바뀔 수 있다. 모델은 입력 순서를 포함한 정보를 수치 표현으로 처리하며, 생성 과정에서 출력한 ID 역시 순서대로 결합되어 문장이 된다.

> **핵심 질문:** 문장을 이어 생성한다는 것은 알겠다. 그렇다면 모델은 문장의 어느 부분을 한 단위로 다룰까?

이 질문에 답하는 것이 오늘의 새로운 학습이다. 질문 답변·요약·분류·번역·코드 생성 등 LLM의 활용 목록은 앞 교시에서 이미 다뤘으므로 반복하지 않는다.

---

# 3. 텍스트를 그대로 계산할 수 있을까?

Python에서는 다음처럼 문자열을 다룬다.

```python
text = "AI를 공부합니다."
print(text)
```

문자열은 사람이 읽기 쉽지만 신경망의 내부 연산에 그대로 사용할 숫자 배열은 아니다. 따라서 입력된 텍스트를 모델이 처리할 수 있는 형태로 **변환**해야 한다.

```text
문자열: "AI를 공부합니다."
       ↓
Tokenizer
       ↓
Token 단위로 구분
       ↓
Token ID의 목록: [정수, 정수, ...]
       ↓
모델이 사용하는 수치 입력
```

이때 모델이 사용하는 숫자는 원래 문장의 의미를 직접 적은 숫자가 아니다. 각 Token을 구분하기 위해 부여한 **식별 번호**다. 뒤에서 이 차이를 다시 확인한다.

강사 질문: "문장을 숫자로 바꾼다면 각 한글 글자에 임의로 번호를 하나씩 붙이면 될까요?" 가능한 방식 중 하나처럼 보일 수 있지만, 실제 언어 모델에서는 처리 효율과 어휘 표현을 고려해 다양한 Tokenization 방법을 사용한다.

---

# 4. Token — 단어와 같은가?

**Token은 언어 모델이 텍스트를 처리하기 위해 사용하는 단위**다. 사람이 읽는 단어 또는 한국어 어절과 정확히 일치해야 하는 것은 아니다.

다음 네 가지를 비교해 보자.

| 구분 | 사람이 보는 사례 | Tokenizer에서 가능한 처리 |
|---|---|---|
| 단어 | `Model` | 한 Token일 수도, 여러 조각일 수도 있음 |
| 복합 단어 | `unbelievable` | `un` / `believ` / `able`처럼 분할될 수 있음 |
| 한국어 | `인공지능을` | 하나의 어절이어도 여러 Token이 될 수 있음 |
| 기호·공백 | `AI Application!` | 공백이 다른 조각과 결합되거나 기호가 별도 Token일 수 있음 |

위의 `un / believ / able` 표기는 **분할 방식의 설명을 위한 가상 사례**다. 특정 Tokenizer가 반드시 이렇게 나눈다는 뜻이 아니다.

왜 공백 기준으로 단어를 나누는 방법만 사용하지 않을까?

```text
"나는 인공지능을 공부한다"

공백 기준 구분:
나는 | 인공지능을 | 공부한다
```

공백 분리는 쉬우나, 새로운 단어·합성어·외국어 표기·제품 이름·오타처럼 변화가 많은 텍스트를 유연하게 처리하는 데 한계가 있다. 그래서 많은 Tokenizer는 단어보다 작은 **Subword(부분 단어)**와 같은 단위를 활용한다. 작은 단위를 조합하면 모든 가능한 단어를 각각 하나의 항목으로 준비하지 않고도 여러 표현을 다룰 수 있다.

다만 **모든 Tokenizer가 같은 방식으로 Subword를 사용한다는 뜻은 아니다.** 어떤 단위가 나오고 몇 개의 Token이 되는지는 실제 모델과 Tokenizer에 따라 달라진다.

### 학생 확인 질문

- `AI Application`은 공백이 있으므로 반드시 2 Token일까? → **아니다.**
- 한국어 한 글자는 반드시 1 Token일까? → **아니다.**
- 동일 문장인데 Token 수가 다른 모델이 있을까? → **있을 수 있다.**

---

# 5. Vocabulary와 Token ID — 번호는 무엇을 뜻할까?

Tokenizer에는 모델과 연결된 **Vocabulary(어휘 집합)**가 있다. 여기에는 Token과 그 Token을 식별하는 ID의 대응 관계가 포함된다.

예를 들어 다음과 같은 단순한 표를 상상해 보자.

| Token | Token ID |
|---|---:|
| `AI` | 1024 |
| ` Model` | 3912 |
| `Fast` | 8821 |
| `API` | 5510 |

**표 안의 숫자는 모두 가상의 예시**이며 실제 모델에서의 Token·ID와 무관하다.

이 표를 이용하면 다음처럼 표현할 수 있다.

```text
원문: "AI Model"
      ↓
Token 목록: ["AI", " Model"]
      ↓
ID 목록: [1024, 3912]
```

여기서 특히 기억할 점은 두 가지다.

첫째, **Token과 Token ID는 같은 것이 아니다.** `"AI"`는 사람이 확인할 수 있는 Token의 표현이고 `1024`는 그 Token을 구분하는 번호다.

둘째, **ID의 숫자가 크다고 더 중요한 단어이거나 의미가 풍부한 것은 아니다.** 예를 들어 3912가 1024보다 중요한 개념인 것은 아니다. ID는 식별자 역할을 한다.

모델 내부에서는 이 ID를 그대로 문장의 뜻으로 간주하지 않고, **Embedding** 등을 거쳐 계산에 사용하는 벡터 표현으로 바꾼다. 벡터의 구성·연산은 뒤 교시와 Phase 2에서 다룬다.

### 모델과 Tokenizer의 관계

```text
Model A  ↔  Model A와 호환되는 Tokenizer / Vocabulary
Model B  ↔  Model B와 호환되는 Tokenizer / Vocabulary
```

다른 Tokenizer를 무작정 교체해서 같은 ID를 보낸다면, 기대한 입력 표현이 아닐 수 있다. 따라서 실제 모델을 사용할 때는 **해당 모델과 호환되는 Tokenizer**를 확인해야 한다.

---

# 6. Encoding과 Decoding — 두 방향을 구분하자

**Encoding(인코딩)**은 텍스트를 Token ID 형태로 바꾸는 과정이고, **Decoding(디코딩)**은 Token ID들을 사람이 읽을 텍스트로 다시 변환하는 과정이다.

```text
[Encoding]
Text → Tokenizer → Token IDs

[Decoding]
Token IDs → Tokenizer → Text
```

예를 들어 앞의 **가상 Vocabulary**를 이용한다면:

```text
Encode: "AI Model" → [1024, 3912]
Decode: [1024, 3912] → "AI Model"
```

문장 생성의 입구와 출구를 연결해 보자.

```text
사용자 질문
    ↓ Encode
입력 Token IDs
    ↓
Language Model
    ↓
출력 Token IDs
    ↓ Decode
화면에 표시할 답변 Text
```

**실제 실습 시 주의:** Encoding 과정에 Special Token이 자동으로 들어가거나, Decoding에서 일부 표시 형태가 달라질 수 있다. 따라서 `decode(encode(text))`를 실행했을 때 출력이 **항상 원본 문자열과 글자 단위까지 동일할 것이라고 단정하지 않는다.** 실습에서 Special Token 포함 여부와 Decode 옵션을 함께 관찰해야 한다.

### 강사 미니 활동 — 순서 맞추기

다음 항목을 올바른 순서로 배열하게 한다.

```text
Token IDs / Text / Tokenizer / Vocabulary 대응 / Model Input
```

예상 답: `Text → Tokenizer(분할 및 Vocabulary 참조) → Token IDs → Model Input`.

---

# 7. 한 단계 더 정확한 흐름 — ID에서 모델 입력까지

Token ID가 준비되면 모델이 사용할 입력 배열로 전달된다. 원문에서 소개한 흐름을 오늘의 범위에 맞게 정리하면 다음과 같다.

```text
Text
  ↓
Tokenizer
  ├─ Token 분할
  └─ Vocabulary에 따른 ID 변환
  ↓
input_ids
  ↓
[다음 교시] Tensor 형태로 묶어 계산에 사용
  ↓
[이후 교시] Embedding / Model 연산
```

`input_ids`는 Hugging Face Tokenizer 결과에서 자주 만나는 키 이름이다. 여기에는 보통 Token ID들이 순서대로 담긴다.

중요한 구분:

- **Token:** 구분된 입력 단위
- **Token ID:** 그 단위의 식별 번호
- **Tensor:** 숫자 데이터를 담는 계산용 자료 구조 — 상세 내용은 2교시
- **Embedding:** ID에 대응하는 학습 가능한 벡터 표현을 이용하는 단계 — 상세 원리는 후속 강의

이 네 가지를 하나의 용어처럼 사용하지 않는다. 특히 **`Token ID = Embedding Vector`가 아니다.**

---

# 8. Special Token — 일반 텍스트 외에도 필요한 표시

모델마다 일반 문장 조각 외에 특별한 역할을 가진 Token을 사용할 수 있다. 원문에서 소개한 대표 사례는 다음과 같다.

| 종류 | 의미 | 사용 맥락 |
|---|---|---|
| BOS | Beginning Of Sequence, 시작 표시 | Sequence의 시작을 구분하는 데 사용 가능 |
| EOS | End Of Sequence, 끝 표시 | Sequence의 끝을 나타내는 데 사용 가능 |
| PAD | Padding Token | 여러 입력의 길이를 맞추기 위한 자리 채움 |
| UNK | Unknown Token | 어휘에 없는 입력을 나타내는 방식에서 사용 가능 |

예를 들어 다음은 **개념 설명을 위한 표기**다.

```text
<BOS> 안녕하세요 저는 AI입니다 <EOS>
```

실제 모델이 `<BOS>`·`<EOS>`라는 문자열을 그대로 사용하는 것은 아니다. 모델마다 사용하는 Special Token의 종류, 토큰 문자열, ID, 적용 규칙이 다르다. 따라서 코드에서 임의의 특수 문자열을 넣기보다 **해당 Tokenizer가 제공하는 설정**을 확인해야 한다.

### Special Token이 Decode에 미치는 영향

예를 들어 Encode 과정에서 시작·끝 표식이 추가되면 Decode 결과에도 표시가 남을 수 있다. Hugging Face의 `skip_special_tokens=True` 옵션은 이러한 토큰을 제외하고 사람이 읽는 문자열을 얻을 때 사용할 수 있다.

이 옵션이 원래 입력 내용을 무조건 완벽하게 복원해 준다는 의미는 아니다. 출력 차이를 실제로 확인하는 것이 실습 목표다.

---

# 9. Padding과 Attention Mask — 길이가 다른 입력을 함께 처리한다면

원문에 나온 두 입력을 생각해 보자.

```text
A: "AI is useful"
B: "AI"
```

Tokenizer를 거친 뒤 길이가 다를 수 있다. 여러 입력을 한 번에 처리하는 **Batch(묶음)**를 만들 때는 계산 형식을 맞추기 위해 짧은 입력 뒤에 Padding을 추가할 수 있다.

```text
설명용 Token IDs

A: [11, 25, 39]
B: [11,  0,  0]    ← 뒤의 0 두 개는 PAD의 가상 ID
```

하지만 Padding은 사용자가 입력한 실제 텍스트가 아니다. 따라서 **Attention Mask** 같은 정보로 실제 입력과 채워 넣은 부분을 구분할 수 있다.

```text
input_ids        attention_mask
[11, 25, 39]     [1, 1, 1]
[11,  0,  0]     [1, 0, 0]

1: 실제 입력 위치
0: Padding 위치
```

위 숫자는 단순 예시다. 실제 PAD ID는 모델에 따라 다르며, Mask의 쓰임과 표현도 모델 구조에 따라 달라질 수 있다.

이 교시에서 알아야 할 것은 **Padding은 길이를 맞추는 일**, **Attention Mask는 어떤 위치가 실제 입력인지 구분하는 정보**라는 점이다. Attention의 수학적 계산, Tensor의 Shape와 Dimension은 다음 학습에서 다룬다.

> 주의: 모든 모델이 Padding Token을 미리 정의해 둔 것은 아니다. 실습에서 `padding=True`를 사용할 때는 해당 Tokenizer에 PAD 설정이 있는지 확인해야 한다.

---

# 10. 같은 문장이라도 Token 수가 달라지는 이유

Token 수는 글자 수나 공백으로 나눈 단어 수만으로 정해지지 않는다.

**설명용 가상 비교:**

```text
문장: "Generative AI is useful."

Tokenizer A
[Generative] [ AI] [ is] [ useful] [.]
→ 5개

Tokenizer B
[Gener] [ative] [ AI] [ is] [ use] [ful] [.]
→ 7개
```

두 결과 중 어느 쪽이 무조건 잘못된 것은 아니다. 각각 다른 Vocabulary와 분할 방식을 사용했을 수 있다.

한국어에도 같은 원리가 적용된다.

```text
"인공지능을 공부합니다."
```

사람이 보기에는 두 어절이지만 이것이 Token 2개라는 보장은 없다. 한국어 어절·형태소·글자 수는 **언어 분석에서 유용한 단위**일 수 있어도, 모든 모델의 Tokenizer 단위와 동일하지는 않다.

### 실습에서 실제로 비교할 값

| 비교 항목 | 의미 |
|---|---|
| 원문 Text | 입력한 문자열 |
| Token 목록 | 실제 Tokenizer가 구분한 단위들 |
| Token 개수 | Token 목록의 길이 |
| Token IDs | 각 Token에 대응하는 숫자들 |
| Decode 결과 | ID를 텍스트로 복원한 결과 |

서로 다른 Tokenizer를 비교할 수 있는 환경이면 같은 Text를 각각 Encode해서 결과가 다른지 관찰한다. 모델 접근 권한이나 다운로드 환경이 없다면 오늘은 **하나의 Tokenizer**로 한국어·영어·일본어를 비교해도 충분하다.

---

# 11. Context Window와 Token 사용량 — 개발자가 알아야 하는 이유

7교시 Cloud API 실습에서는 API 응답에 Token 사용량(`usage`) 정보가 포함될 수 있음을 확인했다. 이제 왜 글자 수 대신 Token 수를 보아야 하는지 설명할 수 있다.

언어 모델이 한 번의 처리에서 다루는 입력과 관련 정보에는 제한이 있으며, 이 범위를 **Context Window**라고 부른다. 개념적으로 다음 내용이 하나의 요청에 포함될 수 있다.

```text
Instruction + 대화 이력 + 현재 질문 + 문서 내용 + Tool 결과
                         ↓
                  Tokenized Context
                         ↓
                     Language Model
```

여기서 Token 수가 늘어나면 모델의 한도와 사용량에 영향을 줄 수 있다. Cloud API에서는 제공자와 모델의 정책에 따라 입력·출력 Token이 과금, 제한, 지연시간과 연결될 수 있다.

**개발에서 흔히 발생하는 문제:**

> 사용자가 긴 문서를 올렸는데, 개발자가 글자 수만 보고 모델이 충분히 처리할 수 있을 것이라고 가정한다.

실제 Tokenizer의 분할 방식과 모델 한도를 고려하지 않으면 예상과 다를 수 있다. 또한 관련 없는 문장을 많이 넣는다고 답변의 품질이 무조건 좋아지는 것은 아니다.

따라서 실무에서는 다음처럼 판단한다.

1. 어떤 Model/Tokenizer를 사용할지 확인한다.
2. Context 한도와 실제 입력 Token 수를 확인한다.
3. 꼭 필요한 정보인지, 중복되거나 관련 없는 부분은 없는지 검토한다.
4. API가 제공하는 Usage 정보를 확인해 비용과 운영 조건을 판단한다.

긴 문서를 나눠 필요한 부분만 검색해 전달하는 **Chunking·Retrieval·RAG**는 뒤 과정에서 원리와 구현을 배운다. 이 교시에서 관련 구조를 반복해서 설명하지 않는다.

---

# 12. 실습 준비 — 실제 Tokenizer를 불러온다

이제 이론을 관찰 가능한 결과로 바꾼다. 원본에서 사용한 도구는 Hugging Face의 `Transformers`와 `AutoTokenizer`다.

## 12.1 준비물

- Python과 Terminal
- 인터넷이 연결된 환경(최초 Tokenizer 파일을 내려받아야 할 수 있음)
- Python 가상환경
- `transformers` 라이브러리
- **강사가 실습 전에 확인한 Model ID**

다음 코드는 설치 예시다.

```bash
python -m pip install transformers
```

실제 교육장에 배포할 때는 시험한 Python·Transformers 버전과 Model ID를 확정해 제공한다. 지금 원본에는 `MODEL_ID` 자리표시자만 있으며 **실행 가능한 특정 모델이 검증되어 있지 않다.** 따라서 임의로 모델을 지정하고 검증이 끝났다고 가정하지 않는다.

## 12.2 Model ID란?

`AutoTokenizer.from_pretrained(MODEL_ID)`의 `MODEL_ID`는 불러올 모델과 연결된 Tokenizer를 지정하는 값이다. 이 문자열을 `"MODEL_ID"` 그대로 입력하면 실습용 Tokenizer가 자동으로 선택되는 것이 아니다.

강사는 수업 전에 사용할 모델의 Repository, 접근 권한, 다운로드 가능 여부, Tokenizer 파일과 라이브러리 호환성을 확인해 **실제 ID**를 전달한다. 학생에게는 그 값을 그대로 사용하도록 한다.

**실습 범위:** 이번에는 모델의 가중치를 불러와 문장을 생성하는 실습이 아니다. Tokenizer를 로드하고 **입력 Text를 Token과 ID로 바꾸는 과정**만 확인한다. 실제 Pre-trained Model을 불러와 생성하는 과정은 Day 2의 5교시에서 진행한다.

---

# 13. 첫 실습 — Token, Token ID, Decode를 한 번에 확인하기

파일 이름: `tokenizer_inspect.py`

```python
import os

from transformers import AutoTokenizer


MODEL_ID = os.environ.get("MODEL_ID", "").strip()
if not MODEL_ID:
    raise SystemExit(
        "MODEL_ID가 비어 있습니다. 강사가 확인한 모델 ID를 환경 변수로 설정하세요."
    )

# 이 교시에서는 모델이 아니라 해당 모델의 Tokenizer만 불러옵니다.
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

text = "AIKOS는 AI Application을 개발합니다."

# 1. 사람이 확인할 수 있는 Token의 표현
pieces = tokenizer.tokenize(text)

# 2. Token을 ID 형태로 변환
#    처음 비교할 때는 자동 Special Token 삽입을 제외합니다.
ids = tokenizer.encode(text, add_special_tokens=False)

# 3. 다시 사람이 읽는 Text로 복원
restored = tokenizer.decode(ids, skip_special_tokens=True)

print("원문:", text)
print("Token 목록:", pieces)
print("Token 개수:", len(pieces))
print("Token IDs:", ids)
print("ID 개수:", len(ids))
print("Decode 결과:", restored)
```

## 13.1 실행 전 Model ID 지정

강사가 확인한 값을 `MODEL_ID`에 지정한다. 아래 `<검증한_모델_ID>`는 **직접 바꿔야 하는 자리표시자**다.

macOS / Linux Terminal:

```bash
export MODEL_ID="<검증한_모델_ID>"
python tokenizer_inspect.py
```

Windows PowerShell:

```powershell
$env:MODEL_ID="<검증한_모델_ID>"
python tokenizer_inspect.py
```

모델 ID를 지정하지 않았으면 프로그램은 API 호출이나 모델 다운로드를 시도하기 전에 안내 메시지를 출력하고 종료한다. 설치 오류, 모델 접근 오류, Tokenizer 호환성 오류와 구분해서 확인한다.

## 13.2 예상하는 출력의 **형태**

다음은 출력 **형식만 보여 주는 예시**다. Token 목록과 ID 숫자, 개수는 특정 모델에서 검증한 결과가 아니다.

```text
원문: AIKOS는 AI Application을 개발합니다.
Token 목록: ['...', '...', ...]
Token 개수: (실제 결과에 따라 달라짐)
Token IDs: [정수, 정수, ...]
ID 개수: (실제 결과에 따라 달라짐)
Decode 결과: AIKOS는 AI Application을 개발합니다.
```

실제 Decode에서는 Tokenizer에 따른 공백·표기 차이가 나타날 수 있다. **결과가 정확히 몇 개의 Token인지 강사가 미리 단정하지 않고 실습 결과를 기록한다.**

## 13.3 코드 한 줄씩 해석하기

`AutoTokenizer.from_pretrained(MODEL_ID)`는 지정한 모델에 맞는 Tokenizer 관련 구성과 파일을 불러온다. 모델 가중치를 학습시키는 명령도 아니고, 언어 모델이 문장을 생성하도록 하는 명령도 아니다.

`tokenizer.tokenize(text)`는 어떤 문자열 조각으로 나뉘는지 보여 준다. 각 Token의 표시 방식에는 Tokenizer가 사용하는 내부 기호 등이 보일 수 있다.

`tokenizer.encode(text, add_special_tokens=False)`는 문자열을 ID 목록으로 바꾼다. Special Token의 자동 추가를 끄는 이유는 우선 **텍스트 자체가 어떻게 나뉘는지** 관찰하기 위해서다.

`tokenizer.decode(ids, skip_special_tokens=True)`는 ID들을 문자열로 복원한다. 이때 **ID 숫자가 문장의 의미 그 자체는 아니라는 점**을 다시 연결한다.

---

# 14. 확장 실습 — Special Token, 입력 묶음, Attention Mask

이제 앞 실습 결과와 비교한다. 아래 코드는 **13번 실습에서 `tokenizer`를 불러온 다음** 실행하는 코드다.

## 14.1 Special Token 포함 여부 비교

```python
example = "AI를 공부합니다."

without_special = tokenizer.encode(
    example,
    add_special_tokens=False,
)
with_special = tokenizer.encode(
    example,
    add_special_tokens=True,
)

print("일반 입력 ID:", without_special)
print("Special Token 허용 ID:", with_special)
print("Special Token 목록:", tokenizer.special_tokens_map)
print("복원:", tokenizer.decode(with_special, skip_special_tokens=True))
```

확인 질문: `add_special_tokens=True`를 지정하면 반드시 모든 모델에서 BOS/EOS가 추가될까? **그렇지 않다.** 모델과 Tokenizer에 따라 결과가 다를 수 있다. 변화가 없더라도 오류로 단정하지 않는다.

## 14.2 길이가 다른 두 문장을 한 번에 처리

```python
sentences = ["AI is useful", "AI"]

if tokenizer.pad_token_id is None:
    print("이 Tokenizer에는 PAD 설정이 없어 Padding 비교를 건너뜁니다.")
else:
    batch = tokenizer(
        sentences,
        padding=True,
        return_attention_mask=True,
    )
    print("input_ids:", batch["input_ids"])
    print("attention_mask:", batch["attention_mask"])
```

이 코드에는 PyTorch 설치가 필수는 아니다. Python 목록 형태의 `input_ids`와 `attention_mask`만 비교하기 때문이다. **PAD가 정의되지 않은 Tokenizer**에서는 무리하게 임의의 ID를 넣지 않고 다음 교시 이후의 모델별 실행 설정으로 넘긴다.

확인 질문:

- 두 문장의 원래 길이는 같은가?
- Padding이 추가되었다면 어느 입력에 들어갔는가?
- `attention_mask`의 1과 0은 각각 어디를 나타내는가?

`return_tensors="pt"`를 이용하여 PyTorch Tensor로 결과를 반환하는 방식은 **2교시의 Tensor 학습에서 직접 확인**한다.

---

# 15. 실습 활동 — 비교하여 판단하기

이 교시는 이미 본 개념을 다른 말로 다시 쓰는 것보다 **같은 도구로 다른 입력을 관찰하고 이유를 설명하는 것**이 중요하다.

## 활동 A. 사람의 예상과 실제 Tokenizer 비교

입력:

```text
AIKOS는 AI Application을 개발합니다.
```

실행하기 전에 학생에게 묻는다.

- `AIKOS`가 하나의 Token일까?
- `Application`이 하나의 Token일까?
- 공백 개수만 알면 Token 개수를 알 수 있을까?

그다음 실제 Token 목록을 확인하여 예상과 달랐던 지점을 두 개 이상 적는다. **강사가 정답 Token 개수를 미리 제시할 필요는 없다.** 사용한 Tokenizer에 따라 결과가 달라지기 때문이다.

## 활동 B. 언어가 바뀌면 어떻게 될까?

같은 Tokenizer를 사용하여 다음 세 입력을 비교한다.

```text
Artificial intelligence is useful.
인공지능은 유용합니다.
人工知能は便利です。
```

`tokenizer.tokenize()`, `tokenizer.encode()`를 실행한 뒤 다음 표를 작성한다.

| Text | Token 목록 | Token 개수 | ID 목록 |
|---|---|---:|---|
| 영어 문장 | 학생 기록 | 학생 기록 | 학생 기록 |
| 한국어 문장 | 학생 기록 | 학생 기록 | 학생 기록 |
| 일본어 문장 | 학생 기록 | 학생 기록 | 학생 기록 |

같은 뜻에 가까운 문장이라고 해서 글자 수나 Token 수가 반드시 같지는 않다. 차이를 발견하는 것이 목적이며, 이 결과만으로 특정 언어의 **모델 응답 품질**이 더 좋거나 나쁘다고 판단하지 않는다.

## 활동 C. Encoding과 Decoding 비교

```python
original = "AI를 공부합니다."
encoded_ids = tokenizer.encode(original, add_special_tokens=False)
decoded_text = tokenizer.decode(encoded_ids, skip_special_tokens=True)

print("원문:", original)
print("인코딩:", encoded_ids)
print("디코딩:", decoded_text)
print("문자열 완전 일치:", original == decoded_text)
```

질문: Decode 결과가 원문과 다르다면 바로 모델 오류라고 판정할까? **아니다.** 먼저 Tokenization·정규화·공백·Special Token 옵션을 확인한다.

## 활동 D. Token 사용량을 설명할 수 있을까?

긴 문서가 모델 한도를 넘을 수 있는 이유를 `글자 수`, `Token 수`, `Context Window`라는 세 단어를 이용해 설명한다. 단순히 "문서가 길어서"라고 답하지 않고 실제 입력 표현과 연결해 답하게 한다.

---

# 16. 강사 시연 및 예상 질문

### Q1. Tokenizer는 AI 모델과 같은가?

아니다. Tokenizer는 문자열을 모델이 사용할 수 있는 입력 형태로 바꾸는 데 사용된다. 실제 언어 모델의 생성 연산이나 학습 자체를 수행하는 것은 아니다.

### Q2. Token은 영어 단어와 같은가?

아니다. Token은 단어 전체일 수도 있지만 부분 단어, 기호, 공백이 결합된 조각 등일 수 있다. 실제 분할은 모델과 Tokenizer에 따라 달라진다.

### Q3. Token ID가 크면 더 중요한 Token인가?

아니다. ID는 Token을 구분하는 식별 번호다. 숫자 크기로 단어의 중요성을 판단하지 않는다.

### Q4. `encode()` 결과가 모델이 이해하는 의미 벡터인가?

아니다. `encode()`의 결과는 Token ID의 나열이다. 모델 내부에서 이 ID를 계산용 벡터 표현으로 바꾸는 단계가 이어진다.

### Q5. 모든 언어 모델은 같은 Tokenizer를 사용할까?

아니다. 호환되는 Tokenizer와 Vocabulary가 다르므로 동일한 문장도 서로 다른 ID 목록을 만들 수 있다.

### Q6. Decode하면 원문이 완전히 똑같이 돌아올까?

항상 그렇다고 보장할 수는 없다. Special Token, 공백 표현, 문자 정규화 등의 처리 방식에 따라 차이가 생길 수 있다. 실습에서는 실제 결과를 관찰한다.

### Q7. Context Window가 크면 아무 문서나 전부 넣는 것이 좋은가?

아니다. Token 한도뿐 아니라 필요한 정보와 불필요한 정보의 구분, 비용, 지연시간 등을 고려해야 한다.

### Q8. Tokenizer 코드를 실행했는데 Model을 다운로드한 건가?

`AutoTokenizer.from_pretrained()`는 Tokenizer 관련 파일을 불러오는 단계다. 모델 가중치를 불러와 생성 작업을 수행하는 과정과 구분한다. 실제 Pre-trained Model 실행은 Day 2의 5교시에서 진행한다.

---

# 17. 실습 문제 해결 — 어디에서 실패했는지 구분하기

| 증상 | 먼저 확인할 사항 | 설명 |
|---|---|---|
| `ModuleNotFoundError: transformers` | 설치한 가상환경과 `pip` 실행 위치 | 라이브러리가 현재 Python 환경에 없는 상태 |
| `MODEL_ID가 비어 있습니다` | 환경 변수 지정 여부 | 실습에서 의도적으로 제공한 안내 메시지 |
| 모델/Tokenizer를 찾을 수 없음 | 정확한 Model ID, Repository 접근 가능성 | 잘못된 이름이나 접근 권한 등의 문제일 수 있음 |
| 다운로드 실패 | 인터넷 연결, 교육장 접근 정책, 캐시 상태 | Tokenizer 파일을 내려받지 못한 것일 수 있음 |
| `padding=True` 관련 오류 | `tokenizer.pad_token_id` 설정 | 모든 Tokenizer에 PAD가 사전 지정되지는 않음 |
| Encode/Decode 결과가 다름 | Special Token, 정규화, 공백 처리 | 반드시 고장이라고 단정하지 않음 |
| 한국어가 여러 조각으로 나뉨 | Tokenizer의 Vocabulary와 분할 방식 | Tokenizer에 따라 자연스러운 결과일 수 있음 |

**강사의 검증 범위:** 이 문서에서는 명령과 코드 구조를 제공하지만, **강사가 사용할 Model ID와 실제 수업 환경은 미확정**이다. 따라서 특정 Token 결과, 설치 성공, 다운로드 성공, 실행 시간, 모델별 특수 토큰 구성을 확인된 사실로 표시하지 않는다.

---

# 18. 수업 마무리 — 학생이 설명해야 할 한 가지 흐름

오늘 배운 내용을 긴 정의 목록 대신 하나의 사례로 확인한다.

> 학생에게 "`AI를 공부합니다.`가 모델에 입력되는 과정을 처음부터 끝까지 설명해 보세요"라고 질문한다.

모범 답안의 흐름은 다음과 같다.

```text
① Text: 사용자가 문장을 입력한다.
         ↓
② Tokenizer: 문장을 Token 단위로 처리한다.
         ↓
③ Vocabulary: 각 Token에 대응하는 ID를 찾는다.
         ↓
④ input_ids: 순서 있는 Token ID 목록을 얻는다.
         ↓
⑤ [다음 교시] Tensor와 수치 표현으로 Model에 전달한다.
         ↓
⑥ [후속 학습] Model이 출력 Token ID들을 생성한다.
         ↓
⑦ Decode: Token ID들을 사람이 읽을 Text로 바꾼다.
```

**반드시 구분할 내용:**

- Token은 텍스트의 처리 단위이며 **반드시 단어는 아니다**.
- Token ID는 그 Token을 가리키는 **숫자 식별자**다.
- Vocabulary는 Token과 ID의 **대응 체계**다.
- Encoding과 Decoding은 **변환 방향이 반대**다.
- Special Token은 모델별 입력 규칙을 표현할 수 있다.
- Padding과 Attention Mask는 길이가 다른 입력을 함께 처리할 때 중요할 수 있다.
- Context Window와 API 사용량은 **Token 단위**로 검토해야 한다.

## 최종 확인 체크리스트

- [ ] 단어/어절 수와 Token 수를 동일시하지 않는다.
- [ ] Token·Token ID·Embedding의 역할을 구분한다.
- [ ] `AutoTokenizer`에 실제 Model ID가 필요함을 알고 있다.
- [ ] `tokenize()`·`encode()`·`decode()`의 결과를 확인했다(실행 환경이 있는 경우).
- [ ] Special Token 포함 여부를 비교했다(실행 환경이 있는 경우).
- [ ] Padding·Attention Mask의 목적을 설명할 수 있다.
- [ ] Context와 Token 사용량이 왜 관련되는지 설명할 수 있다.

## 다음 교시 연결

이제 Token ID를 얻었다. 하지만 모델은 수많은 수치 값을 어떤 형태로 담아 연산할까?

```text
Text → Tokenizer → Token IDs
                           ↓
                     [다음 교시]
                  NumPy / PyTorch
                           ↓
                     Tensor / Shape
                           ↓
                       Model
```

다음 교시에는 NumPy와 PyTorch를 사용하여 **Scalar·Vector·Matrix·Tensor, Shape, Dimension, dtype, Device**를 직접 확인한다. 이번에 다룬 Tokenizer 정의를 다시 길게 설명하지 않고, `input_ids`가 숫자 데이터 구조로 전달되는 장면부터 시작한다.

---

# 참고자료 — 원본 ZIP 내부 강의의 연결 문서

- `Day1_05_생성형_AI와_Foundation_Model_강의용.md`: Language Model과 생성형 AI의 기본 원리(선행 학습)
- `Day1_06_현대_AI_개발_생태계와_핵심_라이브러리_강의용.md`: Hugging Face 및 `Transformers`의 도구상 위치(선행 학습)
- `Day2_02_AI의_데이터와_Tensor_NumPy와_PyTorch_강의용.md`: Tensor·Shape·dtype·Device(다음 교시)
- `Day2_05_Transformers로_Pretrained_Model_직접_실행하기_강의용.md`: Tokenizer와 실제 모델을 연결하는 Generation 실습(후속 실습)

> **강사 준비:** 배포 전 `MODEL_ID`·Python/Transformers 버전·다운로드 경로를 확정하고, 실제 교육장 환경에서 Tokenizer의 분할·ID·Decode 결과를 기록한다.
