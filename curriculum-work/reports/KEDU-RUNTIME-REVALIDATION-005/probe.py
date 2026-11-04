"""Verify the L0 browser route, output limits, and real L2 repair behavior."""
import argparse
import hashlib
import json
import resource
import socket
import subprocess
import threading
import time
from contextlib import closing
from pathlib import Path

import uvicorn

from app.experiments import prepare
from app.harness import Limits, run_harness
from app.main import create_app
from app.providers.hf_cpu_provider import HFCpuProvider, REVISION
from app.schemas import ChatRequest

SETTINGS_CASES = ("C02", "C07")
HARNESS_CASES = ("C01", "C03", "C07")
SETTINGS_SENTENCE = " 상한과 실제 지급액을 구분해서 설명하라."


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def verify_files(snapshot):
    manifest = json.loads(Path(__file__).with_name("model-files.json").read_text())
    assert manifest["revision"] == REVISION
    for file in manifest["files"]:
        path = snapshot / file["name"]
        with path.open("rb") as source:
            assert path.stat().st_size == file["size"]
            assert hashlib.file_digest(source, "sha256").hexdigest() == file["sha256"], path


def browser_probe(provider, dependencies):
    before = len(provider.observations)
    message = prepare("C01", "focused")["message"]
    with closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(16)
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(create_app(provider), log_level="warning"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        try:
            for _ in range(200):
                if server.started:
                    break
                time.sleep(0.05)
            assert server.started
            script = Path(__file__).with_name("browser.mjs")
            child = subprocess.run(
                ["node", str(script), f"http://127.0.0.1:{port}", str(dependencies)],
                input=json.dumps({"message": message}), text=True, capture_output=True, timeout=220,
            )
            if child.returncode:
                raise RuntimeError(child.stderr)
            result = json.loads(child.stdout)
            observed = provider.observations[before:]
            assert len(observed) == 1
            assert result["input_sha256"] == sha(message)
            assert result["displayed_answer_sha256"] == sha(observed[0]["raw_output"])
        finally:
            server.should_exit = True
            thread.join(timeout=10)
    assert not thread.is_alive()
    return dict(case="C01", condition="focused", server_stopped=True, result=result, generation=observed)


def settings_probe(provider, record):
    for case in SETTINGS_CASES:
        original = prepare(case, "instruction")["message"]
        instruction, rest = original.split("\n\n", 1)
        message = ChatRequest(message=instruction + SETTINGS_SENTENCE + "\n\n" + rest).message
        for limit in (192, 256):
            provider.profile["max_new_tokens"] = limit
            provider.generate(message)
            record(dict(event="setting", case=case, limit=limit, input_sha256=sha(message),
                        generation=[provider.observations[-1]]))
    provider.profile["max_new_tokens"] = 192


def harness_probe(provider, record):
    for case in HARNESS_CASES + ("C10",):
        for repairs in (0, 1):
            start = len(provider.observations)
            result = run_harness(provider, case, "focused", limits=Limits(max_repairs=repairs))
            assert not result["factuality_verified"] and not result["approval_granted"]
            assert not result["side_effects_executed"] and result["retries"] == 0
            attempts = provider.observations[start:]
            assert len(attempts) == result["calls"] <= repairs + 1
            if case == "C10":
                assert not attempts and result["stop_reason"] == "input_rejected"
            record(dict(event="harness", case=case, repair_limit=repairs,
                        result=result, generation=attempts))


def run(snapshot, output, browser_dependencies):
    if output.exists():
        raise FileExistsError(output)
    verify_files(snapshot)
    start = time.perf_counter()
    provider = HFCpuProvider(offline=True, max_new_tokens=192)
    with output.open("x", encoding="utf-8") as log:
        def record(event):
            log.write(json.dumps(event, ensure_ascii=False) + "\n")
            log.flush()

        record(dict(event="start", profile=provider.profile,
                    model_load_seconds=round(time.perf_counter() - start, 4)))
        try:
            record(dict(event="browser", **browser_probe(provider, browser_dependencies)))
        except (RuntimeError, subprocess.TimeoutExpired, AssertionError) as failure:
            record(dict(event="browser_failure", detail=str(failure), observations=len(provider.observations)))
        settings_probe(provider, record)
        harness_probe(provider, record)
        record(dict(event="end", observations=len(provider.observations),
                    peak_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--browser-dependencies", required=True, type=Path)
    args = parser.parse_args()
    run(args.snapshot, args.output, args.browser_dependencies)
