import json
from copy import deepcopy
import pytest
from pydantic import ValidationError
from app.agent import (Registry,Policy,AgentLimits,ToolFailure,ToolTransientError,
    approval_key,run_agent)
from retrieval.index import LocalIndex,StaleSelection
from tools.harness_demo import ScriptedProvider


class Encoder:
    profile=dict(model_id='boundary-fixture',revision='v1',dimension=2,normalized=True)
    def encode(self,texts,kind):return [[1.,0.] for _ in texts]


@pytest.fixture
def registry(tmp_path):
    docs=[dict(id='A',version='v1',access='staff',current=True,title='meal',text='cap 30000'),
        dict(id='R',version='v1',access='restricted',current=True,title='secret',text='PRIVATE_MARKER')]
    index=LocalIndex.create(tmp_path/'index.sqlite',Encoder(),docs)
    yield Registry(index,Policy())
    index.close()


def tool(name,**arguments):return json.dumps(dict(kind='tool',name=name,arguments=arguments))
SEARCH=tool('search_documents',query='meal',k=3)
READ=tool('read_evidence',source_id='A@v1:L1')
FINAL=json.dumps(dict(kind='final',draft=dict(outcome='answer',answer='cap 30000',
    claims=[dict(text='cap 30000',source_id='A@v1:L1',quote='cap 30000')])))


def test_model_selected_search_read_final(registry):
    result=run_agent(registry,ScriptedProvider([SEARCH,READ,FINAL]),'meal cap')
    assert result['draft']['answer']=='cap 30000'
    assert result['dispatched_tool_names']==['search_documents','read_evidence']
    assert result['semantic_grounding_verified'] is False


@pytest.mark.parametrize('name',['eval','__import__','delete_all_documents'])
def test_unknown_tools_never_dispatch(registry,name):
    result=run_agent(registry,ScriptedProvider([tool(name)]*2),'request')
    assert result['tool_attempts']==2 and result['tool_dispatches']==0
    assert result['stop_reason']=='repeated_failure'


@pytest.mark.parametrize('arguments',[dict(query='meal',approved=True),dict(query=' '),dict(query='meal',k=True),dict(query='meal',k=4)])
def test_schema_rejects_before_dispatch(registry,arguments):
    with pytest.raises(ToolFailure,match='TOOL_ARGUMENTS'):registry.invoke('search_documents',arguments)
    assert registry.executions==[]


def test_approval_cannot_be_model_argument(registry):
    for args in [dict(text='note',approved=True),dict(text='note')]:
        with pytest.raises(ToolFailure):registry.invoke('save_note',args)
    assert registry.notes==[] and registry.executions==[]


def test_trusted_run_and_argument_bound_grant_is_single_use(registry):
    args=dict(text='note');key=approval_key('run1','save_note',args)
    authorized=Registry(registry.index,Policy(run_id='run1',approvals=frozenset({key})))
    assert authorized.invoke('save_note',args)['status']=='created_in_memory_only'
    with pytest.raises(ToolFailure):authorized.invoke('save_note',args)
    wrong_run=Registry(registry.index,Policy(run_id='run2',approvals=frozenset({key})))
    with pytest.raises(ToolFailure):wrong_run.invoke('save_note',args)
    wrong_args=Registry(registry.index,Policy(run_id='run1',approvals=frozenset({key})))
    with pytest.raises(ToolFailure):wrong_args.invoke('save_note',dict(text='changed'))
    assert authorized.notes==['note']


def test_undiscovered_restricted_and_out_of_scope_sources(registry):
    with pytest.raises(ToolFailure):registry.invoke('read_evidence',dict(source_id='A@v1:L1'))
    scoped=Registry(registry.index,Policy(manifest_ids=frozenset({'R'})))
    assert scoped.invoke('search_documents',dict(query='secret'))==dict(hits=[])
    assert not scoped.discovered


def test_changed_index_invalidates_discovered_and_final_sources(registry):
    registry.invoke('search_documents',dict(query='meal'));registry.invoke('read_evidence',dict(source_id='A@v1:L1'))
    registry.index.delete('A')
    with pytest.raises(StaleSelection):registry.invoke('read_evidence',dict(source_id='A@v1:L1'))
    result=run_agent(registry,ScriptedProvider([FINAL]),'meal')
    assert result['stop_reason']=='stale_selection' and result['draft'] is None


def test_final_without_read_is_rejected(registry):
    result=run_agent(registry,ScriptedProvider([FINAL,FINAL]),'meal')
    assert result['draft'] is None and result['stop_reason']=='repeated_failure'


