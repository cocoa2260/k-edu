"""Run one NF4 Qwen training step as a CPU readiness check."""
import argparse
import json
import math
import platform
import resource
import time
from pathlib import Path

import bitsandbytes as bnb
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from app.training_data import MODEL_ID, REVISION, as_example
from tools.lora_lab import tensor_row


def run(data_path):
    torch.set_num_threads(2)
    torch.manual_seed(37)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=REVISION, local_files_only=True, trust_remote_code=False
    )
    quantization = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float32
    )
    started = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=REVISION, local_files_only=True, trust_remote_code=False,
        use_safetensors=True, quantization_config=quantization, device_map={"": "cpu"},
        dtype=torch.float32, attn_implementation="eager"
    )
    load_seconds = time.perf_counter() - started
    layers = [layer for layer in model.modules() if isinstance(layer, bnb.nn.Linear4bit)]
    assert layers and all(layer.weight.quant_state.quant_type == "nf4" for layer in layers)
    assert all(layer.weight.quant_state.nested for layer in layers)
    frozen_sample = layers[0].weight.detach().flatten()[:32].clone()
    prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(
        r=4, lora_alpha=8, lora_dropout=0., target_modules=["q_proj", "v_proj"],
        task_type="CAUSAL_LM", bias="none", revision=REVISION
    )).train()
    trainable = {name: param for name, param in model.named_parameters() if param.requires_grad}
    assert trainable and all("lora_" in name for name in trainable)
    initial = {name: param.detach().clone() for name, param in trainable.items()}
    row = next(row for row in json.loads(data_path.read_text())["examples"] if row["split"] == "train")
    example = as_example(row)
    batch = tensor_row(example, tokenizer)
    optimizer = torch.optim.AdamW(trainable.values(), lr=.0002)
    started = time.perf_counter()
    loss = model(**batch).loss
    assert math.isfinite(float(loss.detach()))
    loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in trainable.values())
    optimizer.step()
    elapsed = time.perf_counter() - started
    delta = sum(float((p.detach() - initial[name]).abs().sum()) for name, p in trainable.items())
    assert delta > 0 and layers[0].weight.grad is None
    assert torch.equal(frozen_sample, layers[0].weight.detach().flatten()[:32])
    return {
        "platform": platform.machine(), "torch": str(torch.__version__), "bitsandbytes": bnb.__version__,
        "cuda_available": torch.cuda.is_available(), "torch_cuda": torch.version.cuda,
        "model_id": MODEL_ID, "revision": REVISION, "quantization": "NF4 double quant",
        "quantized_linear_layers": len(layers), "storage_dtype": str(layers[0].weight.dtype),
        "compute_dtype": "float32", "train_example_id": example.id, "optimizer_steps": 1,
        "loss": float(loss.detach()), "adapter_absolute_delta": delta,
        "frozen_weight_sample_unchanged": True, "load_seconds": round(load_seconds, 3),
        "training_seconds": round(elapsed, 3),
        "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.data), indent=2), flush=True)
