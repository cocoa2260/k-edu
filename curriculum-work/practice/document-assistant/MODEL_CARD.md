# Model Card — 전체 Train 포함 LoRA 실험

Qwen/Qwen3-0.6B Revision c1899de289a04d12100db370d81485cdf75e47ca. 원본 20개/증강 28개를 포함한 조건별 28 Step, Seed 37, rank 4·alpha 8·dropout 0·q_proj/v_proj·CPU float32·AdamW 0.0002. Base 모델 이용 조건은 원 Card에서 확인한다.

[실제 학습·회귀·선택·재로드 결과](../../reports/KEDU-PRODUCTION-011/RESULT.md). Validation으로 후보를 고정한 뒤 Test·18개 Agent 회귀를 실행했다. 공개 소규모 자료·단일 Seed·다른 Token 노출량이라는 한계가 있다. 품질·독립 수업·QLoRA·병합/Runtime 변환은 미검증이며 공통 운영 모델로 교체하지 않았다. 이전 4 Step 실험은 reports/KEDU-PRODUCTION-010에 보존한다.
