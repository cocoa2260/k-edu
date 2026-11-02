# KEDU-PRODUCTION-020 · Transformer 내부 원리 5개 단원

**K2-02.U01~U05 강의·활동지·강사용 해설 작성과 합성 수치 검증을 마쳤다. 누적 자료는 66/70개, 남은 기초는 K2-03.U01~U04의 4개다. 실제 모델·독립 품질·수업 완료 수가 아니다.**

읽을 파일은 [강의](../../lessons/transformer-basics/lesson.md)다. 교육생은 [활동지](../../lessons/transformer-basics/worksheet.md)를 작성한다. [강사용 해설](../../lessons/transformer-basics/teacher-guide.md)은 선택 참고이며 실행 코드·JSON을 먼저 읽을 필요는 없다.

| 단원 | 작성한 내용·제출물 |
|---|---|
| K2-02.U01 | Weight·Bias·ReLU와 행벡터/Shape, 활성화 전후 Forward 계산 |
| K2-02.U02 | Q/K/V 투영·내적·√dₖ·행별 Softmax·Value 가중합과 Shape |
| K2-02.U03 | Multi-head 연결/투영·Residual·LayerNorm·FFN의 수치·역할, Pre/Post-LN 구분 |
| K2-02.U04 | 위치 없는 Attention의 순열 성질·Sinusoidal/RoPE 예시, Encoder/Decoder/Cross-Attention, Padding/Causal Mask |
| K2-02.U05 | 이동한 학습 목표·병렬 학습과 자기회귀 생성, Prefill/Decode/Cache 시점, KV 메모리 요인 |

## 직접 계산해 확인한 것

외부 의존성이 없는 [예제 검사기](../../practice/transformer-basics/check_examples.py)로 [합성 수치 자료](../../practice/transformer-basics/examples.json)를 계산했다. 수치는 학습된 모델에서 추출한 값이 아니다.

| 검사 | 확인 결과 |
|---|---|
| 한 층의 Forward | 활성화 전 [3,-1], ReLU 후 [3,0] |
| T3 Query의 Attention | 가중치 약 [0.2483,0.2483,0.5035], 출력 [1.5035,3.0070] |
| T2 Query의 Causal Mask | 미래 가중치 0, 출력 약 [0.6605,2.6790] |
| Block 구성 요소 | Head 연결/투영·Residual, 특성 축 LayerNorm, FFN 계산 일치. 전체 Block 실행은 아님 |
| 위치·Mask 경계 | Sinusoidal 0/1 위치·단순 RoPE 회전·위치/Mask 없는 순열 성질, PAD 제외와 미래 입력 차단 확인 |
| 한 층의 K/V 증분 재사용 | 처리한 Prefix 길이 3·4·5에서 전체 재계산의 마지막 출력과 Cache 계산이 일치. 이번 예제 최대 절대 차이 0 |
| KV 데이터 바이트 계산 | 가상 기본 64 KiB, 문맥/동시 시퀀스 각각 2배 128 KiB, KV Head만 줄인 경우 16 KiB |

행렬 차원·불규칙 행렬·모든 Key 차단·Mask 길이·Cache K/V 길이·Residual 크기·비유한 점수·0인 Cache 차원의 **8개 잘못된 입력을 거부**했다. 스케일링 생략, Softmax 뒤 가중치를 지우기만 하는 방법, 미래를 보는 비인과적 Attention의 차이도 반례로 확인했다. 계산 비교 허용 오차는 1e-9이며 강의 표는 읽기 좋게 반올림했다.

단원 성과·제출물·강사용 기준의 연결, 문서 상대 링크·JSON·66/70 집계와 사람용 Markdown에 코드 블록이 없는 것을 검사했다. Attention 가중치/어휘 확률, Causal Mask/권한, Cache/영구 기억, 별도 합성 예시/전체 모델을 구분하는 내용 검토는 같은 제작 세션에서 수행했다. 상세 결과·자료/코드 해시는 [validation.json](validation.json)에 있다.

## 미실행과 남은 검증

위 Cache 비교는 **위치 표현·정규화·FFN·언어 출력층 없는 단일 Head Attention**이다. 사전학습 모델 호출·모델 학습·Token 생성·속도/실제 VRAM 측정·배포 모델의 위치 사양 확인은 하지 않았다. 계산기 구현과 고정 수치의 일치는 독립 의미/수업 검증을 대신하지 않는다.

이전 앱·모델·훈련 코드와 기록을 보존했으며 해당 회귀 테스트는 다시 실행하지 않았다. QLoRA·기존 학습/답변 품질·Framework/MCP·일반 문서/Vision·실제 운영 채택·독립 강사/교육생 수업 게이트는 그대로 미완료다.

**다음은 K2-03 기초 4개 단원. 추천 추론 강도 High.** 학습 목표/Post-training, Logit에서 Token 선택, Parameter/Context/Memory/Retrieval, 환각·불확실성/시스템 평가를 연결한다. 기존 Hugging Face 3개 단원은 보존한다. 그다음에는 전체 자료의 연결과 독립 품질·수업 검증이 남는다.
