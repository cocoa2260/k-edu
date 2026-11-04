import json
import pytest
from pydantic import ValidationError
from app.agent import Policy,ToolAction,ToolFailure
from app.multi_agent import MultiRuntime,MultiLimits,Ledger,Halt,ReviewAction,decode_role_output
from app.providers.errors import ProviderTimeoutError
from retrieval.index import LocalIndex,StaleSelection
from tools.harness_demo import ScriptedProvider


class Encoder:
    profile=dict(model_id='boundary-fixture',revision='v1',dimension=2,normalized=True)
    def encode(self,texts,kind):return [[1.,0.] for _ in texts]


@pytest.fixture
def index(tmp_path):
    result=LocalIndex.create(tmp_path/'index.sqlite',Encoder(),[
        dict(id='A',version='v1',access='staff',current=True,title='meal',text='cap 30000'),
        dict(id='R',version='v1',access='restricted',current=True,title='private',text='PRIVATE_MARKER')])
    yield result
    result.close()


def action(**value):return json.dumps(value)
SEARCH=action(kind='tool',name='search_documents',arguments=dict(query='meal',k=3))
READ=action(kind='tool',name='read_evidence',arguments=dict(source_id='A@v1:L1'))
HANDOFF=action(kind='handoff',evidence_ids=['A@v1:L1'],missing_information=[])
EMPTY=action(kind='handoff',evidence_ids=[],missing_information=['NEED_MORE_CONTEXT'])
REQUEST=action(kind='request_evidence',query='meal cap')
FINAL=action(kind='final',draft=dict(outcome='answer',answer='30000',claims=[dict(text='cap 30000',source_id='A@v1:L1',quote='cap 30000')]))
PASS=action(kind='review',verdict='pass',failure_ids=[],comment='Source compared')
REPAIR=action(kind='review',verdict='repair',failure_ids=['UNSUPPORTED_CLAIM'],comment='Check claim')


def test_three_real_role_contracts_and_trusted_handoffs(index):
    result=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL,PASS])).run('meal')
    assert result['draft']['answer']=='30000'
    assert result['budget']['roles']==dict(researcher=3,writer=1,reviewer=1)
    assert [h['target_role'] for h in result['handoffs']]==['writer','reviewer','delivery']
    assert [h['budget_used']['models'] for h in result['handoffs']]==[3,4,5]
    assert result['approval_granted'] is False and result['semantic_grounding_verified'] is False


def test_receiver_lacks_known_source(index):
    runtime=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,HANDOFF]),receiver_ids={'writer':frozenset()})
    result=runtime.run('meal')
    assert result['stop_reason']=='repeated_failure' and result['budget']['roles'].get('writer',0)==0
    assert result['handoffs']==[]


def test_unknown_source_never_handed_to_writer(index):
    bad=action(kind='handoff',evidence_ids=['R@v1:L1'],missing_information=[])
    result=MultiRuntime(index,ScriptedProvider([bad,bad])).run('meal')
    assert result['draft'] is None and result['handoffs']==[]


def test_writer_one_evidence_request_uses_global_repair_and_old_role_count(index):
    result=MultiRuntime(index,ScriptedProvider([EMPTY,REQUEST,SEARCH,READ,HANDOFF,FINAL,PASS])).run('meal')
    assert result['budget']['repairs']==1
    assert result['budget']['roles']==dict(researcher=4,writer=2,reviewer=1)
    assert result['budget']['models']==7 and result['draft']


def test_review_same_failure_after_one_repair_stops(index):
    result=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL,REPAIR,FINAL,REPAIR])).run('meal')
    assert result['stop_reason']=='repeated_failure' and result['draft'] is None
    assert result['partial_draft'] and result['budget']['repairs']==1


def test_writer_and_reviewer_do_not_get_new_repair_budgets(index):
    result=MultiRuntime(index,ScriptedProvider([EMPTY,REQUEST,SEARCH,READ,HANDOFF,FINAL,REPAIR])).run('meal')
    assert result['stop_reason']=='repair_budget' and result['draft'] is None


def test_global_budget_precedes_next_role(index):
    result=MultiRuntime(index,ScriptedProvider([SEARCH,READ,HANDOFF,FINAL]),limits=MultiLimits(max_model_calls=4)).run('meal')
    assert result['stop_reason']=='model_budget' and result['partial_draft']
    assert result['budget']['roles'].get('reviewer',0)==0


