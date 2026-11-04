"""python -m tools.report_lab --output NEW_DIR --font NotoSansKR-Regular.ttf

Run from backend. Actual DOCX+PDF from a fixed teacher fixture, no LLM or human
approval claim. Mark/render the produced documents in the authoring workflow.
"""
import argparse
import json
from pathlib import Path
from app.document_registry import Registry
from app.report_spec import Reports,ReportRejected
from tools.report_export import export


def run(output,font):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    r=Registry(output/'registry.sqlite')
    try:
        meta=dict(id='pdf-policy',version='external-1',title='가상 환불 안내',access='staff',current=True)
        r.upload('data/document-v1/digital.pdf',meta,'pdf');r.parse('pdf-policy',1);r.index('pdf-policy',1);r.review('pdf-policy',1)
        row=r.context(r.search('영수증'))[0]
        txt=output/'policy.txt';txt.write_text('신청 기한 7일\n금액 15000원',encoding='utf-8')
        r.upload(txt,meta|dict(id='txt-policy'),'txt');r.parse('txt-policy',1);r.index('txt-policy',1);r.review('txt-policy',1)
        claims=[dict(id='C1',statement='합성 안내에는 영수증을 함께 제출하도록 적혀 있다.',citations=[dict(doc='pdf-policy',version=1,element=row['element']['id'],quote='영수증을 함께 제출')]),dict(id='C2',statement='합성 텍스트의 신청 기한은 7일이다.',citations=[dict(doc='txt-policy',version=1,element='line-1',quote='신청 기한 7일')])]
        reports=Reports(r);spec=reports.prepare('환불 안내의 제출 자료와 신청 기한',claims)
        pending_blocked=False
        try:reports.authorized(spec)
        except ReportRejected:pending_blocked=True
        reports.decide(spec,'approve','fixture-reviewer','교육용 고정 검토 시연이며 독립 강사 승인 아님')
        export(reports,spec,output/'artifacts',font)
        observed=dict(batch='KEDU-PRODUCTION-014',claim_count=2,citation_count=2,pending_blocked=pending_blocked,review='trusted same-session fixture; no independent human authentication',llm_calls=0,semantic_quality_accepted=False,output_formats=['DOCX','PDF'],document_spec=spec)
        (output/'observed.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(dict(claim_count=2,pending_blocked=pending_blocked,outputs=['artifacts/evidence-report.docx','artifacts/evidence-report.pdf'])))
    finally:r.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',required=True);p.add_argument('--font',required=True);a=p.parse_args();run(a.output,a.font)
