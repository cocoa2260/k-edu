"""Prepare comparison inputs, never generate or grade model answers."""
import argparse,json
from pathlib import Path
from app.experiments import prepare,VARIANTS
from pydantic import ValidationError

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists() and any(a.output.iterdir()):p.error('Use a new or empty output directory')
 rows=[];samples=[]
 for i in range(1,13):
  for variant in VARIANTS:
   case=f'C{i:02}'
   try:
    d=prepare(case,variant)
    if case=='C01':samples.append(d)
    rows.append({k:v for k,v in d.items() if k!='message'})
   except ValidationError:
    rows.append({'case_id':case,'variant':variant,'status':'input_rejected_before_generation','generation_executed':False})
 a.output.mkdir(parents=True,exist_ok=True)
 for name,data in [('manifest.json',rows),('samples.json',samples)]:
  (a.output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'prepared':sum(d['status']=='prepared_not_generated' for d in rows),'rejected':sum(d['status']=='input_rejected_before_generation' for d in rows),'generation_executed':False}))
if __name__=='__main__':main()
