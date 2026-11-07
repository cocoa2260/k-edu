import json

import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.experiments import DATA, VARIANTS
from app.providers.errors import ProviderConnectionError, ProviderTimeoutError, ProviderUpstreamError, ProviderResponseError


class FakeProvider:
    provider_name='fixture'
    model_name='no-model-called'

    def __init__(self):
        self.calls=[]

    def generate(self,message):
        self.calls.append(message)
        return '모의 응답: '+message


@pytest.fixture
def fake():
    return FakeProvider()


@pytest.fixture
def client(fake):
    with TestClient(create_app(fake)) as test_client:
        yield test_client


def test_health_config_only(client,fake):
    assert client.get('/health').json()=={'status':'ok','provider':'fixture','model':'no-model-called'}
    assert fake.calls==[]


def test_chat_contract(client,fake):
    response=client.post('/ai/chat',json={'message':'  안녕하세요  '})
    assert response.status_code==200
    assert response.json()=={'provider':'fixture','model':'no-model-called','answer':'모의 응답: 안녕하세요'}
    assert fake.calls==['안녕하세요']


@pytest.mark.parametrize('payload',[{}, {'message':None},{'message':7},{'message':''},{'message':'   '},{'message':'x'*2001}])
def test_chat_input_validation(client,fake,payload):
    assert client.post('/ai/chat',json=payload).status_code==422
    assert fake.calls==[]


def test_chat_at_max_length(client,fake):
    assert client.post('/ai/chat',json={'message':'x'*2000}).status_code==200
    assert fake.calls==['x'*2000]


@pytest.mark.parametrize('failure,expected',[(ProviderConnectionError(),503),(ProviderTimeoutError(),504),
                                                  (ProviderUpstreamError(),502),(ProviderResponseError(),502)])
def test_provider_error_mapping(failure,expected):
    class BadProvider(FakeProvider):
        def generate(self,_message):raise failure
    with TestClient(create_app(BadProvider())) as test_client:
        r=test_client.post('/ai/chat',json={'message':'질문'})
    assert r.status_code==expected
    assert 'Traceback' not in r.text


def test_cors_valid(client):
    r=client.options('/ai/chat',headers={'Origin':'http://127.0.0.1:5173','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
    assert r.status_code==200
    assert r.headers['access-control-allow-origin']=='http://127.0.0.1:5173'


def test_cors_external_denied(client):
    r=client.options('/ai/chat',headers={'Origin':'https://invalid.example','Access-Control-Request-Method':'POST'})
    assert r.status_code==400


def test_prepare_case_fixed(client,fake):
    r=client.post('/ai/prepare',json={'case_id':'C01','variant':'focused'})
    assert r.status_code==200,r.text
    d=r.json()
    assert d['document_ids']==['DOC-A']
    assert d['generation_executed'] is False and d['selection']=='manual_fixture_not_retrieval'
    assert '30000원' in d['message'] and 'SYNTHETIC-RESTRICTED' not in d['message']
    assert fake.calls==[]


@pytest.mark.parametrize('variant',VARIANTS)
def test_prepare_variants(client,variant):
    r=client.post('/ai/prepare',json={'case_id':'C01','variant':variant})
    assert r.status_code==200,r.text
    assert r.json()['generation_executed'] is False


@pytest.mark.parametrize('case_id,variant',[('C10','baseline'),('UNKNOWN','baseline'),('C01','wrong')])
def test_prepare_reject_invalid(client,case_id,variant):
    assert client.post('/ai/prepare',json={'case_id':case_id,'variant':variant}).status_code==422


def test_fixtures_intact():
    docs=json.loads((DATA/'documents-v1.json').read_text(encoding='utf-8'))['documents']
    cases=json.loads((DATA/'core-v1.json').read_text(encoding='utf-8'))['cases']
    shots=json.loads((DATA/'shots-v1.json').read_text(encoding='utf-8'))['examples']
    assert len(docs)==6 and len(cases)==12 and len(shots)==2
    assert sum(d['access']=='restricted' for d in docs)==1
    assert sum(not d['current'] for d in docs)==1
    assert cases[-1]['supplied_manifest_ids']==['DOC-B','DOC-I','DOC-T']


def test_no_future_routes(client):
    for route in ['/api/v1/retrieval/search','/api/v1/assistant/run','/api/v1/documents/chunks']:
        assert client.get(route).status_code==404


def test_ollama_factory_with_env(monkeypatch):
    from app.providers.factory import create_provider
    monkeypatch.setenv('AI_PROVIDER','ollama')
    monkeypatch.setenv('OLLAMA_MODEL','qwen3:1.7b')
    p=create_provider()
    assert (p.provider_name,p.model_name)==('ollama','qwen3:1.7b')
    monkeypatch.setenv('AI_PROVIDER','unexpected')
    with pytest.raises(RuntimeError):create_provider()


def test_ollama_http_contract_mock(monkeypatch):
    from app.providers.ollama_provider import OllamaProvider
    monkeypatch.setenv('OLLAMA_MODEL','qwen3:1.7b')
    def mock_post(url,*,json,timeout):
        assert url.endswith('/api/chat') and json['model']=='qwen3:1.7b'
        assert json['messages']==[{'role':'user','content':'안녕하세요'}]
        assert json['stream'] is False and timeout==60.0
        return httpx.Response(200,json={'message':{'content':'가상 응답'}},request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',mock_post)
    assert OllamaProvider().generate('안녕하세요')=='가상 응답'


@pytest.mark.parametrize('payload',[{}, {'message':{'content':None}}, {'message':{'content':''}}])
def test_ollama_invalid_response(monkeypatch,payload):
    from app.providers.ollama_provider import OllamaProvider
    monkeypatch.setenv('OLLAMA_MODEL','qwen3:1.7b')
    def mock_post(url,*,json,timeout):
        return httpx.Response(200,json=payload,request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',mock_post)
    with pytest.raises(ProviderResponseError):OllamaProvider().generate('안녕하세요')
