"""Small reading exercise: the actual tokenizer calls used by the lab.

Run inspect_tokenizer.py once with downloads allowed to prepare the cache.
This file uses that cache only. It does not load model weights or generate text.
"""
from inspect_tokenizer import HERE, SetupRequired, load_profile, load_real_tokenizer


def main():
    profile = load_profile(HERE / "models.json", "qwen")
    tokenizer, _ = load_real_tokenizer(profile, allow_download=False)

    # 1. Text -> token IDs -> text. Character count and token count can differ.
    text = "안녕하세요. 모델의 입력을 확인합니다."
    ids = tokenizer.encode(text, add_special_tokens=False)
    print("입력:", text)
    print("문자 수 / Token 수:", len(text), len(ids))
    print("IDs:", ids)
    print("복원:", tokenizer.decode(ids, clean_up_tokenization_spaces=False))

    # 2. Compare a long and a short input as one padded batch.
    batch = tokenizer([text, "Hi!"], add_special_tokens=False, padding=True)
    print("패딩된 IDs:", batch["input_ids"])
    print("Attention mask:", batch["attention_mask"])

    # 3. This is rendered INPUT, not a generated answer.
    messages = [{"role": "user", "content": "What is a tokenizer?"}]
    rendered = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        **profile["template_kwargs"],
    )
    print("대화 입력 문자열:", rendered)


if __name__ == "__main__":
    try:
        main()
    except SetupRequired as exc:
        print("준비 필요:", exc)
        raise SystemExit(2)
