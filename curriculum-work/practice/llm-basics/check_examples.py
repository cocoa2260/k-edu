"""Check K2-03 synthetic probability/decoding and annotated exercise records.

Python standard library only: python check_examples.py [--output PATH]
No pretrained model, response generation, semantic grader or latency benchmark.
The evaluation annotations are authored answer keys, not inferred by this code.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

FIXTURE = Path(__file__).with_name("examples.json")
TOLERANCE = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def close(actual, expected) -> None:
    if isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), "reference shape mismatch")
        for a, b in zip(actual, expected):
            close(a, b)
    else:
        require(math.isfinite(actual) and abs(actual - expected) <= TOLERANCE, "numeric reference mismatch")


def probabilities(logits: list[float], temperature: float) -> list[float]:
    require(math.isfinite(temperature) and temperature > 0, "positive finite temperature required")
    require(bool(logits) and all(math.isfinite(z) for z in logits), "finite nonempty logits required")
    maximum = max(logits)
    exponents = [math.exp((z - maximum) / temperature) for z in logits]
    denominator = sum(exponents)
    return [e / denominator for e in exponents]


def check_distribution(p: list[float]) -> None:
    require(bool(p) and all(math.isfinite(x) and 0 <= x <= 1 for x in p), "invalid probabilities")
    close(sum(p), 1.0)


def renormalize(p: list[float], keep: list[int]) -> list[float]:
    mass = sum(p[i] for i in keep)
    require(mass > 0, "no retained probability mass")
    return [x / mass if i in keep else 0.0 for i, x in enumerate(p)]


def top_k(p: list[float], k: int) -> list[float]:
    check_distribution(p)
    require(type(k) is int and 1 <= k <= len(p), "k must be in vocabulary range in this exercise")
    order = sorted(range(len(p)), key=lambda i: (-p[i], i))
    return renormalize(p, order[:k])


def top_p(p: list[float], threshold: float) -> list[float]:
    check_distribution(p)
    require(math.isfinite(threshold) and 0 < threshold <= 1, "top-p threshold outside (0,1]")
    order = sorted(range(len(p)), key=lambda i: (-p[i], i))
    keep, mass = [], 0.0
    for i in order:
        keep.append(i)
        mass += p[i]
        if mass >= threshold:
            break
    return renormalize(p, keep)


def select(p: list[float], u: float) -> int:
    check_distribution(p)
    require(math.isfinite(u) and 0 <= u < 1, "sampling lookup must be in [0,1)")
    cumulative = 0.0
    for i, probability in enumerate(p):
        cumulative += probability
        if u < cumulative:
            return i
    # Accommodate floating-point summation at the upper endpoint, not a zero-mass token.
    return max(i for i, probability in enumerate(p) if probability > 0)


def beam_two_steps(tree: dict, width: int) -> list[tuple[str, float]]:
    require(type(width) is int and width > 0, "positive beam width required")
    rank = lambda items: sorted(items, key=lambda x: (-x[1], x[0]))[:width]
    prefix = rank(list(tree["root"].items()))
    return rank([(first + second, p1 * p2) for first, p1 in prefix for second, p2 in tree["after"][first].items()])


def exercise_candidate(statuses: dict[str, str]) -> bool:
    require(set(statuses) == {"format", "content", "grounding", "safety", "illustrative_timeliness"}, "missing evaluation dimension")
    require(all(s in {"pass", "fail", "not_assessed"} for s in statuses.values()), "invalid review label")
    return all(s == "pass" for s in statuses.values())


def evaluate_annotated_case(case: dict, policy: dict) -> dict:
    response = case["response"]
    format_ok = all(isinstance(response.get(field), str) and bool(response[field].strip()) for field in policy["required_fields"])
    review = case["annotated_review"]
    require(set(review) == {"content", "grounding", "safety"}, "annotation dimensions differ")
    latency = case["illustrative_latency_ms"]
    require(type(latency) is int and latency >= 0, "invalid illustrative latency")
    statuses = {
        "format": "pass" if format_ok else "fail", **review,
        "illustrative_timeliness": "pass" if latency <= policy["illustrative_max_latency_ms"] else "fail",
    }
    candidate = exercise_candidate(statuses)
    require(format_ok == case["expected_format"], "format differs from authored key")
    require(candidate == case["expected_exercise_candidate"], "candidate differs from authored key")
    return {"id": case["id"], "statuses": statuses, "exercise_candidate": candidate, "actual_release_accepted": False}


def reject(name: str, action) -> str:
    try:
        action()
    except ValueError:
        return name
    raise AssertionError(f"did not reject: {name}")


def run() -> dict:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    d, tree, policy = (fixture[k] for k in ("decoding", "beam_tree", "evaluation"))
    observed = {}
    for temperature in (1, 0.5, 2):
        p = probabilities(d["logits"], temperature)
        close(p, d["expected_probabilities"][str(temperature)])
        check_distribution(p)
        observed[str(temperature)] = p
    base = observed["1"]
    close(probabilities([z + 1000 for z in d["logits"]], 1), base)
    loss = -math.log(base[d["target_index"]])
    close(loss, d["expected_target_nll_nats"])
    filtered_k = top_k(base, d["top_k"])
    filtered_p = top_p(base, d["top_p"])
    close(filtered_k, d["expected_filtered"])
    close(filtered_p, d["expected_filtered"])
    # The token crossing the top-p boundary must be retained, then mass renormalized.
    close(top_p(base, base[0]), [1, 0, 0, 0])
    require(sum(x > 0 for x in top_p(base, base[0] + 0.00001)) == 2, "top-p crossing token lost")
    close(top_k(base, len(base)), base)
    close(top_p(base, 1), base)
    require(select([1, 0, 0, 0], 0) == 0, "sampling zero endpoint differs")
    comparisons = []
    for temperature, expected in zip(d["comparison_temperatures"], d["expected_selected"]):
        p = probabilities(d["logits"], temperature)
        chosen = d["tokens"][select(p, d["comparison_fixed"]["uniform_draw"])]
        require(chosen == expected, "sampling comparison differs")
        config = {**copy.deepcopy(d["comparison_fixed"]), "logits": d["logits"], "temperature": temperature}
        comparisons.append({"config": config, "probabilities": p, "selected_token": chosen, "pretrained_generation_executed": False})
    changed = [k for k in comparisons[0]["config"] if comparisons[0]["config"][k] != comparisons[1]["config"][k]]
    require(changed == ["temperature"], "more than one decoding condition changed")
    greedy = [d["tokens"][max(range(len(base)), key=lambda i: probabilities(d["logits"], temperature)[i])] for temperature in (1, 0.5)]
    require(greedy == ["A", "A"], "positive temperature changed greedy rank")
    joint = {first + second: p1 * p2 for first, p1 in tree["root"].items() for second, p2 in tree["after"][first].items()}
    close(sum(joint.values()), 1.0)
    for sequence, value in joint.items():
        close(value, tree["expected_joint"][sequence])
    width1, width2 = beam_two_steps(tree, 1), beam_two_steps(tree, 2)
    require(width1[0][0] == tree["expected_greedy"] and width2[0][0] == tree["expected_width2_best"], "beam example differs")
    require(policy["latency_origin"] == "authored_numbers_not_measured", "latency provenance changed")
    require([c["id"] for c in policy["cases"]] == [f"E{i:02}" for i in range(1, 7)], "case IDs differ")
    case_results = [evaluate_annotated_case(c, policy) for c in policy["cases"]]
    all_pass = {k: "pass" for k in ("format", "content", "grounding", "safety", "illustrative_timeliness")}
    require(not exercise_candidate({**all_pass, "grounding": "not_assessed"}), "unknown grounding promoted to pass")
    require(not exercise_candidate({**all_pass, "safety": "fail"}), "safety failure averaged away")
    negative_latency = {**copy.deepcopy(policy["cases"][0]), "illustrative_latency_ms": -1}
    rejected = [
        reject("zero temperature in Softmax formula", lambda: probabilities(d["logits"], 0)),
        reject("nonfinite logit", lambda: probabilities([float("nan")], 1)),
        reject("zero top-k", lambda: top_k(base, 0)),
        reject("zero top-p", lambda: top_p(base, 0)),
        reject("top-p above one", lambda: top_p(base, 1.1)),
        reject("sampling lookup at excluded endpoint one", lambda: select(base, 1)),
        reject("unknown review label", lambda: exercise_candidate({**all_pass, "safety": "probably"})),
        reject("negative illustrative latency", lambda: evaluate_annotated_case(negative_latency, policy)),
    ]
    return {
        "status": "passed", "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), "tolerance": TOLERANCE,
        "scope": "synthetic decoding arithmetic, structural format checks and authored-review bookkeeping only",
        "probabilities": observed, "target_nll_nats": loss,
        "filters": {"top_k_2": filtered_k, "top_p_0_8": filtered_p},
        "one_setting_comparison": comparisons, "changed_configuration_keys": changed, "greedy_selected": greedy,
        "beam_example": {"joint_probabilities": joint, "width1_best": width1[0], "width2_best": width2[0]},
        "annotated_case_results": case_results,
        "evaluation_provenance": {"content_grounding_safety": "same_author_supplied_example_annotations_not_independent_semantic_grading", "latency": policy["latency_origin"]},
        "unknown_and_safety_blocking": "verified_on_supplied_statuses_only", "rejected_invalid_inputs": rejected,
        "pretrained_model_calls": 0, "training_executed": False, "pretrained_generation_comparison": "not_run",
        "real_latency_measurement": "not_run", "independent_quality_review": "not_run", "classroom_trial": "not_run",
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
