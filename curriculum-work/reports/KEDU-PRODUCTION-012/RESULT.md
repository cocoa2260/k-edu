# K2-13 · 실제 PDF/OCR와 원문 추적 결과

**네 단원과 L8 자료를 작성하고 합성 PDF 네 개·총 5쪽을 실제 처리했다. 변경 범위 테스트 44개가 통과했다. 전체 자료 작성은 48/70개다.** 일반 문서 품질·Vision·독립 수업 검증은 미완료다.

읽을 파일은 [강의](../../lessons/document-parsing/lesson.md) → 이 결과다. 사례별 확인이 필요하면 [REVIEW.md](REVIEW.md), 실행 담당자는 [L8 안내](../../practice/document-assistant/L8.md)를 본다. JSON과 코드는 필수 읽기 대상이 아니다.

## 실제로 실행한 것

| 항목 | 실제 결과 | 해석 범위 |
|---|---|---|
| 문서 유형 | digital 직접 추출, scan/degraded OCR, mixed는 1쪽 직접 추출·2쪽 OCR | 페이지별 경로. 일반 영역 분할 모델 아님 |
| 스캔 확인 | scan/degraded의 pypdf 텍스트 추출이 빈 값 | 숨은 정답 텍스트 층 없이 실제 OCR 실행 |
| 표 | 머리글 포함 3×3 셀 값과 정답 일치 | 경계선 표 한 개. 일반 표 정확도 아님 |
| 읽기 순서 | PDF 저장 순서 B1→B2→A1→A2, 수동 열 분리 A1→A2 / B1→B2 | 사람이 영역을 정한 비교. 자동 Layout 분석 아님 |
| 원문 연결 | 실제 PDF 추출 → 기존 LocalIndex BM25 → 문맥 → 원본 1쪽 좌표 | 비의미적 상수 Encoder 사용. E5/LLM 품질 평가 아님 |
| 변경 경계 | 권한·삭제·버전·원본 해시·Parser 버전 변경 및 잘못된 줄 거부 | 고정 staff 실습. 실제 인증 아님 |
| 화면 검사 | pdftoppm으로 네 PDF 5쪽 렌더링 후 직접 확인 | 한글·표·배치 확인. 열화는 의도한 실험 조건 |

실제 Tesseract 5.3.4의 한글+영어 인식 데이터, LSTM·PSM 6·216dpi를 사용했다. Python 3.12.14, pdfplumber 0.11.9, pypdf 6.10.0, Pillow 12.3.0, ReportLab 4.4.9였다. 외부 Vision/LLM 호출은 0회다.

## OCR를 돌려 보니

| 입력 | 공백 제외 CER | 공백 토큰 WER | 중요 문자열 존재 |
|---|---:|---:|---|
| 깨끗한 스캔 | 2.50% | 42.86% | 7일·15000원·RF-1048 모두 발견 |
| 열화 스캔 | 0.00% | 28.57% | 세 문자열 모두 발견 |
| 열화 후 임계값 175 흑백화 | 0.00% | 28.57% | 세 문자열 모두 발견 |

깨끗한 스캔의 ‘환불’이 실제로 ‘완 불’이 됐다. 열화본이 이 예제에서는 더 정확했으며 흑백화 효과는 관찰되지 않았다. 결과를 원하는 방향으로 바꾸지 않고 보존했다. 한국어 띄어쓰기 차이가 WER를 크게 바꾸므로 CER와 함께 읽는다. 중요 문자열 존재는 올바른 필드·조건 연결이나 답변 정답을 보장하지 않는다.

평가 정답은 상단 네 줄이며 하단 합성 표시는 제외했다. 같은 정답과 같은 평가 영역으로 세 조건을 비교했다. 네 줄의 합성 문서는 실제 업무 문서 품질을 대표하지 않는다.

## 검사와 수정

44개 검사는 실제 문서 유형·텍스트 층 부재·표·열 비교·좌표 범위·문서 지시문 보존·Index 연결/삭제와 거부 조건을 확인했다. 암호·회전·Crop·원점·UserUnit·크기·페이지 수·용량·언어 부재·빈 페이지·시간초과·TSV 오형식도 포함한다. **기존 278개 ML 검사 전체는 이번에 재실행하지 않았다.** 기존 코드·데이터·API의 보존은 게시 전 Git Blob 비교로 별도 확인한다.

첫 실행에서는 별도 인식 데이터 폴더에 TSV 설정 파일이 없어 일반 텍스트가 반환됐다. TSV 생성 변수를 명시하고 형식 검사를 추가했다. 원문 연결의 첫 검색도 ‘영수증’과 원문 ‘영수증을’이 단순 어절 BM25에서 달라 비었다. 경계 실험의 질의를 원문 어절에 맞췄으며 기존 검색기를 바꾸거나 의미 검색 성공으로 포장하지 않았다. 관련 한계는 강의에 남겼다.

## 남은 일과 다음 작업

자료 작성 48/70은 수업 완료 수가 아니다. CLIP·VLM·OCR-free/Layout-aware 모델, 일반 문서 영역별 처리·자동 읽기 순서·복잡한 표, 실제 인증·보안 격리·업로드/하이라이트 UI는 실행하지 않았다. 정상 추출도 검토 필요 상태로 남긴다. RAG/Agent/LoRA의 기존 품질 보류와 QLoRA·독립 수업 검증도 유지한다.

다음은 **K2-14/L9 Document AI 통합·보고서 생성 6개 단원**이다. **추천 추론 강도: High.** 형식별 원본/공통 구조, 문서 상태·권한, 근거와 보고서, Provider·예산, React/Streaming, 최종 평가를 연결해야 한다. 남은 기초/안내 16개 단원은 이후 별도 제작한다.

<details>
<summary>문제 조사·재현 담당자용 기록</summary>

- [observed.json](observed.json): 실제 환경·OCR 출력/지표·표·열·검색 문맥·물리 Locator.
- [tests.json](tests.json): 이번 변경 범위 44개 검사 이름·결과·소요 시간.
- [validation.json](validation.json): 작성/검토/실행/미완료의 구분과 파일 해시.
- [run.json](run.json): 게시 상태·기준 커밋·게시 검증.
- [원본 자료 안내](../../practice/document-assistant/backend/data/document-v1/README.md): PDF·정답·실제 렌더링과 라이선스.
- [디지털 추출](details/digital-extraction.json), [스캔 추출](details/scan-extraction.json), [열화 추출](details/degraded-extraction.json), [혼합 추출](details/mixed-extraction.json), [전처리 추출](details/degraded-preprocessed-extraction.json): 줄·단어·표·Confidence·좌표의 상세.

</details>
