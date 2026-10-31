# Model Card — LoRA 소규모 실험 v1

Qwen/Qwen3-0.6B Revision c1899de289a04d12100db370d81485cdf75e47ca. CPU float32·PEFT 0.17.1. Base 이용 조건은 원 Model Card에서 확인한다. 운영 모델로 채택하지 않았다.

[실제 결과와 한계](../../reports/KEDU-PRODUCTION-010/RESULT.md). finetuning-v1의 고정 AI 작성 예제 중 조건별 4개만 학습했다. rank 4·alpha 8·q_proj/v_proj·dropout 0·AdamW 0.0002·4 Step·Seed 37. 전체 훈련/독립 품질·18개 회귀·QLoRA·병합/변환은 미검증이다. Base Weight는 포함하지 않고 Manifest의 정확한 Revision으로 불러온다.
