# Fine-tuning — 실제 갱신·평가·저장·다시 불러오기

K2-12.U05~U08 · 제작본 v0.1 · 2026-10-31

[데이터·입력 준비](lesson.md) 다음 강의다. [실제 실행 검토](../../reports/KEDU-PRODUCTION-010/RESULT.md)에서 실행한 것과 남은 것을 구분한다. 실행 코드는 Backend tools/lora_lab.py에 있다.

## K2-12.U05 LoRA 원리·설정·실제 훈련

LoRA는 Base Weight를 고정하고 작은 두 행렬의 곱으로 갱신을 더한다. 입력 d개·출력 k개의 Weight에 rank r을 사용하면 추가 행렬의 Parameter는 r(d+k)개다. 예를 들어 1024×1024 Weight에 r=4면 추가 8192개다. 모델 전체가 8192개라는 뜻은 아니다.

출력에 더하는 갱신은 보통 alpha/r로 조절한다. rank는 갱신 표현의 크기, alpha는 그 배율, dropout은 학습 중 적용하는 드롭 비율이다. target_modules는 어느 Layer에 적용할지 정한다. 이름만 입력하지 말고 실제 모델의 Layer 이름·모양·추가 Parameter 수를 확인한다.

이번 기준은 Qwen3-0.6B의 q_proj/v_proj, rank 4, alpha 8, dropout 0이다. Base는 CPU float32, 추가 Parameter만 AdamW로 갱신한다. 입력 label은 앞 실습의 assistant 정답~EOS이며 Validation/Test를 Optimizer에 넣지 않는다.

| 단계 | 확인할 증거 |
|---|---|
| 주입 | 실제 LoRA Layer와 학습 가능 Parameter 수 |
| Forward | 유한한 실제 모델 Loss |
| Backward | 추가 Parameter의 Gradient |
| Optimizer Step | 추가 Weight가 초기값에서 바뀜 |
| 동결 | Base requires_grad와 Optimizer 대상·동결 Weight 표본 |

첫 LoRA 행렬 중 하나가 0으로 초기화되면 첫 Step에서 모든 추가 행렬의 Gradient가 동시에 0이 아니어야 한다고 요구하는 것은 잘못이다. 실제 갱신과 이후 Gradient를 함께 본다. Base 표본 불변 검사는 전체 Weight 해시 검사를 대체하지 않는다.

이번에는 원본과 증강 조건 각각 4개 예제·4 Step만 사용한다. 전체 Train 20/28개를 충분히 학습한 비교가 아니다. **활동/제출:** Layer·Parameter·Gradient·실제 갱신 로그와 한 설정을 바꿀 때의 가설. **확인 질문:** trainable Parameter 수가 작으면 활성값 메모리도 항상 작을까?

## K2-12.U06 QLoRA·양자화와 자원 조건

QLoRA는 양자화한 동결 Base 위에서 추가 LoRA를 학습한다. 4-bit 추론만 실행한 것은 QLoRA 훈련이 아니다. NF4는 Weight 표현, 이중 양자화는 양자화 상수의 저장 부담을 줄이는 구성이다. 저장 정밀도와 실제 계산 dtype도 구분한다.

전체 메모리에는 Base 외에 활성값·Gradient·Optimizer 상태·임시 Tensor가 포함된다. 길이·배치·Gradient 누적·체크포인팅에 따라 달라진다. Paged Optimizer는 메모리 급증을 다루는 기법이지 모든 OOM을 없애는 장치가 아니다.

| 확인 대상 | 해석 |
|---|---|
| GPU·CPU와 backend | 공식 지원 목록과 실제 설치/연산을 구분 |
| NF4·double quant·계산 dtype | 서로 다른 설정이며 적합성 별도 확인 |
| 실제 메모리 | CPU RSS·GPU VRAM·프로세스 전체 최고값 구분 |
| 시간·배치·길이 | 같은 조건과 초기화/추론 시간을 구분 |

공식 bitsandbytes 문서는 CPU backend도 다룬다. CUDA가 없다는 사실만으로 QLoRA가 원천 불가능하다고 결론 내리지 않는다. 이번 실행은 CPU 일반 정밀도 LoRA를 선택했고 QLoRA backend의 학습·저장·재로드는 검증하지 않았다. GTX 1060 계열의 일부 연산 지원과 3GB에서 이 실습 전체를 실행할 수 있다는 판단도 다르다.

