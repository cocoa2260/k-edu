import json
import sqlite3
from copy import deepcopy
import pytest

from app.rag import run_rag,build_prepared,check_grounding,CONTRACT
from app.providers.errors import ProviderTimeoutError
from app.harness import Limits
from retrieval.index import LocalIndex,StaleSelection
from tools.harness_demo import ScriptedProvider


class Encoder:
    profile=dict(model_id='boundary-fixture',revision='v1',dimension=2,normalized=True)
    def encode(self,texts,kind):return [[1.0,0.0] for _ in texts]


@pytest.fixture
def index(tmp_path):
    documents=[dict(id='A',version='v1',access='staff',current=True,title='meal',text='cap 30000\nreceipt required'),
        dict(id='R',version='v1',access='restricted',current=True,title='secret',text='SECRET-NEVER-INPUT')]
    result=LocalIndex.create(tmp_path/'index.sqlite',Encoder(),documents)
    yield result
    result.close()


def response(text='cap is 30000',quote='cap 30000',source='A@v1:L1'):
    return json.dumps(dict(outcome='answer',answer=text,
        claims=[dict(text=text,source_id=source,quote=quote)]))


def test_actual_retrieval_context_not_manual_answer_keys(index):
    provider=ScriptedProvider([response()])
    result=run_rag(index,provider,'meal cap',case_id='C01')
    assert result['status']=='draft_needs_review' and result['calls']==1
    assert 'cap 30000' in provider.messages[0] and 'SECRET-NEVER-INPUT' not in provider.messages[0]
    assert 'required_facts' not in provider.messages[0] and 'rubric' not in provider.messages[0]
    assert result['source_resolution'][0]['source_locator'].startswith('sqlite:documents/')
    assert result['semantic_grounding_verified'] is False


@pytest.mark.parametrize('source,quote,expected',[
    ('R@v1:L1','SECRET','CITATION_NOT_SUPPLIED'),
    ('A@v1:L1','cap 50000','QUOTE_NOT_IN_SOURCE'),
    ('A@v1:L1','cap 30000',None),
])
def test_source_and_quote_checks(index,source,quote,expected):
    prepared=build_prepared(index,'meal')
    _,failure=check_grounding(response(source=source,quote=quote),prepared['sources'])
    assert failure==expected


def test_correct_quote_does_not_prove_claim(index):
    result=run_rag(index,ScriptedProvider([response(text='cap is 50000')]),'meal')
    assert result['structural_validation_passed'] is True
    assert result['semantic_grounding_verified'] is False
    assert result['draft']['answer']=='cap is 50000'


def test_wrong_quote_repair_is_bounded(index):
    provider=ScriptedProvider([response(quote='wrong quote'),response()])
    result=run_rag(index,provider,'meal')
    assert result['repairs']==1 and result['status']=='draft_needs_review'
    assert 'QUOTE_NOT_IN_SOURCE' in provider.messages[1]
    stopped=run_rag(index,ScriptedProvider([response(quote='wrong quote')]*2),'meal')
    assert stopped['stop_reason']=='repair_limit' and stopped['draft'] is None


def test_retry_and_repair_share_l2_budget(index):
    result=run_rag(index,ScriptedProvider([ProviderTimeoutError(),'not json',response()]),'meal')
    assert (result['calls'],result['retries'],result['repairs'])==(3,1,1)


@pytest.mark.parametrize('question',['','  ','x'*2001])
def test_bad_input_never_calls_provider(index,question):
    provider=ScriptedProvider([])
    result=run_rag(index,provider,question)
    assert result['failure_stage']=='input' and result['calls']==0


def test_empty_context_can_abstain_but_cannot_invent_source(index):
    provider=ScriptedProvider([json.dumps(dict(outcome='abstain',answer='No source',claims=[]))])
    result=run_rag(index,provider,'question',manifest_ids=set())
    assert result['draft']['outcome']=='abstain' and result['retrieval']['sources']=={}
    failure=run_rag(index,ScriptedProvider([response()]*2),'question',manifest_ids=set())
    assert failure['draft'] is None


def test_mutation_during_generation_discards_answer(index):
    class Mutating(ScriptedProvider):
        def generate(self,message):
            index.delete('A')
            return super().generate(message)
    result=run_rag(index,Mutating([response()]),'meal')
    assert result['failure_stage']=='context' and result['draft'] is None


def test_context_neighbors_preserve_bounds_and_exclude_restricted(index):
    prepared=build_prepared(index,'meal',neighbors=True,manifest_ids={'A'})
    assert set(prepared['sources'])=={'A@v1:L1','A@v1:L2'}
    assert 'SECRET' not in prepared['message']


def test_rewrite_changes_query_only(index):
    original=build_prepared(index,'original meal',search_query='rewritten query')
    assert original['original_question']=='original meal'
    assert original['search_query']=='rewritten query'
    assert 'original meal' in original['message']


def test_retrieval_failure_has_own_stage(index,monkeypatch):
    def fail(*args,**kwargs):raise sqlite3.OperationalError('unavailable')
    monkeypatch.setattr(index,'search',fail)
    result=run_rag(index,ScriptedProvider([]),'meal')
    assert result['failure_stage']=='retrieval' and result['calls']==0


@pytest.mark.parametrize('raw',[
    json.dumps(dict(outcome='answer',answer='a',claims=[])),
    json.dumps(dict(outcome='abstain',answer=' ',claims=[])),
    json.dumps(dict(outcome='deny',answer='deny',claims=[],approved=True)),
    'not json',None,
])
def test_schema_failures(raw):
    assert check_grounding(raw,{})[1] is not None
