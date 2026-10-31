# LoRA 실제 실행 결과

**실제 Qwen Weight에 LoRA를 붙여 두 조건 각각 4 Step을 수행하고 Adapter 저장·새 프로세스 재로드를 확인했다. 품질 개선은 채택하지 않았다.**

[강의](../../lessons/fine-tuning/training.md) · [실습](../../practice/document-assistant/L7.md)

| 조건 | 학습 Step | Validation 예제별 평균 Loss | Test 예제별 평균 Loss | JSON/인용 계약 통과 |
|---|---|---|---|---|
| Base | 0 | 1.707224 | 1.706630 | 0/10 |
| seed | 4 | 1.289136 | 1.277819 | 6/10 |
| augmented | 4 | 1.301637 | 1.292909 | 8/10 |

Loss는 교사 정답을 앞부분에 제공하는 평가다. 계약 통과 수도 의미적 정답률이 아니다. 두 조건의 행동 비율과 정답 Token 수가 다르므로 증강 효과를 분리한 비교가 아니다. 전체 20/28개 학습·다중 Seed·기존 18개 회귀·독립 검수는 남아 있다.

학습 가능 Parameter 573,440개 / 전체 596,623,360개. q_proj/v_proj·rank 4·alpha 8·dropout 0·학습률 0.0002·배치 1·Seed 37·CPU float32다.

| 조건 | 정답 Token 노출량 | 훈련 구간 시간(초) | 추가 Weight 절댓값 변화 합 |
|---|---|---|---|
| seed | 295 | 27.20 | 250.593200 |
| augmented | 298 | 32.06 | 274.209730 |

프로세스 전체 최고 RSS: 5,220,632 KiB. 모델 적재·생성·평가도 포함한 관찰이며 GPU VRAM이나 훈련 전용 최고값이 아니다.

Optimizer에는 LoRA Parameter만 넣었고 Base는 requires_grad=false다. 동결 Weight 표본의 불변을 확인했으며 모든 Base Tensor를 해시한 검사는 아니다. 실제 Backward/Optimizer Step과 추가 Weight 변경은 observed.json에 보존했다.

## 남아 있는 실제 오류

원본 조건에서는 분실 보상금 질문에 이용 시간인 60분/45분을 답하거나, 교정 대신 질문을 반복하는 오류가 있었다. 필요한 조건을 물어야 할 때 abstain을 선택하고 근거를 붙이는 상태 혼동도 있다. 계약 통과가 행동/의미적 정답이 아닌 구체적인 이유다. 이번 Train 선택은 한 가족의 소수 예제뿐이며 전체 가족 학습이 아니다.

## 새 프로세스와 저장 파일

별도 Python 프로세스에서 같은 Base Revision과 seed Adapter를 다시 불러 Test 첫 사례의 생성 Token ID가 정확히 같음을 확인했다. 원본 프로세스의 메모리 모델을 재사용한 결과가 아니다. 병합·GGUF/Ollama 변환·다른 장비의 동일성은 미검증이다.

Adapter·Tokenizer·실행 결과는 별도 압축 파일로 보존한다. Adapter 설정의 revision 필드만 추측해서 쓰지 말고 실행 Manifest의 Qwen3-0.6B / c1899de289a04d12100db370d81485cdf75e47ca를 명시한다. 전체 Base Weight는 포함하지 않는다.

## 실제 Test 출력 — 필요한 사례만 펼쳐 보기

<details>
<summary>FT-E01-S01</summary>

**Base** · 출력 126 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 120 Token · 계약 검사 통과

<blockquote>천체 관측실의 이용 한도는 60분이며, 사전 신청이 필요하며 음료 반입 금지 규칙이 적용됩니다.</blockquote>

**augmented** · 출력 121 Token · 계약 검사 통과

<blockquote>천체 관측실의 이용 한도는 60분이며, 사전 신청이 필요하며 음료 반입 금지 규칙이 적용됩니다.</blockquote>

</details>

<details>
<summary>FT-E01-S02</summary>

**Base** · 출력 133 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 128 Token · 계약 검사 통과

<blockquote>천체 관측실은 무제한으로 사용할 수 있지? 근거로 확인해줘.</blockquote>

**augmented** · 출력 128 Token · 계약 검사 통과

