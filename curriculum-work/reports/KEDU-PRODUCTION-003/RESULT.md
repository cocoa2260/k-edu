# Prompt·Context 강의와 L1 입력 준비 검증

2026-10-31 · KEDU-PRODUCTION-003 · **8개 단원 자료·공통 자료·입력 준비 검증 완료 / 실제 생성·품질 평가 미실행**

학생은 [Prompt 강의](../../lessons/prompt/lesson.md), [Context 강의](../../lessons/context/lesson.md), [공통 L1 실습](../../practice/document-assistant/L1.md)을 순서대로 읽는다.

| 만든 것 | 결과 |
|---|---|
| K2-04 4개 단원 | 지시·Shot 비교·실행 전략의 경계·Golden/회귀 |
| K2-05 4개 단원 | 출처/신뢰·선택/순서·Token 예산·State와 현재 Context |
| 가상 자료 | 문서 6개, 동일 평가 사례 12개, 별도 예시 2개 |
| 입력 준비 | 기존 앱에 POST /ai/prepare 추가. 기존 /ai/chat 입력·출력 Schema 유지 |
| 실제 준비 실행 | 12사례×5조건: 입력 55개 준비, 공백 입력 5개 거부. 모델 정답률이 아님 |
| 실제 기준 Token 계산 | C01 다섯 입력을 고정 Qwen Tokenizer와 대화 Template으로 계산 |
| 검사 | 기존 30개 + L1 경계/비교/Schema 보존 63개 = 93개 통과 |

## 실제 Token 관찰

| 조건 | 문자 수 | 대화 Template 포함 기준 입력 Token |
|---|---|---|
| baseline | 1050 | 585 |
| instruction | 1151 | 657 |
| one_shot | 1272 | 723 |
| few_shot | 1403 | 793 |
| focused | 398 | 264 |

예시 기준 상한 2048에서 출력 여유 256을 남기면 위 다섯 입력은 범위 안에 들어간다. 이는 **C01과 Qwen 기준 Tokenizer에 대한 실제 관찰**이다. 실제 Ollama 모델의 Template·Context·출력 설정·메모리 용량과 답변 품질을 확인한 것은 아니다. focused가 짧다는 사실을 답변 품질 개선으로 바꾸어 기록하지 않았다.

## 검증한 경계

평가의 기대 답·rubric은 모델 입력으로 보내지 않는다. 제한 문서는 staff 준비 Context에서 제외한다. C12의 현재 수동 Manifest에 없는 출장 규정도 제외한다. 이 선택은 교사가 정한 자료 준비이며 자동 검색·Index 삭제·실제 인증/권한 구현의 검증이 아니다.

지시 비교, 예시 수 비교, 제공 문서 묶음 비교를 분리했다. 정상 사실/근거 6개와 경계 행동 6개는 따로 집계하도록 채점 기준을 만들었다. 실제 생성 응답과 채점 점수는 아직 없다. 자료가 없거나 잘못된 인용 내용의 경우도 사람이 근거 문장과 대조하도록 했다.

## 남은 일과 다음 작업

G-MODEL의 실제 생성과 사람의 사례별 채점, 선택 Provider의 Tokenizer/Template/실행 예산 검증은 남아 있다. 기존 로컬 Ollama 연결 미확인을 생성 성공으로 표시하지 않았다. 자료 작성은 총 70개 단원 중 11개이며, 이번 8개를 최종 수업·성능 검증까지 마쳤다고 표시하지 않는다.

**다음 작업:** K2-06/L2 Harness·검증 실패·상한·중단 구현 및 강의 제작. **추천 추론 강도: High.** 실제 모델 준비·평가 Gate는 별도로 유지한다.

<details>
<summary>실행 담당자용 증거</summary>

- [validation.json](validation.json): 범위·검사·미확인
- [tests.json](tests.json): 실제 93개 테스트 결과
- [prepared/manifest.json](prepared/manifest.json): 60개 준비/거부 기록·입력 해시
- [prepared/samples.json](prepared/samples.json): C01의 다섯 실제 준비 입력. 답변이 아님
- [token-counts.json](token-counts.json): 실제 기준 Token 관찰
- [run.json](run.json): 작업·게시 기록

</details>
