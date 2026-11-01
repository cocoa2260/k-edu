"""python -m tools.registry_lab --output NEW_DIR (from backend)

Actual PDF+UTF8 registry, lifecycle filtering, no model/vector/web integration.
"""
import argparse
import json
from pathlib import Path
from app.document_registry import Registry, RegistryError


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    r=Registry(output/'registry.sqlite')
    metadata=dict(id='pdf-policy',version='external-1',title='합성 PDF',access='staff',current=True)
    try:
        uploaded=r.upload(Path('data/document-v1/digital.pdf'),metadata,'pdf-first')
        ir=r.parse('pdf-policy',1);r.index('pdf-policy',1);r.review('pdf-policy',1)
        selection=r.search('영수증');context=r.context(selection)
        txt=output/'policy.txt';txt.write_text('신청 기한 7일\n금액 15000원',encoding='utf-8')
        r.upload(txt,metadata|dict(id='text-policy'),'text-first');text_ir=r.parse('text-policy',1);r.index('text-policy',1)
        text_context=r.context(r.search('15000'))
        replay=r.upload(txt,metadata|dict(id='text-policy'),'text-first')
        stale=r.search('15000');r.upload(txt,metadata|dict(id='text-policy'),'text-v2')
        blocked={}
        try:r.context(stale)
        except RegistryError:blocked['old_selection_after_version_change']=True
        r.parse('text-policy',2);r.index('text-policy',2);r.restrict('text-policy',2)
        blocked['restricted_absent']=not any(h['doc']=='text-policy' for h in r.search('15000')['hits'])
        r.delete('pdf-policy',1);r.close();r=Registry(output/'registry.sqlite')
        blocked['deleted_absent_after_reopen']=not r.search('영수증')['hits']
        row=r.db.execute("SELECT source,ir FROM docs WHERE id='pdf-policy'").fetchone()
        blocked['deleted_source_ir_cleared']=row['source'] is None and row['ir'] is None
        assert context and text_context and all(blocked.values())
        result=dict(batch='KEDU-PRODUCTION-013',scope=['K2-14.U01','K2-14.U02'],formats_executed=['PDF','UTF8 TXT'],pdf_upload=uploaded,pdf_ir=ir,pdf_context=context,text_ir=text_ir,text_context=text_context,idempotent_replay=replay,boundaries=blocked,search='literal substring; no vectors or ranking',llm_calls=0,vision_calls=0,quality_accepted=False,remaining=['DOCX/HWPX/HWP adapters','report rendering','Provider/SSE/React','real authentication','concurrent workers and secure deletion/backups'])
        (output/'observed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(dict(formats=result['formats_executed'],boundaries=blocked,pdf_elements=len(ir['elements'])),ensure_ascii=False))
    finally:r.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',required=True);run(p.parse_args().output)
