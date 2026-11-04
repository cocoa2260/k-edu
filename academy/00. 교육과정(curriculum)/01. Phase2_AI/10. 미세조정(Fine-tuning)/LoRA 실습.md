# 작은 갱신을 학습하고, 결과를 평가하고, 다시 불러오기

회의실 예제의 질문·자료·교사 정답과 학습할 Token 범위를 [앞 수업](lesson.md)에서 준비했다. 이제 예제를 읽는 것에서 한 걸음 더 나아가 모델의 일부 Parameter를 실제로 바꾼다. 그런데 Loss가 줄었는데도 없는 보상금을 답한다면 성공이라고 할 수 있을까? 저장한 Adapter를 다시 불러와 같은 잘못된 답을 내면 무엇까지 확인한 것일까?

이번 수업은 **갱신 원리 → 한 Step의 동작 → 자원 선택 → 답변 평가 → 저장과 재현**을 연결한다. 아래 ‘기존 실행’ 수치는 Qwen3-0.6B CPU LoRA의 과거 실제 기록이다. 이번 설명 정비에서 새 훈련을 돌린 수치는 아니다. [연결 실습](../../practice/document-assistant/L7.md)에는 작은 계산·저장 기록 관찰과 별도로 실제 재실행 경로가 있다. 처음 읽을 때 긴 JSON 전체를 열 필요는 없다.

## 1. LoRA는 원래 계산에 작은 갱신 경로를 더한다

신경망의 Linear Layer는 입력 벡터에 Weight 행렬을 곱한다. 입력이 d개, 출력이 k개라면 Weight W는 k×d개 숫자다. Full fine-tuning에서는 이런 기존 Weight도 학습으로 바꾼다. LoRA에서는 W를 동결하고, 입력을 작은 r차원으로 줄였다가 출력 차원으로 보내는 두 행렬 A·B를 학습한다. ‘작은 경로’는 저장할 갱신을 작게 표현한다는 뜻이며 전체 모델을 작은 모델로 교체했다는 뜻이 아니다.

출력은 다음과 같이 계산한다. 여기서는 열벡터 표기이며 실제 라이브러리의 Tensor 축 배치와 구분한다.

\[
y = Wx + \frac{\alpha}{r}B(Ax),\qquad A\in\mathbb{R}^{r\times d},\ B\in\mathbb{R}^{k\times r}
\]

r은 **갱신 행렬의 최대 rank를 제한하는 중간 차원**이다. 작은 r로 표현할 수 있는 갱신에는 제약이 생긴다. 따라서 저장할 숫자는 줄지만 어떤 과제든 같은 품질을 얻는다는 보장은 없다. alpha/r은 기본 LoRA의 배율이다. rank를 바꾸면서 alpha를 그대로 두면 갱신의 표현 크기와 배율을 동시에 바꾸게 된다. Rank-stabilized LoRA처럼 배율이 다른 옵션도 있으므로 이 식을 모든 변형의 공통식으로 외우지 않는다.

### 숫자로 한 번 따라가기

W가 2×2 단위행렬이고 입력 x가 [2,1]이면 원래 출력은 [2,1]이다. r=1, A=[1,0], B=[0.1,0.2]를 세로로 놓고 alpha=2로 정하자. **작동 설명용 가상 값**이며 실제 모델 Weight가 아니다.

A는 입력에서 2를 만들고 B는 이를 [0.2,0.4]로 바꾼다. 배율 2를 곱한 갱신은 [0.4,0.8]이다. 원래 출력에 더하면 [2.4,1.8]이 된다. W는 그대로이며 A·B만 달라져도 출력이 바뀔 수 있음을 보여준다. 이 작은 예제는 rank=1인데도 4개 숫자가 필요해 원래 4개 Weight보다 적지 않다. 절약은 큰 행렬에서 r이 충분히 작을 때 나타난다.

1024×1024 Weight 하나는 1,048,576개 숫자이고 r=4의 A·B는 4×1024+1024×4=8,192개다. 이 값은 **Layer 하나에 추가하는 Parameter 수**다. 실제 모델에는 여러 Layer와 Embedding 등이 있으며 q_proj와 v_proj의 모양도 같다고 단정할 수 없다. 모델 전체의 학습 가능 수는 실제 주입 결과로 확인한다.

### 설정이 바꾸는 것과 바꾸지 않는 것

