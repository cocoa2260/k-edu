# K-Edu 008 · PDF·OCR·Vision과 보고서 렌더링

2026년 11월 4일 · `KEDU-RUNTIME-REVALIDATION-008`

**디지털 PDF와 v2 보고서 출력은 시험 범위에서 통과했다. 병합 표의 OCR과 Vision은 행·금액 연결 기준에 미달했다.**

## L8 · 기존 환불 문서 재실행

| 문서 | 실제 경로 | 확인 결과 |
|---|---|---|
| 디지털 PDF | 1쪽 텍스트·표 직접 추출 | 3×3 표가 정답과 일치했다. 영수증 문장의 1쪽 영역을 원본으로 역추적했다. |
| 깨끗한 스캔 | 1쪽 Tesseract OCR | 기한 7일, 15,000원, 접수 번호 RF-1048은 모두 나왔다. 제목의 ‘환불’은 ‘완 불’로 읽었고, 공백을 뺀 문자 오류율은 2.5%였다. |
| 열화 스캔 | 1쪽 Tesseract OCR | 지정한 본문 영역에서 같은 핵심 값 3개가 나왔다. 공백을 뺀 문자 오류율은 기본과 임곗값 전처리 모두 0%였다. 해당 합성 문서에서 관찰한 결과다. |
| 혼합 PDF | 1쪽 직접 추출, 2쪽 OCR | 페이지별 경로가 기대와 일치했다. |

기존 실습의 핵심 값 검사는 문서 안에 문자열이 있는지 확인한다. 따라서 값이 어느 조건의 값인지 보려면 아래처럼 행 위치를 별도로 대조해야 한다.

## L8 · 병합 셀과 예외 각주가 있는 표

같은 교육용 표를 디지털 PDF와 이미지 전용 PDF로 만들었다. 표 안의 0원과 각주의 0원을 구분하도록 기준 영역을 따로 정했다. 원본 좌상단을 기준으로 한 PDF 포인트 좌표를 사용했다.

| 원본의 행 | 기대 부담금 | 디지털 PDF | 스캔 OCR |
|---|---:|---|---|
| 일반 · 미사용 | 0원 | 올바른 행에서 확인 | 해당 행에서 누락 |
| 일반 · 사용 이력 있음 | 15,000원 | 올바른 행에서 확인 | 올바른 행에서 확인 |
| 특별 · 기한 경과 | 25,000원 | 올바른 행에서 확인 | 누락 |
| 특별 · 운영자 귀책 | 5,000원 | 올바른 행에서 확인 | 누락 |

디지털 추출은 머리글을 포함한 5×4 표와 두 병합 셀의 이어지는 빈 칸을 보존했다. 스캔 OCR은 줄 단위 결과를 반환했고 표 구조는 복원하지 않았다. OCR의 15,000원은 1쪽의 `[169.7, 220.7, 508.3, 245.7]` 포인트 줄 영역으로 원본에 연결됐다. 각주의 0원도 다른 영역에서 읽었지만, 미사용 행을 복원한 것으로 세지 않았다. 스캔 각주의 내용은 읽혔고 마침표는 빠졌다. 디지털 각주 전체는 원문과 일치했다.

## L8 · 로컬 Vision 비교

기존 실습의 외부 API나 Provider를 거치지 않고, 공개 SmolVLM-256M-Instruct의 고정 리비전을 Linux CPU에서 실행했다. 입력은 교육용 이미지이고 모델은 오프라인으로 생성했다. 테스트는 다음 세 조건이다. [모델 카드](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct)

| 이미지 | 기대 결과 | 실제 출력과 판정 |
|---|---|---|
| 스캔 공지 1쪽 | 7일, 15,000원, RF-1048 | 15,000에 해당하는 숫자를 한 번 적은 뒤 근거 없는 10,000을 반복했다. 기한·접수 번호가 없었고 출력 한도 96토큰에서 끝났다. |
| 복잡한 표 1쪽 전체 | 행 순서대로 0, 15,000, 25,000, 5,000원과 각주 예외 | `15000 / 25000 / 50000 / 0`을 반환했다. 네 값의 행 대응이 모두 틀렸고 각주를 설명하지 않았다. |
| 같은 표와 각주 영역 확대 | 같은 정답 | `1.5000 / 2.5000 / 3. 5000 / 4. 0`을 반환했다. 확대 범위에 각주가 포함됐지만 예외가 나오지 않았고 금액과 행 연결도 복구되지 않았다. |

