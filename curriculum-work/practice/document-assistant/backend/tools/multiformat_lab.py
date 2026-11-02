"""python -m tools.multiformat_lab --output NEW_DIR --font FONT.ttf

Three actual formats -> Registry/IR -> fixed review -> DOCX/PDF output.
Evaluation is a synthetic software contract suite, not model quality acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from app.document_registry import Registry
from app.report_spec import Reports
from tools.report_export import export


def run(output,font):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);r=Registry(output/'registry.sqlite')
    try:
        gold=json.loads(Path('data/multiformat-v1/gold.json').read_text());cases=[];irs={}
        for name,path in [('pdf',Path('data/document-v1/digital.pdf')),('txt',Path('data/multiformat-v1/policy.txt')),('docx',Path('data/multiformat-v1/policy.docx'))]:
            sha=hashlib.sha256(path.read_bytes()).hexdigest()
            if name!='pdf' and sha!=gold['source_sha256'][path.name]:raise ValueError('Source hash drift')
            if name=='pdf':
                old=json.loads(Path('data/document-v1/gold.json').read_text());assert sha==old['files']['digital.pdf']
            meta=dict(id=name,version='external-v1',title='가상 '+name+' 정책',access='staff',current=True)
            r.upload(path,meta,'upload-'+name);start=time.perf_counter();ir=r.parse(name,1);elapsed=time.perf_counter()-start
            irs[name]=ir;start=time.perf_counter();r.index(name,1);index_seconds=time.perf_counter()-start;r.review(name,1)
            tables=[e for e in ir['elements'] if e['kind']=='table'];expected=gold['docx_table']
            table_exact=bool(tables and tables[0]['rows']==expected) if name in ('pdf','docx') else None
            assert table_exact is not False
            cases.append(dict(format=name,source_sha256=sha,input_bytes=path.stat().st_size,parser=ir['parser'],elements=len(ir['elements']),tables=len(tables),table_exact=table_exact,parse_seconds=round(elapsed,6),index_seconds=round(index_seconds,6),model_calls=0,tokenizer_tokens=None,billed_cost=None))
        # All mutations precede selection/spec preparation.
        selections={name:r.context(r.search('영수증' if name=='pdf' else '15000원' if name=='docx' else '신청 기한')) for name in irs}
        pdf=next(x for x in selections['pdf'] if x['doc']=='pdf')
        txt=next(x for x in selections['txt'] if x['doc']=='txt')
        docx=next(x for x in selections['docx'] if x['doc']=='docx' and x['element']['kind']=='table_cell')
        def claim(id,row,statement,quote):return dict(id=id,statement=statement,citations=[dict(doc=row['doc'],version=row['version'],element=row['element']['id'],quote=quote)])
        claims=[claim('C1',pdf,'합성 PDF는 영수증을 함께 제출하라고 안내한다.','영수증을 함께 제출'),claim('C2',txt,'합성 텍스트는 신청 기한을 7일로 안내한다.','신청 기한은 7일입니다.'),claim('C3',docx,'합성 DOCX의 사용 이력 행 부담금은 15000원으로 표시돼 있다.','15000원')]
        reports=Reports(r);spec=reports.prepare('세 형식의 문단과 표 근거 비교',claims);reports.decide(spec,'approve','fixture-reviewer','원본 대조를 시연하는 고정 결정이며 독립 승인 아님');start=time.perf_counter();export(reports,spec,output/'artifacts',font);export_seconds=time.perf_counter()-start
        r.restrict('docx',1)
        try:reports.authorized(spec);raise AssertionError('Expected stale/restricted source rejection')
        except ValueError:blocked=True
        observed=dict(batch='KEDU-PRODUCTION-017',formats=cases,document_spec=spec,source_irs=irs,fixed_review_only=True,export_seconds=round(export_seconds,6),source_restricted_after_output_blocks_new_export=blocked,existing_files_not_automatically_recalled=True,quality_accepted=False,real_model_calls=0,output_formats=['docx','pdf'],release_gate=dict(status='BLOCKED',software_fixture_contracts='passed',general_document_quality='not_accepted',independent_review='not_run',actual_model_streaming='not_run',qlora='not_run',hwpx_hwp='unsupported',classroom_devices='not_run',foundations_units_unwritten=16))
        (output/'observed.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(formats=cases,release_gate=observed['release_gate']),ensure_ascii=False,indent=2))
    finally:r.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',required=True);p.add_argument('--font',required=True);a=p.parse_args();run(a.output,a.font)
