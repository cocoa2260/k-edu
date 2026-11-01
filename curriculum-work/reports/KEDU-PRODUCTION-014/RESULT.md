# U03 근거 검토와 보고서 출력 결과

**K2-14.U03 강의와 DOCX/PDF 출력 실습을 작성했다. 전체 자료는 51/70개다.** 검토 절차는 고정 역할의 로컬 시연이며 독립 강사 승인이나 의미 품질 채택은 아니다.

[강의](../../lessons/document-ai/report.md) 다음 이 결과를 읽으면 된다. 실제 예제는 [DOCX](../../practice/document-assistant/backend/data/report-v1/evidence-report.docx)와 [PDF](../../practice/document-assistant/backend/data/report-v1/evidence-report.pdf)다.

| 실제 수행 | 결과 | 해석 범위 |
|---|---|---|
| PDF/TXT 원문 → 공통 IR → Claim/Citation | 주장 2개에 각각 원문 인용·버전·해시·위치 연결 | 새 모델 생성 아님 |
| 검토와 출력 연결 | 승인 전 출력 거부, 내용 해시에 연결한 고정 검토 결정 뒤 출력 | 실제 인증 사용자·독립 의미 평가 아님 |
| DOCX/PDF 출력 | 같은 명세에서 각각 1쪽 생성 | DOCX/HWPX/HWP 입력 어댑터 추가 아님 |
| 내용 비교 | DOCX 16개 문단이 직접 PDF·DOCX 렌더링 PDF에 모두 존재 | 의미 정답 여부는 별도 검토 |
| 화면 확인 | 최종 두 형식의 한글·배치·원본/명세 해시 확인 | 다른 PC/Word 버전은 미검증 |
| 자동 검사 | 새 보고서 20개 + 기존 Registry 25개 통과 | 과거 L8 44개·ML 278개 전체는 재실행하지 않음 |

처음 DOCX 화면은 한글이 빠지고 기본 제목의 파란 선이 남았다. 렌더러의 임시 HOME에서도 찾을 수 있는 글꼴 준비, 직접 글꼴 지정과 테마/제목 테두리 제거 후 다시 생성·렌더링했다. 문자열 저장 검사만으로 출력 품질을 완료 처리하지 않았다. 최종 PDF는 글꼴 부분 포함, DOCX는 Noto Sans KR 또는 호환 글꼴 설치가 필요하다.

검사에는 승인 전·거부·Claim 수정·템플릿/좌표 변조·인용 불일치·미확인 Element·원문 버전/권한/삭제·원본 바이트 손상·재색인·출력 도중 삭제·변환 예외·재시작 후 검토 기록 유지가 포함된다. 원문 7일/주장 30일처럼 인용은 맞아도 의미가 틀린 사례는 자동으로 정답 처리하지 않고 고정 검토자가 거부하는 예제로 남겼다.

단일 CLI에서 원문/검토를 전후 확인하고 임시 폴더에서 출력한 뒤 최종 디렉터리로 옮긴다. 동시 Worker·DB/파일시스템 간 원자적 발행·검토 철회·배포 후 회수·실제 인증·독립 수업은 미완료다. 기존 RAG/Agent/LoRA 의미 품질과 QLoRA 게이트도 그대로 남긴다.

다음은 **U04 Provider 기능·Readiness·Context/시간 예산·Fallback·Trace**다. **추천 추론 강도 High**. 실패를 감추는 대체 호출 없이 기능·예산·최종 판정이 연결되는지 확인해야 한다. U05 React/Streaming·U06 다중 형식/최종 평가와 기초/안내 16개도 남아 있다.

<details>
<summary>재현 담당자용 기록</summary>

- [observed.json](observed.json): 실제 Claim·Citation·명세·고정 검토·출력 조건.
- [text-check.json](text-check.json): 두 PDF 경로의 16개 문단 비교.
- [tests.json](tests.json): 20+25개 검사 범위.
- [validation.json](validation.json): 환경·해시·화면 검사와 미완료.
- [run.json](run.json): 게시 상태와 기준 커밋.

</details>
