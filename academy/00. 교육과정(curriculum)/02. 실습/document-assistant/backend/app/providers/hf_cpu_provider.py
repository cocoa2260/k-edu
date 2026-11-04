"""Explicit local Qwen generation adapter; not selected by the web API factory."""
import time
from app.providers.errors import ProviderResponseError

MODEL_ID='Qwen/Qwen3-0.6B'
REVISION='c1899de289a04d12100db370d81485cdf75e47ca'


class HFCpuProvider:
    provider_name='hf-cpu'
    model_name=MODEL_ID

    def __init__(self,*,offline=True,max_new_tokens=512):
        if type(max_new_tokens) is not int or not 32<=max_new_tokens<=512:
            raise ValueError('Local generation output limit must be 32..512')
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM
        self.torch=torch
        torch.set_num_threads(2)
        self.tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=REVISION,
            local_files_only=offline,trust_remote_code=False)
        self.model=AutoModelForCausalLM.from_pretrained(MODEL_ID,revision=REVISION,
            local_files_only=offline,trust_remote_code=False,use_safetensors=True,
            dtype=torch.float32).to('cpu').eval()
        self.observations=[]
        self.profile=dict(model_id=MODEL_ID,revision=REVISION,device='cpu',dtype='float32',
            threads=2,do_sample=False,enable_thinking=False,max_new_tokens=max_new_tokens,
            input_token_limit=1536,teaching_total_token_limit=2048)

    def generate(self,message):
        text=self.tokenizer.apply_chat_template([dict(role='user',content=message)],
            tokenize=False,add_generation_prompt=True,enable_thinking=False)
        inputs=self.tokenizer(text,return_tensors='pt',add_special_tokens=False)
        count=inputs['input_ids'].shape[1]
        if count>self.profile['input_token_limit']:
            raise ProviderResponseError('Local generation input budget exceeded')
        start=time.perf_counter()
        with self.torch.inference_mode():
            output=self.model.generate(**inputs,max_new_tokens=self.profile['max_new_tokens'],do_sample=False,
                temperature=None,top_p=None,top_k=None)
        generated=output[0,count:]
        result=self.tokenizer.decode(generated,skip_special_tokens=True)
        self.observations.append(dict(input_tokens=count,output_tokens=len(generated),
            elapsed_seconds=round(time.perf_counter()-start,4),raw_output=result,
            hit_output_limit=len(generated)>=self.profile['max_new_tokens']))
        if not result.strip():raise ProviderResponseError('Empty local generation')
        return result
