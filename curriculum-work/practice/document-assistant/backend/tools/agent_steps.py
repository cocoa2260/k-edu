"""Read saved actual-model or scripted Agent records; no inference or writes."""
import argparse
import json
from pathlib import Path


def read_case(path, name):
    data=json.loads(path.read_text())
    kind=data.get('evidence_kind')
    if kind=='actual_CPU_model_actions_and_dispatch':
        row=data['cases'][name];label='과거 실제 모델의 선택·실행 기록'
    elif kind=='observed_scripted_faults_and_real_library_API_not_model_quality':
        row=data['scenarios'][name];label='과거 고정 응답의 제어 실험 (모델 품질 아님)'
    else:
        raise ValueError('Expected a saved aggregate Agent record')
    return label,row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record',type=Path,required=True)
    p.add_argument('--case',default='A02')
    p.add_argument('--raw',action='store_true')
    a=p.parse_args()
    try:
        label,row=read_case(a.record,a.case)
        print(label,'/',a.case,'— 지금 모델/Framework를 실행한 것이 아닙니다.')
        print('질문:',row.get('question','고정 제어 시나리오'))
        for e in row['trace']:
            if e['event']=='action_selected':print('모델/고정 행동:',json.dumps(e['action'],ensure_ascii=False))
            elif e['event']=='tool_observed':print('검사 통과 관찰:',json.dumps(e['observation'],ensure_ascii=False))
            elif e['event'] in ('failure','tool_transient_failure','tool_retry_scheduled'):
                print('실행 사건:',e['event'],e.get('failure_id',e.get('name','')))
        print('종료:',row['stop_reason'])
        print('결정/도구 처리/함수 진입:',row['decisions'],row['tool_attempts'],row['tool_dispatches'])
        print('읽은 출처:',list(row['sources']))
        print('최종 초안:',json.dumps(row['draft'],ensure_ascii=False))
        if a.raw:
            for obs in row.get('generation_observations',[]):print('저장된 모델 원응답:',obs['raw_output'])
    except (OSError,ValueError,KeyError,TypeError) as exc:
        p.exit(2,f'입력/기록 확인 필요: {exc}\n')


if __name__=='__main__':main()
