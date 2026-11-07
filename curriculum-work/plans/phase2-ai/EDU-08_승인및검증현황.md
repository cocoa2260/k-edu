# EDU-08 — 학생용 기본 Chat 시작본 승인 및 검증 현황

- **승인일:** 2026-11-07
- **상태:** 사용자 승인 / 사용자 Mac에서 가이드에 따른 실행·일부 기능 동작 확인 / 교육장 PC 검증 대기
- **저장소:** `cocoa2260/k-edu`, 브랜치 `work/curriculum-production-001`

## 승인 범위

- 11개 단원에 걸쳐 **하나의 React·FastAPI 문서 도우미 실습앱**을 계속 수정하는 시작본.
- 첫 단원은 기본 Chat·Provider만 제공한다. Embedding, 검색, RAG, Tool Calling, Single-Agent, Multi-Agent의 완성 코드를 시작본에 미리 넣지 않는다.
- Python 가상환경 생성·활성화·패키지 설치·실행·재사용·오류 확인 부록.
- Ollama **`qwen3:1.7b`** 기본 생성 모델. 수업 초기 Chat부터 이후 RAG 답변 생성 및 Agent 판단용 모델로 유지하는 교육 설계. 실제 도구 실행/Agent 품질 검증은 후속 단계.
- **`intfloat/multilingual-e5-small`**은 후속 Embedding 단원의 별도 CPU 모델로 구분.

## 실행 검증 기록 — 범위 구분

- **사용자 확인:** 2026-11-07 Mac에서 가이드대로 수행하여 동작하는 부분을 확인했다고 보고함. 구체적으로 어떤 기능·명령·모델 추론·React 화면까지 검증했는지는 별도로 구분하여 기록하지 않았으므로 전체 E2E 성공이라고 확대하지 않는다.
- **앞선 제작 보고:** Backend 계약 테스트 31건, Frontend API 테스트 8건, 가상 Ollama 응답을 이용한 로컬 HTTP 연결 6건 통과로 보고됨. 본 문서는 기존 보고를 인용하며 이 커밋에서 해당 테스트를 새로 재실행한 기록이 아니다.
- **미확인:** 학원 PC GTX 1060 3GB의 GPU 적재·응답속도·안정성, Windows/Linux 학생 PC 재현, 후속 Embedding/RAG/Agent 기능의 실제 정확도.

## 이번 GitHub 반영 파일

- [Python 가상환경 및 Qwen3 모델 설치 부록](../../../academy/00.%20%EA%B5%90%EC%9C%A1%EA%B3%BC%EC%A0%95(curriculum)/03.%20Phase2_AI_%EC%88%98%EC%97%85%EC%9A%A9/%EA%B5%90%EC%95%88/%EB%B6%80%EB%A1%9D.%20Python%20%EA%B0%80%EC%83%81%ED%99%98%EA%B2%BD%20%EB%A7%8C%EB%93%A4%EA%B8%B0.md)
- 학생용 실습앱 `backend/.env.example` 기본 생성 모델 설정

**중요:** 직전 단계에 생성·검토된 **전체 학생용 Chat 시작본 ZIP은 이 GitHub 커밋에서 파일 원본을 확보하지 못하여 아직 저장소에 반영되지 않았다.** 전체 시작본의 개별 소스 코드를 임의로 재구성해 동일본이라고 주장하지 않는다. 따라서 현재 GitHub의 수업용 디렉터리는 **부록·설정 파일만 반영된 부분 상태**이며, 전체 시작본 업로드와 clean checkout 실행 재현을 별도로 완료해야 한다. 기존 `academy/01. Phase2_AI` 및 `academy/02. 실습` 원본 변경 없음.
