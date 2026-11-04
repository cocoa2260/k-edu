# 합성 문서 입력 자료 v1

실제 정책·개인정보가 없는 교육용 문서다. [L8 안내](../../../L8.md)에서 사용한다.

| 파일 | 역할 |
|---|---|
| [digital.pdf](digital.pdf) | 한글 텍스트·두 열·경계선 표·문서 지시문 사례. PDF 저장 순서와 화면 순서가 다름 |
| [scan.pdf](scan.pdf) | 이미지뿐인 한글 네 줄. 텍스트 층 없음 |
| [degraded.pdf](degraded.pdf) | 같은 이미지의 축소·흐림·기울임·흰 띠 처리본. 오류가 반드시 커진다는 가정 없음 |
| [mixed.pdf](mixed.pdf) | digital 1쪽 + scan 1쪽을 연결한 2쪽 문서 |
| gold.json | 작성한 정답·표·열 영역·PDF 해시. OCR 추출 입력과 분리 |
| digital/scan/degraded-preview-1.png | 실제 PDF를 pdftoppm으로 렌더링한 화면. 재구성 그림이 아님 |
| [FONT-OFL.txt](FONT-OFL.txt) | PDF에 부분 포함한 Noto Sans KR의 SIL OFL |
| [TESSDATA-LICENSE.txt](TESSDATA-LICENSE.txt) | 외부 OCR 인식 데이터의 Apache 2.0 라이선스 안내 |

PDF 네 개 합계 약 450KB와 미리보기 세 개만 저장한다. 모델·글꼴 원본·인식 데이터·SQLite는 Git에 넣지 않는다. 글꼴과 인식 데이터는 tools.document_assets가 기록한 입력 SHA256으로 준비한다. upstream main URL이 바뀌면 검사를 실패시키며 새 버전을 조용히 대입하지 않는다.

재생성이 필요하면 tools.document_specimens에 새 output 폴더와 준비한 NotoSansKR-Regular.ttf를 지정한다. 원래 실행의 폰트·PDF 해시는 gold.json에 있다. 재생성한 글꼴/PDF의 메타데이터·라이브러리 버전에 따른 바이너리 동일성은 보장하지 않는다. 재실행에는 저장된 PDF 사용을 권장한다.