이번 기준선은 Qwen3-0.6B에서 Attention의 Query·Value 투영에 해당하는 `q_proj`, `v_proj`에 LoRA를 붙인다. 모든 Layer를 학습한 결과로 해석하지 않는다.

| 설정 | 이번 값 | 의미와 비교 시 주의 |
|---|---:|---|
| r | 4 | 중간 차원. 늘리면 추가 Parameter와 학습 표현 범위가 늘지만 품질 보장은 아님 |
| lora_alpha | 8 | 기본 배율은 8/4=2. Learning rate와 별도 |
| lora_dropout | 0 | LoRA 경로의 학습 중 Dropout을 사용하지 않음 |
| target_modules | q_proj, v_proj | 실제 모델의 Layer 이름과 모양을 확인할 대상 |
| bias | none | 이 구성에서 별도 Bias 학습을 추가하지 않음 |
| Optimizer / lr | AdamW / 0.0002 | Gradient로 Parameter를 갱신할 규칙과 학습률 |

기존 실행의 학습 가능 Parameter는 573,440개, Adapter를 포함한 전체 Parameter는 596,623,360개다. 약 0.0961%만 학습 가능하지만 Base Weight와 Forward/Backward 계산에 필요한 중간값은 여전히 메모리에 있다. ‘학습 가능한 수’와 ‘불러올 전체 수’를 구분한다. 다른 target_modules·모델·저장 모듈을 쓰면 다시 세어야 한다.

### 한 Step에서 일어나는 일

회의실 질문과 교사 응답을 넣으면, 모델은 앞 Token을 보고 다음 Token의 확률을 계산한다. 정답 Token에 높은 확률을 주지 못하면 Loss가 커진다. 앞 수업의 labels=-100은 이번 직접 정답 채점에서 제외한다. Backward는 그 Loss를 줄일 방향의 Gradient를 계산하고 Optimizer Step이 실제 Parameter를 바꾼다.

다음은 **현재 훈련 코드의 핵심 발췌**다. 단독 실행용 코드가 아니며 model·batch·optimizer는 실행 도구가 먼저 만든다.

```python
optimizer.zero_grad(set_to_none=True)
loss = model(**batch).loss
loss.backward()
torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
optimizer.step()
```

zero_grad는 이전 Step의 Gradient를 지운다. Forward의 유한한 Loss, Backward의 Gradient, Step 이후 실제 Weight 변화는 다른 증거다. Gradient clipping은 큰 Gradient를 제한하며 로그의 gradient_norm은 clipping 전 전체 norm이다. 학습률이 너무 크면 갱신이 불안정해질 수 있고 작으면 주어진 Step에서 충분히 바뀌지 않을 수 있다. 이번 값은 최적값이라는 결론이 아니다.

기본 초기화에서는 B가 0이라 시작 출력의 LoRA 갱신은 0이다. 첫 Backward에서 A의 Gradient가 0이어도 B는 바뀔 수 있다. ‘모든 Adapter Tensor에 첫 Step부터 0이 아닌 Gradient가 있어야 한다’는 검사는 잘못이다. 이후 갱신·Gradient와 trainable 대상, Base 동결을 함께 본다. 기존 코드는 동결 Weight마다 앞 16개 값이 그대로인지 확인했다. 이는 전체 Base Weight의 모든 바이트를 해시 비교한 증거와 다르다.

학습은 model.train(), 평가는 model.eval()로 전환한다. 평가에서는 Gradient를 계산하지 않는다. 이 실습은 훈련에서 KV cache를 끄고 생성에서 켠다. Dropout·cache·생성 길이 같은 조건이 다르면 훈련/생성 시간도 같은 기준으로 비교할 수 없다.

**확인 질문**

1. 1024×1024 Layer의 r=4 계산값 8,192를 모델 전체의 크기라고 말하면 왜 틀리는가?
2. 처음에 B=0이면 A의 첫 Gradient가 0일 수 있는 이유는 무엇인가? 무엇을 더 확인해야 하는가?
3. rank·alpha·Learning rate는 각각 무엇을 바꾸는가? rank만 높이면 품질이 좋아진다고 보장할 수 있는가?

## 2. QLoRA에서는 저장 정밀도와 계산·학습 메모리를 구분한다