**활동/제출:** LoRA/QLoRA 구성표와 해당 장비의 실제 backend·메모리·실행/미실행 기록. **확인 질문:** Base 파일이 4분의 1로 줄면 전체 훈련 메모리도 반드시 4분의 1이 되는가?

## K2-12.U07 동일 기준 평가·실패 진단·선택 기법 비교

Validation으로 설정을 고른 뒤 고정 Test를 확인한다. Base·원본 학습·증강 학습은 같은 Template·생성 설정·평가 입력으로 비교한다. Loss 감소와 과제 해결은 다른 지표다. Teacher forcing Loss는 정답을 앞부분에 주고 다음 Token을 평가하며, 실제 생성은 모델 자신의 이전 출력도 입력으로 받는다.

이번에는 Validation/Test 각 10개의 예제별 평균 Loss와 Test 10개의 생성 원문을 기록한다. 예제별 평균을 다시 평균한 값이므로 긴 응답의 Token 수로 가중한 전체 Loss와도 다르다. JSON/인용 검사를 통과해도 숫자·조건·예외의 의미적 정답까지 증명되지 않는다. 잘린 응답은 출력 길이 상한과 함께 본다.

원본 조건의 4개와 증강 조건의 4개는 행동 비율과 질문 구성이 다르다. 같은 Step 수라도 정답 Token 노출량이 다르므로 이번 결과로 증강의 인과적 효과를 주장하지 않는다. 이후 전체 20/28개 학습·여러 Seed·노출량 통제·기존 18개 회귀·독립 검수를 추가해야 한다. Test를 보고 설정을 고르면 새 Test가 필요하다.

IA3나 DoRA는 선택 비교 후보이지 필수 전수 실험이 아니다. 비교한다면 Base·데이터·Token·Step·Seed·평가를 고정하고 추가 Parameter·메모리·시간 차이를 같이 남긴다. 이번에는 해당 대안을 훈련하지 않았다.

**활동/제출:** Loss와 실제 출력의 오류 분류·과적합/누수/라벨 오류 가설·회귀 계획. **확인 질문:** Loss가 조금 내려갔지만 올바른 답변이 없으면 개선을 채택할 수 있을까?

## K2-12.U08 Adapter 저장·새 프로세스 Reload·결과 Card

Adapter 파일에는 보통 전체 Base Weight가 들어 있지 않다. 같은 Base ID·Revision·Tokenizer·Template·PEFT 설정을 다시 맞춰야 한다. adapter_config와 adapter_model.safetensors만 다른 Base에 붙이면 된다고 가정하지 않는다.

같은 프로세스의 메모리 모델로 답한 것은 재로드 증거가 아니다. 저장 뒤 프로세스를 끝내고 새 Python 프로세스에서 Base와 Adapter를 읽어 고정 입력의 Token ID·출력을 비교한다. dropout을 끄고 eval 모드·greedy 설정·dtype를 맞춘다. 같아도 다른 장비·Runtime·양자화 변환의 호환성까지 확인한 것은 아니다.

| 저장할 것 | 이유 |
|---|---|
| Base Revision·Tokenizer/Template | 입력·Weight 기준 고정 |
| Adapter 설정·파일 해시 | 실제 훈련한 추가 Weight 식별 |
| Dataset·Split·학습량·Seed | 무엇을 학습했는지 재현 |
| 평가·실패·자원·한계 | 사용 가능한 범위를 판단 |

병합과 재로드도 다르다. Adapter를 Base에 병합하거나 GGUF/Ollama로 변환하는 것은 별도 검증 대상이다. 결과 Card에는 성공뿐 아니라 짧은 학습·공개된 소규모 평가·AI 작성 라벨·미검증 QLoRA·독립 검수 부재도 적는다.

**활동/제출:** 저장 Manifest·새 프로세스 비교·Model Card. **확인 질문:** Adapter 파일만 보관하고 Base Revision을 잃으면 무엇을 재현하기 어려울까?

공식 참고: [PEFT 구성·저장/로드](https://huggingface.co/docs/peft/v0.17.0/en/tutorial/peft_model_config), [LoRA](https://huggingface.co/docs/peft/en/package_reference/lora), [양자화·backend](https://huggingface.co/docs/transformers/v4.57.1/quantization/bitsandbytes). 실습은 설치 버전을 고정하며 최신 문서의 모든 옵션을 실행한 것은 아니다.
