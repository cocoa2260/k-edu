"""Offline injected boundaries and real StructuredTool bridge, not model inference."""
import argparse
import json
from pathlib import Path
import tempfile
from app.agent import Registry,Policy,run_agent,ToolTransientError,ToolFailure,approval_key
from app.agent_bridge import make_tools,invoke_without_tracing
from retrieval.index import LocalIndex
from tools.harness_demo import ScriptedProvider


class FixtureEncoder:
    profile=dict(model_id='nonsemantic-boundary-fixture',revision='v1',dimension=2,normalized=True)
    def encode(self,texts,kind):return [[1.,0.] for _ in texts]


def tool(name,**arguments):return json.dumps(dict(kind='tool',name=name,arguments=arguments))
SEARCH=tool('search_documents',query='meal cap',k=3)
READ=tool('read_evidence',source_id='A@v1:L1')
FINAL=json.dumps(dict(kind='final',draft=dict(outcome='answer',answer='cap 30000',
    claims=[dict(text='cap 30000',source_id='A@v1:L1',quote='cap 30000')])))


def run_fixture_lab(path):
    documents=[dict(id='A',version='v1',access='staff',current=True,title='meal',text='cap 30000'),
               dict(id='R',version='v1',access='restricted',current=True,title='secret',text='PRIVATE_FIXTURE')]
    index=LocalIndex.create(path,FixtureEncoder(),documents);results={}
    try:
        scripts={
            'A01':[json.dumps(dict(kind='respond',text='안녕하세요.'))],
            'A02':[SEARCH,READ,FINAL],
            'A03':[tool('delete_all_documents')]*2,
            'A04':[tool('save_note',text='note',approved=True)]*2,
            'A05':[SEARCH,READ,FINAL],
            'A06':[tool('never_exists')]*2,
            'protected_without_grant':[tool('save_note',text='note')]*2,
            'successful_repeat_cap':[SEARCH]*4,
        }
        for case,actions in scripts.items():
            registry=Registry(index,Policy(allow_direct_response=case=='A01'))
            if case=='A05':
                original=registry.handlers['search_documents'];attempts=[]
                def flaky(**kwargs):
                    attempts.append(1)
                    if len(attempts)==1:raise ToolTransientError()
                    return original(**kwargs)
                registry.handlers['search_documents']=flaky
            results[case]=run_agent(registry,ScriptedProvider(actions),'meal cap')
        assert results['A01']['tool_dispatches']==0
        assert results['A02']['draft'] is not None
        assert all(results[c]['tool_dispatches']==0 for c in ['A03','A04','A06','protected_without_grant'])
        assert results['A05']['tool_attempts']==3 and results['A05']['tool_retries']==1
        assert results['successful_repeat_cap']['stop_reason']=='tool_limit'
        args=dict(text='note');grant=approval_key('approved-fixture','save_note',args)
        authorized=Registry(index,Policy(run_id='approved-fixture',approvals=frozenset({grant})))
        saved=authorized.invoke('save_note',args)
        try:authorized.invoke('save_note',args);raise AssertionError('Replay accepted')
        except ToolFailure as exc:replay=exc.code
        bridge_registry=Registry(index,Policy());tools=make_tools(bridge_registry)
        direct=Registry(index,Policy()).invoke('search_documents',dict(query='meal cap'))
        bridged=invoke_without_tracing(tools,'search_documents',dict(query='meal cap'))
        assert direct==bridged
        read=invoke_without_tracing(tools,'read_evidence',dict(source_id='A@v1:L1'))
        try:invoke_without_tracing(tools,'search_documents',dict(query='meal',approved=True));raise AssertionError('extra field accepted')
        except Exception as exc:
            if isinstance(exc,AssertionError):raise
            rejected=type(exc).__name__
        return dict(evidence_kind='observed_scripted_faults_and_real_library_API_not_model_quality',
            scenarios=results,approval_probe=dict(result=saved,replay_rejected=replay,note_count=len(authorized.notes),
                scope='trusted run/argument-bound in-memory grant, no external write or durable authorization'),
            framework=dict(tool_class='langchain_core.tools.StructuredTool',search_result_equal=direct==bridged,
                read_result=read,extra_argument_rejection=rejected,protected_tool_exported='save_note' in tools,
                input_schema=tools['search_documents'].args_schema.model_json_schema(),
                tracing_enabled=False,full_framework_agent_executed=False,MCP_transport_executed=False),
            actual_model_generations=0,paid_api_calls=0)
    finally:index.close()


def main():
    import requests
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    requests_attempts=[]
    original=requests.sessions.Session.request
    def forbidden(*args,**kwargs):requests_attempts.append(1);raise AssertionError('Framework probe HTTP forbidden')
    requests.sessions.Session.request=forbidden
    try:
        with tempfile.TemporaryDirectory() as directory:result=run_fixture_lab(Path(directory)/'index.sqlite')
    finally:requests.sessions.Session.request=original
    result['guarded_requests_attempts']=len(requests_attempts)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(scenarios=len(result['scenarios']),framework_equal=result['framework']['search_result_equal'],http_attempts=len(requests_attempts))))


if __name__=='__main__':main()
