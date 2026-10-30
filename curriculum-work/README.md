# K-Edu 교육과정 개편 — 현재 위치와 읽을 파일

**현재: RAG 4개 단원과 L4를 작성했다. 70개 중 28개 단원 자료 작성. 실제 검색·생성 경로는 실행했고 답변 품질은 채택 보류다.**

[RAG 강의](lessons/rag/lesson.md) · [실제 사례 검토](reports/KEDU-PRODUCTION-006/REVIEW.md) · [L4 실습](practice/document-assistant/L4.md) · [검증 범위](reports/KEDU-PRODUCTION-006/RESULT.md)


## 전체 구성안

**[전체 목차와 누적 실습 구성안 — CURRICULUM_PLAN.md](reports/KEDU-DESIGN-001/20261030T101518Z/CURRICULUM_PLAN.md)**

이번 보완은 구성안 상단의 Hugging Face 첫 방문·실제 화면 예시·PEFT 학습 깊이 표에서 볼 수 있다. 전체는 2번 목차표와 3번 누적 실습표를 보면 된다. 상세 단원·원문 이동·역할/상한·평가·제작 조건은 같은 문서의 접힌 부록에 있다. 실행 코드나 JSON 예시를 본문에 넣지 않았다.

추천은 Phase1 24교시 기반 유지, Phase2 본과목 14개와 시작 안내, 70개 학습 단위(시간 수 아님), 같은 앱의 Prompt·Context → Harness·Loop → 검색·RAG → Single-Agent → Multi-Agent 확장이다. 실제 Fine-tuning·Adapter Reload는 별도 실험, OCR·다중 문서 형식·보고서는 확장 경로로 연결했다.

| 순서 | 하는 일 | 현재 상태 |
|---|---|---|
| 1 | 강의 하나로 분석 방식을 시험 | 완료 |
| 2 | 결과를 보고 분석 방식 보완 | 완료 |
| 3 | 전체 강의 비교·분석 | 결과 보존 |
| 4 | 전체 목차·누적 실습 구성 결정 | v0.3을 첫 제작 묶음의 기준으로 사용 |
| 5 | 확정한 강의·실습 제작 및 검증 | 28개 단원 자료·실제 RAG 실행. 답변 품질 보류, 다음 Single-Agent/L5 |

구성안은 과목명·배치·범위의 추천이다. 기존 academy 원문·파일명은 유지한다. 새 강의와 누적 앱 L0~L4와 실제 검색·로컬 생성을 작성했다. RAG 답변 품질은 채택 보류이며 실제 훈련은 제작 전이다. 실제 모델·훈련·교육장 성능은 검증 게이트를 둔 후속 작업이다.

## 분석 근거와 과거 시범

- [3단계 전체 분석 검토본](reports/KEDU-ANALYSIS-001/20261030T080144Z/REVIEW.md)
- [Phase2-02 시범 — Day1 4교시 추가 비교 결과](reports/KEDU-PILOT-001/20261030T064535Z-r2/RESULT.md)

현재 구성안이 과거의 분석·검증 기록이나 원문을 덮어쓰지 않는다.

<details>
<summary>운영 담당자용 파일 안내 — 구성안 검토에 필수 아님</summary>

| 파일 | 역할 |
|---|---|
| [curriculum.json](reports/KEDU-DESIGN-001/20261030T101518Z/curriculum.json) | 실제 구성안 데이터. 과목/단원·선수 관계·누적 실습·역할/예산·평가·원문/성과 이동·검증 게이트 |
| [validation.json](reports/KEDU-DESIGN-001/20261030T101518Z/validation.json) | 정적 검사·오류 검출 사례·동일 Work의 의미 검토·보완 기록·미확정 사항 |
| [run.json](reports/KEDU-DESIGN-001/20261030T101518Z/run.json) | 이번 실행의 상태·시도/보완·체크포인트·게시 결과 |
| [KEDU-DESIGN-001.json](loop/tasks/KEDU-DESIGN-001.json) | 이번 4단계 작업 범위·제한·보호/출력 경로 |
| [check_design.py](loop/checks/check_design.py) | 구성안 데이터·선수 그래프·보존 성과·역할/예산·평가/미실행 상태의 정적 검사 코드. Usage는 파일 상단 참조 |
| [check_curriculum.py](loop/checks/check_curriculum.py) | 3단계 전체 분석 기록용 검사기 |
| [check_analysis.py](loop/checks/check_analysis.py) | 최초 시범 S04 전용 검사기 |
| [loop-spec.md](loop/loop-spec.md) | 최초 시범 전의 v0.1 설계 원본. 예시와 당시 미실행 상태는 현재 결과가 아님 |
| [prompts.md](loop/prompts.md) | 최초 시범의 역할별 지시. 전체 범용 Runner가 구현되었다는 뜻은 아님 |

표의 JSON은 설명용 예시가 아니라 해당 실행의 실제 구성 데이터/기록이다. 다만 그 안의 학습용 모델 호출 상한·Token 예산·Dataset 수량은 구현·실측 전의 설계값이다. 코드가 있다는 사실과 실제 검사 결과는 구분하고 후자는 validation.json을 확인한다.

4단계 검사는 구성안의 내부 정합성을 확인한다. 강의 수업 가능성·실제 모델 성능·훈련 가능성·교육장 처리량을 검증한 결과가 아니다. 의미 검토는 같은 Work 세션이며 독립 평가자가 아니다. 독립 자동 Runner·추론 강도 자동 전환도 이번 범위에 포함하지 않았다.

</details>