def test_one_read_timeout_retry_consumes_shared_tool_budget(registry):
    original=registry.handlers['search_documents'];calls=[]
    def flaky(**args):
        calls.append(1)
        if len(calls)==1:raise ToolTransientError()
        return original(**args)
    registry.handlers['search_documents']=flaky
    result=run_agent(registry,ScriptedProvider([SEARCH,READ,FINAL]),'meal')
    assert result['tool_attempts']==3 and result['tool_retries']==1 and result['draft']


def test_repeated_timeouts_stop(registry):
    def timeout(**args):raise ToolTransientError()
    registry.handlers['search_documents']=timeout
    result=run_agent(registry,ScriptedProvider([SEARCH]),'meal')
    assert result['stop_reason']=='tool_retry_limit' and result['tool_attempts']==2


def test_protected_operation_is_not_automatically_retried(registry):
    args=dict(text='note');key=approval_key('run','save_note',args)
    authorized=Registry(registry.index,Policy(run_id='run',approvals=frozenset({key})))
    def timeout(**kwargs):raise ToolTransientError()
    authorized.handlers['save_note']=timeout
    result=run_agent(authorized,ScriptedProvider([tool('save_note',**args)]),'save')
    assert result['stop_reason']=='protected_tool_error' and result['tool_attempts']==1
    assert result['tool_retries']==0 and authorized.notes==[]


def test_malformed_actions_are_bounded_and_never_dispatched(registry):
    result=run_agent(registry,ScriptedProvider(['not JSON']*2),'meal')
    assert result['stop_reason']=='repeated_failure' and result['tool_dispatches']==0


def test_late_tool_result_is_not_returned_as_observation(registry):
    now=[0.];original=registry.handlers['search_documents']
    def late(**kwargs):now[0]=181.;return original(**kwargs)
    registry.handlers['search_documents']=late
    result=run_agent(registry,ScriptedProvider([SEARCH]),'meal',clock=lambda:now[0])
    assert result['stop_reason']=='elapsed_limit'
    assert not any(e['event']=='tool_observed' for e in result['trace'])


def test_repeated_successful_search_has_finite_tool_cap(registry):
    result=run_agent(registry,ScriptedProvider([SEARCH]*4),'meal')
    assert result['stop_reason']=='tool_limit' and result['tool_dispatches']==3


def test_bad_tool_output_does_not_grant_source_capability(registry):
    original=registry.handlers['search_documents']
    def bad(**kwargs):original(**kwargs);return dict(bad='output')
    registry.handlers['search_documents']=bad
    with pytest.raises(ToolFailure):registry.invoke('search_documents',dict(query='meal'))
    assert registry.discovered=={}


def test_direct_response_is_trusted_task_option(registry):
    action=json.dumps(dict(kind='respond',text='안녕하세요.'))
    denied=run_agent(registry,ScriptedProvider([action]*2),'hello')
    assert denied['stop_reason']=='repeated_failure'
    allowed=run_agent(Registry(registry.index,Policy(allow_direct_response=True)),ScriptedProvider([action]),'hello')
    assert allowed['stop_reason']=='direct_response' and allowed['tool_dispatches']==0


@pytest.mark.parametrize('question',['','  ','x'*2001])
def test_invalid_question_never_plans(registry,question):
    assert run_agent(registry,ScriptedProvider([]),question)['decisions']==0


def test_soft_elapsed_and_cancellation(registry):
    assert run_agent(registry,ScriptedProvider([]),'meal',cancelled=lambda:True)['stop_reason']=='cancelled'
    now=[0.]
    class Late(ScriptedProvider):
        def generate(self,message):now[0]=181.;return super().generate(message)
    result=run_agent(registry,Late([SEARCH]),'meal',clock=lambda:now[0])
    assert result['stop_reason']=='elapsed_limit' and result['tool_dispatches']==0


@pytest.mark.parametrize('kwargs',[dict(max_decisions=5),dict(max_tools=4),dict(max_tool_retries=2),dict(elapsed_seconds=float('nan'))])
def test_no_unbounded_settings(kwargs):
    with pytest.raises(ValidationError):AgentLimits(**kwargs)


def test_structured_tool_bridge_keeps_runtime_boundary(registry):
    pytest.importorskip('langchain_core')
    from app.agent_bridge import make_tools,invoke_without_tracing
    tools=make_tools(registry)
    assert set(tools)=={'search_documents','read_evidence'}
    assert invoke_without_tracing(tools,'search_documents',dict(query='meal'))['hits'][0]['source_id']=='A@v1:L1'
    assert invoke_without_tracing(tools,'read_evidence',dict(source_id='A@v1:L1'))['text']=='cap 30000'
    with pytest.raises(ValidationError):invoke_without_tracing(tools,'search_documents',dict(query='meal',approved=True))