LoRA는 갱신을 줄여 저장하지만 Base는 여전히 필요하다. QLoRA는 이 동결 Base를 저비트로 보관하고 LoRA 갱신을 학습하는 구성이다. 양자화한 모델로 답변 한 번 생성하는 것과 Gradient·Optimizer Step까지 실행하는 것은 다르다.

양자화는 각 Weight를 원래의 부동소수점 그대로 저장하는 대신 제한된 값과 보조 정보로 표현한다. 4-bit면 하나의 코드가 16가지 값을 구분한다. 정수 -8~7이 실제 Weight 값이라는 뜻은 아니다. NF4는 대체로 정규분포인 Weight에 맞춘 4-bit 표현이며, 블록별 Scale 등으로 실제 값의 범위를 복원한다. Double quantization은 이 **양자화 상수도 다시 양자화**하여 보조 정보의 저장 부담을 줄인다.

저장된 4-bit Weight를 이용한 연산은 필요에 따라 더 높은 계산 정밀도로 수행한다. 예를 들어 compute dtype을 bfloat16으로 지정하는 것은 Adapter·Gradient·Optimizer까지 전부 4-bit로 저장한다는 뜻이 아니다. 해당 장비와 backend가 그 dtype/연산을 지원하는지 확인해야 한다. 공개 QLoRA 구성의 all-linear 대상과 이번 q_proj/v_proj 기준선도 다르므로, 단순히 로딩 옵션 하나만 바꾼 동등 실험이라고 부르지 않는다.

### ‘파일이 작다’에서 ‘학습 가능하다’로 바로 넘어가지 않기

**거친 산술 예**로 6억 Parameter를 float32로만 저장하면 약 24억 바이트, 4-bit 코드만 세면 약 3억 바이트다. 8배 차이지만 실제 메모리 비율은 아니다. 양자화 상수와 일부 고정밀도 Layer·Adapter·Gradient·AdamW 상태·활성값·임시 Tensor를 빼고 센 값이기 때문이다. 실제 모델의 정확한 Parameter 수나 파일 크기도 이 반올림 값과 구분한다.

| 메모리 항목 | 왜 남는가 | 조정할 때 생기는 관계 |
|---|---|---|
| Base와 양자화 보조 정보 | 원래 계산이 필요함 | 정밀도/지원 연산과 정확도 확인 |
| Adapter·Gradient·Optimizer 상태 | 학습 가능한 값을 갱신함 | rank·대상 범위·Optimizer에 따라 변함 |
| 활성값 | Backward에 중간 결과가 필요함 | Sequence 길이·Microbatch가 크면 부담 증가 |
| 임시 메모리·cache | 연산과 생성 과정에 필요함 | Runtime·평가·동시 실행까지 실측 필요 |

Microbatch를 줄이고 여러 번 Gradient를 누적하면 한 번에 처리할 예제 수를 줄일 수 있다. 그러나 한 예제 자체가 너무 길어 생기는 메모리 문제를 항상 해결하지는 못한다. Gradient checkpointing은 중간값 일부를 다시 계산해 메모리를 줄이는 대신 시간이 더 들 수 있다. Paged Optimizer는 메모리 급증을 관리하는 기법이지 어떤 크기의 모델도 실행하게 하는 보장이 아니다.

이번 기존 실행은 **CPU float32 LoRA**다. QLoRA의 설치·실제 Forward/Backward/Step·저장/재로드는 확인하지 않았다. 공식 bitsandbytes 문서는 CPU backend도 다루므로 CUDA 부재만으로 불가능이라고 판단하지 않는다. 반대로 backend 지원 표에 장비가 있어도 GTX 1060 3GB에서 이 수업 전체를 실행할 수 있다는 증거는 아니다. 장비·드라이버/패키지·연산/dtype·입력 길이·실제 최고 메모리를 확인한 뒤 가능 범위를 정한다.

CPU RSS와 GPU VRAM도 같은 값이 아니다. 기존 전체 실행의 프로세스 최고 RSS 기록은 약 4.65 GiB이며 GPU 사용량이 아니다. 훈련·평가·회귀가 포함된 프로세스 기록이어서 LoRA 한 Step만의 메모리로 쓰지 않는다. 중복 프로세스 하나가 메모리 한도로 종료된 기록도 있어 동시 실행 인원을 이 수치만으로 결정할 수 없다.

**확인 질문**

