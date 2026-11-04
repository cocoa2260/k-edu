# 세 형식 비교 자료

[강의](../../../../../lessons/document-ai/evaluation.md)와 [결과](../../../../../reports/KEDU-PRODUCTION-017/RESULT.md)에서 사용한다. 실제 회사 정책이 없는 교육용 합성 자료다.

| 파일 | 용도 |
|---|---|
| [policy.docx](policy.docx) | 실제 한글 문단과 3×3 표가 있는 입력 |
| [policy.txt](policy.txt) | 같은 일부 조건을 풀어 쓴 UTF-8 입력. 자동 표 구조로 취급하지 않음 |
| gold.json | 문단·표의 정답과 원본 해시. 추출 입력과 분리 |
| [기존 digital.pdf](../document-v1/digital.pdf) | 비교용 PDF 입력. 표 값은 같지만 전체 레이아웃/내용은 다른 예제 |
| [출력 DOCX](output/evidence-report.docx) · [출력 PDF](output/evidence-report.pdf) | 세 Claim/인용으로 만든 고정 검토 시연 보고서 |
| output/document-spec.json·review.json | 출력 당시 명세와 고정 검토 기록. 독립 승인 자료 아님 |

원본 DOCX는 tools.multiformat_specimen으로 만들고 render_docx.py로 화면을 확인했다. DOCX 글꼴은 내장하지 않아 Noto Sans KR 또는 호환 글꼴이 필요하다. PDF 글꼴은 부분 포함하며 [기존 OFL](../document-v1/FONT-OFL.txt)을 따른다. 재생성에는 문서 메타데이터 차이가 생길 수 있어 저장한 원본을 비교 기준으로 사용한다.

실험은 보고서를 만든 뒤 DOCX 권한을 제한해 같은 승인으로 재출력할 수 없는지 확인한다. 저장된 출력은 권한 변경 전의 과거 시연 결과이며 원문 변경 뒤에도 언제나 현재 자료라는 뜻은 아니다. 기존 파일의 자동 회수는 미구현이다.
