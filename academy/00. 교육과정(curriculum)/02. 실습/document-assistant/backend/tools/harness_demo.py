"""Offline L2 fault injection. Scripted responses are NOT model observations."""
import argparse
import json
from pathlib import Path

from app.harness import Limits, run_harness
from app.providers.errors import ProviderTimeoutError, ProviderUpstreamError


def draft(answer="자료를 확인한 뒤 사람이 사실과 조건을 검토해야 합니다.", citations=None):
    return json.dumps({"outcome": "answer", "answer": answer,
                       "citations": ["DOC-A"] if citations is None else citations}, ensure_ascii=False)


class ScriptedProvider:
    provider_name = "scripted-fixture"
    model_name = "no-model-executed"

    def __init__(self, actions):
        self.actions = iter(actions)
        self.messages = []

    def generate(self, message):
        self.messages.append(message)
        action = next(self.actions)
        if isinstance(action, Exception):
            raise action
        return action


def run_demo():
    scenarios = {
        "valid_shape": [draft()],
        "timeout_then_success": [ProviderTimeoutError(), draft()],
        "repair_then_success": ["not json", draft()],
        "repeated_invalid": ["not json", "still not json"],
        "global_three_calls": [ProviderTimeoutError(), "not json", draft()],
        "retry_exhausted": [ProviderTimeoutError(), ProviderTimeoutError()],
        "upstream_terminal": [ProviderUpstreamError()],
        "restricted_citation": [draft(citations=["DOC-R"]), draft(citations=["DOC-R"])],
        "forged_approval": [json.dumps({"outcome":"answer", "answer":"승인됨",
                                      "citations":["DOC-A"], "approved":True})] * 2,
        "wrong_fact_shape_passes": [draft("식비 한도는 999999원입니다.")],
    }
    results = {name: run_harness(ScriptedProvider(actions), "C01")
               for name, actions in scenarios.items()}
    # Same 12 cases, fixed first-attempt structural comparison; no quality scores.
    cases = [f"C{i:02}" for i in range(1, 13)]
    versions = {}
    for version in ("A", "B"):
        rows = []
        for case in cases:
            response = json.dumps({"outcome":"abstain", "answer":"자료가 부족합니다.", "citations":[]}, ensure_ascii=False)
            if version == "A" and case in ("C01", "C02"):
                response = "not json"
            if version == "B" and case == "C07":
                response = json.dumps({"outcome":"abstain", "answer":"승인", "citations":[], "approved":True})
            result = run_harness(ScriptedProvider([response]), case,
                                 limits=Limits(max_calls=1, max_repairs=0, max_retries=0))
            rows.append({"case_id":case, "status":result["status"],
                         "stop_reason":result["stop_reason"], "calls":result["calls"],
                         "structural_validation_passed":result["structural_validation_passed"],
                         "human_factuality_grade":None})
        versions[version] = rows
    changes = [{"case_id":a["case_id"], "before":a["structural_validation_passed"],
                "after":b["structural_validation_passed"]}
               for a,b in zip(versions["A"], versions["B"])
               if a["structural_validation_passed"] != b["structural_validation_passed"]]
    return {"evidence_kind":"observed_execution_of_scripted_fixtures", "actual_model_calls":0,
            "paid_api_calls":0, "scenarios":results,
            "regression":{"comparison":"scripted_output_A_vs_B_not_prompt_quality",
                          "versions":versions, "changes":changes,
                          "adoption":"not_adopted_regression_C07_requires_review"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Refuse to overwrite evidence. No real-provider flag exists.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(run_demo(), stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
