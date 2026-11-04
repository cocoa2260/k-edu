# 문서 도우미를 단계별로 확장하는 실습

교육생의 전체 시작점은 [수강 안내](<../../교육과정 안내.md>)다. 이 폴더에서는 기준 대화 앱에 입력 준비·실행기·검색·도구 실행을 추가하고, 별도 학습 실험과 문서 처리로 넓힌다. 각 행의 **강의 → 연결 실습 → 관찰/해석 제출** 순서로 진행한다.

## 읽을 순서와 현재 확인된 범위

아래 ‘확인된 범위’는 저장소의 과거 실행과 후속 설명 정비에서 확인한 범위다. 지금 모든 모델/환경을 다시 실행했거나 독립 수업을 마쳤다는 뜻은 아니다. 본인의 실행 기록은 별도로 남긴다.

| 순서 | 강의와 실습 | 확인된 범위와 남은 것 |
|---|---|---|
| 기준 앱 준비 | [기준 대화 앱](<../../01. Phase2_AI/12. AI Integration/강의용.md>) · [Backend 시작](backend/README.md) | API/Provider 계약·고정 HTTP 응답. 실제 웹 생성은 별도 확인 |
| 지시와 제공 자료 | [Prompt](<../../01. Phase2_AI/05. 프롬프트 엔지니어링(Prompt Engineering)/강의용.md>) → [지시 실습](L1.md) → [Context](<../../01. Phase2_AI/05. 프롬프트 엔지니어링(Prompt Engineering)/Context Engineering/강의용.md>) → [자료 선택 실습](CONTEXT.md) | 입력 준비·자료/순서·기존 Token 관찰의 계산. 다섯 조건 실제 생성 비교는 남음 |
| 호출·검사·종료 | [Harness](<../../01. Phase2_AI/05. 프롬프트 엔지니어링(Prompt Engineering)/Harness/강의용.md>) → [실습](L2.md) | 고정 응답의 재시도·보완·상한·회귀·중단 경계. 실제 모델 비교와 다름 |
| 검색과 Index | [Embedding](<../../01. Phase2_AI/06. 임베딩(Embedding)/강의용.md>) → [Index](<../../01. Phase2_AI/07. 벡터 데이터베이스(VectorDB)/강의용.md>) · [공통 실습](L3.md) | 과거 실제 CPU E5/검색/FAISS, 현재 작은 계산·SQLite 변경. 현재 모델 전체 재실행과 품질 채택은 별도 |
| 근거로 답변 | [RAG](<../../01. Phase2_AI/08. 검색 증강 생성(RAG)/강의용.md>) → [실습](L4.md) | 실제 E5/Qwen 검색·생성·보완 기록. 조건 누락/잘못된 주장 등 답변 품질은 채택 보류 |
| 도구 요청 | [Single-Agent](<../../01. Phase2_AI/09. AI 에이전트(Agent)/01. Single-Agent/강의용.md>) → [실습](L5.md) | 실제 모델 요청·Runtime/종료 기록과 고정 완주 실험. 과제 품질·Framework/MCP는 별도 |
| 역할 전달 | [Multi-Agent](<../../01. Phase2_AI/09. AI 에이전트(Agent)/02. Multi-Agent/강의용.md>) → [실습](L6.md) | 실제 역할 호출·전달/공통 예산 기록. 최종 답변 품질은 채택 보류 |
| 데이터와 학습 실험 | [데이터 준비](<../../01. Phase2_AI/10. 미세조정(Fine-tuning)/강의용.md>) → [훈련/평가](<../../01. Phase2_AI/10. 미세조정(Fine-tuning)/LoRA 실습.md>) · [실습](L7.md) | 전체 Train 포함 제한 Step LoRA·재로드/18개 Agent 회귀 기록. 수렴·의미 품질·QLoRA는 미완료 |
| PDF/OCR 입력 | [문서 추출](<../../01. Phase2_AI/11. 광학 문자 인식과 멀티모달(OCR_Multimodal)/강의용.md>) → [실습](L8.md) | 합성 한글 PDF/OCR·표·물리 원문 연결. 일반 문서/Vision·실제 업로드 UI는 별도 |
| 문서 등록부터 최종 평가 | [문서 등록](<../../01. Phase2_AI/13. Document AI/01. 문서 등록.md>)부터 [최종 평가](<../../01. Phase2_AI/13. Document AI/05. 최종 평가.md>)까지 → [통합 실습](L9.md) | 좁은 PDF/TXT/DOCX·근거 검토/출력·Provider 고정 HTTP·React/SSE 고정 화면. 실제 모델 Token Streaming/운영·독립 품질/수업 채택은 남음 |

## 같은 프로젝트에서 실행 경로는 구분하기

[Backend 안내](backend/README.md)는 기존 대화 API와 누적 모듈/명령행 도구의 위치다. RAG·Agent를 CLI로 실행했다고 `/ai/chat`이 자동으로 그 기능을 사용하는 것은 아니다. [React/SSE 실습](stream-ui/README.md)은 같은 프로젝트 안의 **별도 화면과 로컬 서버**이며 기존 FastAPI API 전환이나 실제 모델 Token Streaming을 완료한 앱이 아니다.

고정 응답·작은 계산·저장된 모델 기록 읽기는 학습 활동이며, 본인의 새 모델 실행을 대신하지 않는다. 실제 실행을 요구하는 활동은 각 안내의 별도 환경/파일/자원 조건을 확인한다. LoRA 훈련과 PDF/OCR·보고서 확장은 따로 준비하고 원래 자료·기록을 덮어쓰지 않는다.

## 강사와 재현 담당자

학생 제출은 각 실습의 작성 표와 관찰 근거를 사용한다. 강사용 해설은 [전체 연결 점검표](https://github.com/cocoa2260/k-edu/blob/work/curriculum-production-001/curriculum-work/reports/KEDU-TEACHING-INTEGRATION-001/RESULT.md)에 모았다. 현재 미완료 작업은 [제작 현황](https://github.com/cocoa2260/k-edu/blob/work/curriculum-production-001/curriculum-work/PROGRESS.md), 실행 당시 상세 근거는 해당 과목에서 연결한 제작/수정 보고서를 확인한다. 과거 보고서의 ‘미작성’이나 ‘다음 작업’을 현재 집계로 복사하지 않는다.

[baseline-source-map.json](baseline-source-map.json)은 기준 앱으로 원문을 옮겼을 당시의 해시다. 이후 확장된 현재 소스 전체가 당시와 같다는 뜻이 아니다. 누적 실행의 역사와 게이트는 [단원/단계 기록](https://github.com/cocoa2260/k-edu/blob/work/curriculum-production-001/curriculum-work/curriculum/production-index.json)에 보존한다. React 고정 화면은 실제 Chromium 상태/한글 화면을 검사한 기록이 있지만, 교육생 장비·독립 수업·실제 모델 연결까지 확인한 것은 아니다.
