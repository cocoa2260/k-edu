"""Readable saved RAG observations and a teacher-made checker counterexample.

Record modes require only the standard library. The counterexample imports the
existing Pydantic checker; no mode loads an encoder/generator or writes records.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load_record(path):
    data = json.loads(path.read_text())
    if data.get('evidence_kind')!='actual_CPU_E5_and_Qwen' or data.get('paid_api_calls')!=0:
        raise ValueError('Expected the saved aggregate actual E5/Qwen record, not a fixture or one-case file')
    return data


def case(data, version, name):
    row = data['versions'][version][name]
    if row.get('evidence_kind')!='actual_cpu_E5_and_Qwen_not_scripted' or row.get('paid_api_calls')!=0:
        raise ValueError('This case is not the expected actual local-generation record')
    return row


def reconstructed_inputs(row):
    """Reconstruct harness strings and verify EVERY stored call hash, not token IDs."""
    if not row.get('calls'):
        return []
    original = row['prepared_message'].strip()
    message, calls = original, []
    for event in row['trace']:
        if event['event']=='call_started':
            if digest(message)!=event['prompt_sha256']:
                raise ValueError('Input reconstruction does not match saved call hash')
            calls.append(message)
        elif event['event']=='repair_scheduled':
            message = original + f"\n검사 실패 ID: {event['failure_id']}. 원래 질문과 자료는 유지하고 출력 계약만 보완하라."
    if len(calls)!=row['calls']:
        raise ValueError('Saved calls/trace count mismatch')
    return calls


def show_case(data, version, name, show_input=False):
    row = case(data,version,name)
    inputs = reconstructed_inputs(row)
    print(f'저장된 실제 RAG 기록 읽기: {version} / {name}')
    print('지금 모델을 실행한 결과가 아닙니다. 형식 통과는 의미/승인이 아닙니다.')
    print('원 질문:',row['question'])
    retrieval = row.get('retrieval')
    if retrieval:
        print('검색 질의:',retrieval['query'],'/ 인접 줄 확장:',retrieval['neighbors'])
        for sid, source in retrieval['sources'].items():
            print('전달 자료:',sid,'|',source['text'])
    for number, obs in enumerate(row.get('actual_generation_observations',[]),1):
        print(f"\n저장된 호출{number}: Template 포함 입력 {obs['input_tokens']} Token, 새 출력 {obs['output_tokens']} Token")
        print('저장된 모델 원응답:')
        print(obs['raw_output'])
    for event in row.get('trace',[]):
        if event['event'] in ('output_checked','repair_scheduled','stopped'):
            print('실행 사건:',event['event'],event.get('failure_id') or event.get('reason'))
    print('최종 초안:',json.dumps(row.get('draft'),ensure_ascii=False))
    print('종료:',row['stop_reason'],'/ 기술적 실패 구간:',row.get('failure_stage'))
    if row['calls']:
        print('의미 검증:',row.get('semantic_grounding_verified'),'→ 원문과 사람의 대조가 필요합니다.')
    else:
        print('생성 전 거부: 모델 원응답과 의미 평가가 없습니다.')
    print('호출 문자열 재구성/저장 해시 일치:',len(inputs),'회. Tokenizer를 새로 실행한 것은 아닙니다.')
    if show_input:
        for number, message in enumerate(inputs,1):
            print(f'\n호출{number} 문자열 재구성 (Chat Template 적용 전, 저장 해시 일치):')
            print(message)


def show_comparison(data, version, kind):
    if kind=='prompt':
        pairs=[('v1','C01'),('v2','C01')]
    elif kind=='rewrite':
        pairs=[(version,'C07'),(version,'C07-rewrite')]
    else:
        pairs=[(version,'C09'),(version,'C09-neighbors')]
    print('저장된 비교 읽기입니다. 새 모델 실행이나 자동 채점이 아닙니다.')
    previous = None
    for ver,name in pairs:
        row=case(data,ver,name);reconstructed_inputs(row)
        print(f'\n{ver} / {name}')
        print('원 질문:',row['question'],'/ 검색 질의:',row['retrieval']['query'])
        sources=row['retrieval']['sources']
        print('전달 자료 순서:',list(sources))
        if previous:
            for sid in sorted(sources.keys()-previous.keys()):
                print('추가 자료:',sid,'|',sources[sid]['text'])
            print('빠진 자료:',sorted(previous.keys()-sources.keys()))
        previous=sources
        print('Template 전 첫 호출 문자 수:',len(row['prepared_message'].strip()))
        print('저장된 호출 수:',row['calls'])
        print('최종 초안:',json.dumps(row.get('draft'),ensure_ascii=False))
    if kind=='neighbors':
        print('이 구현은 인접 줄 확장과 함께 조각ID 순으로 재배치합니다. 내용·길이·순서가 함께 달라집니다.')
    print('필요한 줄이 들어왔는지와 답의 금액/조건/인용이 맞는지는 따로 검토하세요.')


def counterexample():
    from app.rag import check_grounding
    doc=next(d for d in json.loads((ROOT/'data/documents-v1.json').read_text())['documents'] if d['id']=='DOC-A')
    source=doc['text'].splitlines()[0]
    raw=json.dumps(dict(outcome='answer',answer='식비 상한은 50000원이다.',claims=[dict(
        text='식비 상한은 50000원이다.',source_id='DOC-A@v1:L1',
        quote='사전 승인을 받은 국내 당일 출장의 식비 상한은 30000원이다.')]),ensure_ascii=False)
    draft,failure=check_grounding(raw,{'DOC-A@v1:L1':dict(text=source)})
    return dict(evidence_kind='teacher_authored_wrong_answer_through_current_checker_not_model_generation',
                source=source,raw=raw,automatic_check_passed=draft is not None,failure_id=failure)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--record',type=Path)
    mode.add_argument('--counterexample',action='store_true')
    p.add_argument('--version',choices=['v1','v2'],default='v2')
    p.add_argument('--case',default='C01')
    p.add_argument('--compare',choices=['prompt','rewrite','neighbors'])
    p.add_argument('--input',action='store_true',help='Show hash-verified reconstructed call strings, not model Token IDs')
    args=p.parse_args()
    if args.counterexample and (args.compare or args.input or args.case!='C01' or args.version!='v2'):
        p.error('The counterexample does not select saved version/case/input')
    if args.compare and args.input:
        p.error('Select a single case to show input strings')
    if args.compare and args.case!='C01':
        p.error('Comparisons select their own cases; omit --case')
    try:
        if args.counterexample:
            r=counterexample()
            print('교사가 만든 틀린 답을 현재 검사기에 넣는 반례입니다. 모델 생성이 아닙니다.')
            print('원문:',r['source']);print('검사할 JSON:',r['raw'])
            print('자동 검사 통과:',r['automatic_check_passed'],'/ 실패 ID:',r['failure_id'])
            print('인용은 실제 존재하지만 50000원 주장을 지지하지 않습니다.')
        else:
            data=load_record(args.record)
            if args.compare:
                show_comparison(data,args.version,args.compare)
            else:
                show_case(data,args.version,args.case,args.input)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        p.exit(2,f'입력/기록 확인 필요: {exc}\n')


if __name__=='__main__':
    main()
