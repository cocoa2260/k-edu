"""Inspect real tokenizer files on CPU; no model weights or inference calls.

Start with --preflight. Downloads require --allow-download; otherwise cached
files are required. A missing dependency/cache never triggers a fake fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.metadata
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPENDENCIES = {"transformers": "4.57.1", "tokenizers": "0.22.1", "huggingface-hub": "0.36.0", "jinja2": "3.1.6"}
TOKENIZER_FILES = ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "added_tokens.json", "vocab.json", "merges.txt", "chat_template.jinja"]


class SetupRequired(Exception):
    """A real execution prerequisite is missing; no success is implied."""


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile(path: Path, profile_name: str) -> dict:
    registry = read_json(path)
    profiles = registry.get("profiles", [])
    names = [p.get("name") for p in profiles]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate profile name")
    chosen = next((p for p in profiles if p.get("name") == profile_name), None)
    if chosen is None:
        raise ValueError("Unknown profile; use qwen or smol")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", chosen.get("model_id", "")):
        raise ValueError("Expected an owner/model ID")
    if not re.fullmatch(r"[0-9a-f]{40}", chosen.get("revision", "")):
        raise ValueError("A full immutable model commit SHA is required")
    if not isinstance(chosen.get("template_kwargs", {}), dict):
        raise ValueError("template_kwargs must be an object")
    return chosen


def load_inputs(path: Path) -> dict:
    data = read_json(path)
    samples, messages = data.get("samples"), data.get("messages")
    if not isinstance(samples, list) or not 2 <= len(samples) <= 20:
        raise ValueError("Provide 2..20 samples")
    ids = [s.get("id") for s in samples if isinstance(s, dict)]
    if len(ids) != len(samples) or any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("Samples need unique nonempty string IDs")
    if any(not isinstance(s.get("text"), str) or not 1 <= len(s["text"]) <= 5000 for s in samples):
        raise ValueError("Each sample text must contain 1..5000 characters")
    if not isinstance(messages, list) or not 1 <= len(messages) <= 10:
        raise ValueError("Provide 1..10 chat messages")
    for m in messages:
        if not isinstance(m, dict) or m.get("role") not in {"system", "user", "assistant"}:
            raise ValueError("This introductory lab supports system/user/assistant roles only")
        if not isinstance(m.get("content"), str) or not 1 <= len(m["content"]) <= 5000:
            raise ValueError("Each chat content must contain 1..5000 characters")
    if messages[-1]["role"] != "user":
        raise ValueError("End this lab's conversation with a user message")
    return data


def dependency_status() -> dict:
    result = {}
    for package, expected in DEPENDENCIES.items():
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed = None
        result[package] = {"expected": expected, "installed": installed, "matches": installed == expected}
    return result


def load_real_tokenizer(profile: dict, allow_download: bool):
    deps = dependency_status()
    if not all(item["matches"] for item in deps.values()):
        raise SetupRequired("Install the pinned lab requirements first; see --preflight")
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer

    try:
        # The explicit allowlist excludes .safetensors, .bin and arbitrary code.
        folder = Path(snapshot_download(
            repo_id=profile["model_id"], revision=profile["revision"],
            allow_patterns=TOKENIZER_FILES, local_files_only=not allow_download,
        ))
    except Exception as exc:
        # Avoid echoing URLs, authentication details or a dependency traceback.
        raise SetupRequired("Tokenizer files unavailable. Check the pinned revision, cache, network and access conditions. No model was run.") from exc
    if not (folder / "tokenizer.json").is_file() or not (folder / "tokenizer_config.json").is_file():
        raise SetupRequired("Cache lacks tokenizer.json or tokenizer_config.json; complete the selected download")
    manifest = [{"name": name, "sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest()}
                for name in TOKENIZER_FILES if (folder / name).is_file()]
    try:
        tokenizer = AutoTokenizer.from_pretrained(str(folder), local_files_only=True, trust_remote_code=False)
    except Exception as exc:
        raise SetupRequired("Pinned tokenizer could not be loaded locally; check library compatibility. No fallback was used.") from exc
    if not tokenizer.chat_template:
        raise SetupRequired("This lab needs the model's own chat template; do not invent one")
    if tokenizer.pad_token_id is None:
        raise SetupRequired("This profile has no pad token; record the limitation instead of silently assigning EOS")
    return tokenizer, manifest


def inspect(tokenizer, profile: dict, inputs: dict, max_length: int) -> dict:
    rows = []
    for sample in inputs["samples"]:
        ids = tokenizer.encode(sample["text"], add_special_tokens=False)
        short = tokenizer.encode(sample["text"], add_special_tokens=False, truncation=True, max_length=max_length)
        decoded = tokenizer.decode(ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        rows.append({"id": sample["id"], "text": sample["text"], "character_count": len(sample["text"]),
                     "token_count": len(ids), "ids": ids, "pieces": tokenizer.convert_ids_to_tokens(ids),
                     "decoded": decoded, "round_trip_exact": decoded == sample["text"],
                     "truncated_ids": short, "truncated_count": len(short), "was_truncated": len(short) < len(ids)})
    texts = [s["text"] for s in inputs["samples"]]
    padded = tokenizer(texts, add_special_tokens=False, padding=True, return_attention_mask=True)
    kwargs = profile.get("template_kwargs", {})
    rendered = tokenizer.apply_chat_template(inputs["messages"], tokenize=False, add_generation_prompt=True, **kwargs)
    native_ids = tokenizer.apply_chat_template(inputs["messages"], tokenize=True, add_generation_prompt=True, **kwargs)
    encoded_once = tokenizer.encode(rendered, add_special_tokens=False)
    with_extra_specials = tokenizer.encode(rendered, add_special_tokens=True)
    return {"schema_version": "0.1", "status": "actual_tokenizer_observed", "scope": "tokenizer_only_no_generation_no_training",
            "model_id": profile["model_id"], "revision": profile["revision"],
            "max_length": max_length, "samples": rows,
            "special_tokens": {"bos_token": tokenizer.bos_token, "bos_token_id": tokenizer.bos_token_id,
                               "eos_token": tokenizer.eos_token, "eos_token_id": tokenizer.eos_token_id,
                               "pad_token": tokenizer.pad_token, "pad_token_id": tokenizer.pad_token_id,
                               "all_special_tokens": tokenizer.all_special_tokens},
            "padding": {"padding_side": tokenizer.padding_side, "input_ids": padded["input_ids"],
                        "attention_mask": padded["attention_mask"]},
            "chat": {"messages": inputs["messages"], "template_kwargs": kwargs, "rendered": rendered,
                     "ids": native_ids, "token_count": len(native_ids),
                     "encode_without_added_specials_matches": native_ids == encoded_once,
                     "encode_with_added_specials_changes_ids": native_ids != with_extra_specials,
                     "extra_specials_token_count": len(with_extra_specials)}}


def check_observation(data: dict) -> list[str]:
    """Consistency checks, not proof of model quality or human authorship."""
    errors = []
    if data.get("status") != "actual_tokenizer_observed" or not re.fullmatch(r"[0-9a-f]{40}", data.get("revision", "")):
        errors.append("Missing actual-tokenizer marker or immutable revision")
    rows = data["samples"]
    pad = data["padding"]
    if len(pad["input_ids"]) != len(rows) or len(pad["attention_mask"]) != len(rows):
        errors.append("Padding row count differs from the input samples")
        return errors
    widths = set()
    for row, ids, mask in zip(rows, pad["input_ids"], pad["attention_mask"]):
        widths.add(len(ids))
        if row["token_count"] != len(row["ids"]) or len(row["pieces"]) != len(row["ids"]):
            errors.append("Sample token/ID/piece lengths differ: " + row["id"])
        if row["truncated_count"] != len(row["truncated_ids"]) or row["truncated_count"] > data["max_length"]:
            errors.append("Truncation limit/count mismatch: " + row["id"])
        expected_count = min(len(row["ids"]), data["max_length"])
        if row["truncated_count"] != expected_count or row["was_truncated"] != (len(row["ids"]) > data["max_length"]):
            errors.append("Truncation behavior differs from input length/limit: " + row["id"])
        if len(ids) != len(mask) or any(m not in (0, 1) for m in mask):
            errors.append("Invalid padding mask: " + row["id"])
        elif [x for x, m in zip(ids, mask) if m == 1] != row["ids"]:
            errors.append("Padding mask changes actual content: " + row["id"])
        elif any(x != data["special_tokens"]["pad_token_id"] for x, m in zip(ids, mask) if m == 0):
            errors.append("Masked padding is not the tokenizer's pad token: " + row["id"])
    if len(widths) > 1:
        errors.append("Padding did not produce a common batch width")
    if not data["chat"]["encode_without_added_specials_matches"]:
        errors.append("Chat template tokenization and rendered-text encoding disagree")
    return errors


def readable(data: dict) -> str:
    def safe(value):
        return html.escape(str(value)).replace("|", "&#124;").replace("`", "&#96;")
    lines = ["# Tokenizer 실제 관찰 결과", "", "이 파일은 Tokenizer 실행 결과다. 모델 답변 생성·훈련 결과가 아니다.", "",
             "- 모델: " + safe(data["model_id"]), "- 리비전: " + data["revision"],
             "- 검사: " + ("내부 정합성 통과" if not data["checks"] else "오류 확인 필요"), "",
             "## 문장별 관찰", ""]
    for row in data["samples"]:
        lines += ["### " + safe(row["id"]), "", "- 입력: " + safe(row["text"]),
                  f'- 문자 수 / Token 수: {row["character_count"]} / {row["token_count"]}',
                  "- Token IDs: " + safe(row["ids"]), "- Token 표시: " + safe(row["pieces"]),
                  "- decode: " + safe(row["decoded"]), "- 완전 복원 여부: " + str(row["round_trip_exact"]),
                  "- 길이 제한 뒤 IDs: " + safe(row["truncated_ids"]),
                  "- 잘림 발생: " + str(row["was_truncated"]), ""]
    lines += ["## Padding", "", "- 입력 IDs: " + safe(data["padding"]["input_ids"]),
              "- Attention mask: " + safe(data["padding"]["attention_mask"]), "",
              "0은 패딩 자리, 1은 실제 입력 자리다. 학습 정답용 Loss mask와 혼동하지 않는다.", "",
              "## Chat Template", "", "다음은 입력을 변환한 문자열이며 모델이 생성한 답변이 아니다.", ""]
    lines += ["> " + safe(line) for line in data["chat"]["rendered"].splitlines()]
    lines += ["", "- Template→IDs와 문자열 재인코딩 일치: " + str(data["chat"]["encode_without_added_specials_matches"]),
              "- 특수 Token 자동 추가를 켰을 때 IDs 변화: " + str(data["chat"]["encode_with_added_specials_changes_ids"]),
              "", "변화가 없을 수도 있다. 해당 Tokenizer의 자동 추가 규칙을 확인하고 관찰 사실을 기록한다.", ""]
    if data["checks"]:
        lines += ["## 확인할 오류", ""] + ["- " + safe(x) for x in data["checks"]]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["qwen", "smol"], default="qwen")
    parser.add_argument("--profiles", type=Path, default=HERE / "models.json")
    parser.add_argument("--inputs", type=Path, default=HERE / "inputs.json")
    parser.add_argument("--max-length", type=int, default=8)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--preflight", action="store_true", help="Check local configuration/dependency metadata without network or tokenizer execution")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.max_length <= 128:
            raise ValueError("--max-length must be 1..128")
        profile, inputs = load_profile(args.profiles, args.profile), load_inputs(args.inputs)
        if args.preflight:
            deps = dependency_status()
            ready = all(x["matches"] for x in deps.values())
            print(json.dumps({"status": "dependency_metadata_ready_cache_not_checked" if ready else "setup_required", "python": platform.python_version(),
                              "dependencies": deps, "profile": profile, "sample_count": len(inputs["samples"]),
                              "tokenizer_executed": False, "network_used": False}, ensure_ascii=False, indent=2))
            return 0 if ready else 2
        if args.output is None:
            raise ValueError("--output is required for a real observation")
        if args.output.exists() and any(args.output.iterdir()):
            raise ValueError("Use a new/empty output folder; existing observations are never overwritten")
        tokenizer, manifest = load_real_tokenizer(profile, args.allow_download)
        data = inspect(tokenizer, profile, inputs, args.max_length)
        data.update({"created_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                     "dependencies": dependency_status(), "tokenizer_files": manifest,
                     "input_sha256": hashlib.sha256(args.inputs.read_bytes()).hexdigest(),
                     "download_permission": args.allow_download})
        data["checks"] = check_observation(data)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "observations.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.output / "observations.md").write_text(readable(data), encoding="utf-8")
        print(json.dumps({"status": data["status"], "checks_passed": not data["checks"], "report": str(args.output / "observations.md")}, ensure_ascii=False))
        return 0 if not data["checks"] else 1
    except SetupRequired as exc:
        print(json.dumps({"status": "setup_required", "message": str(exc), "tokenizer_executed": False}, ensure_ascii=False), file=sys.stderr)
        return 2
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input_or_output", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