1. 4-bit Base로 추론이 성공하면 QLoRA 훈련·저장/재로드도 검증됐는가?
2. 6억 Weight의 코드 저장량이 줄었다고 전체 훈련 메모리가 같은 비율로 줄지 않는 이유는 무엇인가?
3. 입력 한 개가 너무 길어 OOM이면 Gradient 누적만 늘리면 되는가? 무엇을 기록하고 조정할 것인가?

## 3. Loss·형식·행동·사실과 Agent 과제를 따로 평가한다

Teacher forcing Loss는 교사 정답의 앞부분을 입력으로 주면서 다음 Token을 얼마나 잘 예측하는지 확인한다. 실제 생성에서는 정답 앞부분 대신 모델 자신의 이전 출력을 이어 간다. 첫 선택이 어긋나면 뒤 문맥도 달라질 수 있다. 따라서 Loss 감소와 실제 답변의 정답률은 같은 지표가 아니다.

기존 평가의 macro_mean_loss는 각 예제의 평균 Loss를 다시 동일 비중으로 평균한 값이다. 짧은 응답과 긴 응답이 각각 한 표씩 가지므로 모든 정답 Token을 합친 가중 평균과 다를 수 있다. 서로 다른 데이터·Mask·Template에서 잰 Loss를 그대로 비교하지 않는다.

### 기존 전체 Train 실행은 어떤 비교였나

원본 20행을 학습한 조건은 `seed`, Train 바꿔쓰기까지 포함한 28행 조건은 `augmented`, Adapter를 적용하지 않은 조건은 `base`다. 이름 속 seed와 난수 Seed 37은 다른 뜻이다. 두 학습 조건은 동일 초기 Adapter에서 출발해 Microbatch 1로 각각 28 Step을 실행했다.

원본은 20행을 모두 한 번 보고 8행을 반복했고 증강은 28행을 한 번씩 봤다. 정답 Token 노출량은 각각 1,727/1,947이다. 같은 Step을 썼지만 같은 Token 수나 행동 비율을 학습한 것은 아니다. 이는 원본/증강 두 구성의 관찰이며 증강만의 인과적 효과를 분리한 실험이 아니다. 최초 4개·4 Step 실험은 동작 확인용으로 구분한다.

다음은 **과거 전체 실행의 저장값을 반올림한 표**다. 같은 Template·생성 설정·Validation/Test 입력을 사용했다.

| 조건 | Validation Loss | Test Loss | JSON/인용 계약 통과 | 계약 통과+행동 이름 일치 |
|---|---:|---:|---:|---:|
| base | 1.707224 | 1.706630 | 0/10 | 0/10 |
| seed | 0.375139 | 0.349665 | 8/10 | 4/10 |
| augmented | 0.459348 | 0.444199 | 8/10 | 3/10 |

선택 규칙은 두 학습 후보 중 Validation Loss가 작은 쪽이며 동률이면 seed다. 이 규칙으로 seed를 선택한 기록을 저장한 뒤 Test 지표를 확인했다. 프로그램의 선택에 Test 지표를 쓰지 않았다는 뜻이다. 이 Test는 앞 실험부터 공개·열람한 작은 자료이므로 독립 블라인드 최종 평가라는 뜻은 아니다.

### 행동 이름이 맞아도 답은 틀릴 수 있다

천체 관측실의 분실 보상금 질문에서 원문에는 보상 기준이 없다. 원본 학습 모델의 **과거 실제 응답**은 다음과 같다.

```json
{"answer":"0","claims":[],"outcome":"abstain"}
```

abstain은 보류라는 행동 이름이고 claims도 비어 있어 계약을 통과한다. 그러나 answer의 ‘0’은 ‘기준이 없어 답할 수 없다’와 다르다. 금액처럼 해석될 근거 없는 숫자를 제시했다. 이 한 사례는 계약·행동 이름 일치까지 세어도 의미 정답을 따로 봐야 하는 이유다.

반대로 첫 관측실 한도 질문의 seed 응답은 60분·사전 신청·음료 반입 금지를 쓰지만 claims가 비어 계약에 실패했다. 여기서는 사실 내용과 근거 전달 계약을 각각 평가한다. 어느 한쪽을 통과했다고 다른 쪽 실패를 지우지 않는다. 응답이 잘렸다면 생성 Token 수와 길이 상한도 보되, 상한에 닿았다는 이유만으로 모든 내용 오류를 길이 탓으로 돌리지 않는다.

