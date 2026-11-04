"""All-training-row, equal-step LoRA comparison with resumable Agent regressions.

Validation-only selection is persisted before reading Test results. This is one
seed and 28 steps, not proof of convergence or semantic quality.
"""
import argparse,contextlib,gc,hashlib,importlib.metadata as metadata,json,random,resource,time
from pathlib import Path
import torch
from peft import LoraConfig,get_peft_model,get_peft_model_state_dict,set_peft_model_state_dict
from safetensors.torch import load_file
from transformers import AutoTokenizer
from app.training_data import MODEL_ID,REVISION,validate_seeds,adopt_candidates,digest
from app.agent import Registry,Policy,run_agent,ToolTransientError
from app.providers.hf_cpu_provider import HFCpuProvider
from tools.lora_lab import load_model,tensor_row,evaluate,generate,read
from tools.agent_lab import all_cases,save
from retrieval.encoder import E5Encoder
from retrieval.index import LocalIndex

ROOT=Path(__file__).resolve().parents[2];BACK=Path(__file__).resolve().parents[1];DATA=ROOT/'data/finetuning-v1'

def schedule_ids(ids,steps=28,seed=37):
    if not ids or len(ids)!=len(set(ids)) or steps<len(ids):raise ValueError('Must cover all unique training rows')
    rng=random.Random(seed);order=[]
    while len(order)<steps:
        shuffled=list(ids);rng.shuffle(shuffled);order.extend(shuffled)
    return order[:steps]

def verify_config(path,config):
    if path.exists():
        if read(path)!=config:raise ValueError('Configuration/data/code changed; use a new output folder')
    else:save(path,config)

