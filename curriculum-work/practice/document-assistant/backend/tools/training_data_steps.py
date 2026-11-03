"""Read seed/lineage or saved Token labels. No tokenizer, Datasets or training."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/finetuning-v1'
RECORD=ROOT.parents[1]/'reports/KEDU-PRODUCTION-009/token-example.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['data','labels'],default='data')
    p.add_argument('--example',default='FT-T01-S01')
    a=p.parse_args()
    try:
        if a.mode=='data':
            seeds=json.loads((DATA/'seeds.json').read_text())['examples']
            row=next((r for r in seeds if r['id']==a.example),None)
            if row is None:raise ValueError('Unknown seed example')
            print('저장된 교사 예제 읽기입니다. 모델 생성/학습이 아닙니다.')
            print('ID/가족/Split:',row['id'],row['group_id'],row['split'])
            print('질문:',row['question'],'/ 허용 여부:',row['permitted'])
            for s in row['sources']:print('원문:',s['source_id'],s['text'])
            print('교사 정답:',json.dumps(row['target'],ensure_ascii=False))
            for child in json.loads((DATA/'augmentation-candidates.json').read_text())['examples']:
                if child['parent_id']==row['id']:print('파생 후보:',child['id'],child['question'],'정답 유지:',child['target']==row['target'])
            print('원본 Split 수:',{s:sum(r['split']==s for r in seeds) for s in ['train','validation','test']})
        else:
            r=json.loads(RECORD.read_text());ids=r['input_ids'];labels=r['labels']
            if len(ids)!=len(labels):raise ValueError('Saved length mismatch')
            positions=[i for i,x in enumerate(labels) if x!=-100]
            if not positions:raise ValueError('No supervised labels')
            if any(labels[i]!=ids[i] for i in positions):raise ValueError('Saved label mismatch')
            print('과거 실제 Tokenizer의 저장 결과 읽기입니다. 지금 Tokenizer/훈련을 실행하지 않습니다.')
            print('예제:',r['id'],'전체/Prefix/정답:',len(ids),r['prompt_tokens'],len(positions))
            print('정답 위치(0부터):',positions[0],'~',positions[-1])
            print('정답 복원 저장값:',r['supervised_decoded'])
            print('마지막 위치 label:',labels[-1],'/ -100은 Token ID가 아니라 Loss 제외 표식입니다.')
    except (OSError,ValueError,KeyError,TypeError) as exc:p.exit(2,f'자료/기록 확인 필요: {exc}\n')


if __name__=='__main__':main()