입력 페이지와 확대 영역은 실행기가 기록했다. Vision 답변이 확인 가능한 근거 좌표를 반환한 사례는 없었다. **이 모델과 시험 조건에서는 OCR이나 PDF 직접 추출을 대체할 품질을 확인하지 못했다.** 합성 문서와 단일 모델의 결과이며 일반 문서나 다른 Vision 모델의 품질은 별도 검증 범위다.

## L9 · 현재 v2 보고서 렌더링

PDF·TXT·DOCX 원본을 등록한 뒤 기존 v2 보고서를 새로 생성했다. 현재 저장소의 DocumentSpec과 생성한 명세가 바이트 단위로 일치했다. 직접 생성한 PDF와 LibreOffice로 렌더링한 DOCX는 모두 한 페이지였고, 두 출력에서 제목과 본문 21개 단락을 모두 찾았다. 페이지 이미지로 한글, 인용 위치, 원본 해시와 페이지 경계를 확인했다.

| 주장 | 실제로 대조한 원문 위치 | 확인한 근거 |
|---|---|---|
| 영수증을 함께 제출한다 | PDF 물리 1쪽, 지정 영역 | 영수증을 함께 제출 |
| 신청 기한은 7일이다 | TXT 2번째 줄 | 신청 기한은 7일입니다. |
| 사용 이력 행의 부담금은 15,000원이다 | DOCX 1번 표, 3행 3열 | 15000원 |

보고서를 만든 뒤 DOCX 원본을 제한 상태로 바꾸자 같은 명세의 새 출력을 막았다. 먼저 만들어진 파일은 그대로 존재했다. 검토 결정은 교육용 고정 검토자 시연이다.

## 판정과 다음 작업

- PDF 직접 추출과 v2 보고서 출력은 시험 범위에서 통과했다. 기존 L8·Registry·DOCX·보고서 자동 검사 112개와 하위 검사 25개가 통과했다.
- 복잡한 스캔의 행·금액 연결과 Vision 응답 품질은 채택 보류다. 이번 결과는 실습과 합성 원본에 대한 검증이며 독립 수업이나 실제 업무 승인 결과는 별도다.
- 다음은 **009 · 권장 추론 강도 High**다. L9의 실제 모델 연결과 Streaming 전송, 사용자 취소, 강제 중단, 인증·승인 경계를 검증한다.

## 재현

기준 커밋은 `826065796353cdd7125a8e7641dabbaaa22a6c2a`다. [L8](../../practice/document-assistant/L8.md)과 [L9](../../practice/document-assistant/L9.md)의 의존성을 사용한다. 이번에는 Python 3.12.14, Tesseract 5.3.4, Poppler 26.05.0을 사용했다. 로컬에서 Noto Sans KR을 글꼴 검색 경로에 등록한 뒤 DOCX를 렌더링한다. 환경·모델 해시·실측 결과는 [검증 기록](observations-summary.json)에 있다.

아래 명령은 저장소의 `curriculum-work/practice/document-assistant/backend`에서 실행한다. `$run`은 별도의 절대 경로다.

```sh
report=../../../reports/KEDU-RUNTIME-REVALIDATION-008
python -m tools.document_assets --output "$run/assets"
python -m tools.document_lab --specimens data/document-v1 --tessdata-dir "$run/assets" --output "$run/l8"
PYTHONPATH="$PWD" python "$report/table_probe.py" --assets "$run/assets" --output "$run/complex"
python -m tools.multiformat_lab --output "$run/l9" --font "$run/assets/NotoSansKR-Regular.ttf"
L8_SPECIMENS=data/document-v1 L8_TESSDATA="$run/assets" python -m pytest -q -rs document_tests registry_tests report_tests multiformat_tests
pdftoppm -r 216 -png -singlefile data/document-v1/scan.pdf "$run/notice"
```

보고서 DOCX를 LibreOffice로 PDF에 렌더링한 뒤, 두 PDF 페이지를 이미지로 확인하고 [보고서 검사기](report_audit.py)에 DOCX 렌더 PDF 경로를 전달한다. Vision은 기록된 모델 리비전의 로컬 스냅샷에 대해 [Vision 검사기](vision_probe.py)를 실행한다. `--complex-image`에는 `$run/complex/complex.png`, `--notice-image`에는 `$run/notice.png`를 넘긴다.
