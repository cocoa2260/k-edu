"""Loopback-only live Qwen SSE and owned-worker lifecycle experiment."""
import argparse
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import multiprocessing as mp
from pathlib import Path
import threading
import time

from app.providers.hf_cpu_provider import MODEL_ID, REVISION

PROMPT = "한국어로 1부터 50까지 숫자를 순서대로 적어 주세요. 각 숫자 뒤에 쉼표와 공백을 붙여 주세요."
NORMAL_PROMPT = "1부터 12까지 숫자만 순서대로 적고 숫자 사이에 쉼표를 넣어 주세요."
MAX_TOKENS = 64


def verify_model(snapshot, manifest):
    doc = json.loads(manifest.read_text())
    assert doc["revision"] == REVISION
    for file in doc["files"]:
        path = snapshot / file["name"]
        with path.open("rb") as reader:
            assert path.stat().st_size == file["size"]
            assert hashlib.file_digest(reader, "sha256").hexdigest() == file["sha256"]


def generate(snapshot, sender, cancel, run_id):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextStreamer

    torch.set_num_threads(2)
    tok = AutoTokenizer.from_pretrained(snapshot, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        snapshot, local_files_only=True, trust_remote_code=False,
        use_safetensors=True, dtype=torch.float32,
    ).eval()
    message = tok.apply_chat_template(
        [{"role": "user", "content": NORMAL_PROMPT if run_id == "normal" else PROMPT}], tokenize=False,
        add_generation_prompt=True, enable_thinking=False,
    )
    inputs = tok(message, return_tensors="pt", add_special_tokens=False)
    began = time.monotonic_ns()
    sender.send(("begin", {"worker_generate_start_ns": began, "input_tokens": inputs["input_ids"].shape[-1]}))

    class CancelAtToken(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            return cancel.is_set()

    class Stream(TextStreamer):
        def on_finalized_text(self, text, stream_end=False):
            if text:
                sender.send(("delta", {"text": text, "worker_emitted_ns": time.monotonic_ns()}))

    with torch.inference_mode():
        result = model.generate(
            **inputs, max_new_tokens=MAX_TOKENS, do_sample=False, temperature=None, top_p=None, top_k=None,
            streamer=Stream(tok, skip_prompt=True, skip_special_tokens=True),
            stopping_criteria=StoppingCriteriaList([CancelAtToken()]),
        )
    tail = result[0, inputs["input_ids"].shape[-1]:]
    answer = tok.decode(tail, skip_special_tokens=True)
    sender.send(("done", {
        "answer": answer, "generated_tokens": len(tail), "worker_generate_end_ns": time.monotonic_ns(),
        "cancel_observed": cancel.is_set(), "torch": str(torch.__version__),
    }))
    sender.close()


def make_probe(snapshot):
    context = mp.get_context("spawn")
    records = {}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, data):
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size < 256:
                self.reply(400, {})
                return
            run_id = json.loads(self.rfile.read(size))["id"]
            if run_id not in {"normal", "cancel", "hard"}:
                self.reply(400, {})
                return
            if self.path == "/probe/stream":
                self.stream(run_id)
                return
            if (self.path, run_id) not in {("/probe/cancel", "cancel"), ("/probe/force", "hard")}:
                self.reply(404, {})
                return
            with lock:
                row = records.get(run_id)
                ack = bool(row and "status" not in row and row["process"].is_alive()
                           and row.get("stop_requested_ns") is None)
                if ack:
                    row["stop_requested_ns"] = time.monotonic_ns()
                    row["stop_path"] = self.path
                    if self.path == "/probe/force":
                        row["process"].kill()
                    else:
                        row["cancel"].set()
            self.reply(200, {"ack": ack})

        def stream(self, run_id):
            receive, sender = context.Pipe(duplex=False)
            cancel = context.Event()
            process = context.Process(target=generate, args=(snapshot, sender, cancel, run_id), name="kedu-qwen-probe")
            row = {"process": process, "cancel": cancel, "start_ns": time.monotonic_ns()}
            with lock:
                assert run_id not in records
                process.start()
                records[run_id] = row
            sender.close()
            seq = 0
            answer = ""
            status = "failed"
            reason = "worker_exited_without_result"
            finished = None

            def emit(event, **fields):
                nonlocal seq
                payload = {"id": run_id, "seq": seq, **fields}
                seq += 1
                frame = "event: " + event + "\r\ndata: " + json.dumps(payload, ensure_ascii=False) + "\r\n\r\n"
                self.wfile.write(frame.encode())
                self.wfile.flush()

            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
                emit("start", fixture=False, model=MODEL_ID)
                while time.monotonic_ns() - row["start_ns"] < 120_000_000_000:
                    if not receive.poll(0.1):
                        if not process.is_alive():
                            break
                        continue
                    try:
                        kind, data = receive.recv()
                    except EOFError:
                        break
                    if kind == "begin":
                        row.update(data)
                    if kind == "delta":
                        with lock:
                            if "stop_requested_ns" not in row:
                                answer += data["text"]
                                emit("delta", **data)
                    if kind == "done":
                        finished = data
                        break
                else:
                    reason = "probe_deadline"
            finally:
                receive.close()
                process.join(5)
                if process.is_alive():
                    process.kill()
                    process.join(5)
                    reason = "cleanup_force"
                assert not process.is_alive()
                row.update(worker_pid=process.pid, worker_exitcode=process.exitcode, worker_joined_ns=time.monotonic_ns())
                if finished is not None:
                    row.update({key: val for key, val in finished.items() if key != "answer"})
                if row.get("stop_path") == "/probe/force" and process.exitcode == -9:
                    reason = "worker_sigkill"
                elif row.get("stop_path") == "/probe/cancel" and finished and finished["cancel_observed"] and process.exitcode == 0:
                    status, reason = "cancelled", "token_stopping_criteria"
                elif not row.get("stop_path") and finished and process.exitcode == 0 and answer and answer == finished["answer"]:
                    if finished["generated_tokens"] >= MAX_TOKENS:
                        status, reason = "output_limit", "model_token_cap"
                    else:
                        status, reason = "completed", "model_generated"
                with lock:
                    row.update(status=status, reason=reason, emitted_characters=len(answer))
                    process.close()
                emit("final", status=status, answer=answer if status == "completed" else None)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    return server, records


