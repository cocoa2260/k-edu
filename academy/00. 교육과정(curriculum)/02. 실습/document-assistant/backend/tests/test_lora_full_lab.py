"""Checkpoint/schedule tests use tiny random weights, not model quality data."""
from types import SimpleNamespace
import pytest,torch
from transformers import Qwen3Config,Qwen3ForCausalLM
from peft import LoraConfig,get_peft_model,get_peft_model_state_dict
from tools import lora_full_lab as lab

def test_schedule_covers_every_training_row_and_is_reproducible():
    ids=[str(i) for i in range(20)];order=lab.schedule_ids(ids)
    assert len(order)==28 and set(order)==set(ids) and len(set(order[:20]))==20
    assert order==lab.schedule_ids(ids)
    assert len(set(lab.schedule_ids([str(i) for i in range(28)])))==28

@pytest.mark.parametrize('ids,steps', [([],28),(['x','x'],28),(['a','b'],1)])
def test_invalid_schedule_fails(ids,steps):
    with pytest.raises(ValueError):lab.schedule_ids(ids,steps)

def test_changed_run_configuration_is_rejected(tmp_path):
    f=tmp_path/'config.json';lab.verify_config(f,dict(a=1));lab.verify_config(f,dict(a=1))
    with pytest.raises(ValueError):lab.verify_config(f,dict(a=2))

def test_resume_ignores_uncommitted_step_and_matches_uninterrupted_weights(tmp_path,monkeypatch):
    torch.set_num_threads(2)
    def build():
        torch.manual_seed(37)
        c=Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=8)
        m=get_peft_model(Qwen3ForCausalLM(c),LoraConfig(r=2,lora_alpha=4,lora_dropout=0.,target_modules=['q_proj','v_proj'],bias='none',task_type='CAUSAL_LM'))
        return m,{k:v.detach().clone() for k,v in get_peft_model_state_dict(m).items()}
    rows=[SimpleNamespace(id='row'+str(i)) for i in range(4)]
    monkeypatch.setattr(lab,'tensor_row',lambda e,t:dict(input_ids=torch.tensor([[1,2,3,4]]),attention_mask=torch.ones((1,4),dtype=torch.long),labels=torch.tensor([[-100,-100,3,4]])))
    full,initial=build();reference=lab.record_training(full,None,rows,tmp_path/'full',initial)
    reference_weights={k:v.detach().clone() for k,v in get_peft_model_state_dict(full).items()}
    interrupted,init=build();original_save=lab.save
    def fail_pointer(path,value):
        if path.name=='progress.json' and len(value['logs'])==9:raise RuntimeError('simulated interruption before pointer commit')
        return original_save(path,value)
    monkeypatch.setattr(lab,'save',fail_pointer)
    with pytest.raises(RuntimeError,match='simulated interruption'):lab.record_training(interrupted,None,rows,tmp_path/'resumed',init)
    assert (tmp_path/'resumed/step-0009/optimizer.pt').exists()
    assert lab.read(tmp_path/'resumed/progress.json')['checkpoint']=='step-0008'
    monkeypatch.setattr(lab,'save',original_save)
    result=lab.record_training(interrupted,None,rows,tmp_path/'resumed',init)
    assert result['logs']==reference['logs']
    assert all(torch.equal(v,reference_weights[k]) for k,v in get_peft_model_state_dict(interrupted).items())
    assert result['unique_rows_seen']==4 and result['optimizer_steps']==28
