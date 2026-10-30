"""Validate curriculum analysis records, not educational correctness or model performance.

Usage: python3 curriculum-work/loop/checks/check_curriculum.py <run-directory>
Requires the unchanged expanded academy sources in the same checkout.
No network access, LLM calls, package installation or lesson execution.
"""
import argparse
import ast
import copy
import datetime
import hashlib
import json
import re
from pathlib import Path


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check(run_dir, evidence_override=None):
    root = Path(__file__).resolve().parents[3]
    evidence = evidence_override if evidence_override is not None else json.loads((run_dir / "evidence.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())
    task = json.loads((root / "curriculum-work/loop/tasks/KEDU-ANALYSIS-001.json").read_text())
    report = (run_dir / "REVIEW.md").read_text()
    sources = evidence["sources"]
    by_id = {s["id"]: s for s in sources}
    source_rows = {}
    results = []

    def record(cid, errors, scope):
        results.append({"id": cid, "status": "fail" if errors else "pass", "errors": errors, "scope": scope})

    errors = []
    if evidence["source_commit"] != task["source_commit"]:
        errors.append("Source commit mismatch")
    if len(by_id) != len(sources) or len({s['path'] for s in sources}) != len(sources):
        errors.append("Duplicate source ID/path")
    for s in sources:
        path = root / s["path"]
        if not path.is_file():
            errors.append("Missing source: " + s["id"])
            continue
        data = path.read_bytes()
        source_rows[s["id"]] = data.decode("utf-8").splitlines()
        if git_blob(data) != s["sha"] or len(data) != s["size"]:
            errors.append("Source bytes differ: " + s["id"])
        if len(source_rows[s["id"]]) != s["line_count"]:
            errors.append("Line count differs: " + s["id"])
    record("A01", errors, "Source commit and all manifested source bytes/size/lines; not live freshness.")

    errors = []
    required = {"id", "title", "kind", "judgment", "preserve", "proposal", "refs", "decision_required", "priority", "status"}
    findings = evidence["findings"]
    ids = [f["id"] for f in findings]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate finding ID")
    for f in findings:
        if not required.issubset(f):
            errors.append("Missing fields: " + f.get("id", "?"))
        if not f.get("refs") or not all(f.get(k) for k in ["judgment", "preserve", "proposal"]):
            errors.append("Empty reasoning/evidence: " + f["id"])
        if not isinstance(f["decision_required"], bool) or f["priority"] not in {"P0", "P1", "P2"}:
            errors.append("Invalid value: " + f["id"])
        if f["id"] not in report:
            errors.append("Finding missing from human report: " + f["id"])
    record("A02", errors, "Findings have reasons, preserved outcomes, proposals, references, unique IDs and report counterparts.")

    errors = []
    refs = [r for f in findings for r in f["refs"]] + [r["anchor"] for r in evidence["lessons"]]
    for r in refs:
        sid = r["source_id"]
        rows = source_rows.get(sid, [])
        a, b, q = r["start_line"], r["end_line"], r["quote_line"]
        if not all(type(n) is int for n in [a, b, q]) or not 1 <= a <= q <= b <= len(rows):
            errors.append("Invalid evidence range: " + sid)
            continue
        if rows[q - 1] != r["excerpt"]:
            errors.append("Excerpt mismatch: " + sid + ":" + str(q))
        if "/blob/" + evidence["source_commit"] + "/" not in r["url"]:
            errors.append("Unpinned evidence URL: " + sid)
    record("A03", errors, f"{len(refs)} evidence/role references have valid ranges and exact anchor excerpts; semantic support is reviewed separately.")

    errors = []
    primary = {s["id"] for s in sources if s["kind"] in {"day_lesson", "phase2_lesson", "architecture_lesson", "development_lesson"}}
    lesson_ids = [l["source_id"] for l in evidence["lessons"]]
    if set(lesson_ids) != primary or len(lesson_ids) != len(primary):
        errors.append("Missing/duplicate primary lesson role")
    qa_ids = {s["id"] for s in sources if s["kind"] == "qa"}
    if {r["source_id"] for r in evidence["qa"]} != qa_ids:
        errors.append("Missing QA disposition")
    md_ids = {s["id"] for s in sources if s["path"].endswith(".md")}
    covered = set(lesson_ids) | qa_ids | {r["source_id"] for r in evidence["other_md_dispositions"]}
    if covered != md_ids:
        errors.append("Missing Markdown disposition")
    for s in sources:
        cursor = 1
        for a, b in s["sections"]:
            if a != cursor or b < a:
                errors.append("Section partition gap/overlap: " + s["id"])
            cursor = b + 1
        if cursor != s["line_count"] + 1:
            errors.append("Section partition does not cover file: " + s["id"])
    if len(sources) != 164 or len(primary) != 42 or len(md_ids) != 79:
        errors.append("Declared scope count mismatch")
    record("A04", errors, "All declared Markdown dispositions and primary roles; line partitions are structural coverage, not a semantic-completeness score.")

    errors = []
    allowed = {"REVIEW.md", "evidence.json", "run.json", "validation.json"}
    unexpected = [p.name for p in run_dir.iterdir() if p.is_file() and p.name not in allowed]
    if unexpected:
        errors.append("Unexpected run output: " + ",".join(unexpected))
    for s in sources:
        path = root / s["path"]
        if not path.is_file() or git_blob(path.read_bytes()) != s["sha"]:
            errors.append("Protected source changed: " + s["id"])
    record("A05", errors, "Protected source bytes unchanged and run output allowlist; full remote tree diff is checked separately on publication.")

    errors = []
    if re.search(r"^\s*(`{3,}|~{3,})", report, re.M):
        errors.append("Human review document unexpectedly contains code fences")
    if report.count("<details>") != report.count("</details>"):
        errors.append("Unclosed details block")
    if "\ufffd" in report:
        errors.append("Replacement character")
    for link in re.findall(r"\]\((https://[^\s]+)\)", report):
        if "/blob/" in link and "/blob/" + evidence["source_commit"] + "/" not in link:
            errors.append("Human report has an unpinned source link")
    if not all(s in report for s in ["최종 목차", "독립 평가자", "제목", "제안"]):
        errors.append("Human report lacks decision/review boundary labels")
    record("A06", errors, "Human report has no code/JSON fences, balanced details, pinned source links and decision boundary labels; no live external link check.")

    errors = []
    claims = evidence["execution_claims"]
    for key in ["real_model_called", "ollama_verified", "rag_end_to_end_verified", "multi_agent_end_to_end_verified", "fine_tuning_verified", "real_tool_side_effects", "telemetry_complete"]:
        if claims.get(key) is not False:
            errors.append("Unsupported execution assertion: " + key)
    if evidence["proposal_approval"] is not False or evidence["lesson_files_modified"] is not False:
        errors.append("Unapproved curriculum edit/approval assertion")
    if claims.get("external_model_api_calls") != 0 or any(claims.get(k) is not None for k in ["input_tokens", "output_tokens", "tool_calls"]):
        errors.append("Unsupported usage measurement")
    py_count = 0
    for s in sources:
        if s["path"].endswith(".py"):
            py_count += 1
            try:
                ast.parse((root / s["path"]).read_text())
            except SyntaxError:
                errors.append("Python syntax: " + s["id"])
    if py_count != claims["python_files_ast_checked"]:
        errors.append("Python AST count mismatch")
    demo = evidence["boundary_demo"]
    if not claims["teaching_registry_mock_executed"] or demo["real_calendar_called"] or demo["model_called"] or demo["external_network_used"]:
        errors.append("Boundary demo scope mismatch")
    record("A07", errors, "84 independent Python AST parses and bounded mock execution are separated from actual LLM/E2E/training claims and unknown usage.")

    errors = []
    if not 1 <= run["attempt_count"] <= task["limits"]["max_attempts"]:
        errors.append("Attempt limit")
    if run["repairs_completed"] != run["attempt_count"] - 1 or run["repairs_completed"] > task["limits"]["max_repairs"]:
        errors.append("Repair count mismatch")
    if run["runner_implemented"] or run["independent_reviewer"] or run["reasoning_effort_auto_switched"]:
        errors.append("Unimplemented execution feature claimed")
    if run["attempt_count"] > 1 and not run.get("revision_records"):
        errors.append("Repair lacks change record")
    if not run.get("checkpoint_times") or run["telemetry_complete"] is not False:
        errors.append("Missing/inaccurate checkpoint accounting")
    record("A08", errors, "Attempt cap, changes and actual checkpoint accounting; this script does not implement a Runner or enforce model deadlines.")
    return {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "passed": all(r["status"] == "pass" for r in results), "checks": results}


def controls(run_dir):
    base = json.loads((run_dir / "evidence.json").read_text())
    cases = []
    for cid, expected in [("bad_reference", "A03"), ("missing_primary_role", "A04"), ("unsupported_model_execution", "A07")]:
        mutated = copy.deepcopy(base)
        if cid == "bad_reference":
            mutated["findings"][0]["refs"][0]["start_line"] = 999999
        elif cid == "missing_primary_role":
            mutated["lessons"].pop()
        else:
            mutated["execution_claims"]["ollama_verified"] = True
        result = check(run_dir, mutated)
        failed = [r["id"] for r in result["checks"] if r["status"] == "fail"]
        cases.append({"case": cid, "expected": expected, "failed_checks": failed, "detected": expected in failed})
    return cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    result = check(args.run_directory.resolve())
    if args.controls:
        result["controls"] = controls(args.run_directory.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] and all(c["detected"] for c in result.get("controls", [])) else 1)
