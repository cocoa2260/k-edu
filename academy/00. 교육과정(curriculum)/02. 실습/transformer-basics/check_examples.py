"""Check K2-02 synthetic arithmetic, shape/mask boundaries and incremental K/V.

Python standard library only. Run: python check_examples.py [--output PATH]
This is not trained-model inference, a complete Transformer or a benchmark.
Mask convention in this file: True permits a key, False excludes it before softmax.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

FIXTURE = Path(__file__).with_name("examples.json")
TOLERANCE = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def close(actual, expected, tolerance: float = TOLERANCE) -> None:
    if isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), "shape differs from reference")
        for a, e in zip(actual, expected):
            close(a, e, tolerance)
    else:
        require(math.isfinite(actual) and abs(actual - expected) <= tolerance, "numeric reference mismatch")


def shape(matrix: list[list[float]]) -> tuple[int, int]:
    require(bool(matrix) and bool(matrix[0]), "empty matrix")
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    require(all(math.isfinite(v) for row in matrix for v in row), "nonfinite matrix")
    return len(matrix), width


def dot(a: list[float], b: list[float]) -> float:
    require(bool(a) and len(a) == len(b), "dot dimensions differ")
    return sum(x * y for x, y in zip(a, b))


def multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    _, inner = shape(a)
    b_rows, b_cols = shape(b)
    require(inner == b_rows, "matrix inner dimensions differ")
    return [[sum(row[k] * b[k][j] for k in range(inner)) for j in range(b_cols)] for row in a]


def add(a: list[float], b: list[float]) -> list[float]:
    require(len(a) == len(b), "addition dimensions differ")
    return [x + y for x, y in zip(a, b)]


def relu(a: list[float]) -> list[float]:
    return [max(0.0, x) for x in a]


def softmax(scores: list[float], allowed: list[bool]) -> list[float]:
    require(bool(scores) and len(scores) == len(allowed), "mask length differs")
    require(all(type(x) is bool for x in allowed), "boolean mask required")
    require(all(math.isfinite(x) for x in scores), "nonfinite score")
    require(any(allowed), "all keys masked")
    maximum = max(x for x, permit in zip(scores, allowed) if permit)
    exponents = [math.exp(x - maximum) if permit else 0.0 for x, permit in zip(scores, allowed)]
    denominator = sum(exponents)
    return [x / denominator for x in exponents]


def attend(query: list[float], keys: list[list[float]], values: list[list[float]],
           allowed: list[bool]) -> tuple[list[float], list[float]]:
    n, dimension = shape(keys)
    value_n, value_dimension = shape(values)
    require(n == value_n and dimension == len(query), "Q/K/V dimensions differ")
    scores = [dot(query, key) / math.sqrt(dimension) for key in keys]
    weights = softmax(scores, allowed)
    output = [sum(weights[i] * values[i][j] for i in range(n)) for j in range(value_dimension)]
    return output, weights


def project(x, attention):
    return tuple(multiply(x, attention[name]) for name in ("WQ", "WK", "WV"))


def full_attention(x, attention, causal: bool):
    q, k, v = project(x, attention)
    outputs, weights = [], []
    for i, query in enumerate(q):
        allowed = [j <= i if causal else True for j in range(len(k))]
        output, row = attend(query, k, v, allowed)
        outputs.append(output)
        weights.append(row)
    return outputs, weights


def sinusoidal(position: int, dimension: int) -> list[float]:
    require(dimension > 0 and dimension % 2 == 0, "even positive dimension required")
    result = []
    for i in range(dimension // 2):
        angle = position / (10000 ** (2 * i / dimension))
        result.extend([math.sin(angle), math.cos(angle)])
    return result


def rotate(pair: list[float], angle: float) -> list[float]:
    require(len(pair) == 2, "rotation needs a two-dimensional pair")
    c, s = math.cos(angle), math.sin(angle)
    return [pair[0] * c - pair[1] * s, pair[0] * s + pair[1] * c]


def layernorm(x: list[float], epsilon: float) -> list[float]:
    require(bool(x) and epsilon > 0, "invalid normalization input")
    mean = sum(x) / len(x)
    variance = sum((v - mean) ** 2 for v in x) / len(x)
    return [(v - mean) / math.sqrt(variance + epsilon) for v in x]


def kv_bytes(config: dict) -> int:
    require(all(type(config[k]) is int and config[k] > 0 for k in ("B", "L", "T", "Hq", "Hkv", "D", "S")), "invalid cache dimensions")
    require(config["Hq"] % config["Hkv"] == 0, "query heads must form equal KV groups in this example")
    return 2 * math.prod(config[k] for k in ("B", "L", "T", "Hkv", "D", "S"))


def reject(name: str, action) -> str:
    try:
        action()
    except ValueError:
        return name
    raise AssertionError(f"invalid case not rejected: {name}")


def run() -> dict:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    a, t, c, p = (fixture[k] for k in ("affine", "attention", "components", "positions"))
    z = add(multiply([a["x"]], a["W"])[0], a["b"])
    close(z, a["expected_z"])
    close(relu(z), a["expected_relu"])
    close(relu(multiply([a["x"]], a["W"])[0]), a["expected_no_bias_relu"])
    q, k, v = project(t["X"], t)
    for actual, expected in zip((q, k, v), (t["expected_Q"], t["expected_K"], t["expected_V"])):
        close(actual, expected)
    close([dot(q[2], key) for key in k], t["row3_dots"])
    unmasked, unmasked_weights = full_attention(t["X"], t, False)
    causal, causal_weights = full_attention(t["X"], t, True)
    for actual, expected in (
        (unmasked[2], t["row3_output"]), (unmasked_weights[2], t["row3_weights"]),
        (unmasked[1], t["row2_unmasked_output"]), (unmasked_weights[1], t["row2_unmasked_weights"]),
        (causal[1], t["row2_causal_output"]), (causal_weights[1], t["row2_causal_weights"]),
    ):
        close(actual, expected)
    for row in unmasked_weights + causal_weights:
        close(sum(row), 1.0)
    stable = softmax([1000, 1001, 1002], [True] * 3)
    close(stable, softmax([0, 1, 2], [True] * 3))
    no_scale = softmax(t["row3_dots"], [True] * 3)
    require(abs(no_scale[2] - unmasked_weights[2][2]) > 0.01, "missing scale counterexample lost")
    post_mask_weights = [unmasked_weights[1][0], unmasked_weights[1][1], 0.0]
    require(abs(sum(post_mask_weights) - 1) > 0.1, "post-softmax masking counterexample lost")
    # A huge PAD key/value must have no effect when excluded before normalization.
    pad_k, pad_v = k + [[100, 100]], v + [[1000, 1000]]
    pad_out, pad_weights = attend(q[1], pad_k, pad_v, [True, True, False, False])
    close(pad_out, causal[1])
    close(pad_weights[2:], [0.0, 0.0])
    # A future token cannot change earlier positions under a causal mask.
    altered_x = t["X"][:2] + [[10, -10]]
    changed_causal, _ = full_attention(altered_x, t, True)
    close(changed_causal[:2], causal[:2])
    changed_unmasked, _ = full_attention(altered_x, t, False)
    require(max(abs(x - y) for x, y in zip(changed_unmasked[1], unmasked[1])) > 0.01, "future-leakage counterexample lost")
    joined = c["heads"][0] + c["heads"][1]
    projection = multiply([joined], c["WO"])[0]
    residual = add(c["residual_input"], projection)
    norm = layernorm(c["layernorm_x"], c["epsilon"])
    ffn_z = add(multiply([c["ffn_x"]], c["W1"])[0], c["b1"])
    ffn_hidden = relu(ffn_z)
    ffn_output = multiply([ffn_hidden], c["W2"])[0]
    for actual, expected in (
        (projection, c["expected_projection"]), (residual, c["expected_residual"]),
        (norm, c["expected_layernorm"]), (ffn_z, c["expected_ffn_z"]),
        (ffn_hidden, c["expected_ffn_hidden"]), (ffn_output, c["expected_ffn_output"]),
    ):
        close(actual, expected)
    for position in (0, 1):
        close(sinusoidal(position, p["sinusoidal_dimension"]), p[f"position_{position}"])
    rotated = rotate(p["rotation_input"], p["rotation_radians"])
    close(rotated, p["expected_rotated"])
    close(dot(p["rotation_input"], rotated), 0.0)
    close(dot(rotated, rotated), 1.0)
    close(dot(rotate([1, 2], 0.7), rotate([3, 4], 0.7)), 11.0)
    permutation = [2, 0, 1]
    permuted_x = [t["X"][i] for i in permutation]
    permuted_out, _ = full_attention(permuted_x, t, False)
    close(permuted_out, [unmasked[i] for i in permutation])
    pooled = [sum(row[j] for row in unmasked) / len(unmasked) for j in range(2)]
    permuted_pooled = [sum(row[j] for row in permuted_out) / len(permuted_out) for j in range(2)]
    close(pooled, permuted_pooled)
    # Compare the Prefill result and two incremental Decode-input steps.
    prefix = [row[:] for row in t["X"]]
    cache_k, cache_v = [row[:] for row in k], [row[:] for row in v]
    cache_observations = []
    for step in range(3):
        if step:
            new_x = fixture["cache"]["additional_inputs"][step - 1]
            new_q, new_k, new_v = project([new_x], t)
            prefix.append(new_x)
            cache_k.extend(new_k)
            cache_v.extend(new_v)
            query = new_q[0]
        else:
            query = q[-1]
        incremental, _ = attend(query, cache_k, cache_v, [True] * len(cache_k))
        full, _ = full_attention(prefix, t, True)
        close(incremental, full[-1])
        close(full[:3], causal)
        expected_length = fixture["cache"]["expected_processed_prefix_lengths"][step]
        require(len(cache_k) == len(cache_v) == expected_length, "cache length differs")
        cache_observations.append({"processed_prefix_length": len(cache_k), "full_last": full[-1], "incremental_last": incremental, "max_absolute_difference": max(abs(x-y) for x,y in zip(full[-1], incremental))})
    memories = []
    for config in fixture["memory"]:
        size = kv_bytes(config)
        require(size == config["expected_bytes"], "KV payload size differs")
        memories.append({"name": config["name"], "bytes": size, "KiB": size / 1024})
    rejected = [
        reject("matrix inner-dimension mismatch", lambda: multiply([[1, 2]], [[1, 0], [0, 1], [1, 1]])),
        reject("ragged matrix", lambda: multiply([[1, 2], [1]], [[1], [2]])),
        reject("all keys masked", lambda: softmax([0, 1], [False, False])),
        reject("mask length mismatch", lambda: softmax([0, 1], [True])),
        reject("cache K/V length mismatch", lambda: attend([1, 0], [[1, 0]], [[1, 0], [0, 1]], [True])),
        reject("residual shape mismatch", lambda: add([1, 2], [1, 2, 3])),
        reject("nonfinite attention score", lambda: softmax([float("nan")], [True])),
        reject("invalid zero cache dimension", lambda: kv_bytes({**fixture["memory"][0], "T": 0})),
    ]
    return {
        "status": "passed", "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "tolerance": TOLERANCE, "scope": "synthetic component and single-layer attention arithmetic only",
        "affine": {"pre_activation": z, "relu": relu(z)},
        "attention": {"row3_weights": unmasked_weights[2], "row3_output": unmasked[2], "row2_causal_weights": causal_weights[1], "row2_causal_output": causal[1], "masked_pad_weights": pad_weights[2:]},
        "components": {"projection": projection, "residual": residual, "layernorm": norm, "ffn_output": ffn_output},
        "position_checks": {"sinusoidal_0_1": "passed", "same_rotation_dot_product": "passed", "unmasked_no_position_permutation_equivariance": "passed", "mean_pooling_permutation_invariance": "passed"},
        "boundary_counterexamples": {"missing_sqrt_scale_changes_weights": True, "post_softmax_zero_without_renormalization_sum": sum(post_mask_weights), "future_token_changes_unmasked_but_not_causal_prefix": True},
        "cache_prefix_comparisons": cache_observations, "cache_includes_position_or_full_block": False,
        "kv_memory_payload": memories, "rejected_invalid_inputs": rejected,
        "pretrained_model_calls": 0, "training_executed": False, "token_generation_executed": False,
        "performance_benchmark": "not_run", "independent_quality_review": "not_run", "classroom_trial": "not_run",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = json.dumps(run(), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
