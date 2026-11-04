"""Pinned E5 CPU encoder. No model-provided code and no generation API."""
import hashlib
import json

MODEL_ID = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"


def profile_hash(profile):
    return hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()


class E5Encoder:
    def __init__(self, *, offline=True, max_tokens=512):
        import torch
        from transformers import AutoModel, AutoTokenizer
        if max_tokens not in (128, 512):
            raise ValueError("Only documented teaching profiles are supported")
        self.profile = dict(model_id=MODEL_ID, revision=REVISION, dimension=384,
            pooling="attention_mask_mean", normalized=True, max_tokens=max_tokens,
            query_prefix="query: ", passage_prefix="passage: ")
        self.torch = torch
        torch.set_num_threads(2)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION,
            local_files_only=offline, trust_remote_code=False)
        self.model = AutoModel.from_pretrained(MODEL_ID, revision=REVISION,
            local_files_only=offline, trust_remote_code=False, use_safetensors=True).to("cpu").eval()

    def encode(self, texts, kind):
        if kind not in ("query", "passage"):
            raise ValueError("Unknown encoding role")
        if not texts:
            return []
        prefixed = [self.profile[kind + "_prefix"] + text for text in texts]
        # Reject overflow instead of silently losing a policy condition.
        lengths = [len(x) for x in self.tokenizer(prefixed, truncation=False)["input_ids"]]
        if max(lengths) > self.profile["max_tokens"]:
            raise ValueError("Embedding Token limit exceeded; split explicitly")
        batch = self.tokenizer(prefixed, padding=True, return_tensors="pt")
        with self.torch.inference_mode():
            hidden = self.model(**batch).last_hidden_state
            mask = batch["attention_mask"].unsqueeze(-1).to(hidden.dtype)
            pooled = (hidden * mask).sum(1) / mask.sum(1)
            unit = self.torch.nn.functional.normalize(pooled, p=2, dim=1)
        return unit.tolist()
