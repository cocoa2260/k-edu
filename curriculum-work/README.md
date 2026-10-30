# K-Edu 교육과정 개편 — 첫 강의 분석

**최신 추천: 기초 설명의 반복을 줄이고, 데이터 설계·모델 평가 중심으로 재구성한다.**

제목 제안은 **「머신러닝의 데이터 설계와 모델 평가」**다. 과목 구성과 제목은 아직 확정하지 않았다.

- [최신 결과 요약](reports/KEDU-PILOT-001/20261030T064535Z-r2/RESULT.md)
- [상세 분석과 원문별 근거](reports/KEDU-PILOT-001/20261030T064535Z-r2/attempt-01/analysis.md)
- [자동 검사 결과](reports/KEDU-PILOT-001/20261030T064535Z-r2/attempt-01/automatic_checks.json)
- [추가 비교 실행 기록](reports/KEDU-PILOT-001/20261030T064535Z-r2/run.json)
- [최초 시범의 초안·보완 기록](reports/KEDU-PILOT-001/20261030T061100Z/)

Day1 4교시 본문을 추가 비교해 CNN·RNN·Transformer의 기초 소개가 Phase1에 이미 있음을 확인했다. 원래 시범은 비교 3개 파일, 추가 비교 후는 4개 파일이다. 최초 시범의 범위를 소급해 확대하지 않았다.

## 자동 검사 재현

저장소 루트에서 실행한다.

```bash
python3 curriculum-work/loop/checks/check_analysis.py curriculum-work/reports/KEDU-PILOT-001/20261030T064535Z-r2 attempt-01
```

강의 원문 복사본은 추가하지 않는다. 검사기는 `sources.json`에 기록된 원본 저장소 경로를 읽어 고정 Blob SHA와 대조한다. 원문이 바뀌면 해당 기준 커밋에서 재현해야 한다.

자동 검사는 근거·형식·상태 검증이다. 교육적 의미 검토나 전체 Work 실행을 자동 재현하는 Runner는 아니다. 강의 원문 수정·과목 통합·최종 목차·시수 확정·모델 실행은 이번 범위에 포함되지 않는다.

## 기록 안내

`loop/loop-spec.md`는 실행 전에 작성한 v0.1 설계 원본이다. 그 안의 미실행 표시는 설계 당시 기록이며 현재 결과는 위 최신 보고서와 실행 기록을 따른다. 최초 시범의 `attempt-01`은 검사 실패가 있던 실제 초안, `attempt-02`는 당시 보완본이다. 이번 추가 비교는 별도 run과 task revision 2로 기록했다.
