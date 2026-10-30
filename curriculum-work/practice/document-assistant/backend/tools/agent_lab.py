"""Single-Agent experiment, explicit local model and per-case resume checkpoints."""
import argparse
import json
from pathlib import Path
from app.agent import Registry,Policy,run_agent,ToolTransientError
from app.providers.hf_cpu_provider import HFCpuProvider
from retrieval.encoder import E5Encoder
from retrieval.index import LocalIndex,sha

ROOT=Path(__file__).resolve().parents[2]
BACK=Path(__file__).resolve().parents[1]


def save(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(path)


def all_cases():
    core=json.loads((ROOT/'data/core-v1.json').read_text())['cases']
    extra=json.loads((ROOT/'data/agent-v1.json').read_text())['cases']
    return core+extra


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--download',action='store_true')
    p.add_argument('--resume',action='store_true')
    p.add_argument('--cases',nargs='*')
    args=p.parse_args()
    if args.output.exists() and not args.resume:raise FileExistsError(args.output)
    args.output.mkdir(parents=True,exist_ok=True)
    cases=all_cases();requested=set(args.cases) if args.cases else {c['id'] for c in cases}
    if requested-{c['id'] for c in cases}:raise ValueError('Unknown case')
    encoder=E5Encoder(offline=not args.download);provider=HFCpuProvider(offline=not args.download,max_new_tokens=192)
    config=dict(embedding=encoder.profile,generation=provider.profile,
        data_hashes={name:sha((ROOT/'data'/name).read_text()) for name in ['documents-v1.json','core-v1.json','agent-v1.json']},
        code_hashes={name:sha((BACK/name).read_text()) for name in ['app/agent.py','app/rag.py','app/providers/hf_cpu_provider.py','retrieval/index.py']})
    config_path=args.output/'configuration.json'
    if config_path.exists():
        if json.loads(config_path.read_text())!=config:raise ValueError('Configuration changed; use new folder')
    else:save(config_path,config)
    db=args.output/'index.sqlite'
    index=LocalIndex(db,encoder) if db.exists() else LocalIndex.create(db,encoder,
        json.loads((ROOT/'data/documents-v1.json').read_text())['documents'])
    try:
        for case in cases:
            if case['id'] not in requested:continue
            path=args.output/(case['id']+'.json')
            if path.exists():print(json.dumps(dict(case=case['id'],status='checkpoint_reused')),flush=True);continue
            policy=Policy(manifest_ids=frozenset(case['supplied_manifest_ids']) if 'supplied_manifest_ids' in case else None,
                allow_direct_response=case.get('allow_direct_response',False))
            registry=Registry(index,policy);fault=[False]
            if case['id']=='A05':
                original=registry.handlers['search_documents']
                def flaky(**kwargs):
                    if not fault[0]:fault[0]=True;raise ToolTransientError()
                    return original(**kwargs)
                registry.handlers['search_documents']=flaky
            before=len(provider.observations)
            result=run_agent(registry,provider,case['question'])
            result.update(case_id=case['id'],question=case['question'],
                evidence_kind='actual_cpu_model_actions_and_runtime_dispatch',
                generation_observations=provider.observations[before:],fault_injected=fault[0],paid_api_calls=0,
                policy=dict(role='staff_teaching_fixture_not_authentication',manifest_ids=sorted(policy.manifest_ids) if policy.manifest_ids is not None else None,
                            allow_direct_response=policy.allow_direct_response,approval_count=0))
            save(path,result)
            print(json.dumps(dict(case=case['id'],reason=result['stop_reason'],decisions=result['decisions'],
                tool_attempts=result['tool_attempts'],dispatches=result['tool_dispatches'])),flush=True)
        save(args.output/'index-manifest.json',index.manifest())
    finally:index.close()


if __name__=='__main__':main()
