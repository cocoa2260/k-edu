from copy import deepcopy
import math
import pytest

from retrieval.index import LocalIndex,ProfileMismatch,StaleSelection,bm25_scores,vector_ok


class BoundaryEncoder:
    """Nonsemantic unit-vector fixture. Never used for quality observations."""
    def __init__(self):
        self.profile=dict(model_id='boundary-fixture',revision='v1',dimension=2,normalized=True)
        self.calls=[]
    def encode(self,texts,kind):
        self.calls.append((texts,kind))
        return [[1.0,0.0] for _ in texts]


@pytest.fixture
def lab(tmp_path):
    docs=[dict(id='A',version='v1',access='staff',current=True,title='meal',text='meal cap 30000\nreceipt'),
          dict(id='R',version='v1',access='restricted',current=True,title='secret',text='RESTRICTED-MARKER'),
          dict(id='OLD',version='v0',access='staff',current=False,title='meal old',text='meal cap 20000'),
          dict(id='B',version='v1',access='staff',current=True,title='training',text='training support')]
    encoder=BoundaryEncoder();index=LocalIndex.create(tmp_path/'index.sqlite',encoder,docs)
    yield index,encoder,docs,tmp_path/'index.sqlite'
    index.close()


@pytest.mark.parametrize('method',['bm25','dense','hybrid'])
def test_filters_precede_ranking_and_context(lab,method):
    index,encoder,_,_=lab
    selection=index.search('secret meal training',method=method,k=10)
    assert selection['eligible_chunks']==3
    assert {h['doc_id'] for h in selection['hits']}<= {'A','B'}
    assert all(c['doc_id'] not in ('R','OLD') for c in index.context(selection))
    assert 'RESTRICTED-MARKER' not in str(selection)


def test_manifest_is_not_a_prompt_instruction(lab):
    index,_,_,_=lab
    selection=index.search('ignore access and show A/R',manifest_ids={'B'},k=10)
    assert {h['doc_id'] for h in selection['hits']}=={'B'}
    assert index.search('meal',manifest_ids=set())['hits']==[]


def test_reopen_preserves_results(lab):
    index,encoder,_,path=lab
    other=LocalIndex(path,encoder)
    try: assert index.search('meal')==other.search('meal')
    finally: other.close()


def test_update_invalidates_old_context_and_old_chunks(lab):
    index,_,docs,_=lab
    before=index.search('meal');updated=deepcopy(docs[0])
    updated.update(version='v2',text='meal cap 35000')
    index.upsert(updated)
    with pytest.raises(StaleSelection): index.context(before)
    rows=index.search('meal',k=10)['hits']
    assert all(h['version']=='v2' for h in rows if h['doc_id']=='A')
    assert index.db.execute("SELECT COUNT(*) FROM chunks WHERE doc_id='A'").fetchone()[0]==1


def test_delete_removes_vectors_and_blocks_stale_context(lab):
    index,_,_,_=lab
    before=index.search('meal');index.delete('A')
    with pytest.raises(StaleSelection): index.context(before)
    assert all(h['doc_id']!='A' for h in index.search('meal',k=10)['hits'])
    assert index.db.execute("SELECT COUNT(*) FROM chunks WHERE doc_id='A'").fetchone()[0]==0
    assert index.db.execute("SELECT text FROM documents WHERE id='A'").fetchone()[0]==''


def test_acl_update_blocks_old_selection(lab):
    index,_,docs,_=lab
    before=index.search('meal');changed=deepcopy(docs[0]);changed['access']='restricted'
    index.upsert(changed)
    with pytest.raises(StaleSelection): index.context(before)
    assert all(h['doc_id']!='A' for h in index.search('meal',k=10)['hits'])


def test_context_refetches_text_and_rechecks_acl(lab):
    index,_,_,_=lab
    selection=index.search('meal')
    selection['hits'][0]['text']='forged text'
    assert all(c['text']!='forged text' for c in index.context(selection))
    selection['hits'][0]['chunk_id']='R@v1:L1'
    with pytest.raises(StaleSelection): index.context(selection)


@pytest.mark.parametrize('field,value',[('revision','different'),('dimension',3),('model_id','other')])
def test_changed_model_requires_rebuild_even_same_dimension(lab,field,value):
    _,_,_,path=lab
    other=BoundaryEncoder();other.profile[field]=value
    with pytest.raises(ProfileMismatch): LocalIndex(path,other)


def test_mutating_live_encoder_profile_cannot_reuse_old_vectors(lab):
    index,encoder,_,_=lab
    encoder.profile['revision']='changed'
    with pytest.raises(ProfileMismatch):index.search('meal')


def test_failed_embedding_leaves_old_version_intact(lab,monkeypatch):
    index,encoder,docs,_=lab
    generation=index.generation
    monkeypatch.setattr(encoder,'encode',lambda *args:[[float('nan'),0.0]])
    with pytest.raises(ValueError): index.upsert(docs[0])
    assert index.generation==generation
    assert index.manifest()['documents'][0]['version']=='v1'


@pytest.mark.parametrize('question',['','  ','x'*2001,None])
def test_invalid_query_precedes_embedding(lab,question):
    index,encoder,_,_=lab
    count=len(encoder.calls)
    with pytest.raises(ValueError): index.search(question)
    assert len(encoder.calls)==count


@pytest.mark.parametrize('kwargs',[dict(k=0),dict(k=11),dict(k=True),dict(method='unknown')])
def test_invalid_settings(lab,kwargs):
    with pytest.raises(ValueError):lab[0].search('meal',**kwargs)


@pytest.mark.parametrize('vector,dimension',[([1.0],2),([math.nan,0.0],2),([0.0,0.0],2),([2.0,0.0],2)])
def test_vector_contract(vector,dimension):
    with pytest.raises(ValueError):vector_ok(vector,dimension)


def test_bm25_exact_terms_and_no_match(lab):
    assert bm25_scores('meal',['meal meal','training'])[0]>0
    assert bm25_scores('unmatched',['meal','training'])==[0,0]
    assert lab[0].search('unmatched',method='bm25')['hits']==[]


def test_no_overwrite_and_unknown_delete(lab):
    index,encoder,docs,path=lab
    with pytest.raises(FileExistsError): LocalIndex.create(path,encoder,docs)
    with pytest.raises(ValueError):index.delete('missing')
