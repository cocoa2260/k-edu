"""Run local temporary Registry/review examples or read historical report records.
No model calls, web API, real reviewer authentication or DOCX/PDF file creation.
"""
import argparse
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

BACK = Path(__file__).resolve().parents[1]


def meta(id='policy'):
    return dict(id=id, version='external-v1', title='가상 환불 안내', access='staff', current=True)


def blocked(label, action):
    from app.document_registry import RegistryError
    from app.report_spec import ReportRejected
    try:
        action()
    except (RegistryError, ReportRejected) as error:
        print(label, '거부:', error)
        return
    raise AssertionError('Expected refusal: ' + label)


def run(mode):
    from app.document_registry import Registry
    from app.report_spec import Reports, fingerprint, TEMPLATE
    from tools.report_export import export
    if mode == 'history':
        report = BACK / 'data/report-v1'
        spec = json.loads((report / 'document-spec.json').read_text())
        review = json.loads((report / 'review.json').read_text())
        print('과거 보고서 기록 읽기: 현재 파일 출력/승인/모델 실행이 아닙니다.')
        print('과거/현재 템플릿:', spec['template'], TEMPLATE)
        print('주장/인용 수:', len(spec['claims']), sum(len(c['citations']) for c in spec['claims']))
        print('저장 내용 해시와 검토 연결:', fingerprint(spec) == review['binding'])
        print('검토 방식:', spec['review_mode'])
        return
    print('현재 코드·임시 SQLite 실습입니다. 모델/독립 승인/보고서 파일 생성이 아닙니다.')
    with TemporaryDirectory(prefix='kedu-doc-example-') as folder:
        root = Path(folder)
        source = root / 'policy.txt'
        source.write_text('신청 기한 7일\n\n금액 15000원', encoding='utf-8')
        registry = Registry(root / 'registry.sqlite')
        try:
            if mode == 'intake':
                for id, path, query in [('pdf', BACK/'data/document-v1/digital.pdf', '영수증'),
                                        ('txt', source, '15000'),
                                        ('docx', BACK/'data/multiformat-v1/policy.docx', '15000')]:
                    uploaded = registry.upload(path, meta(id), id + '-first')
                    ir = registry.parse(id, uploaded['version'])
                    print(id, '형식/Parser/Element 수:', ir['format'], ir['parser'], len(ir['elements']))
                    print('추출 뒤 상태/검색:', registry.eligible(id,1)['state'], sum(h['doc']==id for h in registry.search(query)['hits']))
                    registry.index(id,1)
                    rows = [r for r in registry.context(registry.search(query)) if r['doc']==id]
                    print('검색 문맥:', [(r['element']['id'], r['element']['text'], r['element']['locator']) for r in rows])
                    print('표 행렬 수:', sum(e['kind']=='table' for e in ir['elements']))
                return
            registry.upload(source, meta(), 'first')
            registry.parse('policy',1)
            registry.index('policy',1)
            if mode == 'lifecycle':
                print('동일 요청 재전송:', registry.upload(source,meta(),'first'))
                selection = registry.search('15000')
                selection['hits'][0]['text'] = '변조한 문장'
                print('문맥은 저장 원문:', registry.context(selection)[0]['element']['text'])
                source.write_text('신청 기한 14일\n\n금액 15000원', encoding='utf-8')
                print('PC 파일을 14일로 바꿔도 저장 사본은:', registry.context(registry.search('7일'))[0]['element']['text'])
                blocked('같은 키 다른 입력', lambda: registry.upload(source,meta(),'first'))
                print('새 요청 등록:', registry.upload(source,meta(),'second'))
                print('재처리 전 검색:', registry.search('15000')['hits'])
                blocked('과거 문맥', lambda: registry.context(selection))
                registry.parse('policy',2);registry.index('policy',2);registry.review('policy',2)
                print('재처리한 기한:', registry.context(registry.search('14일'))[0]['element']['text'])
                registry.restrict('policy',2)
                print('권한 제한 뒤 검색:', registry.search('15000')['hits'])
                blocked('제한 뒤 요청 재전송', lambda: registry.upload(source,meta(),'second'))
                registry.delete('policy',2)
                registry.close();registry=Registry(root/'registry.sqlite')
                row=registry.db.execute("SELECT source,ir,state FROM docs WHERE id='policy'").fetchone()
                print('재시작 뒤 삭제 상태/원본/IR:', row['state'], row['source'], row['ir'])
                blocked('삭제 ID 재등록', lambda: registry.upload(source,meta(),'third'))
                return
            reports=Reports(registry)
            claims=[dict(id='deadline',statement='신청 기한은 7일이다.',
                         citations=[dict(doc='policy',version=1,element='line-1',quote='신청 기한 7일')])]
            blocked('검토 대상 상태 전 명세 작성',lambda:reports.prepare('가상 안내',claims))
            registry.review('policy',1)
            spec=reports.prepare('가상 안내',claims)
            destination=root/'not-published'
            blocked('승인 전 출력',lambda:export(reports,spec,destination,'unused-font'))
            print('승인 전 최종 폴더 존재:',destination.exists())
            wrong=copy.deepcopy(claims);wrong[0]['statement']='신청 기한은 30일이다.'
            wrong_spec=reports.prepare('가상 안내',wrong)
            print('7일 인용/30일 주장 자동 연결 검사 통과. 의미 승인이 아닙니다.')
            reports.decide(wrong_spec,'reject','fixture-reviewer','7일 근거는 30일 주장을 지지하지 않음')
            blocked('의미 불일치 검토 뒤 출력',lambda:reports.authorized(wrong_spec))
            reports.decide(spec,'approve','fixture-reviewer','가상 자료의 7일 문장과 인용 대조 시연')
            print('고정 검토 결정:',reports.authorized(spec)['decision'],'내용 해시:',fingerprint(spec))
            changed=copy.deepcopy(spec);changed['claims'][0]['statement']='신청 기한은 30일이다.'
            blocked('승인 뒤 문장 변경',lambda:reports.authorized(changed))
            registry.upload(source,meta(),'new-version')
            blocked('원문 새 버전 뒤 과거 승인',lambda:reports.authorized(spec))
        finally:
            registry.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['intake','lifecycle','review','history'],default='intake')
    args=parser.parse_args()
    try:
        run(args.mode)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,f'환경/자료 확인 필요: {error}\n')


if __name__=='__main__':
    main()
