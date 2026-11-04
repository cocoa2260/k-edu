"""Read stored synthetic PDF/OCR observations. No PDF extraction, OCR or model call."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT.parents[1] / 'reports/KEDU-PRODUCTION-012'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['routes','layout','ocr','source'], default='layout')
    args = parser.parse_args()
    try:
        record = json.loads((REPORT / 'observed.json').read_text())
        print('과거 합성 PDF 실행 기록 읽기입니다. 지금 PDF/OCR/모델을 실행하지 않습니다.')
        if args.mode == 'routes':
            for name, routes in record['routes'].items():
                print(name, '물리 페이지별 경로:', routes)
            print('스캔 텍스트 층이 비었는가:', record['image_only_text_layer_empty'])
        elif args.mode == 'layout':
            layout = record['layout']
            print('원래 저장 순서:', layout['raw_content_stream_text'])
            for i, column in enumerate(layout['manual_region_columns'], 1):
                print('사람이 정한 열', i, ':', column)
            print('추출한 표:', json.dumps(layout['table_observed'], ensure_ascii=False))
            print('표 정답과 같은가:', layout['table_observed']==layout['table_expected'])
            print('자동 일반 레이아웃 분석:', layout['general_layout_detection'])
        elif args.mode == 'ocr':
            for name, metrics in record['ocr_metrics'].items():
                print(name, '저장 CER/WER:', metrics['cer_whitespace_excluded'], metrics['wer_whitespace_tokens'])
                print('저장 OCR 텍스트:', metrics['prediction'])
                print('중요 문자열 존재:', metrics['critical_fields'])
            print('이 필드 검사는 올바른 행/조건 연결이나 의미 정답을 판정하지 않습니다.')
        else:
            boundary = record['index_boundary']
            for row, location in zip(boundary['context'], boundary['physical_locators']):
                print('검색 문맥:', row['text'])
                print('문서/버전/정규화 줄:', row['doc_id'], row['version'], row['line'])
                print('물리 페이지/bbox/추출방법:', location['page'], location['bbox'], location['method'])
                print('저장 원본 SHA256:', location['source_sha256'])
            print('검색:', boundary['ranking'], '/ Encoder:', boundary['encoder'])
            print('저장 위치 읽기이며 현재 PDF 해시/권한을 재검사한 결과가 아닙니다.')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(2, f'자료/기록 확인 필요: {exc}\n')


if __name__ == '__main__':
    main()
