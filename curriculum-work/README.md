# K-Edu 교육과정 개편 — 현재 위치와 읽을 파일

**3단계: 전체 강의 비교·분석 결과를 검토할 차례다.**

## 먼저 읽을 문서 한 개

**[전체 분석 검토본 — REVIEW.md](reports/KEDU-ANALYSIS-001/20261030T080144Z/REVIEW.md)**

앞의 1~4에는 핵심 판단, Phase2 13과목의 추천 역할, Prompt·Context·Harness·Loop·Multi-Agent의 현재 수준, 다음 결정 사항이 있다. 상세 근거와 주교안·Q&A별 처리는 같은 문서의 접힌 부록에서 볼 수 있다.

| 순서 | 하는 일 | 현재 상태 |
|---|---|---|
| 1 | 강의 하나로 분석 방식을 시험 | 완료 |
| 2 | 결과를 보고 분석 방식 보완 | 완료 |
| 3 | 전체 강의 비교·분석 | 분석·기록 검사 완료, 사용자 검토 대기 |
| 4 | 전체 목차·누적 실습 구성 결정 | 진행 전 |
| 5 | 확정한 강의·실습 제작 및 검증 | 진행 전 |

분석 결과를 보관한 상태다. 강의 본문·파일명·최종 목차·시수는 변경하지 않았다. 과목명과 재배치는 아직 제안이다.

## 과거 시범 결과

[Phase2-02 시범 — Day1 4교시 추가 비교 결과](reports/KEDU-PILOT-001/20261030T064535Z-r2/RESULT.md)

과거 시범의 초안·보완 기록을 그대로 보존했다. 최신 전체 분석의 결론은 위 REVIEW.md를 따른다.

<details>
<summary>운영 담당자용 파일 안내 — 결과 검토에 필수 아님</summary>

| 파일 | 역할 |
|---|---|
| [evidence.json](reports/KEDU-ANALYSIS-001/20261030T080144Z/evidence.json) | 실제 원문 버전·전체 파일 범위·35개 판단·근거·교안/Q&A 연결·수행 범위 |
| [validation.json](reports/KEDU-ANALYSIS-001/20261030T080144Z/validation.json) | 초안/보완본의 실제 검사 결과·순차 의미 검토·오류 검출 사례·남은 판단 |
| [run.json](reports/KEDU-ANALYSIS-001/20261030T080144Z/run.json) | 현재 실행 상태·시도/보완 횟수·체크포인트·기록 한계 |
| [KEDU-ANALYSIS-001.json](loop/tasks/KEDU-ANALYSIS-001.json) | 전체 분석의 실제 작업 범위·제한·출력 지시서 |
| [check_curriculum.py](loop/checks/check_curriculum.py) | 전체 분석 기록용 검사 코드. 실제 재현 명령은 파일의 Usage 참조 |
| [loop-spec.md](loop/loop-spec.md) | 최초 시범 전의 v0.1 설계 원본. 예시와 당시 미실행 상태는 현재 실행 결과가 아님 |
| [prompts.md](loop/prompts.md) | 최초 시범의 실제 역할별 지시. 전체 범용 Runner 구현을 의미하지 않음 |
| [check_analysis.py](loop/checks/check_analysis.py) | 최초 시범 S04 전용 검사기. 전체 자료 검사는 check_curriculum.py로 구분 |

표의 JSON은 설명용 예시가 아니라 해당 실행에서 사용하거나 작성한 기록이다. 검사 코드가 존재한다는 사실과 실제 검사 실행 결과는 구분하며, 후자는 validation.json을 확인한다.

전체 분석은 164개 텍스트 파일의 전체 구조·개념 검색 및 관련 원문 구간 대조다. 모든 문장·코드의 정확성, 외부 SDK의 현재성, 실제 모델 성능까지 승인한 검수가 아니다. 검사 재현에는 같은 기준의 academy 원문이 필요하다.

독립 자동 Runner, 단계별 추론 강도 자동 전환, 실제 교육장 모델/RAG/Multi-Agent/튜닝 실행은 이번 작업에 포함하지 않았다. 의미 검토는 같은 Work 세션의 순차 검토이며 독립 평가자가 아니다.

</details>