def record_training(model,tokenizer,rows,out,initial):
    path=out/'training.json'
    if path.exists():return read(path)
    out.mkdir(parents=True,exist_ok=True);order=schedule_ids([e.id for e in rows]);by_id={e.id:e for e in rows}
    set_peft_model_state_dict(model,initial);model.train();model.config.use_cache=False;torch.manual_seed(37)
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.0002)
    logs=[];elapsed=0.;start_step=0;progress=out/'progress.json'
    if progress.exists():
        previous=read(progress);checkpoint=out/previous['checkpoint'];state=torch.load(checkpoint/'optimizer.pt',weights_only=True,map_location='cpu')
        set_peft_model_state_dict(model,load_file(checkpoint/'adapter_model.safetensors'))
        optimizer.load_state_dict(state['optimizer']);torch.set_rng_state(state['rng'])
        logs=previous['logs'];elapsed=previous['training_seconds'];start_step=len(logs)
        if previous['schedule']!=order:raise ValueError('Schedule mismatch')
    frozen={n:p.detach().flatten()[:16].clone() for n,p in model.named_parameters() if not p.requires_grad}
    for i in range(start_step,len(order)):
        start=time.perf_counter();e=by_id[order[i]];batch=tensor_row(e,tokenizer)
        optimizer.zero_grad(set_to_none=True);loss=model(**batch).loss
        if not torch.isfinite(loss):raise ValueError('Nonfinite training loss')
        loss.backward();norm=float(torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.))
        optimizer.step();elapsed+=time.perf_counter()-start
        logs.append(dict(step=i+1,id=e.id,loss=float(loss.detach()),gradient_norm=norm,supervised_tokens=int((batch['labels']!=-100).sum())))
        # Write a new immutable step directory, then atomically move the pointer.
        # An interruption cannot mix a newer model with an older optimizer.
        checkpoint=out/('step-%04d'%(i+1))
        model.save_pretrained(checkpoint,safe_serialization=True)
        torch.save(dict(optimizer=optimizer.state_dict(),rng=torch.get_rng_state()),checkpoint/'optimizer.pt')
        save(progress,dict(checkpoint=checkpoint.name,schedule=order,logs=logs,training_seconds=elapsed))
        print(json.dumps(dict(variant=out.name,**logs[-1])),flush=True)
    delta=sum(float((v-initial[k]).abs().sum()) for k,v in get_peft_model_state_dict(model).items())
    assert delta>0 and all(torch.equal(p.detach().flatten()[:16],frozen[n]) for n,p in model.named_parameters() if n in frozen)
    model.save_pretrained(out/'adapter',safe_serialization=True)
    result=dict(schedule=order,unique_rows_seen=len(set(order)),available_rows=len(rows),optimizer_steps=len(logs),
        logs=logs,training_seconds=elapsed,supervised_token_exposures=sum(l['supervised_tokens'] for l in logs),
        adapter_absolute_delta=delta,frozen_weight_samples_unchanged=True,
        trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad),
        total_parameters=sum(p.numel() for p in model.parameters()),initial_adapter_digest=digest({k:hashlib.sha256(v.numpy().tobytes()).hexdigest() for k,v in initial.items()}))
    save(path,result);del optimizer;gc.collect();return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume',action='store_true');p.add_argument('--download',action='store_true')
    p.add_argument('--reload-variant',choices=['seed','augmented']);a=p.parse_args();torch.set_num_threads(2);torch.manual_seed(37)
    if a.output.exists() and not a.resume:raise FileExistsError(a.output)
    a.output.mkdir(parents=True,exist_ok=True)
    config=dict(model_id=MODEL_ID,revision=REVISION,seed=37,steps=28,batch_size=1,r=4,alpha=8,dropout=0.,lr=.0002,
        targets=['q_proj','v_proj'],dtype='float32',threads=2,attn_implementation='eager',generation_use_cache=True,
        SFT_max_new_tokens=160,agent_max_new_tokens=192,validation_selection='lowest macro teacher-forced validation loss; tie -> seed',
        versions={k:metadata.version(k) for k in ['torch','peft','transformers','accelerate','tokenizers']},
        data_hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [*sorted(DATA.glob('*.json')),*[ROOT/'data'/n for n in ['core-v1.json','agent-v1.json','documents-v1.json']]]},
        code_hashes={n:hashlib.sha256((BACK/n).read_bytes()).hexdigest() for n in ['tools/lora_full_lab.py','tools/lora_lab.py','app/training_data.py','app/agent.py','app/rag.py','app/providers/hf_cpu_provider.py','retrieval/index.py','retrieval/encoder.py']})
    verify_config(a.output/'configuration.json',config)
    regressions=all_cases();questions=[e['question'] for e in regressions]
    manifest=read(DATA/'split-manifest.json');reviews=read(DATA/'review-manifest.json')
    seeds=validate_seeds(read(DATA/'seeds.json')['examples'],manifest,reviews,questions)
    aug,_=adopt_candidates(read(DATA/'augmentation-candidates.json')['examples'],seeds,manifest,reviews,questions)
    train=[e for e in seeds if e.split=='train'];val=[e for e in seeds if e.split=='validation'];test=[e for e in seeds if e.split=='test']
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,trust_remote_code=False,local_files_only=not a.download)
    base=load_model(not a.download)
    model=get_peft_model(base,LoraConfig(r=4,lora_alpha=8,lora_dropout=0.,target_modules=['q_proj','v_proj'],bias='none',task_type='CAUSAL_LM',revision=REVISION))
    initial={k:v.detach().clone() for k,v in get_peft_model_state_dict(model).items()}
    if a.reload_variant:
        set_peft_model_state_dict(model,load_file(a.output/a.reload_variant/'adapter/adapter_model.safetensors'));model.eval()
        model.config.use_cache=True;model.generation_config.use_cache=True
        result=generate(model,test[0],tokenizer);previous=read(a.output/a.reload_variant/'test'/f'{test[0].id}.json')
        result['token_ids_equal']=result['token_ids']==previous['token_ids'];assert result['token_ids_equal']
        save(a.output/f'reload-{a.reload_variant}.json',result);return
    for name,rows in [('seed',train),('augmented',train+aug)]:record_training(model,tokenizer,rows,a.output/name,initial)
    model.eval();model.config.use_cache=True;model.generation_config.use_cache=True
    def activate(name):
        if name!='base':set_peft_model_state_dict(model,load_file(a.output/name/'adapter/adapter_model.safetensors'))
        return model.disable_adapter() if name=='base' else contextlib.nullcontext()
    for name in ['base','seed','augmented']:
        dest=a.output/name;dest.mkdir(exist_ok=True);f=dest/'validation.json'
        if not f.exists():
            with activate(name):save(f,evaluate(model,val,tokenizer))
            print(name+' validation complete',flush=True)
    selection=a.output/'selection.json'
    if not selection.exists():
        scores={n:read(a.output/n/'validation.json')['macro_mean_loss'] for n in ['seed','augmented']}
        winner=min(scores,key=lambda n:(scores[n],n!='seed'))
        save(selection,dict(winner=winner,scores=scores,criterion=config['validation_selection'],test_not_read_for_selection=True))
    for name in ['base','seed','augmented']:
        dest=a.output/name
        with activate(name):
            if not (dest/'test-loss.json').exists():save(dest/'test-loss.json',evaluate(model,test,tokenizer))
            (dest/'test').mkdir(exist_ok=True)
            for e in test:
                f=dest/'test'/f'{e.id}.json'
                if not f.exists():save(f,generate(model,e,tokenizer));print(name+' SFT '+e.id,flush=True)
    # Keep the same L5 agent, policy, cases and tool limits. Only weights vary.
    encoder=E5Encoder(offline=not a.download);db=a.output/'regression.sqlite'
    index=LocalIndex(db,encoder) if db.exists() else LocalIndex.create(db,encoder,read(ROOT/'data/documents-v1.json')['documents'])
    try:
        for name in ['base','seed','augmented']:
            dest=a.output/name/'regression';dest.mkdir(exist_ok=True)
            with activate(name):
                provider=HFCpuProvider.__new__(HFCpuProvider);provider.torch=torch;provider.tokenizer=tokenizer;provider.model=model;provider.observations=[]
                provider.profile=dict(model_id=MODEL_ID,revision=REVISION,device='cpu',dtype='float32',threads=2,
                    do_sample=False,enable_thinking=False,max_new_tokens=192,input_token_limit=1536,teaching_total_token_limit=2048)
                for case in regressions:
                    f=dest/(case['id']+'.json')
                    if f.exists():continue
                    policy=Policy(manifest_ids=frozenset(case['supplied_manifest_ids']) if 'supplied_manifest_ids' in case else None,allow_direct_response=case.get('allow_direct_response',False))
                    registry=Registry(index,policy);fault=[False]
                    if case['id']=='A05':
                        original=registry.handlers['search_documents']
                        def flaky(**kwargs):
                            if not fault[0]:fault[0]=True;raise ToolTransientError()
                            return original(**kwargs)
                        registry.handlers['search_documents']=flaky
                    before=len(provider.observations);result=run_agent(registry,provider,case['question'])
                    result.update(case_id=case['id'],question=case['question'],generation_observations=provider.observations[before:],fault_injected=fault[0],paid_api_calls=0)
                    save(f,result);print(json.dumps(dict(variant=name,regression=case['id'],reason=result['stop_reason'])),flush=True)
        save(a.output/'index-manifest.json',index.manifest())
    finally:index.close()
    save(a.output/'completion.json',dict(completed=True,peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,quality_accepted=False,paid_api_calls=0))
if __name__=='__main__':main()