실패를 봤을 때 바로 Step만 늘리지 않는다. 정답 라벨이 틀렸는지, 같은 가족이 새어 들어갔는지, 평가 입력·Template이 다른지, 특정 행동 비율이 치우쳤는지, 학습률/훈련량이 적합한지 가설을 나눈다. Training Loss만 내려가고 Validation이 나빠지는 현상은 과적합을 의심할 신호지만 한 번의 출력만으로 원인을 확정하지 않는다. Test를 보고 설정을 고쳤다면 다음 판단에는 새 평가 자료가 필요하다.

### 응답 작성 능력과 Agent의 도구 선택은 다른 계약이다

이번 SFT는 자료를 받은 뒤 outcome·answer·claims를 작성하는 행동을 연습한다. Agent는 먼저 도구를 고르고 그 결과를 읽어 다음 행동을 정한다. SFT 지표가 좋아져도 이 계약까지 잘 수행한다는 보장은 없다.

기존 동일 18개 Agent 회귀에서 Base/원본/증강의 모델 생성은 60/42/40회, 최종 근거 초안은 모두 0개였다. 원본 조건에서 호출이 줄었어도 불필요한 되묻기로 일찍 끝난 사례가 있다. 이를 비용 효율이나 과제 성공 개선으로 발표하지 않는다. Runtime의 권한·도구·상한은 유지하고 모델만 비교했다. Adapter를 공통 서비스 모델로 채택하지 않은 이유다.

IA3·DoRA 같은 대안은 필요한 가설이 있을 때 하나 비교한다. Base·자료/Split·시작 상태·Step과 Token 노출·평가를 맞추고 추가 Parameter·메모리·시간도 기록한다. 여러 Seed와 독립 검토를 추가해야 선택이 우연에 얼마나 민감한지도 볼 수 있다. 이번 기록에는 해당 대안 훈련이나 다중 Seed 결과가 없다.

**확인 질문**

1. 두 조건 모두 28 Step이면 증강 데이터만의 효과를 공정하게 분리했다고 할 수 있는가?
2. 위 abstain 응답이 계약과 행동 이름을 통과해도 의미 검토에서 실패하는 이유는 무엇인가?
3. Agent 호출이 60회에서 42회로 줄었지만 최종 초안이 없다면 무엇을 더 확인해야 하는가?

## 4. Adapter 저장, 추론 재현, 훈련 재개는 확인 대상이 다르다

LoRA Adapter는 Base에 더할 A·B와 구성 정보를 보관한다. 일반적인 PEFT 저장에서 adapter_model.safetensors는 추가 Weight, adapter_config.json은 종류·rank·적용 대상 등의 설정이다. Base 전체가 그 안에 들어 있다고 가정하지 않는다. 다른 모듈도 학습/저장하도록 설정하면 내용이 달라질 수 있다.

| 보관 대상 | 이번에 확인할 내용 | 빠지면 생기는 문제 |
|---|---|---|
| Base | 모델 ID와 고정 Revision | 같은 이름의 다른 Weight를 읽을 수 있음 |
| Tokenizer·Chat Template | Revision·입력 렌더링·특수 Token | 같은 질문도 다른 Token 입력이 됨 |
| Adapter | 구성·Weight 파일·해시 | 어떤 갱신을 붙였는지 재현 불가 |
| 학습 기준 | 자료/분리·설정·초기 상태·Step/노출량·코드/환경 | 결과를 만든 조건 확인 불가 |
| 평가와 제한 | 실제 실패·자원·실행/미실행 | 쓸 수 있는 범위를 과장하기 쉬움 |

### 새 프로세스에서 같은 출력이 나오는지 확인하기

훈련이 끝난 메모리의 model로 다시 생성하면 디스크에 저장한 파일이 정상인지 확인하지 못한다. 별도 Python 프로세스가 같은 Base와 Tokenizer·Adapter를 읽고 model.eval()과 greedy 생성 설정을 맞춘 뒤 고정 입력을 실행해야 한다. 가능하면 문자열뿐 아니라 생성 Token ID도 비교한다.

