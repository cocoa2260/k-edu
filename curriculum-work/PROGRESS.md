# 5단계 제작 현황과 이어서 할 일

**현재: K2-12.U01~U04 네 단원과 L7 Dataset·Token/label 준비 검증. 자료 70개 중 40개 작성. 실제 훈련·품질 개선은 미검증이다.**

[강의](lessons/fine-tuning/lesson.md) · [실제 검토](reports/KEDU-PRODUCTION-009/REVIEW.md) · [실습](practice/document-assistant/L7.md) · [결과](reports/KEDU-PRODUCTION-009/RESULT.md)

## 작업 전 추론 강도 안내 — 사용자 요청

강의 제작 완료까지 각 다음 작업을 시작하기 전에 **진행할 작업 / 추천 추론 강도 / 이유**를 짧게 알린다. 같은 강도를 유지하는 경우에도 다음 작업의 추천을 명시한다. 작업 중 복잡도가 달라져 상향을 추천할 때도 변경 이유를 알린다.

이 안내는 설정 변경을 수행했다는 뜻이 아니다. 실제 추론 설정은 사용자가 선택한다. 강도 안내만을 이유로 매 작업마다 승인 질문을 반복하지 않는다. 일반적인 작업 묶음은 이미 정한 강도와 범위 안에서 계속 진행하며, 상위 강도 적용이 꼭 필요한 작업은 필요한 이유와 다음 행동을 명확히 알린다.

**바로 다음 작업:** KEDU-PRODUCTION-010, K2-12.U05~U08 실제 LoRA 훈련·QLoRA 자원 조건·평가·Adapter 저장/새 프로세스 Reload. **추천: High.** Parameter/Gradient·메모리·평가·Reload를 연결해 확인해야 한다.

## 다음에 바로 할 일

같은 Base Revision과 새 finetuning-v1 Dataset을 고정해 G-TRAIN을 검사한다. Train 원본 20개와 증강 28개를 구분하고 Validation으로 설정을 고른 뒤 Test를 확인한다. 문장 틀·공개 평가 자료·동일 AI 작성/검수라는 제한을 유지한다. 데이터/Tokenizer 준비를 실제 훈련으로 표시하지 않는다. 실제 Optimizer Step·학습/검증 Loss·메모리/시간·저장/새 프로세스 Reload가 필요하다.

QLoRA는 호환 장비/백엔드 확인 후 실제 실행 여부를 기록한다. 추론 API·이론·가짜 로그로 훈련 완료를 대체하지 않는다. GTX 1060 3GB에서 된다고 가정하지 않는다. IA3/DoRA 선택 비교는 시간·환경이 허용할 때 같은 평가로 별도 기록한다.

## 이번 검증

원문 8가족·Seed 40개, 변형 후보 12개 중 8개 채택·4개 기각. 실제 Datasets 로드/filter/map·Arrow 저장/재로드·고정 Qwen Template/label 준비는 28/10/10 총 48개다. 271개 테스트 통과. 가짜 Logit의 Mask 검사는 실제 Qwen Loss가 아니다. Optimizer Step·모델 가중치 로드/생성·유료 API는 모두 0회다.

## 중단 후 재개

1. 이 파일과 [단원별 기록](curriculum/production-index.json), 같은 제작 브랜치의 최신 커밋을 확인한다.
2. 이전 결과·원문·평가 자료를 보존하고 완료한 준비를 전부 재분석하지 않는다.
3. finetuning-v1 내용/검수/코드/Tokenizer 해시와 환경을 먼저 맞춘다. 캐시가 없으면 고정 리비전만 다시 받는다.
4. 실제 실행·고정 검사·미실행을 분리하고 바뀐 범위만 검증한다. 바이너리 캐시/모델/Arrow는 Git에 넣지 않는다.

## 독립 미완료

L4/L5/L6 실제 과제·답변 품질, L0 실제 웹 생성·L1 다섯 조건 전체 비교, Framework Agent/MCP·실제 인증/지속 승인·강제 중단, 남은 기초/안내 단원, L8 OCR·L9 통합, 독립 수업/UI·교육생 장비/동시 실행은 미완료다. 40/70은 자료 작성 수이고 수업·품질 완료 수가 아니다.
