"""Read saved multi-role/fixture records. No model, tool execution or writes."""
import argparse
import json
from pathlib import Path


def select(path, name):
    data=json.loads(path.read_text())
    kind=data.get('evidence_kind','')
    if 'scenarios' in data and kind=='observed_scripted_M01_M04_not_model_quality':
        label='과거 고정 응답 경계 실험 (실제 모델 품질 아님)'
        if name=='control':row=data['control']
        elif name.startswith('M04/'):
            row=data['scenarios']['M04'][name.split('/',1)[1]]
        else:row=data['scenarios'][name]
    elif 'cases' in data and kind=='actual_sequential_CPU_roles_NOT_quality_acceptance':
        # Require the aggregate's known actual case marker, not a fixture labelled as actual.
        row=data['cases'][name]
        if row.get('evidence_kind')!='actual_multi_role_model_calls':
            raise ValueError('Expected a saved actual multi-role case')
        label='과거 실제 모델의 역할 실행 기록'
    else:raise ValueError('Expected a saved Multi-Agent aggregate record')
    return label,row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record',type=Path,required=True);p.add_argument('--case',default='A02')
    p.add_argument('--input',action='store_true',help='Show stored Template-before role messages; not new Tokenizer output')
    a=p.parse_args()
    try:
        label,r=select(a.record,a.case);print(label,'/',a.case,'— 지금 모델을 실행한 것이 아닙니다.')
        print('질문:',r.get('question','가상 meal 규정의 고정 실험'))
        for e in r['trace']:
            if e['event']=='role_action':print('역할/행동:',e['role'],json.dumps(e['action'],ensure_ascii=False))
            elif e['event']=='handoff_validated':
                h=e['handoff'];print('검증된 전달:',h['role_id'],'→',h['target_role'],h['evidence_ids'],'예산',h['budget_used'])
            elif e['event'] in ('failure','repair_consumed','evidence_requested','review_repair_requested','tool_transient_retry','model_transient_retry'):
                print('사건:',e['event'],e.get('failure_id',''),'예산',e['budget'])
        print('전체/역할 누적:',r['budget']);print('종료:',r['stop_reason'])
        print('최종 전달용 초안:',json.dumps(r['draft'],ensure_ascii=False))
        print('부분 초안:',json.dumps(r['partial_draft'],ensure_ascii=False))
        print('승인:',r['approval_granted'],'/ 의미 검증:',r['semantic_grounding_verified'])
        if a.input:
            for o in r.get('generation_observations',[]):
                print('저장된 역할 입력 (Chat Template 적용 전):',o['role'],o['actual_input_message'])
    except (OSError,ValueError,KeyError,TypeError) as exc:p.exit(2,f'입력/기록 확인 필요: {exc}\n')


if __name__=='__main__':main()
