"""Verify K2-01 authored fixtures; no model training or quality evaluation.

Run with Python 3: python check_examples.py [--output PATH]
Uses only the standard library. JSON is a machine record, not a student prerequisite.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check_split(rows: list[dict[str, str]]) -> dict:
    fields = {
        "sample_id", "root_group", "variant", "split", "text",
        "policy_context", "needs_escalation", "label_basis",
    }
    require(len(rows) == 24, "expected 24 authored split-example rows")
    ids: set[str] = set()
    texts: set[str] = set()
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        require(set(row) == fields, "unexpected split-example fields")
        require(all(isinstance(v, str) and v.strip() for v in row.values()), "empty field")
        require(row["sample_id"] not in ids, "duplicate sample ID")
        ids.add(row["sample_id"])
        require(row["text"].strip() not in texts, "exact duplicate text")
        texts.add(row["text"].strip())
        require(row["split"] in {"train", "dev", "test"}, "invalid split")
        require(row["needs_escalation"] in {"0", "1"}, "invalid binary label")
        require(row["variant"] in {"original", "human_paraphrase"}, "invalid variant")
        require(row["policy_context"] == "A-v2-public-only; B-body-unavailable", "context changed")
        groups[row["root_group"]].append(row)
    require(set(groups) == {f"G{i:02}" for i in range(1, 13)}, "unexpected groups")
    for group, members in groups.items():
        require(len(members) == 2, "each group needs original and paraphrase")
        require(len({r["split"] for r in members}) == 1, "root group crosses splits")
        require(len({r["needs_escalation"] for r in members}) == 1, "conflicting group labels")
        require(len({r["label_basis"] for r in members}) == 1, "conflicting group label basis")
        require({r["variant"] for r in members} == {"original", "human_paraphrase"}, "variant missing")
        for row in members:
            suffix = "a" if row["variant"] == "original" else "b"
            require(row["sample_id"] == f"{group}-{suffix}", "broken lineage ID")
    counts = Counter(r["split"] for r in rows)
    require(counts == {"train": 12, "dev": 6, "test": 6}, "unexpected split counts")
    labels = {
        split: dict(Counter(r["needs_escalation"] for r in rows if r["split"] == split))
        for split in ("train", "dev", "test")
    }
    require(labels == {"train": {"0": 4, "1": 8}, "dev": {"0": 2, "1": 4}, "test": {"0": 2, "1": 4}}, "unexpected label counts")
    return {
        "rows": len(rows), "original_groups": len(groups), "split_rows": dict(counts),
        "label_counts": labels, "known_lineage_overlap": False,
        "semantic_deduplication_verified": False,
        "known_similar_intents": ["G05", "G11"],
        "new_document_generalization_evaluated": False,
    }


def check_scores(rows: list[dict[str, str]]) -> None:
    fields = {"case_id", "split", "needs_escalation", "illustrative_score", "score_origin"}
    require(len(rows) == 20, "expected 20 arithmetic rows")
    require({r.get("case_id") for r in rows} == {f"D{i:02}" for i in range(1, 21)}, "missing/duplicate metric ID")
    for row in rows:
        require(set(row) == fields, "unexpected arithmetic fields")
        require(row["split"] == "dev", "arithmetic fixture is Dev, not Test")
        require(row["needs_escalation"] in {"0", "1"}, "invalid arithmetic label")
        require(row["score_origin"] == "authored_arithmetic_example_not_model_output", "score origin changed")
        try:
            score = Decimal(row["illustrative_score"])
        except (InvalidOperation, TypeError):
            raise ValueError("invalid score") from None
        require(score.is_finite() and Decimal(0) <= score <= Decimal(1), "score out of range/nonfinite")
    require(Counter(r["needs_escalation"] for r in rows) == {"1": 4, "0": 16}, "unexpected arithmetic class counts")


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def summarize(truth: list[int], predicted: list[int]) -> dict:
    require(len(truth) == len(predicted) and bool(truth), "nonempty equal-length labels required")
    require(all(x in (0, 1) for x in truth + predicted), "binary labels required")
    tp = sum(y == 1 and p == 1 for y, p in zip(truth, predicted))
    fp = sum(y == 0 and p == 1 for y, p in zip(truth, predicted))
    fn = sum(y == 1 and p == 0 for y, p in zip(truth, predicted))
    tn = sum(y == 0 and p == 0 for y, p in zip(truth, predicted))
    return {
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "accuracy": ratio(tp + tn, len(truth)), "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn), "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "illustrative_error_weight_10FN_plus_FP": 10 * fn + fp,
    }


def check_rejection(name: str, function, rows: list[dict[str, str]], row_number: int,
                    key: str, value: str) -> str:
    changed = copy.deepcopy(rows)
    changed[row_number][key] = value
    try:
        function(changed)
    except ValueError:
        return name
    raise AssertionError(f"failed to reject: {name}")


def run() -> dict:
    split_rows = read_rows(DATA / "split-examples.csv")
    score_rows = read_rows(DATA / "metric-examples.csv")
    split_summary = check_split(split_rows)
    check_scores(score_rows)
    truth = [int(r["needs_escalation"]) for r in score_rows]
    results = {"always_0": summarize(truth, [0] * len(truth))}
    for cutoff in ("0.70", "0.30"):
        predicted = [int(Decimal(r["illustrative_score"]) >= Decimal(cutoff)) for r in score_rows]
        results[cutoff] = summarize(truth, predicted)
    expected_counts = {
        "always_0": (0, 0, 4, 16), "0.70": (2, 1, 2, 15), "0.30": (4, 4, 0, 12),
    }
    expected_metrics = {
        "always_0": (0.8, None, 0.0, 0.0, 40),
        "0.70": (0.85, 2 / 3, 0.5, 4 / 7, 21),
        "0.30": (0.8, 0.5, 1.0, 2 / 3, 4),
    }
    for cutoff, result in results.items():
        require(tuple(result[k] for k in ("TP", "FP", "FN", "TN")) == expected_counts[cutoff], "confusion matrix differs from lesson")
        values = tuple(result[k] for k in ("accuracy", "precision", "recall", "f1", "illustrative_error_weight_10FN_plus_FP"))
        require(values == expected_metrics[cutoff], "metrics differ from lesson")
    rejected = [
        check_rejection("same-parent paraphrase moved to Test", check_split, split_rows, 1, "split", "test"),
        check_rejection("contradictory paraphrase label", check_split, split_rows, 1, "needs_escalation", "1"),
        check_rejection("duplicate sample ID", check_split, split_rows, 1, "sample_id", "G01-a"),
        check_rejection("nonbinary label", check_split, split_rows, 0, "needs_escalation", "2"),
        check_rejection("score above range", check_scores, score_rows, 0, "illustrative_score", "1.1"),
        check_rejection("nonfinite score", check_scores, score_rows, 0, "illustrative_score", "NaN"),
        check_rejection("Dev relabeled as Test", check_scores, score_rows, 0, "split", "test"),
        check_rejection("wrong score provenance", check_scores, score_rows, 0, "score_origin", "real_model"),
    ]
    no_positives = summarize([0, 0], [0, 0])
    require(all(no_positives[k] is None for k in ("precision", "recall", "f1")), "undefined metric policy differs")
    file_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.glob("*.csv"))}
    return {
        "status": "passed", "scope": "authored fixture structure, lineage and arithmetic only",
        "data_sha256": file_hashes, "split_fixture": split_summary,
        "arithmetic_fixture_rows": len(score_rows), "positive_label": "needs_escalation=1",
        "threshold_rule": "score >= threshold", "score_provenance": "authored_not_model_output",
        "arithmetic_results": results, "rejected_mutations": rejected,
        "zero_denominator_example": no_positives, "model_calls": 0,
        "training_executed": False, "test_performance_evaluated": False,
        "independent_label_review": "not_run", "classroom_trial": "not_run",
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
