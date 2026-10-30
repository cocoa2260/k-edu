# 강의 하나를 분석해 본 결과

**대상: Phase2-02 「AI·머신러닝·딥러닝 개요」**

기초 정의를 다시 가르치는 부분은 줄이고, 데이터·평가를 설계하는 내용에 무게를 옮기는 것을 추천한다. **강의를 통째로 삭제하자는 결론은 아니다.** 아래 내용은 개편 제안이며 원문은 수정하지 않았다.

| 지금의 내용 | 추천하는 처리 |
|---|---|
| AI·ML·DL 정의, 규칙 대 학습, Training·Inference, Loss·Parameter | Phase1을 짧게 연결하고 평가 문제로 확장 |
| 데이터 분리, 과적합, 누수, 평가 지표, 전체 Pipeline 설계 | 핵심 내용으로 보존 |
| 신경망 층·Activation, 학습 신호 구분 | 앞선 설명을 인정하고 새 원리만 차별화 |
| CNN·RNN·Transformer·Diffusion | Phase1의 다른 교시와 추가 비교 후 배치 결정 |

## 1. 실제로 확인한 범위

- 원본 커밋: [bc58756](https://github.com/cocoa2260/k-edu/commit/bc58756866cd6bdee20c102fb54340f21e65ad56) — 실행 시작 시 브랜치와 일치.
- 대상 1개 파일 1,693줄과 Phase1 비교 3개 파일 전체를 읽었다. 아래 38개 구간으로 대상 전체를 추적했다.
- Phase1 전체, Phase2의 다른 과목, 별도 Q&A 파일의 전수 분석은 이번 범위에 포함되지 않는다.
- 코드 실행·Ollama·RAG·Multi-Agent·교육장 하드웨어 검증은 수행하지 않았다. 대상의 Practice는 코드 없는 설계 활동이다.
- 이전 ZIP 기준 운영 문서보다 현재 대화에서 정한 GitHub 원본·작업 범위를 적용했다.

| ID | 비교 자료 | 줄 수 |
|---|---|---:|
| S01 | [Day1_02_AI_전체_지도_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 557 |
| S02 | [Day1_03_일반_프로그램과_AI의_차이_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 632 |
| S03 | [Day2_03_AI_Model과_Parameter_Training과_Inference_강의용_v0.2.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md) | 825 |
| S04 | [AI 머신러닝 딥러닝 개요_강의용.md](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md) | 1693 |

## 2. 왜 이렇게 판단했는가

중복은 문장 복사 여부만으로 판단하지 않았다. **같은 개념을 같은 수준에서 다시 설명하는지**, 다른 원리·판단·활동으로 확장하는지 나눴다. 예를 들어 집값 표는 수치가 다르므로 동일 데이터 복사가 아니지만, Feature·Label을 가르치는 예시 구조가 반복된다.

Phase1의 Loss 수업은 이미 PyTorch로 Gradient 계산과 Parameter 갱신을 구분하고 값을 비교한다. Phase2에서 이 용어를 다시 정의하는 것만으로는 심화가 되지 않는다. 반면 Phase1에서 예고만 한 평가를 데이터 분리·누수·업무 오류 비용으로 설명하는 구간은 보존해야 한다.

## 3. 원문 안에서 함께 다듬을 부분

1. **요약 그림의 분류 기준:** S04 L910–915의 구분 설명과 L1187–1204의 나무 그림이 맞지 않는다. 학습 신호와 모델 구조를 다른 축으로 보여줄 필요가 있다.
2. **“정답만 제공하면”이라는 단순화:** S04 L768–788과 L1674–1676의 주의사항을 일관되게 연결해야 한다.
3. **보강 학습이 뒤에 붙은 구성:** 다음 강의 안내(L1056, L1371) 뒤에도 핵심 평가 내용이 계속된다. 평가를 부록처럼 읽지 않도록 본문 흐름에 배치하는 편이 좋다.
4. **실습의 실물:** 6행 Dataset을 쓰라는 지시는 있지만 본문의 아파트 표는 한 행이다. 후속 제작에서는 실제 표와 강사용 판별 예시가 필요하다.
5. **Transfer Learning의 표현 경계:** Prompt·RAG까지 묶은 L1550은 학습/추론 구분과 연결해 읽게 해야 한다. 엄밀한 용어 범위는 별도 기술 검증 대상으로 남겼다.

## 4. 남길 내용을 잃지 않는 구성 제안

다음은 이 강의의 개편 방향을 검토하기 위한 배치안이다. 전체 목차·과목명·교육시간 확정이나 강의안 작성은 아직 하지 않는다.

| 순서 | 학생이 할 일 | 가져올 기존 내용 | 새로 확인할 결과 |
|---|---|---|---|
| 1 | 이미 배운 용어를 짧게 점검 | F01·F02·F07·F08·F14·F16의 Phase1 연결 | 정의를 다시 배우는 대신 평가할 문제를 정함 |
| 2 | 입력·정답·분할을 설계 | F14·F15·F18·F21 | 미래 정보와 복제 데이터가 평가를 오염시키는지 설명 |
| 3 | 학습 점수와 새 데이터 점수를 비교 | F09·F16·F17 | Loss 감소와 Generalization을 다른 판단으로 구별 |
| 4 | 실수의 피해와 지표를 선택 | F12·F19·F22 | Precision/Recall 선택 이유를 업무와 연결 |
| 5 | 전체 Pipeline과 후속 기술을 연결 | F07·F20·F21 | 학습·추론·검색·검증 책임을 구분한 설계표 제출 |

**별도 보존 메모:** F04의 Activation·여러 층, F03의 Representation, F05의 비지도·강화·자기지도 구분은 이 5개 평가 활동에 억지로 끼워 넣지 않는다. 전체 목차 설계 때 신경망·학습 원리를 다루는 위치에 명시적으로 보존한다. F06의 구조별 설명은 추가 비교 전까지 유지 위치를 확정하지 않는다.

기존 긴급 메일 과제를 활용한다면, “규칙 세 개 쓰기”에서 끝내지 않고 **분류 시점에 알 수 없는 입력 찾기 → 유사 메일의 분할 결정 → 놓침과 오탐 중 큰 피해 선택 → 지표 선택 이유 설명**까지 제출하게 하는 방향이 적절하다. 현재 새 실습을 구현하거나 실행한 것은 아니다.

## 5. 이번 반복 검토에서 달라진 것

초안 뒤 검토에서 근거 연결 누락 1건과 보고서 설명 보완 3건을 발견해 한 번 보완했다. 근거 연결은 F03에 원문 주의사항 구간을 추가해 바로잡았다. 보고서에서는 우선, 유지할 내용을 어디에 남길지 연결표가 없어 제안만 보고 편집하면 Activation·학습 방식 설명이 빠질 수 있었다. 다음으로, 학습 활동의 순서를 구체화했고, 추가 확인이 필요한 교육 배치와 기술 용어 검증을 서로 다른 후속 작업으로 명확히 구별할 필요가 있었다.

최종안에는 위 보존·배치 연결표와 아래 판단 대기 항목을 추가했다. 초안의 원문 근거와 분석 결론을 뒤집거나 원문을 바꾸지는 않았다. 독립 모델·독립 Runner 검증 또는 시간 절감 효과를 입증한 실험은 아니다.

## 6. 결과를 보고 결정할 부분

- **추천 방향:** 기초 재설명을 줄이고 데이터·평가 중심으로 이 강의를 재구성한다.
- **추가 비교:** CNN·RNN·Transformer의 배치는 Phase1 Day1 4교시 본문까지 확인한 뒤 결정한다. 이번 비교 파일에 예고가 있다는 이유만으로 그 내용까지 읽었다고 처리하지 않았다.
- **기술 확인:** Transfer Learning과 Prompt/RAG 표현 경계는 외부 공식 원문을 확인하는 별도 기술 검토 대상이다. 사용자 취향으로 결정할 문제가 아니다.
- **교육적 선택:** 별도 과목 유지/다른 과목으로 통합, 최종 과목명·순서·시수는 전체 분석 뒤 결정한다. 지금 확정하거나 반영하지 않았다.
- **이번 종료점:** 한 과목의 분석 결과 제출. 다른 과목 분석과 실제 강의안 수정은 아직 시작하지 않았다.

## 상세 근거 — 검토용 부록

아래 표의 신규는 **지정 비교 3개 파일 대비**를 뜻한다. 전체 Phase1에서 처음 등장한다는 의미가 아니다. 동일 코드가 복사되었다는 판정은 없으며 대상에는 실행 가능한 Python 코드 블록이 없다.

| ID | 개념 | 관계 | 권고 | 원문 / 비교 근거 |
|---|---|---|---|---|
| F01 | AI・ML・DL 포함 관계와 첫 정의 | similar_explanation | 짧게 연결 | [S04 L131–197](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L131-L197) · [S04 L241–398](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L241-L398) · [S01 L35–58](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L35-L58) · [S01 L181–226](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L181-L226) |
| F02 | 규칙 작성과 데이터 학습의 차이 — 과목 내부 재설명 | similar_explanation | 짧게 연결 | [S04 L198–240](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L198-L240) · [S04 L399–479](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L399-L479) · [S04 L590–719](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L590-L719) · [S02 L28–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L28-L120) |
| F03 | Feature Engineering과 Representation Learning | partial_overlap | 차별화 | [S04 L355–398](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L355-L398) · [S04 L720–791](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L720-L791) · [S04 L1672–1676](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1672-L1676) · [S02 L161–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L161-L165) · [S01 L211–224](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L211-L224) |
| F04 | 신경망 한 층: Weight·Bias·Activation·역전파 | partial_overlap | 차별화 | [S04 L480–561](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L480-L561) · [S03 L69–103](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L69-L103) · [S03 L148–230](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L230) · [S03 L321–356](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L356) |
| F05 | 지도·비지도·강화학습과 자기지도 언급 | partial_overlap | 유지 | [S04 L792–907](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L792-L907) · [S02 L104–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L104-L120) |
| F06 | CNN·RNN·Transformer·Diffusion과 발전 흐름 | scope_limited | 판단 보류 | [S04 L562–589](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L562-L589) · [S04 L908–1080](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L908-L1080) · [S02 L612–618](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L612-L618) |
| F07 | Training·Inference 정의와 Prompt/RAG의 위치 | partial_overlap | 짧게 연결 | [S04 L1081–1132](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1081-L1132) · [S02 L213–274](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L213-L274) · [S03 L573–599](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L573-L599) |
| F08 | Classification과 Regression | similar_explanation | 짧게 연결 | [S04 L1133–1162](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1133-L1162) · [S02 L152–159](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L152-L159) · [S01 L80–114](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L80-L114) |
| F09 | Generalization | deeper_treatment | 유지 | [S04 L1163–1182](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1163-L1182) · [S02 L205–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L205-L209) · [S03 L183–185](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L183-L185) · [S03 L721–723](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L721-L723) |
| F10 | 관계도 안에서 분류 기준 혼합 | internal_inconsistency | 차별화 | [S04 L1183–1215](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1183-L1215) · [S04 L908–915](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L908-L915) |
| F11 | 분야별 적용 예시 | similar_explanation | 짧게 연결 | [S04 L1219–1238](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1219-L1238) · [S01 L74–179](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L74-L179) · [S01 L433–471](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L433-L471) |
| F12 | 긴급 메일: Rule 대 ML 설계 활동 | partial_overlap | 차별화 | [S04 L1240–1291](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1240-L1291) · [S02 L77–120](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L77-L120) · [S02 L480–539](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L480-L539) |
| F13 | 요약·이해도 질문·조기 다음 단원 안내 | partial_overlap | 차별화 | [S04 L1292–1347](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1292-L1347) · [S04 L1056–1080](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1056-L1080) · [S04 L1371–1375](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1371-L1375) · [S01 L475–523](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_02_AI_%EC%A0%84%EC%B2%B4_%EC%A7%80%EB%8F%84_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L475-L523) · [S02 L543–618](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L543-L618) |
| F14 | Sample·Feature·Label — 집값 사례 재사용 | partial_overlap | 짧게 연결 | [S04 L1389–1431](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1389-L1431) · [S02 L124–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L165) · [S02 L169–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L169-L209) |
| F15 | Train·Validation·Test 분리 | new_within_scope | 유지 | [S04 L1432–1452](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1432-L1452) |
| F16 | Loss·Optimization·Parameter·Hyperparameter | similar_explanation | 짧게 연결 | [S04 L1453–1478](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1453-L1478) · [S03 L148–248](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L148-L248) · [S03 L321–356](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L321-L356) · [S03 L660–673](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L660-L673) |
| F17 | Underfitting·Overfitting | deeper_treatment | 유지 | [S04 L1479–1501](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1479-L1501) · [S02 L205–209](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L205-L209) · [S03 L183–185](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day2/Day2_03_AI_Model%EA%B3%BC_Parameter_Training%EA%B3%BC_Inference_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L183-L185) |
| F18 | Data Leakage | new_within_scope | 유지 | [S04 L1502–1517](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1502-L1517) |
| F19 | Accuracy·Precision·Recall·F1과 다층 평가 | new_within_scope | 유지 | [S04 L1518–1545](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1518-L1545) |
| F20 | Self-supervised·Transfer와 Prompt/RAG 연결 | partial_overlap | 차별화 | [S04 L1546–1561](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1546-L1561) · [S04 L1081–1128](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1081-L1128) · [S02 L235–274](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L235-L274) |
| F21 | 데이터 책임 나누기·전체 Pipeline 설계 활동 | deeper_treatment | 유지 | [S04 L1562–1635](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1562-L1635) · [S02 L124–165](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L124-L165) · [S02 L480–539](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/00.%20Phase1_Theoretical/04.%20GPT,%20Ollama,%20Gemma/Day1/Day1_03_%EC%9D%BC%EB%B0%98_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%EA%B3%BC_AI%EC%9D%98_%EC%B0%A8%EC%9D%B4_%EA%B0%95%EC%9D%98%EC%9A%A9_v0.2.md#L480-L539) |
| F22 | 보강 요약·확인 활동·실무 팁·주의사항 | mixed_recap_and_application | 유지 | [S04 L1636–1680](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1636-L1680) |
| F23 | 개요·학습 지도·Wiki·참고 안내 | metadata_and_orientation | 차별화 | [S04 L1–130](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1-L130) · [S04 L1348–1376](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1348-L1376) · [S04 L1377–1388](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1377-L1388) · [S04 L1681–1693](https://github.com/cocoa2260/k-edu/blob/bc58756866cd6bdee20c102fb54340f21e65ad56/academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/01.%20Phase2_AI/02.%20AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94/AI%20%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%20%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EA%B0%9C%EC%9A%94_%EA%B0%95%EC%9D%98%EC%9A%A9.md#L1681-L1693) |

### F01. AI・ML・DL 포함 관계와 첫 정의

서로 다른 자동차·운동 비유를 추가하지만 도달 목표는 Phase1의 포함 관계 설명과 같다. 같은 개념의 반복이며 문장 전체가 동일하다는 뜻은 아니다.

**보존·확장할 성과:** ML의 Parameter 학습, DL의 Representation이라는 연결은 남기되 기초 정의 자체는 새 성과가 아니다.

### F02. 규칙 작성과 데이터 학습의 차이 — 과목 내부 재설명

Phase1의 배송비·생산 사진과 Phase2의 사과·에어컨·얼굴·고양이는 소재가 다르지만 사람이 규칙을 쓰는가 데이터로 학습하는가라는 설명 구조가 같다. S04 안에서도 세 차례 재설명된다.

**보존·확장할 성과:** 새 성과 없이 규칙의 한계와 데이터 학습을 반복하는 구간이 중심이다.

### F03. Feature Engineering과 Representation Learning

기초 용어를 다시 길게 설명하기보다 입력 특징과 학습된 표현의 차이를 드러내야 한다. S04 L768의 정답만 제공하면 된다는 문장은 같은 파일 L1675–1676의 설계·전처리 주의와 긴장된다.

**보존·확장할 성과:** 복잡한 입력에서 내부 표현을 학습한다는 연결. Phase1은 원리의 상세 설명을 후속 단원으로 남겨 두었다.

### F04. 신경망 한 층: Weight·Bias·Activation·역전파

Weight·Bias·Loss·Gradient·갱신을 전부 신규로 취급하면 안 된다. Phase1의 선형 모델 실습을 짧게 연결하고 Activation과 여러 층의 차이에 설명을 집중한다.

**보존·확장할 성과:** Activation으로 비선형 변환을 더하고 여러 층의 표현으로 확장하는 부분은 지정 비교 자료의 선형 모델보다 확장된다.

### F05. 지도·비지도·강화학습과 자기지도 언급

지도학습의 재정의는 연결 수준으로 줄이고 비지도·강화학습 및 자기지도와의 구분을 남긴다. 딥러닝의 상위/하위 분류와 학습 신호의 분류를 섞지 않아야 한다.

**보존·확장할 성과:** 정답 Label·데이터 구조·Reward를 학습 신호 기준으로 구분하는 것은 지정 비교 자료보다 자세하다.

### F06. CNN·RNN·Transformer·Diffusion과 발전 흐름

Phase1 Day1 4교시는 이번 입력에 포함되지 않았다. 이 구간이 Phase2 전체의 고유 내용이라는 판정과 최종 배치는 보류한다. 본문에서 분류 기준을 나누는 L910–915는 뒤의 관계도 검토 근거로 사용한다.

**보존·확장할 성과:** 지정 비교 자료에는 구조별 상세 설명이 없으나 S02가 다음 4교시에 CNN·RNN·Transformer를 다룬다고 명시한다.

### F07. Training·Inference 정의와 Prompt/RAG의 위치

정의와 학습 흐름도는 이미 Phase1에 있고 S03에는 Parameter 불변 확인 코드까지 있다. S04 L1123–1128의 후속 기술 연결은 따로 보존한다.

**보존·확장할 성과:** Pre-training·Fine-tuning은 학습, Prompt·RAG는 추론 입력 보강이라는 연결표는 후속 과목의 경계를 묶어 준다.

### F08. Classification과 Regression

스팸·집값 사례는 Phase1에도 등장한다. 전면 재정의보다 평가 지표를 왜 다르게 선택하는지 연결한다.

**보존·확장할 성과:** 단순 범주/숫자 판별만으로는 새로운 성과가 없다. 출력과 Metric 선택의 연결이 확장점이다.

### F09. Generalization

용어 최초 등장 여부와 학습 깊이를 분리한다. Phase1의 예고·주의가 있다는 이유로 평가 구간을 삭제하면 고유 성과를 잃는다.

**보존·확장할 성과:** 기존의 새 입력에서도 잘 작동해야 한다는 주의를 데이터 분리·과적합·누수·평가로 실질적으로 판단하게 한다.

### F10. 관계도 안에서 분류 기준 혼합

L1194–1198은 지도·비지도·강화학습과 딥러닝을 나란히 놓는다. L1200–1203은 CNN·RNN·Transformer와 Diffusion을 나란히 놓는다. 앞의 L910–915가 같은 기준의 형제 기술로 외우지 말라고 한 설명과 요약 그림의 표현이 맞지 않는다. 외부 기술 조사 없이 확인한 문서 내부 표현 불일치다.

**보존·확장할 성과:** 학습 신호의 분류와 신경망 구조, 생성 접근을 서로 다른 축으로 읽는다.

### F11. 분야별 적용 예시

스팸·수요·추천·인식·생성 등 문제 목록 나열은 Phase1에서 충분히 다룬 역할과 겹친다. 동일한 코드 복사라고 판정하지 않는다.

**보존·확장할 성과:** 새 예시 분류 자체보다 같은 업무의 평가 기준을 설명하는 방향으로 활용할 수 있다.

### F12. 긴급 메일: Rule 대 ML 설계 활동

규칙 세 개와 예외 세 개만 다시 만드는 활동은 기존 책임 구분과 유사하다. 미래 정보 사용 여부·오류 비용·지표 선택을 제출 결과로 삼으면 새 성과가 생긴다. 코드가 없는 설계 활동이다.

**보존·확장할 성과:** 예측 시점에 없는 Feature 배제(L1283), 누락과 오탐의 피해 비교(L1288)는 평가로 확장한다.

### F13. 요약·이해도 질문·조기 다음 단원 안내

포함 관계·규칙 대 학습·학습 대 추론을 다시 묻는 문항과 일반화 질문이 혼재한다. 다음 강의 안내가 보강 학습보다 앞서 나타나 평가가 부록처럼 읽힐 수 있다.

**보존·확장할 성과:** 평가 근거를 설명하는 문항은 유지하고 이미 배운 정의 확인은 진입 점검으로 모은다.

### F14. Sample·Feature·Label — 집값 사례 재사용

집/아파트의 면적·방 수·가격 표는 수치가 다르지만 같은 도메인·설명 구조를 반복한다. Sample이라는 단어 자체를 배운 적 없다고 단정하지 않고, 비교 자료에 사례/행 단위의 설명이 있음을 인정한다.

**보존·확장할 성과:** 한 사례의 이름 Sample을 명시하고 미래 정보·정답 누수 판정으로 확장하는 부분을 남긴다.

### F15. Train·Validation·Test 분리

지정 비교 자료는 평가를 예고하나 세 데이터의 역할과 선택 오염을 구체적으로 가르치지 않는다. 비교 원문 전체를 읽은 범위 안의 신규 심화로 판단한다.

**보존·확장할 성과:** 학습·선택·최종평가의 책임을 구분하고 시간·사용자 그룹에 맞는 분할을 설계한다.

### F16. Loss·Optimization·Parameter·Hyperparameter

S03에 MSE·Gradient·SGD·Learning Rate·Parameter/Hyperparameter·갱신 실습·변경 활동까지 이미 있다. S04의 추상 흐름도를 새로운 심화 실습이라고 볼 수 없다.

**보존·확장할 성과:** Loss를 낮추는 것과 Validation 기준으로 설정을 선택하는 것의 차이로 확장해야 한다.

### F17. Underfitting·Overfitting

Phase1은 과적합을 후속 과목으로 예고한다. S04에는 비교 양상과 데이터·복잡도·Regularization·Early Stopping의 대응 관점이 있다.

**보존·확장할 성과:** Train과 Validation의 성능 양상을 읽고 과소/과적합을 구분한다.

### F18. Data Leakage

퇴사 처리 완료일, 문서 복사본, RAG 정답 고정 사례와 점검 질문이 실제로 이미 있다. 누수 설명이 없다고 보고하거나 새로 전부 만들어야 한다고 제안하면 안 된다.

**보존·확장할 성과:** 미래 정보·유사 복제·전처리·Test 반복 선택·평가 정답 노출을 확인한다.

### F19. Accuracy·Precision·Recall·F1과 다층 평가

희귀 양성 사례, 정상 메일의 오분류 피해, 모델·검색·시스템·사람 평가의 구분을 이미 포함한다. 다만 구체적인 계산표와 실행 결과까지 있는 것은 아니다.

**보존·확장할 성과:** 높은 Accuracy가 목적 달성을 보장하지 않는 이유와 업무 피해에 맞는 Metric을 설명한다.

### F20. Self-supervised·Transfer와 Prompt/RAG 연결

Self-supervised 설명은 지정 비교 범위보다 확장된다. L1550은 Transfer Learning, Fine-tuning, Prompt/RAG를 한 문맥에 묶는다. L1123–1128 및 S02의 학습/추론 경계와 연결해 Parameter 갱신 유무를 명시할 필요가 있다. 용어의 엄밀한 범위는 별도 기술 검증 대상으로 남긴다.

**보존·확장할 성과:** 데이터 자체의 학습 신호와 사전학습 모델 재사용을 연결한다.

### F21. 데이터 책임 나누기·전체 Pipeline 설계 활동

설계 활동은 이미 있다. 모델 학습 실행 코드가 아니라 종이/Markdown 과제다. 작은 Dataset은 6행으로 확장하라고만 쓰여 있고 실제 본문 표는 1행(L1393–1395)이라 교사용 완성 표·정답 예시 보완이 필요하다.

**보존·확장할 성과:** 분할·누수·Metric·Failure Cost·운영 Inference를 하나의 제출물에 연결한다.

### F22. 보강 요약·확인 활동·실무 팁·주의사항

평가 관련 질문과 주의를 보존한다. 같은 파일의 기존 정의를 재설명하는 부분은 체크리스트로 모을 수 있다. 전체 반복이라는 이유로 활동까지 삭제하지 않는다.

**보존·확장할 성과:** 데이터 분리·누수·오류 비용을 설명하고 배포 입력과 평가 조건의 차이를 확인한다.

### F23. 개요·학습 지도·Wiki·참고 안내

수업 본문과 운영 메타데이터를 구별한다. 반복 개요는 합칠 수 있으나 외부 링크 최신성·Wiki 실재 경로는 이번에 확인하지 않았다. 참고 링크를 읽었다거나 실행 검증에 사용했다고 표시하지 않는다.

**보존·확장할 성과:** 자료의 목표·연결·참고 위치를 안내한다.

## 전체 구간 확인표

| 구간 | 줄 | 내용 | 상태 | 연결 |
|---|---|---|---|---|
| B01 | 1–69 | Phase 2 — 02. AI / 머신러닝 / 딥러닝 개요 | 검토함 | F23 |
| B02 | 70–100 | [학습] AI / 머신러닝 / 딥러닝 개요 (Unit 1) | 검토함 | F23 |
| B03 | 101–130 | 이번 과목의 학습 지도 | 검토함 | F23 |
| B04 | 131–197 | ① 문제 이해 (Why) | 검토함 | F01 |
| B05 | 198–240 | 왜 이런 기술이 필요했을까? | 검토함 | F02 |
| B06 | 241–280 | ② 개념 이해 (Concept) | 검토함 | F01 |
| B07 | 281–354 | 머신러닝(Machine Learning) | 검토함 | F01 |
| B08 | 355–398 | 딥러닝(Deep Learning) | 검토함 | F01, F03 |
| B09 | 399–479 | ③ 구조와 원리 (Architecture / Principle) | 검토함 | F02 |
| B10 | 480–561 | 딥러닝의 동작 원리 | 검토함 | F04 |
| B11 | 562–589 | AI는 왜 계속 새로운 기술이 등장했을까? | 비교 불충분 | F06 |
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

## 검증과 한계

- 원본 4개의 Git Blob SHA, 인용 구간·짧은 발췌, 전체 줄 범위의 누락·겹침, 결과 형식, 고정 커밋 링크 및 보호 원본 불변을 자동 검사한다.
- 중복·교육적 판단은 같은 Work 세션에서 역할 지시를 나눠 검토했다. 독립 검토자의 결과라고 표현하지 않는다.
- 검사 복사본에는 잘못된 줄 번호, 평가 내용의 일괄 삭제, 실행하지 않은 모델 검증 완료를 넣어 검출을 확인한다. 이 통제 사례는 정상 초안에 실제로 있던 오류와 구분한다.
- Work 내부 Token·모델 호출·추론 설정 변경 내역은 노출되지 않아 측정하지 않았다. 단계별 추론 강도 자동 전환은 이번에 구현하거나 실행하지 않았다.
- 외부 URL의 현재 접속 성공과 기술 최신성, 학생의 실제 이해도·수업시간, 저사양 실행성은 미검증이다.
