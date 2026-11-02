# U06 세 형식과 최종 채택 기준 결과

**U06 자료와 PDF·TXT·DOCX의 실제 입력→IR→근거→고정 검토→보고서 경로를 작성했다. 자료 작성은 54/70개다.** K2-14 여섯 단원 자료를 작성했지만 독립 수업·품질·운영 채택은 보류다.

[강의](../../lessons/document-ai/evaluation.md) 다음 이 결과를 읽으면 된다. 새 [입력 DOCX](../../practice/document-assistant/backend/data/multiformat-v1/policy.docx)와 [출력 DOCX](../../practice/document-assistant/backend/data/multiformat-v1/output/evidence-report.docx)·[출력 PDF](../../practice/document-assistant/backend/data/multiformat-v1/output/evidence-report.pdf)는 교육용 합성 자료다.

| 실제 입력 | Element | 표 | 실제 대조 |
|---|---:|---:|---|
| 이전 디지털 PDF | 11 | 1 | 준비한 표 3×3 값 일치, 물리 페이지/영역 보존 |
| UTF-8 TXT | 5 | 0 | 문단·실제 줄 번호 보존, 표 형식으로 자동 승격하지 않음 |
| 새 DOCX | 16 | 1 | 표 3×3 값/명시된 머리글 일치, 셀은 표 1·행 3·열 3으로 연결 |

DOCX는 본문 문단과 병합 없는 직사각형 표만 지원한다. 감지한 그림·변경 추적·필드·각주·주석·외부 관계·병합/중첩 표·번호/숨김 스타일 등은 거부한다. ZIP 항목/크기/압축 비율·중복·경로와 XML 한계도 검사한다. 전체 OOXML 검증기나 악성 파일 Sandbox는 아니다. HWP/HWPX 입력·변환은 여전히 미지원이다.

세 형식의 세 Claim/인용을 같은 DocumentSpec에 연결하고, 고정 검토자의 시연 결정 후 DOCX/PDF 보고서를 출력했다. 두 출력 모두 1쪽이며 DOCX의 21개 문단이 직접 PDF와 DOCX 렌더링 PDF에 모두 존재했다. 입력 DOCX 1쪽의 한글·표, 출력 두 형식의 한글·위치·배치를 직접 확인했다. DOCX 위치는 구조적 표/셀이고 Word 페이지 번호로 위장하지 않았다.

보고서 템플릿은 DOCX 위치 설명을 포함하는 v2로 올렸다. 이전 v1 자료·출력물은 보존하고 새 명세/검토를 요구한다. 보고서 생성 뒤 DOCX 원문을 restricted로 바꾸자 과거 명세로 새 출력을 승인하는 시도가 거부됐다. 이미 저장·복사한 파일의 자동 회수는 미구현이다.

새 DOCX 검사 **23개와 기존 회귀 88개, 총 111개가 통과**했다. Registry·보고서·Router·HTTP/SSE 계약을 재검사했다. 기존 Office 미지원 검사는 HWP/HWPX 거부를 유지하도록 범위를 갱신했다. 변경하지 않은 React 브라우저 검사와 과거 ML/OCR 전체는 이번에 재실행하지 않았다.

첫 DOCX 시도는 Python 문서 기본 템플릿의 비표시 custom XML 메타데이터까지 일괄 거부해 실패했다. 본문 미지원 구조는 계속 거부하되 비표시 메타데이터와 구분했다. 화면 검사에서는 초기화된 렌더러 글꼴 경로 문제를 발견해 작업 폴더의 글꼴을 명시했고, 보고서 줄 간격/제목 간격을 정리한 뒤 최종 화면과 내용을 다시 확인했다. 문자열 추출 성공만으로 출력을 채택하지 않았다.

입력 바이트·추출 시간·색인 시간을 실제 기록했지만 파일 구성/레이아웃이 달라 단일 수치로 속도 우열을 판단하지 않는다. 모델 호출은 0회이고 실제 Token/청구액은 측정하지 않았다. 빈 비용 값은 무료 운영이라는 뜻이 아니다.

**최종 수업/운영 채택 판정은 BLOCKED다.** 합성 소프트웨어 계약의 통과와 일반 문서 품질·실제 모델 답변·독립 검토·실제 인증·모델 Streaming/강제 중단·QLoRA·교육장 장비/동시 실행은 구분한다. 기존 RAG/Agent/LoRA 미통과 품질도 유지한다. 지원 형식/범위가 바뀌면 추가 대조가 필요하다.

다음은 **K2-00 시작 안내 3개 단원**이다. 추천 추론 강도 **High**. 업무의 허용할 수 없는 실패, AI Lifecycle의 책임, 동향/제품/생성 방식의 구분을 지금까지 만든 실습과 연결해야 한다. 남은 자료는 기초/안내 16개이며 전체 품질·수업 검증은 별도다.

<details>
<summary>재현 담당자용 기록</summary>

- [자료 안내](../../practice/document-assistant/backend/data/multiformat-v1/README.md): 원본·정답·출력과 범위.
- [observed.json](observed.json): 세 형식의 IR·Claim·실측 시간·채택 보류 사유.
- [text-check.json](text-check.json): 두 PDF 경로의 21개 문단 비교.
- [tests.json](tests.json): 새 검사 23개·회귀 88개.
- [validation.json](validation.json): 환경·해시·화면 확인과 미완료.
- [run.json](run.json): 기준 커밋과 게시 상태.

</details>
