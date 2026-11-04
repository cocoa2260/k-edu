"""Local Provider reservation or three-format evidence exercises; stored UI observations.
No real model, external Provider, actual user approval or report file generation.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

BACK = Path(__file__).resolve().parents[1]
REPORTS = BACK.parents[2] / 'reports'


def provider():
    from tools.provider_lab import run
    print('현재 loopback HTTP 고정 응답 실험입니다. 실제 모델 Token/비용이 아닙니다.')
    with TemporaryDirectory(prefix='kedu-delivery-') as folder:
        out=Path(folder)/'http'
        run(out)
        record=json.loads((out/'observed.json').read_text())
        for name,result in record['cases'].items():
            print(name,result['status'],'호출/예약:',result['calls'],result['reserved_tokens'])
            print('판정 순서:',[t['decision'] for t in result['trace']])
        print('실제 로컬 HTTP 요청:',record['loopback_request_count'],'/ 실제 모델:',record['real_model_calls'])


def formats():
    from app.document_registry import Registry,RegistryError
    from app.report_spec import Reports
    gold=json.loads((BACK/'data/multiformat-v1/gold.json').read_text())
    pdf_gold=json.loads((BACK/'data/document-v1/gold.json').read_text())
    print('현재 세 형식 원본/IR/근거·고정 검토 실습입니다. 보고서 파일은 생성하지 않습니다.')
    with TemporaryDirectory(prefix='kedu-formats-') as folder:
        registry=Registry(Path(folder)/'registry.sqlite')
        try:
            for name,path in [('pdf',BACK/'data/document-v1/digital.pdf'),('txt',BACK/'data/multiformat-v1/policy.txt'),('docx',BACK/'data/multiformat-v1/policy.docx')]:
                actual=hashlib.sha256(path.read_bytes()).hexdigest()
                expected=pdf_gold['files']['digital.pdf'] if name=='pdf' else gold['source_sha256'][path.name]
                if actual!=expected:
                    raise ValueError('Stored source hash changed')
                meta=dict(id=name,version='external-v1',title='가상 '+name+' 정책',access='staff',current=True)
                registry.upload(path,meta,'upload-'+name)
                ir=registry.parse(name,1);registry.index(name,1);registry.review(name,1)
                tables=[e for e in ir['elements'] if e['kind']=='table']
                exact=tables[0]['rows']==gold['docx_table'] if tables else None
                print(name,'Element/표/표 값 일치:',len(ir['elements']),len(tables),exact)
            selected={name:next(r for r in registry.context(registry.search(query)) if r['doc']==name and (name!='docx' or r['element']['kind']=='table_cell'))
                      for name,query in [('pdf','영수증'),('txt','신청 기한'),('docx','15000원')]}
            statements={'pdf':'합성 PDF는 영수증을 함께 제출하라고 안내한다.',
                        'txt':'합성 텍스트는 신청 기한을 7일로 안내한다.',
                        'docx':'합성 DOCX의 사용 이력 행 부담금은 15000원으로 표시돼 있다.'}
            quotes={'pdf':'영수증을 함께 제출','txt':'신청 기한은 7일입니다.','docx':'15000원'}
            claims=[]
            for i,(name,row) in enumerate(selected.items(),1):
                print(name,'원문 위치:',row['element']['locator'])
                claims.append(dict(id='C'+str(i),statement=statements[name],citations=[dict(doc=name,version=1,element=row['element']['id'],quote=quotes[name])]))
            reports=Reports(registry);spec=reports.prepare('세 형식의 문단과 표 근거 비교',claims)
            reports.decide(spec,'approve','fixture-reviewer','고정 가상 원문 대조 시연이며 독립 승인 아님')
            print('주장/인용 수:',len(spec['claims']),sum(len(c['citations']) for c in spec['claims']))
            registry.restrict('docx',1)
            try:
                reports.authorized(spec)
            except RegistryError as error:
                print('DOCX 권한 제한 뒤 과거 출력 승인 거부:',error)
            else:
                raise AssertionError('Expected restricted source refusal')
            print('일반 문서/실제 모델/독립 수업 채택: 보류. Token/청구 비용: 미측정.')
        finally:
            registry.close()


def history():
    record=json.loads((REPORTS/'KEDU-PRODUCTION-016/browser.json').read_text())
    print('과거 실제 브라우저 기록 읽기입니다. 지금 브라우저/모델을 실행하지 않습니다.')
    for case in record['cases']:
        print(case['case'],'화면:',case['ui'])
    print('서버 Router/전송 판정:',[(r['scenario'],r['router_status'],r['status']) for r in record['server_runs']])
    print('완성한 고정 답변 전송:',record['buffered_fixture_delivery'],'/ 실제 모델:',record['actual_model_calls'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['provider','formats','history'],default='provider')
    args=parser.parse_args()
    try:
        {'provider':provider,'formats':formats,'history':history}[args.mode]()
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,f'환경/자료 확인 필요: {error}\n')


if __name__=='__main__':
    main()
