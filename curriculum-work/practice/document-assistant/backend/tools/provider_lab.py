"""python -m tools.provider_lab --output NEW_DIR

Loopback HTTP fixture only, not Ollama/OpenAI/model generation or tokenizer.
The server counts Unicode codepoints solely to exercise reservation boundaries.
"""
import argparse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import http.client
import json
from pathlib import Path
import threading
import time

from app.provider_router import Budget,Endpoint,Generation,Readiness,Router,TemporaryFailure,TerminalFailure


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append(dict(path=self.path,input_units=len(payload['message']),max_output=payload['max_output_tokens']))
            if self.path=='/primary':
                self.send_response(503);self.end_headers();return
            text='고정 응답'
            result=dict(text=text,input_tokens=len(payload['message']),output_tokens=len(text))
            body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        def endpoint(alias):
            def generate(message,remaining):
                conn=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=remaining)
                try:
                    conn.request('POST','/'+alias,json.dumps(dict(message=message,max_output_tokens=16)),{'Content-Type':'application/json'})
                    response=conn.getresponse();body=response.read(100001)
                    if response.status==503:raise TemporaryFailure()
                    if response.status!=200 or len(body)>100000:raise TerminalFailure()
                    payload=json.loads(body);return Generation(**payload)
                finally:conn.close()
            return Endpoint(alias,'local',frozenset({'text'}),100,16,'unicode-codepoint-fixture-NOT-model-tokenizer',lambda:Readiness('ready',time.monotonic()),len,generate)
        router=Router([endpoint('primary'),endpoint('backup')])
        cases={
            'temporary_to_backup':router.run('정책 확인',budget=Budget(calls=2,reserved_tokens=42,seconds=5)),
            'feature_refused':router.run('정책 확인',required=frozenset({'vision'})),
            'shared_call_limit':router.run('정책 확인',budget=Budget(calls=1,reserved_tokens=42,seconds=5)),
            'shared_reservation_limit':router.run('정책 확인',budget=Budget(calls=2,reserved_tokens=41,seconds=5))}
        assert [r['status'] for r in cases.values()]==['completed','all_unavailable','budget_exhausted','budget_exhausted']
        assert len(requests)==4
        result=dict(batch='KEDU-PRODUCTION-015',cases=cases,actual_loopback_http_requests=requests,loopback_request_count=len(requests),real_model_calls=0,external_requests=0,token_counts='Unicode codepoints fixture units, not model Tokenizer or billed usage',quality_accepted=False,web_factory_changed=False,hard_deadline_verified=False)
        (output/'observed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(dict(cases={k:v['status'] for k,v in cases.items()},loopback_requests=len(requests)),ensure_ascii=False))
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',required=True);run(p.parse_args().output)
