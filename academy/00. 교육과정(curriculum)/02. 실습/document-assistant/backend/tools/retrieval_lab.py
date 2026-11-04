"""Actual CPU embeddings and exact retrieval. No answer-generation provider."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import platform
import time

from retrieval.encoder import E5Encoder
from retrieval.index import LocalIndex, ProfileMismatch, StaleSelection

ROOT=Path(__file__).resolve().parents[2]


def measure(index,cases,labels):
    rows=[]
    for case in cases:
        for method in ('bm25','dense','hybrid'):
            started=time.perf_counter()
            try:
                selection=index.search(case['question'],method=method,k=3,
                    manifest_ids=set(case['supplied_manifest_ids']))
                context=index.context(selection)
            except ValueError:
                if case['id']!='C10': raise
                rows.append(dict(case_id=case['id'],method=method,status='input_rejected',hits=[]))
                continue
            assert all(h['doc_id'] not in ('DOC-R','DOC-A-OLD') for h in selection['hits'])
            assert all(c['doc_id'] not in ('DOC-R','DOC-A-OLD') for c in context)
            assert 'SYNTHETIC-RESTRICTED-314159' not in str(selection)+str(context)
            if case['id']=='C12':
                assert all(h['doc_id']!='DOC-A' for h in selection['hits'])
            relevant=set(labels.get(case['id'],[]))
            retrieved={h['doc_id'] for h in selection['hits']}
            rows.append(dict(case_id=case['id'],method=method,status='retrieved',
                elapsed_ms=round((time.perf_counter()-started)*1000,4),
                eligible_chunks=selection['eligible_chunks'],hits=selection['hits'],
                document_recall_at_3_chunks=len(relevant & retrieved)/len(relevant) if relevant else None,
                any_relevant_at_1=selection['hits'][0]['doc_id'] in relevant if relevant else None,
                context_document_ids=[c['doc_id'] for c in context]))
    metrics={}
    for method in ('bm25','dense','hybrid'):
        scored=[r for r in rows if r['method']==method and r.get('document_recall_at_3_chunks') is not None]
        metrics[method]=dict(scored_cases=len(scored),
            mean_document_recall_at_3_chunks=sum(r['document_recall_at_3_chunks'] for r in scored)/len(scored),
            relevant_hit_at_1=sum(r['any_relevant_at_1'] for r in scored)/len(scored))
    return rows,metrics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--download',action='store_true',help='Allow pinned model download; never paid inference')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    documents=json.loads((ROOT/'data/documents-v1.json').read_text())['documents']
    cases=json.loads((ROOT/'data/core-v1.json').read_text())['cases']
    # Separate teacher relevance labels; NEVER passed to the search encoder.
    labels=json.loads((ROOT/'data/retrieval-v1.json').read_text())['relevant_document_ids']
    started=time.perf_counter()
    encoder=E5Encoder(offline=not args.download)
    model_load_seconds=time.perf_counter()-started
    index=LocalIndex.create(args.output/'index.sqlite',encoder,documents)
    manifest=index.manifest()
    rows,metrics=measure(index,cases,labels)
    before=index.search('국내 당일 출장 식비 상한',k=3)
    updated=deepcopy(documents[0]);updated['version']='v2-teaching-override'
    updated['text']='1. 갱신 시험용 가상 국내 당일 출장 식비 상한은 35000원이다. 사전 승인·영수증이 필요하다.'
    index.upsert(updated)
    try: index.context(before); raise AssertionError('Stale selection accepted')
    except StaleSelection: stale_after_update=True
    after_update=index.search('국내 당일 출장 식비 상한',k=3)
    context_after_update=index.context(after_update)
    assert any(c['doc_id']=='DOC-A' and c['version']==updated['version'] and '35000' in c['text'] for c in context_after_update)
    assert all('30000' not in c['text'] for c in context_after_update if c['doc_id']=='DOC-A')
    index.delete('DOC-A')
    try: index.context(after_update); raise AssertionError('Deleted selection accepted')
    except StaleSelection: stale_after_delete=True
    after_delete=index.search('국내 당일 출장 식비 상한',k=10)
    assert all(c['doc_id']!='DOC-A' for c in index.context(after_delete))
    lifecycle=dict(stale_after_update_rejected=stale_after_update,
        context_after_update=context_after_update,stale_after_delete_rejected=stale_after_delete,
        after_delete_document_ids=[h['doc_id'] for h in after_delete['hits']],
        after_delete_manifest=index.manifest(),
        note='Temporary SQLite mutation only. Original documents-v1 remains v1 with 30000.')
    index.close()
    # Same weights with a different Token-limit profile: reject reuse, then rebuild.
    encoder.profile['max_tokens']=128
    try: LocalIndex(args.output/'index.sqlite',encoder); raise AssertionError('Old profile accepted')
    except ProfileMismatch: rejected=True
    rebuilt=LocalIndex.create(args.output/'rebuilt.sqlite',encoder,documents)
    rebuilt_result=rebuilt.search('국내 당일 출장 식비 상한',k=3)
    migration=dict(profile_mismatch_rejected=rejected,rebuild_manifest=rebuilt.manifest(),
        result=rebuilt_result,kind='same_model_different_max_tokens_profile',different_weight_model_tested=False)
    rebuilt.close()
    result=dict(evidence_kind='actual_pinned_embedding_and_sqlite_search_cpu',
        answer_generation_calls=0,paid_api_calls=0,model_load_seconds=round(model_load_seconds,4),
        python=platform.python_version(),platform=platform.platform(),
        manifest_before_mutation=manifest,cases=rows,metrics=metrics,lifecycle=lifecycle,migration=migration,
        factual_answer_quality=None,remarks=['tiny fictional corpus; no production latency claim',
            'dense scores are ranking signals, not answerability or trust scores',
            'C12 scopes the searchable manifest; lifecycle separately mutates the actual index'])
    (args.output/'observed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(metrics=metrics,lifecycle_verified=True,profile_rebuild_verified=True),ensure_ascii=False))


if __name__=='__main__': main()
