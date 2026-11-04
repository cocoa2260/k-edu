"""Real PEFT API on tiny random weights; not pretrained model quality evidence."""
import torch
from transformers import Qwen3Config,Qwen3ForCausalLM
from peft import LoraConfig,get_peft_model,PeftModel

def test_tiny_real_peft_update_frozen_base_and_saved_reload(tmp_path):
    torch.set_num_threads(2);torch.manual_seed(37)
    config=Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,
        num_attention_heads=2,num_key_value_heads=1,head_dim=8)
    base=Qwen3ForCausalLM(config);base.save_pretrained(tmp_path/'base')
    model=get_peft_model(base,LoraConfig(r=2,lora_alpha=4,lora_dropout=0.,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    before={n:p.detach().clone() for n,p in model.named_parameters()}
    ids=torch.tensor([[1,2,3,4]]);labels=torch.tensor([[-100,-100,3,4]])
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.001)
    model.train();loss=model(input_ids=ids,labels=labels).loss;loss.backward();optimizer.step()
    assert any(not torch.equal(before[n],p) for n,p in model.named_parameters() if p.requires_grad)
    assert all(torch.equal(before[n],p) for n,p in model.named_parameters() if not p.requires_grad)
    assert all('lora_' in n for n,p in model.named_parameters() if p.requires_grad)
    model.eval()
    with torch.no_grad():expected=model(input_ids=ids).logits
    model.save_pretrained(tmp_path/'adapter')
    loaded=PeftModel.from_pretrained(Qwen3ForCausalLM.from_pretrained(tmp_path/'base'),tmp_path/'adapter');loaded.eval()
    with torch.no_grad():actual=loaded(input_ids=ids).logits
    assert torch.equal(expected,actual)
