"""Actual sequential role calls, one shared CPU model, resumable per-case outputs."""
import argparse
import json
from pathlib import Path
import time
from app.agent import Policy
from app.multi_agent import MultiRuntime
from app.providers.hf_cpu_provider import HFCpuProvider
from retrieval.encoder import E5Encoder
from retrieval.index import LocalIndex,sha
from tools.agent_lab import all_cases,save

ROOT=Path(__file__).resolve().parents[2];BACK=Path(__file__).resolve().parents[1]


class RecordedProvider:
    def __init__(self,provider):
        self.inner=provider;self.provider_name=provider.provider_name;self.model_name=provider.model_name
        self.profile=provider.profile;self.observations=[]
    def generate(self,message):
        before=len(self.inner.observations)
        try:return self.inner.generate(message)
        finally:
            for item in self.inner.observations[before:]:
                self.observations.append(dict(item,role=message.split('.',1)[0].removeprefix('Role: '),
                    actual_input_message=message,prompt_sha256=sha(message)))


def seed_evidence(runtime,question):
    # Explicit isolated role probe setup, NOT a model-generated research handoff.
    selected=runtime.registry.invoke('search_documents',dict(query=question,k=1))
    if selected['hits']:
        key=selected['hits'][0]['source_id'];runtime.registry.invoke('read_evidence',dict(source_id=key))
        runtime.evidence={key:runtime.registry.read_sources[key]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--resume',action='store_true');p.add_argument('--download',action='store_true')
    p.add_argument('--cases',nargs='*');p.add_argument('--role-probes',action='store_true');args=p.parse_args()
    if args.output.exists() and not args.resume:raise FileExistsError(args.output)
    args.output.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();encoder=E5Encoder(offline=not args.download)
    provider=RecordedProvider(HFCpuProvider(offline=not args.download,max_new_tokens=192))
    load_seconds=time.perf_counter()-start
    config=dict(embedding=encoder.profile,generation=provider.profile,
        data_hashes={name:sha((ROOT/'data'/name).read_text()) for name in ['documents-v1.json','core-v1.json','agent-v1.json']},
        code_hashes={name:sha((BACK/name).read_text()) for name in ['app/multi_agent.py','app/agent.py','app/rag.py','app/providers/hf_cpu_provider.py','retrieval/index.py']})
    cp=args.output/'configuration.json'
    if cp.exists():
        if json.loads(cp.read_text())!=config:raise ValueError('Configuration changed; use new folder')
    else:save(cp,config)
    save(args.output/'last-initialization.json',dict(model_and_encoder_load_seconds=round(load_seconds,4),scope='outside case latency'))
    db=args.output/'index.sqlite';documents=json.loads((ROOT/'data/documents-v1.json').read_text())['documents']
    index=LocalIndex(db,encoder) if db.exists() else LocalIndex.create(db,encoder,documents)
    cases=all_cases();requested=set(args.cases) if args.cases else {c['id'] for c in cases}
    if requested-{c['id'] for c in cases}:raise ValueError('Unknown case')
    try:
        for case in cases:
            if case['id'] not in requested:continue
            target=args.output/(case['id']+'.json')
            if target.exists():print(json.dumps(dict(case=case['id'],status='checkpoint_reused')),flush=True);continue
            runtime=MultiRuntime(index,provider,Policy(
                manifest_ids=frozenset(case['supplied_manifest_ids']) if 'supplied_manifest_ids' in case else None,
                allow_direct_response=case.get('allow_direct_response',False)))
            fault=[False]
            if case['id']=='A05':
                from app.agent import ToolTransientError
                original=runtime.registry.handlers['search_documents']
                def flaky(**kwargs):
                    if not fault[0]:fault[0]=True;raise ToolTransientError()
                    return original(**kwargs)
                runtime.registry.handlers['search_documents']=flaky
            before=len(provider.observations);result=runtime.run(case['question'],case['id'])
            result.update(case_id=case['id'],question=case['question'],generation_observations=provider.observations[before:],
                evidence_kind='actual_multi_role_model_calls',fault_injected=fault[0],paid_api_calls=0)
            save(target,result)
            print(json.dumps(dict(case=case['id'],reason=result['stop_reason'],budget=result['budget'])),flush=True)
        if args.role_probes:
            for role in ['writer','reviewer']:
                target=args.output/(role+'-probe.json')
                if target.exists():continue
                runtime=MultiRuntime(index,provider);seed_evidence(runtime,'국내 당일 출장 식비 상한')
                runtime.role=role
                if role=='reviewer':
                    runtime.draft=dict(outcome='abstain',answer='자료가 부족합니다.',claims=[])
                before=len(provider.observations)
                try:
                    action=runtime.ask(role,'국내 당일 출장 식비 상한과 필요한 자료는?')
                    result=dict(action=action.model_dump(),failure_id=None)
                except Exception as exc:result=dict(action=None,failure_id=type(exc).__name__)
                result.update(evidence_kind='isolated_role_probe_with_runtime_seeded_evidence_NOT_integrated_success',
                    role=role,generation_observations=provider.observations[before:],sources=runtime.evidence,
                    budget=runtime.ledger.snapshot(),paid_api_calls=0)
                save(target,result);print(json.dumps(dict(role_probe=role,failure_id=result['failure_id'])),flush=True)
        save(args.output/'index-manifest.json',index.manifest())
    finally:index.close()


if __name__=='__main__':main()
