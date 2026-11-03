"""Run the unchanged tokenizer lab from cache with Python-level network guards.

This is a reproduction probe, not an OS firewall or a model inference runner.
Use a new output directory. HF_HOME must select the previously populated cache.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import socket
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, required=True)
    parser.add_argument('--profile', choices=['qwen', 'smol'], required=True)
    parser.add_argument('--max-length', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--guard-report', type=Path, required=True)
    args = parser.parse_args()
    if args.guard_report.exists():
        raise FileExistsError('Use a new guard-report path')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    import requests
    counts = {'requests_session_request': 0, 'socket_connect': 0, 'socket_connect_ex': 0}

    def refuse(key):
        def blocked(*_args, **_kwargs):
            counts[key] += 1
            raise AssertionError('Network attempt blocked by reproduction probe')
        return blocked

    spec = importlib.util.spec_from_file_location('actual_tokenizer_lab', args.lab)
    lab = importlib.util.module_from_spec(spec)
    with patch.object(requests.sessions.Session, 'request', refuse('requests_session_request')), \
         patch.object(socket.socket, 'connect', refuse('socket_connect')), \
         patch.object(socket.socket, 'connect_ex', refuse('socket_connect_ex')):
        spec.loader.exec_module(lab)
        code = lab.main(['--profile', args.profile, '--max-length', str(args.max_length),
                         '--output', str(args.output)])
    record = {'lab_exit_code': code, 'attempts': counts,
              'offline_environment': True, 'download_permission': False,
              'scope': 'Python requests and socket.connect/connect_ex guards, not OS-wide network isolation'}
    args.guard_report.parent.mkdir(parents=True, exist_ok=True)
    args.guard_report.write_text(json.dumps(record, indent=2) + '\n')
    return code if code else (1 if any(counts.values()) else 0)


if __name__ == '__main__':
    raise SystemExit(main())
