"""Count prepared samples with the pinned reference tokenizer, not a runtime claim."""
import argparse,json,hashlib,importlib.metadata
from pathlib import Path
from transformers import AutoTokenizer
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():p.error('Output exists; keep prior evidence')
profile=json.loads((Path(__file__).resolve().parents[4]/'practice/huggingface-tokenizer/models.json').read_text())['profiles'][0]
t=AutoTokenizer.from_pretrained(profile['model_id'],revision=profile['revision'],local_files_only=True,trust_remote_code=False)
rows=[]
for d in json.loads(a.input.read_text()):
 ids=t.apply_chat_template([{'role':'user','content':d['message']}],tokenize=True,add_generation_prompt=True,**profile['template_kwargs'])
 rows.append({'case_id':d['case_id'],'variant':d['variant'],'characters':d['character_count'],'reference_input_tokens':len(ids),'reference_ceiling':2048,'output_reserve':256,'fits_reference_budget':len(ids)+256<=2048})
result={'scope':'reference tokenizer including user chat template; not Ollama runtime capacity certification','model_id':profile['model_id'],'revision':profile['revision'],'transformers':importlib.metadata.version('transformers'),'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'generation_executed':False,'runtime_token_budget_verified':False,'rows':rows}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
