"""Bounded CPU LoRA smoke experiment; no quality acceptance from four steps."""
import argparse,json,time,hashlib,resource,gc
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from peft import LoraConfig,get_peft_model,PeftModel,get_peft_model_state_dict,set_peft_model_state_dict
from app.training_data import MODEL_ID,REVISION,validate_seeds,adopt_candidates,encode_example,messages
from app.rag import check_grounding

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/finetuning-v1'
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def load_model(offline):
    return AutoModelForCausalLM.from_pretrained(MODEL_ID,revision=REVISION,local_files_only=offline,
        trust_remote_code=False,use_safetensors=True,torch_dtype=torch.float32,attn_implementation='eager')
def tensor_row(e,t):
    r=encode_example(e,t)
    return {k:torch.tensor([r[k]]) for k in ['input_ids','attention_mask','labels']}
def evaluate(model,rows,t):
    model.eval();out=[]
    for e in rows:
        with torch.no_grad():loss=float(model(**tensor_row(e,t)).loss)
        out.append(dict(id=e.id,loss=loss))
    return dict(cases=out,macro_mean_loss=sum(r['loss'] for r in out)/len(out),
        note='Per-example mean of teacher-forced token losses, not factual accuracy')
def generate(model,e,t):
    prompt=t.apply_chat_template(messages(e)[:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False,return_tensors='pt')
    start=time.perf_counter()
    with torch.no_grad():ids=model.generate(prompt,attention_mask=torch.ones_like(prompt),max_new_tokens=160,do_sample=False,pad_token_id=t.eos_token_id)
    tokens=ids[0,prompt.shape[1]:].tolist();raw=t.decode(tokens,skip_special_tokens=True)
    draft,failure=check_grounding(raw,{s.source_id:s.model_dump() for s in e.sources})
    return dict(id=e.id,raw_output=raw,token_ids=tokens,output_tokens=len(tokens),seconds=time.perf_counter()-start,
        contract_failure=failure,outcome=draft.outcome if draft else None,
        expected_outcome=e.target.outcome,semantic_quality_accepted=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--download',action='store_true')
    p.add_argument('--reload',type=Path);a=p.parse_args();torch.set_num_threads(2);torch.manual_seed(37)
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    manifest=read(DATA/'split-manifest.json');reviews=read(DATA/'review-manifest.json')
    seeds=validate_seeds(read(DATA/'seeds.json')['examples'],manifest,reviews)
    aug,decisions=adopt_candidates(read(DATA/'augmentation-candidates.json')['examples'],seeds,manifest,reviews)
    t=AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,local_files_only=not a.download,trust_remote_code=False)
    base=load_model(not a.download);base.config.use_cache=False
    test=[e for e in seeds if e.split=='test'];val=[e for e in seeds if e.split=='validation']
    if a.reload:
        model=PeftModel.from_pretrained(base,str(a.reload),is_trainable=False);model.eval()
        result=generate(model,test[0],t);save(a.output/'reload.json',result);return
    summary=dict(model_id=MODEL_ID,revision=REVISION,seed=37,device='cpu',dtype='float32',
        steps_per_condition=4,batch_size=1,learning_rate=0.0002,training_scope='4-example smoke subsets; NOT full 20/28 training comparison',
        qlora=dict(executed=False,cuda_available=torch.cuda.is_available(),torch_cuda=torch.version.cuda,
            reason='This run selects CPU float32 LoRA; bitsandbytes/backend memory compatibility not tested. CPU support exists in documentation, absence of CUDA is not proof of impossibility.'),
        quality_accepted=False,paid_api_calls=0,variants={})
    summary['base']=dict(validation=evaluate(base,val,t),test=evaluate(base,test,t))
    summary['base']['generations']=[generate(base,e,t) for e in test]
    save(a.output/'observed.json',summary);print('base evaluation complete',flush=True)
    model=get_peft_model(base,LoraConfig(r=4,lora_alpha=8,lora_dropout=0.0,target_modules=['q_proj','v_proj'],bias='none',task_type='CAUSAL_LM'))
    initial={k:v.detach().clone() for k,v in get_peft_model_state_dict(model).items()}
    frozen_sample={n:p.detach().flatten()[:16].clone() for n,p in model.named_parameters() if not p.requires_grad}
    summary['trainable_parameters']=sum(p.numel() for p in model.parameters() if p.requires_grad)
    summary['total_parameters']=sum(p.numel() for p in model.parameters())
    assert all('lora_' in n for n,p in model.named_parameters() if p.requires_grad)
    train=[e for e in seeds if e.split=='train']
    choices={'seed':train[:4],'augmented':[train[0],aug[0],train[3],aug[1]]}
    for name,selected in choices.items():
        set_peft_model_state_dict(model,initial);torch.manual_seed(37);model.train()
        optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.0002)
        logs=[];start=time.perf_counter();seen_tokens=0
        for i,e in enumerate(selected,1):
            row=tensor_row(e,t);optimizer.zero_grad(set_to_none=True)
            loss=model(**row).loss;assert torch.isfinite(loss)
            loss.backward();gn=float(torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.0))
            optimizer.step();seen_tokens+=int((row['labels']!=-100).sum())
            logs.append(dict(step=i,id=e.id,loss=float(loss.detach()),gradient_norm=gn))
            print(json.dumps(dict(variant=name,**logs[-1])),flush=True)
        delta=sum(float((v-initial[k]).abs().sum()) for k,v in get_peft_model_state_dict(model).items())
        assert delta>0
        assert all(torch.equal(p.detach().flatten()[:16],frozen_sample[n]) for n,p in model.named_parameters() if n in frozen_sample)
        dest=a.output/(name+'-adapter');model.save_pretrained(dest,safe_serialization=True);t.save_pretrained(a.output/'tokenizer')
        record=dict(logs=logs,optimizer_steps=4,training_seconds=time.perf_counter()-start,supervised_token_exposures=seen_tokens,
            adapter_absolute_delta=delta,frozen_parameter_samples_unchanged=True,
            validation=evaluate(model,val,t),test=evaluate(model,test,t),generations=[generate(model,e,t) for e in test])
        summary['variants'][name]=record;summary['peak_process_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        summary['adapter_file_hashes']={str(f.relative_to(a.output)):hashlib.sha256(f.read_bytes()).hexdigest() for f in a.output.glob('*-adapter/*') if f.is_file()}
        save(a.output/'observed.json',summary);del optimizer;gc.collect()
        print(name+' complete',flush=True)
if __name__=='__main__':main()
