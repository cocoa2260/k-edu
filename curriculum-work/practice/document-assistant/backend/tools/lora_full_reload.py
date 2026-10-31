"""Fresh process reload of a completed full-data LoRA run, cache only."""
import argparse,hashlib,json
from pathlib import Path
from unittest.mock import patch
import requests,torch
from peft import PeftModel
from transformers import AutoTokenizer
from app.training_data import MODEL_ID,REVISION,as_example
from tools.lora_lab import load_model,generate,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--variant',choices=['seed','augmented'],required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[2];config=read(a.run/'configuration.json')
    assert config['model_id']==MODEL_ID and config['revision']==REVISION
    for name,h in config['data_hashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h
    source=as_example(next(e for e in read(root/'data/finetuning-v1/seeds.json')['examples'] if e['split']=='test'))
    attempts=[]
    def blocked(*args,**kwargs):attempts.append('HTTP attempt');raise RuntimeError('Cache-only reload')
    torch.set_num_threads(2);torch.manual_seed(37)
    with patch.object(requests.Session,'request',blocked):
        t=AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,local_files_only=True,trust_remote_code=False)
        m=PeftModel.from_pretrained(load_model(True),a.run/a.variant/'adapter',is_trainable=False).eval()
        m.config.use_cache=True;m.generation_config.use_cache=True
        result=generate(m,source,t)
    prior=read(a.run/a.variant/'test'/f'{source.id}.json')
    result.update(variant=a.variant,token_ids_equal=result['token_ids']==prior['token_ids'],http_attempts=len(attempts),
        adapter_sha256=hashlib.sha256((a.run/a.variant/'adapter/adapter_model.safetensors').read_bytes()).hexdigest())
    save(a.run/f'reload-{a.variant}.json',result)
    assert result['token_ids_equal'] and not attempts
    print(json.dumps(dict(variant=a.variant,token_ids_equal=True,http_attempts=0)))
if __name__=='__main__':main()
