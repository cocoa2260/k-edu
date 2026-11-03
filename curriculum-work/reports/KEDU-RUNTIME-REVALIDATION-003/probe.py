"""Actual CPU model injected into the unchanged API; loopback HTTP probe.

Run from backend with a prepared HF_HOME and the generation environment.
Use a new output path. No default factory/configuration is changed.
"""
import argparse
import hashlib
import http.client
import json
import pathlib
import resource
import socket
import threading
import time
import uvicorn
from app.main import create_app
from app.experiments import prepare
from app.providers.hf_cpu_provider import HFCpuProvider


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output')
    start = time.perf_counter()
    provider = HFCpuProvider(offline=True, max_new_tokens=192)
    load_seconds = time.perf_counter() - start
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    sock.listen(16)
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(provider), log_level='warning'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    def request(path, body=None):
        client = http.client.HTTPConnection('127.0.0.1', port, timeout=240)
        client.request('POST' if body is not None else 'GET', path,
                       json.dumps(body) if body is not None else None,
                       {'Content-Type': 'application/json'})
        response = client.getresponse()
        result = {'http_status': response.status, 'body': json.loads(response.read())}
        client.close()
        return result
    rows = []
    try:
        for _ in range(100):
            if server.started:
                break
            time.sleep(.05)
        assert server.started
        health = request('/health')
        assert health['http_status'] == 200 and not provider.observations
        invalid = request('/ai/chat', {'message': '   '})
        assert invalid['http_status'] == 422 and not provider.observations
        question = '국내 당일 출장 식비 상한과 필요한 자료는?'
        for label, message in [('question-only', question),
                               ('manual-focused-context', prepare('C01', 'focused')['message'])]:
            response = request('/ai/chat', {'message': message})
            assert response['http_status'] == 200
            assert response['body']['provider'] == 'hf-cpu'
            assert response['body']['answer'] == provider.observations[-1]['raw_output']
            rows.append({'case': label, 'message': message,
                         'message_sha256': hashlib.sha256(message.encode()).hexdigest(),
                         'response': response, 'generation': provider.observations[-1]})
        assert len(provider.observations) == 2
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
    args.output.write_text(json.dumps({'scope': 'actual loopback API with explicitly injected CPU provider',
        'profile': provider.profile, 'model_load_seconds': round(load_seconds, 4),
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'health': health, 'invalid_input': invalid, 'cases': rows,
        'model_calls': len(provider.observations), 'server_stopped': not thread.is_alive(),
        'default_factory_changed': False}, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
