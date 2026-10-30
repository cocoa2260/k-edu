"""Actual local E5 -> Context -> Qwen RAG. Atomic per-case checkpoints allow resume."""
import argparse
import json
from pathlib import Path
import time

from app.providers.hf_cpu_provider import HFCpuProvider
from app.rag import run_rag
from retrieval.encoder import E5Encoder
from retrieval.index import LocalIndex,sha

ROOT=Path(__file__).resolve().parents[2]


def save(path,value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--download',action='store_true')
    p.add_argument('--resume',action='store_true')
    p.add_argument('--cases',nargs='*')
    p.add_argument('--comparisons',action='store_true')
    p.add_argument('--prompt-revision',choices=['v1','v2'],default='v2')
    args=p.parse_args()
    if args.output.exists() and not args.resume:raise FileExistsError(args.output)
    args.output.mkdir(parents=True,exist_ok=True)
    documents=json.loads((ROOT/'data/documents-v1.json').read_text())['documents']
    cases=json.loads((ROOT/'data/core-v1.json').read_text())['cases']
    requested=set(args.cases) if args.cases else {c['id'] for c in cases}
    if requested-{c['id'] for c in cases}:raise ValueError('Unknown case')
    encoder=E5Encoder(offline=not args.download)
    provider=HFCpuProvider(offline=not args.download)
    config=dict(embedding=encoder.profile,generation=provider.profile,
        data_sha256={name:sha((ROOT/'data'/name).read_text()) for name in ['documents-v1.json','core-v1.json']},
        rag_code_sha256=sha((Path(__file__).resolve().parents[1]/'app/rag.py').read_text()),
        method='hybrid',k=3,baseline_neighbors=False,prompt_revision=args.prompt_revision)
    config_path=args.output/'configuration.json'
    if config_path.exists():
        if json.loads(config_path.read_text())!=config:raise ValueError('Configuration changed; use new output directory')
    else:save(config_path,config)
    index_path=args.output/'index.sqlite'
    index=LocalIndex(index_path,encoder) if index_path.exists() else LocalIndex.create(index_path,encoder,documents)
    jobs=[(c,c['id'],{}) for c in cases if c['id'] in requested]
    if args.comparisons:
        jobs.extend([(next(c for c in cases if c['id']=='C07'),'C07-rewrite',
                        dict(search_query='국내 당일 출장 식비 규정 상한 조건')),
                     (next(c for c in cases if c['id']=='C09'),'C09-neighbors',dict(neighbors=True))])
    try:
        for case,name,settings in jobs:
            target=args.output/(name+'.json')
            if target.exists():
                print(json.dumps(dict(case=name,status='checkpoint_reused')),flush=True);continue
            start=time.perf_counter();before=len(provider.observations)
            result=run_rag(index,provider,case['question'],case_id=case['id'],
                manifest_ids=set(case['supplied_manifest_ids']),prompt_revision=args.prompt_revision,**settings)
            result.update(case_id=case['id'],experiment=name,question=case['question'],
                actual_generation_observations=provider.observations[before:],
                elapsed_case_seconds=round(time.perf_counter()-start,4),
                evidence_kind='actual_cpu_E5_and_Qwen_not_scripted',paid_api_calls=0)
            save(target,result)
            print(json.dumps(dict(case=name,status=result['status'],reason=result['stop_reason'],
                calls=result['calls'],seconds=result['elapsed_case_seconds'])),flush=True)
        save(args.output/'index-manifest.json',index.manifest())
    finally:index.close()


if __name__=='__main__':main()
