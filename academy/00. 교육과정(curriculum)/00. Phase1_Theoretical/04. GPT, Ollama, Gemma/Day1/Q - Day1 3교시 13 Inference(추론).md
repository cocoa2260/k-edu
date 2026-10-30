쉽게 말하면 Inference(추론)는 이미 학습이 끝난 모델에게 새로운 데이터를 주고 실제 결과를 얻는 과정입니다.

예를 들어 GPT에게 질문하는 상황을 생각하면 됩니다.

이미 학습된 GPT 모델

        +

"Transformer가 뭐야?"라는 새로운 Input

        ↓

Inference

        ↓

"Transformer는 ..."이라는 Output

즉,

- Training: 모델을 학습시키는 과정
- Inference: 학습된 모델을 실제로 사용하는 과정

Ollama에서 Gemma를 실행해서 질문하는 것도 Gemma를 새로 Training하는 것이 아니라, 이미 학습된 Gemma를 가져와 Inference하는 것입니다.

강의에서는 이렇게 정리하면 가장 쉽습니다.

Training은 모델을 만드는 과정이고, Inference는 만들어진 모델을 사용하는 과정이다.

그리고 Application 개발자의 관점에서는 대규모 모델을 직접 처음부터 Training하는 경우보다, GPT나 Gemma처럼 이미 학습된 모델을 가져와 Inference에 활용하여 서비스를 만드는 경우가 훨씬 일반적이라고 연결하면 됩니다.