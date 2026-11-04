"""Exercise current loopback and local approval boundaries with synthetic data."""
import argparse
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading

from app.agent import Policy, Registry as AgentRegistry, ToolFailure, approval_key
from app.document_registry import Registry, RegistryError
from app.report_spec import ReportRejected, Reports
from tools.stream_lab import make_server


def request(port, method, path, payload=None, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request(method, path, json.dumps(payload) if payload is not None else None, headers or {})
    return conn, conn.getresponse()


def lab_identity(ui):
    server = make_server(ui)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    port = server.server_port
    connections = []
    try:
        payload = {"id": "synthetic-owner-run", "scenario": "slow"}
        starter, stream = request(port, "POST", "/lab/stream", payload)
        connections.append(starter)
        assert stream.status == 200 and stream.readline().strip() == b"event: start"
        foreign, refusal = request(port, "POST", "/lab/cancel", payload, {"Origin": "https://untrusted.invalid"})
        connections.append(foreign)
        assert refusal.status == 403
        reader, runs = request(port, "GET", "/lab/runs")
        connections.append(reader)
        assert runs.status == 200 and any(row["id"] == payload["id"] for row in json.load(runs))
        stranger, cancel = request(port, "POST", "/lab/cancel", {"id": payload["id"]})
        connections.append(stranger)
        assert cancel.status == 200 and json.load(cancel)["ack"]
        stream_tail = stream.read()
        assert b'"status": "cancelled"' in stream_tail
        return dict(bind="127.0.0.1", distinct_http_clients=True, supplied_credentials=False,
                    foreign_origin_cancel_http=403, no_origin_run_list_http=200,
                    no_origin_peer_cancel_ack=True, observed_final="cancelled")
    finally:
        for conn in connections:
            conn.close()
        server.shutdown()
        server.server_close()
        thread.join()


def rejected(fn, exc):
    try:
        fn()
    except exc as error:
        return str(error)
    raise AssertionError("Expected refusal")


def agent_approval():
    args = {"text": "synthetic note"}
    run_id = "approval-probe"
    invoke = lambda registry, fields: registry.invoke("save_note", fields)
    no_grant = AgentRegistry(None, Policy(run_id=run_id))
    supplied_flag = rejected(lambda: invoke(no_grant, args | {"approved": True}), ToolFailure)
    no_grant_error = rejected(lambda: invoke(no_grant, args), ToolFailure)
    grants = frozenset({approval_key(run_id, "save_note", args)})
    approved = AgentRegistry(None, Policy(run_id=run_id, approvals=grants))
    wrong_args = rejected(lambda: invoke(approved, {"text": "different"}), ToolFailure)
    wrong_run = rejected(lambda: invoke(AgentRegistry(None, Policy(run_id="another", approvals=grants)), args), ToolFailure)
    assert invoke(approved, args)["status"] == "created_in_memory_only"
    same_registry_reuse = rejected(lambda: invoke(approved, args), ToolFailure)
    reset = AgentRegistry(None, approved.policy)
    assert invoke(reset, args)["status"] == "created_in_memory_only"
    assert supplied_flag == "TOOL_ARGUMENTS"
    assert {no_grant_error, wrong_args, wrong_run, same_registry_reuse} == {"APPROVAL_REQUIRED"}
    return dict(model_supplied_flag=supplied_flag, no_grant=no_grant_error, wrong_args=wrong_args,
                wrong_run=wrong_run, same_registry_reuse=same_registry_reuse,
                new_registry_same_policy_reuse_accepted=True)


def report_approval(root):
    db = root / "registry.sqlite"
    path = root / "policy.txt"
    path.write_text("신청 기한 7일", encoding="utf-8")
    registry = Registry(db)
    try:
        meta = dict(id="policy", version="test", title="가상 정책", access="staff", current=True)
        registry.upload(path, meta, "request-1")
        registry.parse("policy", 1)
        registry.index("policy", 1)
        registry.review("policy", 1)
        reports = Reports(registry)
        claims = [dict(id="C1", statement="신청 기한 7일", citations=[
            dict(doc="policy", version=1, element="line-1", quote="신청 기한 7일"),
        ])]
        spec = reports.prepare("가상 정책 검토", claims)
        pending = rejected(lambda: reports.authorized(spec), ReportRejected)
        reports.decide(spec, "approve", "synthetic-reviewer-label", "local fixture")
    finally:
        registry.close()
    registry = Registry(db)
    try:
        reports = Reports(registry)
        accepted = reports.authorized(spec)
        assert accepted["decision"] == "approve"
        modified = copy.deepcopy(spec)
        modified["claims"][0]["statement"] = "신청 기한 30일"
        changed = rejected(lambda: reports.authorized(modified), ReportRejected)
        registry.restrict("policy", 1)
        restricted = rejected(lambda: reports.authorized(spec), RegistryError)
        return dict(pending=pending, durable_after_reopen=True, decision_mode=spec["review_mode"],
                    changed_claim=changed, restricted_source=restricted)
    finally:
        registry.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("ui", "output"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        results = dict(loopback_identity=lab_identity(args.ui), agent=agent_approval(),
                       report=report_approval(Path(tmp)))
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