def test_research_role_cap_cannot_be_reset(index):
    result=MultiRuntime(index,ScriptedProvider([SEARCH]*4)).run('meal')
    assert result['stop_reason']=='role_budget_researcher' and result['budget']['models']==4


@pytest.mark.parametrize('role',['writer','reviewer'])
def test_writer_and_reviewer_cannot_search(index,role):
    runtime=MultiRuntime(index,ScriptedProvider([]));runtime.role=role
    request=ToolAction(kind='tool',name='search_documents',arguments=dict(query='meal'))
    with pytest.raises(ToolFailure,match='ROLE_TOOL_DENIED'):runtime.tool(role,request)
    assert runtime.registry.executions==[]


def test_role_read_is_confined_to_received_ids(index):
    runtime=MultiRuntime(index,ScriptedProvider([]))
    runtime.registry.invoke('search_documents',dict(query='meal'))
    with pytest.raises(ToolFailure,match='ROLE_SOURCE_DENIED'):
        runtime.tool('writer',ToolAction(kind='tool',name='read_evidence',arguments=dict(source_id='A@v1:L1')))


def test_deleted_source_invalidates_handoff(index):
    runtime=MultiRuntime(index,ScriptedProvider([]))
    runtime.registry.invoke('search_documents',dict(query='meal'))
    runtime.registry.invoke('read_evidence',dict(source_id='A@v1:L1'))
    index.delete('A')
    with pytest.raises(StaleSelection):runtime.handoff('researcher','writer',['A@v1:L1'],'C01')


def test_free_text_cannot_be_smuggled_in_handoff_metadata(index):
    runtime=MultiRuntime(index,ScriptedProvider([]))
    with pytest.raises(ToolFailure,match='HANDOFF_METADATA'):
        runtime.handoff('researcher','writer',[],'C01',missing=['private document summary'])


def test_whole_json_fence_is_data_not_executable_code():
    parsed,unwrapped=decode_role_output('reviewer','```json\n'+PASS+'\n```')
    assert parsed.verdict=='pass' and unwrapped is True


@pytest.mark.parametrize('raw',['Before\n```json\n'+PASS+'\n```','```python\nprint(1)\n```',
    '```json\n'+PASS+'\n'+PASS+'\n```'])
def test_fence_normalization_cannot_extract_code_or_multiple_messages(raw):
    with pytest.raises(ToolFailure):decode_role_output('reviewer',raw)


def test_model_cannot_supply_runtime_budget_or_scope(index):
    bad=action(kind='handoff',evidence_ids=[],missing_information=[],budget_used=dict(models=0),actor='admin')
    result=MultiRuntime(index,ScriptedProvider([bad,bad])).run('meal')
    assert result['stop_reason']=='repeated_failure' and result['budget']['models']==2


def test_transient_provider_retry_still_consumes_global_model_budget(index):
    result=MultiRuntime(index,ScriptedProvider([ProviderTimeoutError(),ProviderTimeoutError()])).run('meal')
    assert result['stop_reason']=='transient_budget' and result['budget']['models']==2


def test_late_role_output_stops_before_handoff(index):
    now=[0.]
    class Late(ScriptedProvider):
        def generate(self,message):now[0]=241.;return super().generate(message)
    result=MultiRuntime(index,Late([EMPTY]),clock=lambda:now[0]).run('meal')
    assert result['stop_reason']=='deadline' and result['handoffs']==[]


def test_invalid_question_and_cancellation(index):
    assert MultiRuntime(index,ScriptedProvider([])).run(' ')['budget']['models']==0
    assert MultiRuntime(index,ScriptedProvider([]),cancelled=lambda:True).run('meal')['stop_reason']=='cancelled'


@pytest.mark.parametrize('kwargs',[dict(max_model_calls=9),dict(max_tool_calls=7),dict(max_repairs=2),
    dict(researcher_calls=5),dict(elapsed_seconds=float('nan'))])
def test_no_unbounded_limits(kwargs):
    with pytest.raises(ValidationError):MultiLimits(**kwargs)


@pytest.mark.parametrize('kwargs',[dict(verdict='repair',failure_ids=[]),dict(verdict='pass',failure_ids=['UNSUPPORTED_CLAIM']),
    dict(verdict='repair',failure_ids=['arbitrary_new_failure'])])
def test_review_failure_ids_are_fixed(kwargs):
    with pytest.raises(ValidationError):ReviewAction(kind='review',comment='check',**kwargs)
