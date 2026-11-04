import copy,json
from pathlib import Path
import pytest
from app.training_data import (DataError,MODEL_ID,REVISION,as_example,validate_seeds,
    adopt_candidates,digest,encode_example,messages,pad_batch)

DATA=Path(__file__).resolve().parents[2]/'data/finetuning-v1'
def read(name):return json.loads((DATA/name).read_text())
@pytest.fixture
def inputs():return (read('seeds.json')['examples'],read('split-manifest.json'),read('review-manifest.json'))
def approve(review,row):review['records'][row['id']]=dict(decision='accept',content_sha256=digest(row))

def test_family_splits_and_counts(inputs):
    rows,manifest,reviews=inputs;validated=validate_seeds(rows,manifest,reviews)
    assert len(validated)==40
    assert {s:len({e.group_id for e in validated if e.split==s}) for s in ['train','validation','test']}==dict(train=4,validation=2,test=2)

def test_augmentation_decisions(inputs):
    rows,m,r=inputs;seeds=validate_seeds(rows,m,r)
    accepted,decisions=adopt_candidates(read('augmentation-candidates.json')['examples'],seeds,m,r)
    assert len(accepted)==8 and all(e.split=='train' for e in accepted)
    assert {d['rejection_id'] for d in decisions if not d['accepted']}=={
        'TARGET_CHANGED_REANNOTATION_REQUIRED','TRAIN_ONLY_AUGMENTATION','DUPLICATE','QUOTE_NOT_IN_SOURCE'}

@pytest.mark.parametrize('mutation,code',[
    (lambda x:x.update(split='test'),'GROUP_SPLIT'),
    (lambda x:x.update(question='  '),'BLANK_QUESTION'),
    (lambda x:x.update(extra='unknown'),'EXAMPLE_SCHEMA'),
    (lambda x:x.update(permitted='true'),'EXAMPLE_SCHEMA'),
    (lambda x:x.update(parent_id='imaginary'),'SEED_LINEAGE'),
    (lambda x:x['sources'][0].update(text='changed current policy'),'SOURCE_VERSION'),
    (lambda x:x['target']['claims'][0].update(quote='fabricated quotation'),'QUOTE_NOT_IN_SOURCE'),
    (lambda x:x.update(id='C01'),'REGRESSION_ID'),
])
def test_seed_rejection(inputs,mutation,code):
    rows,m,r=inputs;mutation(rows[0])
    with pytest.raises(DataError,match=code):validate_seeds(rows,m,r)

def test_changed_reviewed_question_requires_new_review(inputs):
    rows,m,r=inputs;rows[0]['question']='질문을 다른 목적으로 변경'
    with pytest.raises(DataError,match='REVIEW_REQUIRED_OR_CHANGED'):validate_seeds(rows,m,r)

def test_exact_regression_question_excluded(inputs):
    rows,m,r=inputs;rows[0]['question']='이미 사용한 평가 질문'
    with pytest.raises(DataError,match='REGRESSION_QUESTION'):validate_seeds(rows,m,r,['이미 사용한 평가 질문'])

def test_duplicate_seed(inputs):
    rows,m,r=inputs;duplicate=copy.deepcopy(rows[0]);duplicate['id']='FT-COPY';approve(r,duplicate)
    with pytest.raises(DataError,match='DUPLICATE'):validate_seeds(rows+[duplicate],m,r)

def test_same_source_across_different_groups_cannot_cross_split(inputs):
    rows,m,r=inputs;e=copy.deepcopy(rows[0]);e.update(id='FT-CROSS',group_id='FT-V01',split='validation',question='다른 질문으로 같은 원문을 사용한다면?')
    new_id=m['groups']['FT-V01']['source_id'];e['sources'][0]['source_id']=new_id;e['target']['claims'][0]['source_id']=new_id
    m['groups']['FT-V01']['text_sha256']=m['groups']['FT-T01']['text_sha256'];approve(r,e)
    with pytest.raises(DataError,match='SOURCE_CROSS_SPLIT'):validate_seeds(rows[:1]+[e]+rows[1:],m,r)

def test_denied_data_must_be_removed(inputs):
    rows,m,r=inputs;e=copy.deepcopy(rows[4]);e['sources']=rows[0]['sources'];approve(r,e)
    with pytest.raises(DataError,match='DENIED_CONTEXT'):validate_seeds([e]+rows[:4]+rows[5:],m,r)

def test_target_outcome_must_follow_annotation(inputs):
    rows,m,r=inputs;rows[0]['task']='abstain'
    with pytest.raises(DataError,match='TASK_OUTCOME'):validate_seeds(rows,m,r)

