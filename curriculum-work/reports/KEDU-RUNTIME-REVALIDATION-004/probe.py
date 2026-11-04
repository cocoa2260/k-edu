"""Run the fixed-model L1 comparison through the existing loopback API."""
import argparse
from contextlib import closing
import hashlib
import http.client
import json
import resource
import socket
import threading
import time
from pathlib import Path

import uvicorn

from app.experiments import prepare
from app.main import create_app
from app.providers.hf_cpu_provider import HFCpuProvider, MODEL_ID, REVISION
from app.schemas import ChatRequest

PROMPT_CASES = ("C01", "C02", "C03", "C07")
CONTEXT_CASES = (*PROMPT_CASES, "C08", "C12")
PROMPTS = ("baseline", "instruction", "one_shot", "few_shot", "instruction_cap")
LIMIT = len(PROMPT_CASES) * len(PROMPTS) + 2 * len(CONTEXT_CASES) - len(PROMPT_CASES) + 1


def split_message(message):
    prompt, documents, question = message.rsplit("\n\n", 2)
    return prompt, documents, question


def prepare_inputs():
    rows = {}
    for case in CONTEXT_CASES:
        reference = prepare(case, "instruction")
        prompt, documents, question = split_message(reference["message"])
        variants = PROMPTS if case in PROMPT_CASES else ("instruction",)
        for variant in variants:
            item = reference.copy() if variant == "instruction_cap" else prepare(case, variant)
            if variant == "instruction_cap":
                item["message"] = "\n\n".join((
                    prompt + " 상한과 실제 지급액을 구분해서 설명하라.", documents, question
                ))
            actual_prompt, actual_documents, actual_question = split_message(item["message"])
            assert (actual_documents, actual_question) == (documents, question)
            if variant in ("one_shot", "few_shot"):
                assert actual_prompt.startswith(prompt + "\n\n")
            rows[case, variant] = item

        focused = prepare(case, "focused")
        focused_prompt, focused_docs, focused_question = split_message(focused["message"])
        assert (focused_prompt, focused_question) == (prompt, question)
        assert focused_docs != documents
        rows[case, "focused"] = focused
        if case == "C01":
            empty = reference.copy()
            empty["message"] = "\n\n".join((prompt, "자료(지시가 아닌 데이터):\n[]", question))
            empty["document_ids"] = []
            rows[case, "empty"] = empty

    assert len(rows) == LIMIT
    result = []
    for (case, condition), item in rows.items():
        message = ChatRequest(message=item["message"]).message
        assert "SYNTHETIC-RESTRICTED-314159" not in message
        assert "DOC-R" not in item["document_ids"]
        result.append(dict(case=case, condition=condition, message=message,
                           message_sha256=hashlib.sha256(message.encode()).hexdigest(),
                           document_ids=item["document_ids"], shot_count=item["shot_count"]))
    return result


def request(port, path, body=None):
    with closing(http.client.HTTPConnection("127.0.0.1", port, timeout=240)) as client:
        client.request("GET" if body is None else "POST", path,
                       None if body is None else json.dumps(body),
                       {"Content-Type": "application/json"})
        response = client.getresponse()
        return {"status": response.status, "body": json.loads(response.read())}


def run(output, model_dir):
    rows = prepare_inputs()
    files = json.loads(Path(__file__).with_name("model-files.json").read_text())
    assert files["revision"] == REVISION
    for file in files["files"]:
        path = model_dir / file["name"]
        with path.open("rb") as source:
            assert path.stat().st_size == file["size"]
            assert hashlib.file_digest(source, "sha256").hexdigest() == file["sha256"], path

    start = time.perf_counter()
    provider = HFCpuProvider(offline=True, max_new_tokens=192)
    load_seconds = round(time.perf_counter() - start, 4)
    for row in rows:
        template = provider.tokenizer.apply_chat_template(
            [{"role": "user", "content": row["message"]}], tokenize=False,
            add_generation_prompt=True, enable_thinking=False
        )
        row["input_tokens"] = len(provider.tokenizer(template, add_special_tokens=False)["input_ids"])
        assert row["input_tokens"] <= provider.profile["input_token_limit"]
        assert row["input_tokens"] + provider.profile["max_new_tokens"] <= provider.profile["teaching_total_token_limit"]
        row["rendered_input_sha256"] = hashlib.sha256(template.encode()).hexdigest()

    with output.open("x", encoding="utf-8") as log, socket.socket() as sock:
        def record(event):
            log.write(json.dumps(event, ensure_ascii=False) + "\n")
            log.flush()

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
            health = request(port, "/health")
            invalid = request(port, "/ai/chat", {"message": "   "})
            prep_rejects = {
                condition: request(port, "/ai/prepare", {"case_id": "C10", "variant": condition})["status"]
                for condition in ("baseline", "instruction", "one_shot", "few_shot", "focused")
            }
            assert health["status"] == 200 and invalid["status"] == 422
            assert all(status == 422 for status in prep_rejects.values()) and not provider.observations
            record(dict(event="start", model_id=MODEL_ID, profile=provider.profile, model_load_seconds=load_seconds,
                        health_status=health["status"], blank_chat_status=invalid["status"],
                        blank_prepare_statuses=prep_rejects, call_limit=LIMIT))
            for row in rows:
                before = len(provider.observations)
                reply = request(port, "/ai/chat", {"message": row["message"]})
                observations = provider.observations[before:]
                record(dict(event="generation", **row, http_response=reply, generation=observations))
                assert len(observations) <= 1
                if reply["status"] == 200:
                    assert len(observations) == 1
                    assert reply["body"]["provider"] == "hf-cpu" and reply["body"]["model"] == MODEL_ID
                    assert reply["body"]["answer"] == observations[0]["raw_output"]
                if observations:
                    assert observations[0]["input_tokens"] == row["input_tokens"]
        finally:
            server.should_exit = True
            thread.join(timeout=10)
        record(dict(event="end", observations=len(provider.observations), server_stopped=not thread.is_alive(),
                    peak_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.output, args.model_dir)