기존 실행은 두 Adapter를 새 프로세스에서 각각 읽어 Test 첫 질문의 Token ID 일치를 확인했다. 요청 가드의 HTTP 시도는 0회였다. 다만 첫 질문 하나의 재현이며 다른 장비·Runtime·모든 입력의 동일성을 보장하지 않는다. 특히 seed의 첫 응답은 claims가 없어 계약에 실패했는데 **그 잘못된 응답도 재로드 후 똑같이 나왔다.** 재현 성공과 답변 품질 성공이 서로 다름을 직접 보여준다.

저장 기록을 읽어 token_ids_equal=True를 확인하는 것과 본인이 지금 모델 파일을 읽어 재현하는 것도 구분한다. Git의 JSON에는 해시와 생성 기록이 있지만 실제 모델/Optimizer 바이너리가 들어 있지 않다. 저장된 해시를 읽는 활동만으로 현재 로컬 파일의 해시가 맞다고 보고하지 않는다.

### 추론 재로드와 중단 후 훈련 재개

추론에는 Adapter Weight를 읽어 답을 만들면 된다. 중단 직전 학습을 잇기 위해서는 Optimizer 상태, 난수 상태, 다음에 볼 행의 순서와 완료 Step도 맞아야 한다. Adapter만 읽어 새 Optimizer로 시작하는 것은 같은 훈련을 정확히 이어 간 것과 다르다.

현재 Runner는 Step별 디렉터리에 Adapter·Optimizer/난수 상태를 쓴 뒤 완료 포인터를 바꾼다. 재개할 때 설정·자료·코드·환경이 바뀌면 새 폴더를 요구한다. 기존 관측 실행 후 체크포인트 저장 방식이 보완되어 게시 코드와 당시 실행 코드 해시가 다르다. 따라서 과거 관측 폴더에 현재 코드로 resume하면 거부되는 것이 정상이다. 작은 무작위 모델의 중단/재개 검사는 실제 Qwen 훈련의 중단 실험과도 구분한다.

Adapter를 Base에 병합하는 것, GGUF/Ollama 등 다른 형식/Runtime으로 변환하는 것은 또 다른 작업이다. 추론 재로드 통과만으로 변환·배포까지 완료했다고 하지 않는다.

### 결과 Card는 다른 사람이 사용할 범위를 알려주는 문서다

Model Card를 읽던 사람이 이제 작성자가 된다. “학습 완료” 한 줄 대신 무엇을 바꾸려 했는지, 무엇으로 학습했고 무엇을 실패했는지 적는다. 이번 결과라면 가상 규정 자료·같은 AI 작성자의 라벨/검수, 원본 20/증강 28·한 Seed 28 Step, CPU float32 LoRA와 실제 설정, 낮아진 Loss와 남은 의미/Agent 실패, 첫 사례 재로드, QLoRA·다른 Runtime·독립 검수 미완료를 포함한다. Base·데이터의 사용 조건도 출처에서 확인해 함께 남긴다. 성능 채택을 승인한 Model Card로 쓰지 않는다.

**확인 질문**

1. Adapter 파일만 있고 Base Revision·Template이 없으면 어떤 재현 문제가 생길 수 있는가?
2. 새 프로세스에서 Token ID가 일치해도 왜 정답 품질을 보장하지 않는가? 이번 실제 반례는 무엇인가?
3. Adapter만 읽고 새 Optimizer를 만들면 중단 직전 훈련을 같은 상태로 재개했다고 할 수 있는가?

[연결 실습](../../practice/document-assistant/L7.md)에서 계산·저장 기록·실패 응답·재로드를 구분해 확인한다. [훈련 수업 해설](training-teacher-guide.md)은 질문별 판단 근거를 제공한다.

공식 참고: [고정 PEFT 계열의 LoRA 설정](https://huggingface.co/docs/peft/v0.17.0/package_reference/lora), [QLoRA 논문](https://arxiv.org/abs/2305.14314), [양자화 준비 절차](https://huggingface.co/docs/peft/v0.17.0/developer_guides/quantization), [Adapter 체크포인트](https://huggingface.co/docs/peft/v0.17.0/developer_guides/checkpoint), [bitsandbytes 장비/설치](https://huggingface.co/docs/bitsandbytes/main/en/installation). 장비 지원 문서는 확인 시점의 버전을 기록하며 최신 메뉴/API와 실습의 PEFT 0.17.1·Transformers 4.57.1을 혼용하지 않는다.
