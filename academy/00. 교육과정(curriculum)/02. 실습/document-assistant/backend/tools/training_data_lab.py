"""L7 local JSON -> Datasets -> pinned tokenizer/labels -> Arrow reload. No training."""
import argparse
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import time
from app.training_data import (MODEL_ID,REVISION,Example,validate_seeds,adopt_candidates,
    encode_example,messages,pad_batch,digest,text_hash)

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/finetuning-v1'
def load(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def export_row(e):
    row=e.model_dump();row['sources_json']=json.dumps(row.pop('sources'),ensure_ascii=False)
    row['target_json']=json.dumps(row.pop('target'),ensure_ascii=False)
    return row

def import_row(row):
    keys=['id','group_id','split','task','parent_id','method','permitted','question']
    return Example.model_validate(dict(**{k:row[k] for k in keys},
        sources=json.loads(row['sources_json']),target=json.loads(row['target_json'])))

def toy_loss_probe(batch):
    """Synthetic 17-class logits at REAL mask positions; NOT an LM training loss."""
    import torch
    torch.set_num_threads(2);torch.manual_seed(37)
    labels=torch.tensor(batch['labels']);projected=torch.where(labels==-100,labels,labels%17)
    logits=torch.randn((*labels.shape,17),requires_grad=True)
    shifted_labels=projected[:,1:];shifted_logits=logits[:,:-1,:]
    loss=torch.nn.functional.cross_entropy(shifted_logits.reshape(-1,17),shifted_labels.reshape(-1),ignore_index=-100)
    loss.backward();gradient=logits.grad[:,:-1,:].abs().sum(-1)
    assert gradient[shifted_labels==-100].sum().item()==0
    assert (gradient[shifted_labels!=-100]>0).all().item()
    padded=torch.tensor(batch['attention_mask'])==0
    assert (labels[padded]==-100).all().item()
    return dict(evidence_kind='SYNTHETIC_LOGITS_MASK_PROBE_NOT_MODEL_LOSS',toy_loss=loss.item(),
        direct_logit_gradient_at_ignored_targets=0,supervised_positions_have_gradient=True,
        padding_labels_ignored=True,causal_shift_once=True,optimizer_steps=0,
        note='Ignored target positions have no direct loss; this does NOT stop indirect gradients through prompt context in a real Transformer.')

def run(output,*,download=False):
    if output.exists():raise FileExistsError(output)
    output.mkdir(parents=True);start=time.perf_counter()
    from datasets import load_dataset,load_from_disk,Features,Value
    from transformers import AutoTokenizer
    manifest=load(DATA/'split-manifest.json');reviews=load(DATA/'review-manifest.json')
    regression=[c['question'] for f in ['core-v1.json','agent-v1.json'] for c in load(ROOT/'data'/f)['cases']]
    seeds=validate_seeds(load(DATA/'seeds.json')['examples'],manifest,reviews,regression)
    augmented,decisions=adopt_candidates(load(DATA/'augmentation-candidates.json')['examples'],seeds,manifest,reviews,regression)
    all_rows=seeds+augmented
    keys=['id','group_id','split','task','parent_id','method','question','sources_json','target_json']
    features=Features({**{key:Value('string') for key in keys},'permitted':Value('bool')})
    files={};export_hashes={}
    for split in ['train','validation','test']:
        p=output/(split+'.jsonl')
        p.write_text(''.join(json.dumps(export_row(e),ensure_ascii=False)+'\n' for e in all_rows if e.split==split))
        files[split]=str(p);export_hashes[p.name]=text_hash(p.read_text())
    dataset=load_dataset('json',data_files=files,features=features,cache_dir=str(output/'datasets-cache'))
    loaded_counts={k:len(v) for k,v in dataset.items()}
    filtered=dataset.filter(lambda row:bool(row['question'].strip()),load_from_cache_file=False)
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,local_files_only=not download,trust_remote_code=False)
    def encode(row):return encode_example(import_row(row),tokenizer)
    prepared=filtered.map(encode,load_from_cache_file=False)
    prepared.save_to_disk(str(output/'arrow'))
    reloaded=load_from_disk(str(output/'arrow'))
    before={k:[row for row in v] for k,v in prepared.items()};after={k:[row for row in v] for k,v in reloaded.items()}
    assert digest(before)==digest(after)
    first=import_row(filtered['train'][0]);encoded=encode_example(first,tokenizer)
    first_chat=messages(first)
    trace=dict(id=first.id,messages=first_chat,
        rendered=tokenizer.apply_chat_template(first_chat,tokenize=False,add_generation_prompt=False,enable_thinking=False),
        **encoded,supervised_decoded=tokenizer.decode([x for x in encoded['labels'] if x!=-100],skip_special_tokens=False))
    save(output/'token-example.json',trace)
    # Pick two lengths so real right padding is observed, even when PAD == EOS.
    train_rows=before['train'];short=min(train_rows,key=lambda r:r['total_tokens']);long=max(train_rows,key=lambda r:r['total_tokens'])
    batch=pad_batch([short,long],tokenizer.eos_token_id)
    save(output/'batch-example.json',dict(ids=[short['id'],long['id']],pad_token_id=tokenizer.eos_token_id,**batch))
    loss_probe=toy_loss_probe(batch)
    stats={k:dict(rows=len(v),min_tokens=min(r['total_tokens'] for r in v),max_tokens=max(r['total_tokens'] for r in v),
        supervised_tokens=sum(r['supervised_tokens'] for r in v),ids=[r['id'] for r in v],
        groups=sorted({r['group_id'] for r in v})) for k,v in before.items()}
    observation=dict(evidence_kind='ACTUAL_DATASETS_AND_PINNED_TOKENIZER_PREPARATION_NO_TRAINING',
        versions={k:metadata.version(k) for k in ['datasets','pyarrow','pandas','transformers','tokenizers','torch','pydantic']},
        python=platform.python_version(),tokenizer=dict(model_id=MODEL_ID,revision=REVISION,
            chat_template_sha256=text_hash(tokenizer.chat_template),native_generation_tags_present='{% generation' in tokenizer.chat_template,
            mask_method='verified single-turn token prefix, assistant target through EOS, trailing newline ignored',
            enable_thinking=False,max_length=512,no_truncation=True,eos_token_id=tokenizer.eos_token_id),
        input_hashes={p.name:text_hash(p.read_text()) for p in sorted(DATA.glob('*.json'))},
        code_hashes={p:text_hash((Path(__file__).resolve().parents[1]/p).read_text()) for p in
            ['app/training_data.py','tools/training_data_lab.py','app/rag.py']},
        seed_examples=len(seeds),seed_train_examples=sum(e.split=='train' for e in seeds),
        augmentation_candidates=len(decisions),accepted_augmentations=len(augmented),augmentation_decisions=decisions,
        dataset_features={k:str(v) for k,v in features.items()},loaded_counts=loaded_counts,
        filter_removed={k:loaded_counts[k]-len(filtered[k]) for k in filtered},
        filter_note='Rows already reviewed before export; filter removes blank questions only, not a semantic quality judge.',
        map_added_fields=['input_ids','attention_mask','labels','prompt_tokens','supervised_tokens','total_tokens'],
        splits=stats,export_hashes=export_hashes,arrow_save_reload_equal=True,reloaded_content_sha256=digest(after),
        total_prepared_rows=sum(len(v) for v in before.values()),
        loss_probe=loss_probe,actual_model_generations=0,optimizer_steps=0,paid_api_calls=0,
        quality_accepted=False,independent_review=False,elapsed_seconds=round(time.perf_counter()-start,4))
    save(output/'observed.json',observation)
    return observation

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--download',action='store_true');a=p.parse_args()
    o=run(a.output,download=a.download)
    print(json.dumps(dict(rows=o['total_prepared_rows'],splits={k:v['rows'] for k,v in o['splits'].items()},
        accepted=o['accepted_augmentations'],arrow_reload_equal=True,optimizer_steps=0)))

if __name__=='__main__':main()