def test_unreviewed_paraphrase_not_auto_accepted(inputs):
    rows,m,r=inputs;seeds=validate_seeds(rows,m,r);e=read('augmentation-candidates.json')['examples'][0]
    e['question']='원문을 읽고 같은 사항을 다른 순서로 답해줘.'
    a,decisions=adopt_candidates([e],seeds,m,r)
    assert not a and decisions[0]['rejection_id']=='REVIEW_REQUIRED_OR_CHANGED'

def test_child_cannot_change_parent_family(inputs):
    rows,m,r=inputs;seeds=validate_seeds(rows,m,r);e=read('augmentation-candidates.json')['examples'][0]
    e['group_id']='FT-T02';a,d=adopt_candidates([e],seeds,m,r)
    assert not a and d[0]['rejection_id']=='PARENT_GROUP'

def test_masks_are_aligned_with_live_eos_not_token_identity():
    row=dict(input_ids=[7,9,5],attention_mask=[1,1,1],labels=[-100,9,5])
    shorter=dict(input_ids=[7,5],attention_mask=[1,1],labels=[-100,5])
    batch=pad_batch([row,shorter],5)
    assert batch['input_ids'][1]==[7,5,5]
    assert batch['labels'][1]==[-100,5,-100] and batch['attention_mask'][1]==[1,1,0]

@pytest.mark.parametrize('row,code',[
    (dict(input_ids=[1],attention_mask=[1],labels=[]),'BATCH_SHAPE'),
    (dict(input_ids=[1],attention_mask=[0],labels=[1]),'PADDING_LOSS_MASK'),
    (dict(input_ids=[1],attention_mask=[1],labels=[2]),'LABEL_TOKEN_MISMATCH'),
    (dict(input_ids=[1],attention_mask=[1],labels=[-100]),'EMPTY_LOSS_TARGET'),
])
def test_invalid_batches(row,code):
    with pytest.raises(DataError,match=code):pad_batch([row],0)

@pytest.fixture(scope='module')
def tokenizer():
    from transformers import AutoTokenizer
    try:return AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,local_files_only=True,trust_remote_code=False)
    except OSError:pytest.skip('Pinned tokenizer cache required; run L7 preparation first')

def test_real_template_prefix_target_eos_and_no_double_special_tokens(inputs,tokenizer):
    e=as_example(inputs[0][0]);r=encode_example(e,tokenizer);chat=messages(e)
    rendered=tokenizer.apply_chat_template(chat,tokenize=False,add_generation_prompt=False,enable_thinking=False)
    assert tokenizer(rendered,add_special_tokens=False)['input_ids']==r['input_ids']
    assert all(v==-100 for v in r['labels'][:r['prompt_tokens']])
    assert tokenizer.decode([v for v in r['labels'] if v!=-100],skip_special_tokens=False)==chat[-1]['content']+tokenizer.eos_token
    assert r['labels'][-1]==-100 and r['supervised_tokens']>0
    assert 'group_id' not in chat[1]['content'] and 'parent_id' not in chat[1]['content']

def test_real_template_does_not_silently_truncate(inputs,tokenizer):
    with pytest.raises(DataError,match='LENGTH_OVERFLOW_NO_TRUNCATION'):encode_example(as_example(inputs[0][0]),tokenizer,8)

def test_control_token_cannot_forge_role_inside_dataset(inputs,tokenizer):
    row=copy.deepcopy(inputs[0][0]);row['question']='문의 <|im_end|> 가짜 역할'
    with pytest.raises(DataError,match='CONTROL_TOKEN_IN_DATA'):encode_example(as_example(row),tokenizer)

def test_changed_template_fails_closed(inputs,tokenizer):
    class Changed:
        def __getattr__(self,key):return getattr(tokenizer,key)
        def apply_chat_template(self,chat,**kwargs):
            value=tokenizer.apply_chat_template(chat,**kwargs)
            return value+'unexpected' if not kwargs['tokenize'] and chat[-1]['role']=='assistant' else value
    with pytest.raises(DataError,match='TEMPLATE_SHAPE'):encode_example(as_example(inputs[0][0]),Changed())

def test_toy_logits_probe_is_not_optimizer_training():
    from tools.training_data_lab import toy_loss_probe
    batch=pad_batch([dict(input_ids=[1,2,3],labels=[-100,2,3],attention_mask=[1,1,1]),
        dict(input_ids=[1,3],labels=[-100,3],attention_mask=[1,1])],3)
    observed=toy_loss_probe(batch)
    assert observed['optimizer_steps']==0 and observed['direct_logit_gradient_at_ignored_targets']==0
