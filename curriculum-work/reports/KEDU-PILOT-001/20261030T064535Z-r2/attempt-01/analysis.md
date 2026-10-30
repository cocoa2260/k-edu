# Phase2-02 분석 결과 — Day1 4교시 추가 비교 반영

2026-10-30 / KEDU-PILOT-001 / 작업 명세 revision 2

**추천: 기초 재설명을 줄이고, 데이터 설계와 모델 평가에 집중한다.**

첫 시범에서는 비교 자료 3개만 지정해 Day1 4교시를 빠뜨렸다. 이번 결과는 그 본문 전체를 추가 비교한 보완 결과다. 현재 비교 범위는 대상 강의 1개와 Phase1 관련 강의 4개이며 전체 교육과정의 전수 분석 결과는 아니다.

| 내용 | 확인 결과 | 추천 |
|---|---|---|
| AI·ML·DL 정의, 규칙과 학습의 차이 | Phase1에서 이미 설명 | 짧게 연결 |
| Training·Inference, Loss·Parameter | Phase1에 관찰 실습 코드까지 있음 | 재정의보다 데이터·평가 문제로 확장 |
| Feature Engineering·표현 학습 | Day1 4교시에 비교표·예시·활동까지 있음 | 기본 설명 반복 축소 |
| CNN·RNN·Transformer의 기초 역할·등장 이유 | Day1 4교시에 이미 있음. RNN은 LSTM까지 더 자세함 | 기초 재소개 축소, 구조별 새 원리·실습은 심화 단원에서 연결 |
| Activation·신경망 한 층의 구체적 계산 | 단순 구조 소개와 다른 학습 내용 | 신경망 원리 심화에 보존 |
| Transformer 위치 정보·Diffusion 소개 | 위 기초 설명과 같은 중복으로 묶을 수 없음 | 별도 심화/배치 검토. 일괄 삭제하지 않음 |
| 데이터 분리·일반화·과적합·누수·평가 지표 | Phase1의 예고보다 구체적인 성과 | 재구성의 핵심으로 보존 |

## 제목도 내용에 맞게 바꾸자

**제목 제안: `머신러닝의 데이터 설계와 모델 평가`**

지금 제안한 내용은 AI·ML·DL의 넓은 개요를 다시 배우는 과정이 아니라, 어떤 데이터를 입력하고 어떤 기준으로 학습 결과를 신뢰할지 판단하는 과정이다. 재구성 방향이 확정되면 제목도 이에 맞춰 바꾸는 것이 적절하다. 현재는 제안이며 원문 제목이나 파일명을 변경하지 않았다.

## 검토할 학습 흐름

1. 이미 배운 용어를 짧게 점검한다.
2. Sample·Feature·Label과 실제 예측 시점을 정한다.
3. 학습·선택·최종평가 데이터를 분리한다.
4. 일반화·과적합·데이터 누수를 판단한다.
5. 실수의 피해에 따라 평가 지표를 선택한다.
6. 학습·평가·운영 추론을 전체 Pipeline으로 설계한다.

CNN·RNN의 기초 소개를 줄여도 Activation·신경망 계산·Transformer의 내부 원리까지 없애는 것은 아니다. 전체 목차에서 적절한 심화 위치와 연결해야 한다. Diffusion의 필요성과 위치도 전체 교육 목표를 보고 별도로 결정한다.

## 이번에 보완한 판단

- F03: 표현 학습의 기본 설명도 Day1 4교시와 중복됨을 확인했다.
- F04: 층 구조의 소개와 Activation을 포함한 구체적 계산을 구분했다.
- F06: CNN·RNN·Transformer 비교 보류를 해소하고, 기초 소개 중복과 고유 언급을 구분했다.
- F20: 사전학습 모델 재사용의 큰 흐름도 앞 교시에 이미 있음을 반영했다.
- F24: 재구성 후 제목 변경 제안을 학습 목표와 연결해 추가했다.

자동 검사 통과만으로 비교 범위가 충분해지는 것은 아니다. 후속 분석에서는 직접 연결된 선수·후속 단원의 실제 본문을 비교했는지, 제외했다면 왜인지도 범위 검토에 포함한다.

