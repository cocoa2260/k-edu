"""Static design checks. Passing is not lesson approval or model validation.

Usage: python3 curriculum-work/loop/checks/check_design.py <run-dir> [--controls]
Requires the pinned stage-3 evidence and unchanged academy text sources.
No network, model calls, package installs, training or student app execution.
"""
import argparse
import copy
import datetime
import hashlib
import json
import re
from pathlib import Path


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def cycle_errors(nodes):
    graph = {n["id"]: n["requires"] for n in nodes}
    errors, visited, visiting = [], set(), set()

    def visit(node):
        if node not in graph:
            errors.append("Unknown dependency: " + node)
            return
        if node in visiting:
            errors.append("Dependency cycle: " + node)
            return
        if node in visited:
            return
        visiting.add(node)
        for other in graph[node]:
            visit(other)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return errors


def validate(run_dir, override=None):
    root = Path(__file__).resolve().parents[3]
    p = override if override is not None else json.loads((run_dir / "curriculum.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())
    task = json.loads((root / "curriculum-work/loop/tasks/KEDU-DESIGN-001.json").read_text())
    report = (run_dir / "CURRICULUM_PLAN.md").read_text()
    epath = root / p["input"]["analysis_evidence"]
    evidence = json.loads(epath.read_text())
    out = []

    def result(cid, errors, scope):
        out.append({"id": cid, "status": "fail" if errors else "pass", "errors": errors, "scope": scope})

    errors = []
    for key, path in [("analysis_report_sha256", root / p["input"]["analysis_report"]), ("analysis_evidence_sha256", epath)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != p["input"][key]:
            errors.append("Changed design input: " + str(path))
    if p["input"]["source_commit"] != evidence["source_commit"] or p["input"]["source_commit"] != task["source_commit"]:
        errors.append("Source commit mismatch")
    if p["input"]["parent_commit"] != task["analysis_commit"]:
        errors.append("Analysis commit mismatch")
    for s in evidence["sources"]:
        if blob((root / s["path"]).read_bytes()) != s["sha"]:
            errors.append("Protected source changed: " + s["id"])
    result("D01", errors, "Pinned analysis report/evidence and 164 original text-source blobs are unchanged; no external currentness verification.")

    errors = []
    cs, stages = p["courses"], p["stages"]
    course_ids = {c["id"] for c in cs}
    stage_ids = {s["id"] for s in stages}
    units = [u for c in cs for u in c["units"]]
    unit_ids = {u["id"] for u in units}
    extra_targets = {t["id"] for t in p["prerequisite_tracks"]}
    if len(course_ids) != len(cs) or len(unit_ids) != len(units) or len(stage_ids) != len(stages):
        errors.append("Duplicate course/unit/stage ID")
    for c in cs:
        if not all(c.get(k) for k in ["title", "purpose", "units", "source_ids", "analysis_findings"]):
            errors.append("Incomplete course: " + c["id"])
        for u in c["units"]:
            if not all(u.get(k) for k in ["title", "new_outcome", "student_evidence"]):
                errors.append("Incomplete unit: " + u["id"])
        if c["id"] not in report:
            errors.append("Course absent from human plan: " + c["id"])
    primary = {l["source_id"] for l in evidence["lessons"]}
    mapping_ids = [m["source_id"] for m in p["source_mapping"]]
    if set(mapping_ids) != primary or len(mapping_ids) != len(primary):
        errors.append("A primary source lacks a unique disposition")
    for m in p["source_mapping"]:
        if not m["targets"] or not set(m["targets"]) <= course_ids | extra_targets:
            errors.append("Invalid source destination: " + m["source_id"])
    if {q["source_id"] for q in p["qa_mapping"]} != {q["source_id"] for q in evidence["qa"]}:
        errors.append("Missing QA disposition")
    finding_ids = {f["id"] for f in evidence["findings"]}
    if {f["finding_id"] for f in p["finding_dispositions"]} != finding_ids:
        errors.append("Missing stage-3 finding disposition")
    result("D02", errors, f"{len(cs)} proposed blocks, {len(units)} units, 42 primary mappings, 33 QA dispositions and 35 finding dispositions; not a content-quality score.")

    errors = cycle_errors(cs) + cycle_errors(stages)
    for s in stages:
        if not set(s["owner_courses"]) <= course_ids:
            errors.append("Unknown stage owner: " + s["id"])
        if not all(s.get(k) for k in ["new_features", "outputs", "acceptance", "real_model_requirement"]):
            errors.append("Missing stage contract: " + s["id"])
        if s["id"] not in report:
            errors.append("Stage absent from human plan: " + s["id"])
    for g in p["gates"]:
        if not set(g["needed_by"]) <= stage_ids or not g.get("evidence") or not g.get("if_unmet"):
            errors.append("Incomplete gate: " + g["id"])
        if not set(g.get("blocking_at", [])) | set(g.get("diagnostic_at", [])) <= set(g["needed_by"]):
            errors.append("Gate blocking/diagnostic stages are inconsistent: " + g["id"])
        if g["id"] == "G-UI" and (g.get("blocking_at") != ["L9"] or g.get("diagnostic_at") != ["L0"]):
            errors.append("UI diagnostic incorrectly blocks the CLI learning path")
    result("D03", errors, "Course and cumulative-stage dependency graphs have known nodes and no cycles; gate and owner references exist.")

    errors = []
    must_preserve = {"OUT-DATA", "OUT-NN", "OUT-ATTN", "OUT-MASK", "OUT-LLM", "OUT-PROMPT", "OUT-CONTEXT", "OUT-HARNESS", "OUT-LOOP", "OUT-EMBED", "OUT-INDEX", "OUT-RAG", "OUT-AGENT", "OUT-MULTI", "OUT-FT", "OUT-RELOAD", "OUT-OCR", "OUT-DOC", "OUT-GENERATION", "OUT-SERVICE", "OUT-STREAM", "OUT-LIFECYCLE", "OUT-POSITION", "OUT-DIFFUSION", "OUT-VISION"}
    preserved = p["preserved_outcomes"]
    if {o["id"] for o in preserved} != must_preserve:
        errors.append("Missing/duplicate named preservation outcome")
    for o in preserved:
        if not o["targets"] or not set(o["targets"]) <= course_ids | unit_ids or not set(o["findings"]) <= finding_ids:
            errors.append("Invalid preservation mapping: " + o["id"])
    by_stage = {s["id"]: s for s in stages}
    if by_stage["L5"]["requires"] != ["L4"] or by_stage["L6"]["requires"] != ["L5"]:
        errors.append("RAG to Single to Multi progression broken")
    if "L6" in by_stage["L7"]["requires"]:
        errors.append("Independent training unnecessarily depends on Multi-Agent")
    if p["project"]["source_files_created"] is not False or p["dataset"]["status"] != "designed_not_created":
        errors.append("Design claimed an implemented app/dataset")
    result("D04", errors, f"{len(preserved)} named distinct outcomes have destinations, cumulative progression is preserved, training is a separate branch and artifacts remain planned.")

    errors = []
    runtime = p["runtime"]
    roles = p["role_contracts"]
    if {r["id"] for r in roles} != {"researcher", "writer", "reviewer"}:
        errors.append("Missing role")
    for role in roles:
        if not all(role.get(k) for k in ["goal", "choices", "tools", "input", "output", "state"]):
            errors.append("Role has no behavioral contract: " + role["id"])
        if len(role["choices"]) < 2 or type(role["max_model_calls"]) is not int or role["max_model_calls"] <= 0:
            errors.append("Unbounded or non-agent role: " + role["id"])
    for mode in ["single", "multi"]:
        for key in ["max_model_calls", "max_tool_calls", "total_deadline_seconds"]:
            if type(runtime[mode].get(key)) is not int or runtime[mode][key] <= 0:
                errors.append("Invalid global budget: " + mode + "." + key)
    if runtime["multi"]["concurrent_model_calls"] != 1 or not runtime["retry"]["count_against_global_budget"]:
        errors.append("Concurrency/retry budget mismatch")
    if runtime["multi"].get("max_handoff_repairs") != 1 or not runtime["multi"].get("repair_counter_authority"):
        errors.append("Writer and reviewer do not share a bounded Runtime repair counter")
    if not p["interfaces"].get("agent_action_protocol"):
        errors.append("Actual-model action protocol is unspecified")
    for role in roles:
        if role["max_model_calls"] > runtime["multi"]["max_model_calls"]:
            errors.append("Role cap exceeds the global cap: " + role["id"])
    if not {"actor_scope", "allowed_document_ids", "approval_records", "budget_limits"} <= set(runtime["model_cannot_set"]):
        errors.append("Model can override trusted permission/approval/budget")
    if not p["handoff"]["required_fields"] or not p["handoff"]["validation"]:
        errors.append("Missing handoff validation")
    result("D05", errors, "Roles have goals, action choices, state, handoff contracts and finite global budgets; enforcement is a future implementation requirement.")

    errors = []
    cases = p["dataset"]["cases"]
    case_ids = [c["id"] for c in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("Duplicate case ID")
    groups = {name: [c for c in cases if c["group"] == name] for name in ["core-v1", "agent-v1", "handoff-v1"]}
    if {k: len(v) for k, v in groups.items()} != {"core-v1": 12, "agent-v1": 6, "handoff-v1": 4}:
        errors.append("Comparison case counts changed")
    sets = p["dataset"]["comparison_sets"]
    if sets["single_vs_multi"] != ["core-v1", "agent-v1"] or sets["multi_boundary_only"] != ["handoff-v1"]:
        errors.append("Single/Multi denominators differ")
    for c in cases:
        if not c.get("scenario") or not c.get("expected"):
            errors.append("Incomplete case: " + c["id"])
    gate_ids = {g["id"] for g in p["gates"]}
    if not {"G-MODEL", "G-EMBED", "G-TRAIN", "G-DOC", "G-SPEC"} <= gate_ids:
        errors.append("Missing actual-execution gate")
    train = p["dataset"]["training_set"]
    if any(type(train[k]) is not int or train[k] <= 0 for k in ["planned_train", "planned_validation", "planned_test"]):
        errors.append("Invalid planned training split")
    result("D06", errors, "Frozen comparison-set design, distinct handoff tests, planned train/validation/test split and explicit real-model/training gates; no measured quality claim.")

    errors = []
    if p["approved_curriculum"] is not False or run["approved_curriculum"] is not False:
        errors.append("Inferred approval")
    for key in ["lesson_files_modified", "sample_data_or_app_implemented", "model_verified", "hardware_benchmarked", "training_executed", "final_hours_assigned", "runner_implemented", "reasoning_effort_auto_switched"]:
        if p["scope_limits"].get(key) is not False:
            errors.append("Unsupported completed action: " + key)
    if run["actual_model_or_training_executed"] is not False:
        errors.append("Unperformed model/training execution claimed")
    if re.search(r"^\s*(`{3,}|~{3,})", report, re.M):
        errors.append("Human plan has code/JSON fences")
    if report.count("<details>") != report.count("</details>") or "\ufffd" in report:
        errors.append("Human report structure/encoding issue")
    if not all(x in report for x in ["구성안", "총 시수", "독립 교육 평가자", "실제 모델"]):
        errors.append("Missing design/execution boundary labels")
    if p["scope_limits"]["external_model_api_calls"] != 0 or any(run[k] is not None for k in ["input_tokens", "output_tokens", "tool_calls"]):
        errors.append("Unsupported API/usage claim")
    result("D07", errors, "Human plan has no code fences, design/approval/execution boundaries are labeled, usage is not invented, and no lessons/models/training are claimed completed.")

    errors = []
    if not 1 <= run["attempt_count"] <= task["limits"]["max_attempts"]:
        errors.append("Attempt cap exceeded")
    if run["repairs_completed"] != run["attempt_count"] - 1 or run["repairs_completed"] > task["limits"]["max_repairs"]:
        errors.append("Repair accounting mismatch")
    if run["attempt_count"] > 1 and not run["revision_records"]:
        errors.append("Repair lacks change record")
    if run["telemetry_complete"] is not False or run["independent_reviewer"] is not False:
        errors.append("Unexposed telemetry/independent reviewer claimed")
    allowed = {"CURRICULUM_PLAN.md", "curriculum.json", "run.json", "validation.json"}
    unexpected = [f.name for f in run_dir.iterdir() if f.is_file() and f.name not in allowed]
    if unexpected:
        errors.append("Unexpected run outputs: " + ",".join(unexpected))
    result("D08", errors, "Attempt/repair records and report output allowlist; immutable input checks cover local source protection. Remote diff is checked at publication.")
    return {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "passed": all(r["status"] == "pass" for r in out), "checks": out}


def controls(run_dir):
    base = json.loads((run_dir / "curriculum.json").read_text())
    results = []
    for name, expected in [("cycle", "D03"), ("lost_activation_outcome", "D04"), ("unbounded_calls", "D05"), ("unbounded_handoff_repair", "D05"), ("fake_execution_claim", "D07")]:
        changed = copy.deepcopy(base)
        if name == "cycle":
            changed["courses"][0]["requires"] = ["K2-11"]
        elif name == "lost_activation_outcome":
            changed["preserved_outcomes"] = [o for o in changed["preserved_outcomes"] if o["id"] != "OUT-NN"]
        elif name == "unbounded_calls":
            changed["runtime"]["multi"]["max_model_calls"] = 0
        elif name == "unbounded_handoff_repair":
            changed["runtime"]["multi"]["max_handoff_repairs"] = None
        else:
            changed["scope_limits"]["training_executed"] = True
        r = validate(run_dir, changed)
        failed = [c["id"] for c in r["checks"] if c["status"] == "fail"]
        results.append({"case": name, "expected": expected, "failed_checks": failed, "detected": expected in failed})
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_directory", type=Path)
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args()
    run_dir = args.run_directory.resolve()
    result = validate(run_dir)
    if args.controls:
        result["controls"] = controls(run_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] and all(c["detected"] for c in result.get("controls", [])) else 1)
