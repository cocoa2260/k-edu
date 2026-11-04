"""Compare one offline Vision model on L8 synthetic source images."""
import argparse
import hashlib
import json
import time
from pathlib import Path

from PIL import Image
import torch
import transformers
from transformers import AutoModelForImageTextToText, AutoProcessor

MODEL = "HuggingFaceTB/SmolVLM-256M-Instruct"
REVISION = "7e3e67edbbed1bf9888184d9df282b700a323964"
TABLE = "Read the Korean refund table. Report the four fees in row order and the exception below the table. If unclear, say unreadable. Do not guess."
NOTICE = "Read this Korean refund notice. Extract the application deadline, customer fee and reference ID. If unclear, say unreadable. Do not guess."


def run(snapshot, complex_image, notice_image):
    torch.set_num_threads(4)
    processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True, trust_remote_code=False, use_fast=False)
    model = AutoModelForImageTextToText.from_pretrained(
        snapshot, local_files_only=True, trust_remote_code=False,
        use_safetensors=True, dtype=torch.float32, attn_implementation="sdpa"
    ).eval()
    table = Image.open(complex_image).convert("RGB")
    notice = Image.open(notice_image).convert("RGB")
    # Crop coordinates in PDF points, converted to pixels at 216 dpi (3 px/pt).
    crop_box = (30, 118, 566, 398)
    crop = table.crop(tuple(v * 3 for v in crop_box))
    cases = [
        ("notice", notice, NOTICE, None),
        ("table_full", table, TABLE, None),
        ("table_crop", crop, TABLE, crop_box),
    ]
    results = {}
    for name, picture, prompt, region in cases:
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
        rendered = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=rendered, images=[picture], return_tensors="pt")
        start = time.perf_counter()
        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=96, do_sample=False)
        continuation = outputs[0, inputs["input_ids"].shape[-1]:]
        results[name] = dict(
            page=1, input_crop_points=region, input_size=list(picture.size),
            image_pixel_sha256=hashlib.sha256(picture.tobytes()).hexdigest(),
            output=processor.decode(continuation, skip_special_tokens=True),
            generated_tokens=len(continuation), seconds=round(time.perf_counter() - start, 3),
        )
    return dict(model=MODEL, revision=REVISION, device="cpu", dtype="float32", torch=str(torch.__version__),
                transformers=transformers.__version__, max_new_tokens=96, results=results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ("snapshot", "complex-image", "notice-image", "output"):
        parser.add_argument("--" + argument, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.snapshot, args.complex_image, args.notice_image)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