## 상태와 다음 판단

한 과목의 분석·보완 결과를 기록한 단계다. 강의 본문 수정, 과목 통합·삭제, 최종 목차·시수 확정은 아직 수행하지 않았다. Transfer Learning과 Prompt/RAG의 용어 경계는 별도 기술 검증이 필요하다. 코드 실행·Ollama·RAG·Multi-Agent와 단계별 추론 강도 자동 전환은 이번 작업에서 검증하지 않았다.

원래 시범의 초안·보완·검사 기록은 별도 실행 폴더에 보존했다. 이번 추가 비교를 처음부터 포함했던 것처럼 과거 기록을 바꾸지 않았다.


## 비교에 사용한 자료

원본 커밋: [bc58756](https://github.com/cocoa2260/k-edu/commit/bc58756866cd6bdee20c102fb54340f21e65ad56)

| ID | 원문 | 줄 수 |
|---|---|---:|
| S01 | [Day1_02_AI_전체_지도_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 557 |
| S02 | [Day1_03_일반_프로그램과_AI의_차이_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 632 |
| S03 | [Day2_03_AI_Model과_Parameter_Training과_Inference_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 825 |
| S04 | [AI 머신러닝 딥러닝 개요_강의용.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md) | 1693 |
| S07 | [Day1_04_ML에서_Deep_Learning과_생성형_AI까지_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 802 |

S01·S02·S03·S04는 최초 시범에서 전체를 읽은 고정 원문과 판단을 재사용했다. S07(Day1 4교시)은 후속 대화에서 802줄 전체를 추가로 읽었고 이번 게시 준비에서 동일 Blob SHA를 다시 확인했다. 새 원문으로 바뀌었다고 가정하거나 전체를 다시 읽었다는 측정값을 만들지 않았다.

## 세부 판단과 근거

같은 개념·같은 수준의 설명과 새로운 학습 성과를 구별한다. 아래 신규/중복 판정은 지정한 비교 4개 파일 대비이며 전체 Phase1의 신규성 판정은 아니다. 동일 코드 복사 판정은 없다.

### F01. AI・ML・DL 포함 관계와 첫 정의

**권고:** 짧게 연결 / **확인 상태:** inspected

서로 다른 자동차·운동 비유를 추가하지만 도달 목표는 Phase1의 포함 관계 설명과 같다. 같은 개념의 반복이며 문장 전체가 동일하다는 뜻은 아니다.

**보존·확장할 성과:** ML의 Parameter 학습, DL의 Representation이라는 연결은 남기되 기초 정의 자체는 새 성과가 아니다.

근거: [S04 L131–197](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L131-L197) · [S04 L241–398](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L241-L398) · [S01 L35–58](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L35-L58) · [S01 L181–226](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L181-L226)

### F02. 규칙 작성과 데이터 학습의 차이 — 과목 내부 재설명

**권고:** 짧게 연결 / **확인 상태:** inspected

Phase1의 배송비·생산 사진과 Phase2의 사과·에어컨·얼굴·고양이는 소재가 다르지만 사람이 규칙을 쓰는가 데이터로 학습하는가라는 설명 구조가 같다. S04 안에서도 세 차례 재설명된다.

**보존·확장할 성과:** 새 성과 없이 규칙의 한계와 데이터 학습을 반복하는 구간이 중심이다.

근거: [S04 L198–240](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L198-L240) · [S04 L399–479](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L399-L479) · [S04 L590–719](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L590-L719) · [S02 L28–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L28-L120)

### F03. Feature Engineering과 Representation Learning

**권고:** 짧게 연결 / **확인 상태:** inspected

Day1 4교시 L31–120은 입력 특징 설계와 내부 표현 학습을 설명하고 비교표까지 제공한다. L124–178은 여러 층과 표현 학습을 연결한다. Phase2의 같은 기초 설명은 새 성과로 보지 않는다. Phase2 L768의 정답만 제공하면 된다는 단순화와 L1675–1676의 설계·전처리 주의는 일관되게 다듬어야 한다.

**보존·확장할 성과:** Feature Engineering과 Representation Learning의 대비 자체는 Day1 4교시에서 예시·비교표·활동까지 배운 내용이다. 이 재구성에서는 짧게 연결하고 새로운 신경망 계산/평가 과제로 확장한다.

근거: [S04 L355–398](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L355-L398) · [S04 L720–791](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L720-L791) · [S04 L1672–1676](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1672-L1676) · [S02 L161–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L161-L165) · [S01 L211–224](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L211-L224) · [S07 L31–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L31-L120) · [S07 L124–178](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L178)

### F04. 신경망 한 층: Weight·Bias·Activation·역전파

**권고:** 차별화 / **확인 상태:** inspected

Day1 4교시 L124–178에 층 구조와 표현 학습이 있고, S03에는 Weight·Bias·Loss·Gradient·Parameter 갱신 코드가 있다. 이를 전부 신규로 설명하지 않는다. Phase2 L500–532의 Activation과 구체적 계산 연결은 짧은 재소개와 구별해 신경망 원리 심화 위치에 보존한다.

**보존·확장할 성과:** Layer와 표현 학습의 큰 그림은 Day1 4교시에 이미 있다. 입력×Weight+Bias 뒤 Activation을 적용하는 구체적 한 층 계산과 비선형 변환의 역할을 심화 내용으로 보존한다.

근거: [S04 L480–561](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L480-L561) · [S03 L69–103](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L69-L103) · [S03 L148–230](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L230) · [S03 L321–356](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L356) · [S07 L124–178](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L178)

### F05. 지도·비지도·강화학습과 자기지도 언급

**권고:** 유지 / **확인 상태:** inspected

지도학습의 재정의는 연결 수준으로 줄이고 비지도·강화학습 및 자기지도와의 구분을 남긴다. 딥러닝의 상위/하위 분류와 학습 신호의 분류를 섞지 않아야 한다.

**보존·확장할 성과:** 정답 Label·데이터 구조·Reward를 학습 신호 기준으로 구분하는 것은 지정 비교 자료보다 자세하다.

근거: [S04 L792–907](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L792-L907) · [S02 L104–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L104-L120)

### F06. CNN·RNN·Transformer·Diffusion과 발전 흐름

**권고:** 차별화 / **확인 상태:** inspected

추가 확인 완료. Day1 4교시 L215–248(CNN), L252–305(RNN·LSTM), L308–394(Attention·Transformer)이 Phase2의 입문 소개와 겹친다. RNN은 오히려 Phase1이 LSTM/GRU까지 더 구체적이다. Transformer의 Q/K/V 등 내부 계산은 S07 L345 및 L388–394에서 Phase2로 넘기도록 명시한다. Phase2 L996의 위치 정보와 L1006–1027의 Diffusion은 통째로 삭제하지 않는다. CNN·RNN 기초를 다시 소개하기보다 신경망·Transformer 심화 단원에서 새 계산/실습으로 이어지게 한다.

**보존·확장할 성과:** CNN·RNN·Transformer의 기초 역할·등장 이유는 이미 배웠다. Phase2의 위치 정보 언급과 Diffusion 소개는 같은 중복으로 묶지 않고 별도 보존·배치 판단 대상으로 남긴다.

근거: [S04 L562–589](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L562-L589) · [S04 L908–1080](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L908-L1080) · [S02 L612–618](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L612-L618) · [S07 L215–248](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L215-L248) · [S07 L252–305](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L252-L305) · [S07 L308–394](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L308-L394)

### F07. Training·Inference 정의와 Prompt/RAG의 위치

**권고:** 짧게 연결 / **확인 상태:** inspected

정의와 학습 흐름도는 이미 Phase1에 있고 S03에는 Parameter 불변 확인 코드까지 있다. S04 L1123–1128의 후속 기술 연결은 따로 보존한다.

**보존·확장할 성과:** Pre-training·Fine-tuning은 학습, Prompt·RAG는 추론 입력 보강이라는 연결표는 후속 과목의 경계를 묶어 준다.

근거: [S04 L1081–1132](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1081-L1132) · [S02 L213–274](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L213-L274) · [S03 L573–599](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L573-L599)

### F08. Classification과 Regression

**권고:** 짧게 연결 / **확인 상태:** inspected

스팸·집값 사례는 Phase1에도 등장한다. 전면 재정의보다 평가 지표를 왜 다르게 선택하는지 연결한다.

**보존·확장할 성과:** 단순 범주/숫자 판별만으로는 새로운 성과가 없다. 출력과 Metric 선택의 연결이 확장점이다.

근거: [S04 L1133–1162](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1133-L1162) · [S02 L152–159](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L152-L159) · [S01 L80–114](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L80-L114)

### F09. Generalization

**권고:** 유지 / **확인 상태:** inspected

용어 최초 등장 여부와 학습 깊이를 분리한다. Phase1의 예고·주의가 있다는 이유로 평가 구간을 삭제하면 고유 성과를 잃는다.

**보존·확장할 성과:** 기존의 새 입력에서도 잘 작동해야 한다는 주의를 데이터 분리·과적합·누수·평가로 실질적으로 판단하게 한다.

근거: [S04 L1163–1182](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1163-L1182) · [S02 L205–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L205-L209) · [S03 L183–185](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L183-L185) · [S03 L721–723](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L721-L723)

### F10. 관계도 안에서 분류 기준 혼합

**권고:** 차별화 / **확인 상태:** inspected

L1194–1198은 지도·비지도·강화학습과 딥러닝을 나란히 놓는다. L1200–1203은 CNN·RNN·Transformer와 Diffusion을 나란히 놓는다. 앞의 L910–915가 같은 기준의 형제 기술로 외우지 말라고 한 설명과 요약 그림의 표현이 맞지 않는다. 외부 기술 조사 없이 확인한 문서 내부 표현 불일치다.

**보존·확장할 성과:** 학습 신호의 분류와 신경망 구조, 생성 접근을 서로 다른 축으로 읽는다.

근거: [S04 L1183–1215](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1183-L1215) · [S04 L908–915](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L908-L915)

### F11. 분야별 적용 예시

**권고:** 짧게 연결 / **확인 상태:** inspected

스팸·수요·추천·인식·생성 등 문제 목록 나열은 Phase1에서 충분히 다룬 역할과 겹친다. 동일한 코드 복사라고 판정하지 않는다.

**보존·확장할 성과:** 새 예시 분류 자체보다 같은 업무의 평가 기준을 설명하는 방향으로 활용할 수 있다.

근거: [S04 L1219–1238](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1219-L1238) · [S01 L74–179](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L74-L179) · [S01 L433–471](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L433-L471)

### F12. 긴급 메일: Rule 대 ML 설계 활동

**권고:** 차별화 / **확인 상태:** inspected

규칙 세 개와 예외 세 개만 다시 만드는 활동은 기존 책임 구분과 유사하다. 미래 정보 사용 여부·오류 비용·지표 선택을 제출 결과로 삼으면 새 성과가 생긴다. 코드가 없는 설계 활동이다.

**보존·확장할 성과:** 예측 시점에 없는 Feature 배제(L1283), 누락과 오탐의 피해 비교(L1288)는 평가로 확장한다.

근거: [S04 L1240–1291](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1240-L1291) · [S02 L77–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L77-L120) · [S02 L480–539](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L480-L539)

### F13. 요약·이해도 질문·조기 다음 단원 안내

**권고:** 차별화 / **확인 상태:** inspected

포함 관계·규칙 대 학습·학습 대 추론을 다시 묻는 문항과 일반화 질문이 혼재한다. 다음 강의 안내가 보강 학습보다 앞서 나타나 평가가 부록처럼 읽힐 수 있다.

**보존·확장할 성과:** 평가 근거를 설명하는 문항은 유지하고 이미 배운 정의 확인은 진입 점검으로 모은다.

근거: [S04 L1292–1347](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1292-L1347) · [S04 L1056–1080](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1056-L1080) · [S04 L1371–1375](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1371-L1375) · [S01 L475–523](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L475-L523) · [S02 L543–618](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L543-L618)

### F14. Sample·Feature·Label — 집값 사례 재사용

**권고:** 짧게 연결 / **확인 상태:** inspected

집/아파트의 면적·방 수·가격 표는 수치가 다르지만 같은 도메인·설명 구조를 반복한다. Sample이라는 단어 자체를 배운 적 없다고 단정하지 않고, 비교 자료에 사례/행 단위의 설명이 있음을 인정한다.

**보존·확장할 성과:** 한 사례의 이름 Sample을 명시하고 미래 정보·정답 누수 판정으로 확장하는 부분을 남긴다.

근거: [S04 L1389–1431](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1389-L1431) · [S02 L124–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L165) · [S02 L169–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L169-L209)

### F15. Train·Validation·Test 분리

**권고:** 유지 / **확인 상태:** inspected

지정 비교 자료는 평가를 예고하나 세 데이터의 역할과 선택 오염을 구체적으로 가르치지 않는다. 비교 원문 전체를 읽은 범위 안의 신규 심화로 판단한다.

**보존·확장할 성과:** 학습·선택·최종평가의 책임을 구분하고 시간·사용자 그룹에 맞는 분할을 설계한다.

근거: [S04 L1432–1452](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1432-L1452)

### F16. Loss·Optimization·Parameter·Hyperparameter

**권고:** 짧게 연결 / **확인 상태:** inspected

S03에 MSE·Gradient·SGD·Learning Rate·Parameter/Hyperparameter·갱신 실습·변경 활동까지 이미 있다. S04의 추상 흐름도를 새로운 심화 실습이라고 볼 수 없다.

**보존·확장할 성과:** Loss를 낮추는 것과 Validation 기준으로 설정을 선택하는 것의 차이로 확장해야 한다.

근거: [S04 L1453–1478](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1453-L1478) · [S03 L148–248](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L248) · [S03 L321–356](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L356) · [S03 L660–673](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L660-L673)

### F17. Underfitting·Overfitting

**권고:** 유지 / **확인 상태:** inspected

Phase1은 과적합을 후속 과목으로 예고한다. S04에는 비교 양상과 데이터·복잡도·Regularization·Early Stopping의 대응 관점이 있다.

**보존·확장할 성과:** Train과 Validation의 성능 양상을 읽고 과소/과적합을 구분한다.

근거: [S04 L1479–1501](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1479-L1501) · [S02 L205–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L205-L209) · [S03 L183–185](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L183-L185)

### F18. Data Leakage

**권고:** 유지 / **확인 상태:** inspected

퇴사 처리 완료일, 문서 복사본, RAG 정답 고정 사례와 점검 질문이 실제로 이미 있다. 누수 설명이 없다고 보고하거나 새로 전부 만들어야 한다고 제안하면 안 된다.

**보존·확장할 성과:** 미래 정보·유사 복제·전처리·Test 반복 선택·평가 정답 노출을 확인한다.

근거: [S04 L1502–1517](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1502-L1517)

### F19. Accuracy·Precision·Recall·F1과 다층 평가

**권고:** 유지 / **확인 상태:** inspected

희귀 양성 사례, 정상 메일의 오분류 피해, 모델·검색·시스템·사람 평가의 구분을 이미 포함한다. 다만 구체적인 계산표와 실행 결과까지 있는 것은 아니다.

**보존·확장할 성과:** 높은 Accuracy가 목적 달성을 보장하지 않는 이유와 업무 피해에 맞는 Metric을 설명한다.

근거: [S04 L1518–1545](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1518-L1545)

### F20. Self-supervised·Transfer와 Prompt/RAG 연결

**권고:** 차별화 / **확인 상태:** technical_verification_pending

Day1 4교시 L398–460에 Pre-training·Pre-trained Model·Foundation Model의 구분과 재사용 관점이 있다. 이를 다시 최초 소개로 취급하지 않는다. Phase2 L1548의 자기지도 신호 설명은 지정 비교 범위보다 구체적이다. L1550은 Transfer Learning과 Fine-tuning·Prompt/RAG를 한 문맥에 묶으므로 학습/추론의 Parameter 갱신 경계를 명시해야 한다. 용어의 엄밀한 적용 범위는 별도 공식 원문 기술 검증 대상으로 남긴다.

**보존·확장할 성과:** 사전학습 모델을 후속 작업의 기반으로 재사용한다는 큰 흐름은 Day1 4교시에 이미 있다. 데이터 자체에서 학습 신호를 만드는 Self-supervised 설명을 구분해 보존한다.

근거: [S04 L1546–1561](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1546-L1561) · [S04 L1081–1128](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1081-L1128) · [S02 L235–274](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L235-L274) · [S07 L398–460](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_04_ML%EC%97%90%EC%84%9C_Deep_Learning%EA%B3%BC_%EC%83%9D%EC%84%B1%ED%98%95_AI%EA%B9%8C%EC%A7%80_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L398-L460)

### F21. 데이터 책임 나누기·전체 Pipeline 설계 활동

**권고:** 유지 / **확인 상태:** inspected

설계 활동은 이미 있다. 모델 학습 실행 코드가 아니라 종이/Markdown 과제다. 작은 Dataset은 6행으로 확장하라고만 쓰여 있고 실제 본문 표는 1행(L1393–1395)이라 교사용 완성 표·정답 예시 보완이 필요하다.

**보존·확장할 성과:** 분할·누수·Metric·Failure Cost·운영 Inference를 하나의 제출물에 연결한다.

근거: [S04 L1562–1635](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1562-L1635) · [S02 L124–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L165) · [S02 L480–539](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L480-L539)

### F22. 보강 요약·확인 활동·실무 팁·주의사항

**권고:** 유지 / **확인 상태:** inspected

평가 관련 질문과 주의를 보존한다. 같은 파일의 기존 정의를 재설명하는 부분은 체크리스트로 모을 수 있다. 전체 반복이라는 이유로 활동까지 삭제하지 않는다.

**보존·확장할 성과:** 데이터 분리·누수·오류 비용을 설명하고 배포 입력과 평가 조건의 차이를 확인한다.

근거: [S04 L1636–1680](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1636-L1680)

### F23. 개요·학습 지도·Wiki·참고 안내

**권고:** 차별화 / **확인 상태:** inspected

수업 본문과 운영 메타데이터를 구별한다. 반복 개요는 합칠 수 있으나 외부 링크 최신성·Wiki 실재 경로는 이번에 확인하지 않았다. 참고 링크를 읽었다거나 실행 검증에 사용했다고 표시하지 않는다.

**보존·확장할 성과:** 자료의 목표·연결·참고 위치를 안내한다.

근거: [S04 L1–130](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1-L130) · [S04 L1348–1376](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1348-L1376) · [S04 L1377–1388](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1377-L1388) · [S04 L1681–1693](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1681-L1693)

### F24. 재구성 후 과목 제목

**권고:** 차별화 / **확인 상태:** inspected

기초 정의와 구조별 입문 소개를 줄이고 데이터·평가를 핵심으로 삼는다면 기존 AI·머신러닝·딥러닝 개요라는 제목보다 머신러닝의 데이터 설계와 모델 평가가 실제 학습 목표를 잘 나타낸다. 전체 목차·학습 성과 확정 뒤 제목도 확정하며 현재 파일명이나 원문 제목을 변경하지 않는다.

**보존·확장할 성과:** 데이터 입력·분할·일반화·누수·업무 오류 비용에 따라 모델 평가를 설계한다.

근거: [S04 L1–50](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1-L50) · [S04 L1432–1545](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1432-L1545)

## 대상 전체 구간 추적

| 구간 | 줄 | 내용 | 상태 | 연결 |
|---|---|---|---|---|
| B01 | 1–69 | Phase 2 — 02. AI / 머신러닝 / 딥러닝 개요 | 검토함 | F23, F24 |
| B02 | 70–100 | [학습] AI / 머신러닝 / 딥러닝 개요 (Unit 1) | 검토함 | F23 |
| B03 | 101–130 | 이번 과목의 학습 지도 | 검토함 | F23 |
| B04 | 131–197 | ① 문제 이해 (Why) | 검토함 | F01 |
| B05 | 198–240 | 왜 이런 기술이 필요했을까? | 검토함 | F02 |
| B06 | 241–280 | ② 개념 이해 (Concept) | 검토함 | F01 |
| B07 | 281–354 | 머신러닝(Machine Learning) | 검토함 | F01 |
| B08 | 355–398 | 딥러닝(Deep Learning) | 검토함 | F01, F03 |
| B09 | 399–479 | ③ 구조와 원리 (Architecture / Principle) | 검토함 | F02 |
| B10 | 480–561 | 딥러닝의 동작 원리 | 검토함 | F04 |
| B11 | 562–589 | AI는 왜 계속 새로운 기술이 등장했을까? | 검토함 | F06 |
| B12 | 590–671 | Rule-Based AI의 한계 | 검토함 | F02 |
| B13 | 672–719 | 머신러닝은 규칙을 사람이 만드는 것이 아니라 AI가 학습한다. | 검토함 | F02 |
| B14 | 720–791 | 그런데 머신러닝도 한계가 있었다. | 검토함 | F03 |
| B15 | 792–907 | 머신러닝에는 여러 학습 방법이 있다. | 검토함 | F05 |
| B16 | 908–1029 | 딥러닝도 하나의 모델만을 의미하지 않는다. | 검토함 | F06, F10 |
| B17 | 1030–1080 | 핵심 흐름 다시 정리 | 검토함 | F06, F13 |
| B18 | 1081–1132 | ③-1. Training과 Inference를 구분하자 | 검토함 | F07 |
| B19 | 1133–1162 | ③-2. Classification과 Regression | 검토함 | F08 |
| B20 | 1163–1182 | ③-3. 가장 중요한 목표: Generalization | 검토함 | F09 |
| B21 | 1183–1218 | ④ 관계 이해 (Relation) | 검토함 | F10 |
| B22 | 1219–1239 | ⑤ 적용 예시 (Example / Application) | 검토함 | F11 |
| B23 | 1240–1291 | ⑤-1. Practice — 같은 문제를 Rule과 Machine Learning으로 설계해 보기 | 검토함 | F12 |
| B24 | 1292–1347 | ⑥ 핵심 정리 (Summary) | 검토함 | F13 |
| B25 | 1348–1376 | AIKOS Knowledge 제안 | 검토함 | F23, F13 |
| B26 | 1377–1388 | [보강 학습] “학습한다”는 말을 실제 데이터와 평가 과정으로 이해하기 | 검토함 | F23 |
| B27 | 1389–1431 | 1. Sample, Feature, Label | 검토함 | F14 |
| B28 | 1432–1452 | 2. Train, Validation, Test를 왜 나누는가? | 검토함 | F15 |
| B29 | 1453–1478 | 3. Loss와 Optimization: 틀린 정도를 이용해 조금씩 고치기 | 검토함 | F16 |
| B30 | 1479–1501 | 4. Overfitting과 Underfitting | 검토함 | F17 |
| B31 | 1502–1517 | 5. Data Leakage: 시험 답안이 학습 과정으로 새어 들어간 경우 | 검토함 | F18 |
| B32 | 1518–1545 | 6. Accuracy 하나만 보면 왜 위험한가? | 검토함 | F19 |
| B33 | 1546–1561 | 7. Self-supervised Learning과 Transfer Learning | 검토함 | F20 |
| B34 | 1562–1570 | Practice — 작은 Dataset의 책임 나누기 | 검토함 | F21 |
| B35 | 1571–1635 | Practice 2 — 학습 파이프라인 전체 설계하기 | 검토함 | F21 |
| B36 | 1636–1662 | 보강 핵심 정리 | 검토함 | F22 |
| B37 | 1663–1680 | 실무 팁 | 검토함 | F22, F03 |
| B38 | 1681–1693 | 참고자료 — 원문으로 확인하기 | 해당 없음 | F23 |

## 검증 한계

근거 위치·인용문·원본 SHA·전체 구간·상태를 자동 검사한다. 의미와 교육적 판단은 같은 Work 세션의 검토이며 독립 모델 검증이 아니다. 외부 URL 현재 접속·기술 최신성·학습자 이해도·예상 수업시간·저사양 실행성은 미검증이다. Token·내부 모델 호출량은 노출되지 않아 기록값을 만들지 않았다.