def post(port, path, run_id):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=125)
    conn.request("POST", path, body=json.dumps({"id": run_id}), headers={"Content-Type": "application/json"})
    return conn, conn.getresponse()


def client(port, run_id):
    conn, response = post(port, "/probe/stream", run_id)
    assert response.status == 200 and response.headers["Content-Type"].startswith("text/event-stream")
    events = []
    stop = {"cancel": "/probe/cancel", "hard": "/probe/force"}.get(run_id)
    try:
        while line := response.readline():
            kind = line.decode().strip().removeprefix("event: ")
            payload = json.loads(response.readline().decode().removeprefix("data: "))
            assert response.readline() == b"\r\n"
            assert payload["id"] == run_id and payload["seq"] == len(events)
            events.append((kind, time.monotonic_ns(), payload))
            if stop and kind == "delta":
                other, ack = post(port, stop, run_id)
                try:
                    assert ack.status == 200 and json.load(ack)["ack"]
                finally:
                    other.close()
                stop = None
    finally:
        conn.close()
    return events


def run(snapshot, manifest):
    verify_model(snapshot, manifest)
    server, records = make_probe(snapshot)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    observations = {}
    try:
        for name in ("normal", "cancel", "hard"):
            events = client(server.server_port, name)
            row = {key: val for key, val in records[name].items() if key not in {"process", "cancel"}}
            deltas = [(ts, val) for event, ts, val in events if event == "delta"]
            assert events[0][0] == "start" and events[-1][0] == "final" and deltas
            assert deltas[0][1]["worker_emitted_ns"] < row["worker_joined_ns"]
            final = events[-1][2]
            assert final["status"] == row["status"]
            if name == "normal":
                assert row["status"] == "completed" and len(deltas) > 1
                assert deltas[0][0] < row["worker_generate_end_ns"]
                assert final["answer"] == "".join(item["text"] for _, item in deltas)
            else:
                assert final["answer"] is None
                stop_path = "/probe/cancel" if name == "cancel" else "/probe/force"
                conn, response = post(server.server_port, stop_path, name)
                try:
                    assert response.status == 200 and not json.load(response)["ack"]
                finally:
                    conn.close()
                row["late_stop_ack"] = False
                assert not any(item["worker_emitted_ns"] > row["stop_requested_ns"] for _, item in deltas)
            if name == "cancel":
                assert row["status"] == "cancelled" and row["worker_exitcode"] == 0
                assert row["generated_tokens"] < MAX_TOKENS
            if name == "hard":
                assert row["reason"] == "worker_sigkill" and row["worker_exitcode"] == -9
                assert "worker_generate_end_ns" not in row
            row.update(client_delta_count=len(deltas), client_first_delta_ns=deltas[0][0],
                       client_final_ns=events[-1][1], final_answer_present=final["answer"] is not None)
            if final["answer"] is not None:
                row["final_answer_sha256"] = hashlib.sha256(final["answer"].encode()).hexdigest()
            observations[name] = row
            print(name, row["status"], row["reason"], flush=True)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    return dict(model=MODEL_ID, revision=REVISION, max_tokens=MAX_TOKENS, cases=observations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("snapshot", "manifest", "output"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    results = run(args.snapshot, args.manifest)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
