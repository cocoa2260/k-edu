"""M01-M04 controlled handoff probes; no learned embedding/model inference."""
import argparse
import json
from pathlib import Path
import tempfile
from app.agent import ToolTransientError
from app.multi_agent import MultiRuntime,MultiLimits
from app.providers.errors import ProviderTimeoutError
from retrieval.index import LocalIndex
from tools.harness_demo import ScriptedProvider


class FixtureEncoder:
    profile=dict(model_id='nonsemantic-boundary-fixture',revision='v1',dimension=2,normalized=True)
    def encode(self,texts,kind):return [[1.,0.] for _ in texts]


def action(**values):return json.dumps(values)
SEARCH=action(kind='tool',name='search_documents',arguments=dict(query='meal',k=3))
READ=action(kind='tool',name='read_evidence',arguments=dict(source_id='A@v1:L1'))
HANDOFF=action(kind='handoff',evidence_ids=['A@v1:L1'],missing_information=[])
EMPTY=action(kind='handoff',evidence_ids=[],missing_information=['NEED_MORE_CONTEXT'])
REQUEST=action(kind='request_evidence',query='meal cap')
FINAL=action(kind='final',draft=dict(outcome='answer',answer='30000',claims=[dict(text='cap 30000',source_id='A@v1:L1',quote='cap 30000')]))
PASS=action(kind='review',verdict='pass',failure_ids=[],comment='Source inspected')
REPAIR=action(kind='review',verdict='repair',failure_ids=['UNSUPPORTED_CLAIM'],comment='Check claim')


def probes(path):
    index=LocalIndex.create(path,FixtureEncoder(),[
        dict(id='A',version='v1',access='staff',current=True,title='meal',text='cap 30000')])
    try:
        normal=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL,PASS])).run('meal','CONTROL')
        m1=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,HANDOFF]),receiver_ids={'writer':frozenset()}).run('meal','M01')
        m2=MultiRuntime(index,ScriptedProvider([EMPTY,REQUEST,SEARCH,READ,HANDOFF,FINAL,PASS])).run('meal','M02')
        m3=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL,REPAIR,FINAL,REPAIR])).run('meal','M03')
        budget=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL]),limits=MultiLimits(max_model_calls=4)).run('meal','M04-budget')
        timeout=MultiRuntime(index,ScriptedProvider([ProviderTimeoutError(),ProviderTimeoutError()])).run('meal','M04-timeout')
        now=[0.]
        class Late(ScriptedProvider):
            def generate(self,message):now[0]=241.;return super().generate(message)
        deadline=MultiRuntime(index,Late([EMPTY]),clock=lambda:now[0]).run('meal','M04-deadline')
        assert normal['draft'] and m1['handoffs']==[] and m1['stop_reason']=='repeated_failure'
        assert m2['budget']['repairs']==1 and m2['budget']['models']==7 and m2['draft']
        assert m3['stop_reason']=='repeated_failure' and m3['draft'] is None
        assert budget['stop_reason']=='model_budget' and timeout['stop_reason']=='transient_budget'
        assert deadline['stop_reason']=='deadline' and not deadline['handoffs']
        return dict(evidence_kind='observed_scripted_M01_M04_not_model_quality',control=normal,
            scenarios=dict(M01=m1,M02=m2,M03=m3,M04=dict(model_budget=budget,transient_timeout=timeout,deadline=deadline)),
            actual_model_generations=0,paid_api_calls=0,
            scoring='Four handoff cases excluded from 18-case Single/Multi quality denominator')
    finally:index.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    with tempfile.TemporaryDirectory() as temp:result=probes(Path(temp)/'index.sqlite')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(handoff_cases=4,control_passed=True,model_generations=0)))


if __name__=='__main__':main()