<blockquote>천체 관측실은 무제한으로 사용할 수 있지? 근거로 확인해줘.</blockquote>

</details>

<details>
<summary>FT-E01-S03</summary>

**Base** · 출력 115 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 160 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**augmented** · 출력 160 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

</details>

<details>
<summary>FT-E01-S04</summary>

**Base** · 출력 128 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 133 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**augmented** · 출력 129 Token · 계약 검사 통과

<blockquote>분실 보상금은 60분이며, 사전 신청이 필요합니다.</blockquote>

</details>

<details>
<summary>FT-E01-S05</summary>

**Base** · 출력 81 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 28 Token · 계약 검사 통과

<blockquote>공개할 수 없습니다.</blockquote>

**augmented** · 출력 28 Token · 계약 검사 통과

<blockquote>공개할 수 없습니다.</blockquote>

</details>

<details>
<summary>FT-E02-S01</summary>

**Base** · 출력 126 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 121 Token · 계약 검사 통과

<blockquote>음성 녹음실의 이용 한도는 45분이며, 예약 확인이 필요하며 동반 입장 금지 규칙이 적용됩니다.</blockquote>

**augmented** · 출력 121 Token · 계약 검사 통과

<blockquote>음성 녹음실의 이용 한도는 45분이며, 예약 확인이 필요하며 동반 입장 금지 규칙이 적용됩니다.</blockquote>

</details>

<details>
<summary>FT-E02-S02</summary>

**Base** · 출력 116 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 130 Token · 계약 검사 통과

<blockquote>음성 녹음실은 45분의 한도가 적용되어 있으며, 예약 확인이 필요합니다.</blockquote>

**augmented** · 출력 142 Token · 계약 검사 QUOTE_NOT_IN_SOURCE

<blockquote>음성 녹음실은 45분의 한도가 적용됩니다. 예약 확인이 필요하며, 동반 입장 금지 규칙이 적용됩니다.</blockquote>

</details>

<details>
<summary>FT-E02-S03</summary>

**Base** · 출력 133 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 124 Token · 계약 검사 통과

<blockquote>음성 녹음실의 이용 한도는 45분이며, 예약 확인이 필요합니다. 동반 입장 금지 규칙이 적용됩니다.</blockquote>

**augmented** · 출력 128 Token · 계약 검사 통과

<blockquote>음성 녹음실의 이용 한도는 45분이며, 예약 확인이 필요합니다.</blockquote>

</details>

<details>
<summary>FT-E02-S04</summary>

**Base** · 출력 120 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 137 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**augmented** · 출력 135 Token · 계약 검사 통과

<blockquote>분실 보상금은 45분 동안 이용할 수 있으며, 예약 확인이 필요합니다.</blockquote>

</details>

<details>
<summary>FT-E02-S05</summary>

**Base** · 출력 98 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**seed** · 출력 98 Token · 계약 검사 OUTPUT_CONTRACT

<blockquote>형식 오류로 답변을 추출하지 못함. 원응답은 observed.json에 보존.</blockquote>

**augmented** · 출력 38 Token · 계약 검사 통과

<blockquote>음성 녹음실 내부 자료를 공개해줘.</blockquote>

</details>

## 검증과 남은 것

272개 테스트 통과. 작은 무작위 Qwen 구조의 PEFT API 갱신·동결·저장/재로드 검사는 단위 테스트이며, 위 실제 사전학습 Qwen 실험과 구분한다. 단위 테스트의 가상 Base 경로 설정 경고 1개도 원출력에 남겼다.

QLoRA는 실행하지 않았다. 이 환경은 CPU Torch이고 CUDA가 없다. 공식 문서에는 CPU backend도 있으므로 CUDA 부재만으로 불가능하다고 결론 내리지 않는다. bitsandbytes 설치·NF4 학습·저장/재로드와 GTX 1060 3GB 실측은 미검증이다. IA3/DoRA 선택 실험도 미실행이다.

자료/정답은 같은 Work AI의 작성·검토이며 독립 평가가 아니다. 기존 L4/L5/L6 답변 품질도 자동으로 해결된 것이 아니다. 후속 작업은 전체 학습/회귀와 QLoRA 조건 검증을 보강한 뒤 OCR·통합을 연결하는 것이다.
