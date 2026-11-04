"""python -m tools.stream_lab --ui ../stream-ui/dist --port 8765

Loopback-only React/SSE fixture lab, separate from existing FastAPI routes.
Router generates a fixed complete answer FIRST; delivery is then fragmented.
This is real HTTP streaming of a buffered fixture, NOT model Token streaming.
"""
import argparse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import time

from app.provider_router import Budget,Endpoint,Generation,Readiness,Router

SCENARIOS={'normal','error','truncated','slow','refusal','deadline'}
ANSWER='가상 문서에는 신청 기한이 7일로 적혀 있습니다.'


def make_server(ui,port=0):
    ui=Path(ui).resolve();records={};lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,payload):
            body=json.dumps(payload).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path=='/lab/runs':
                with lock:data=[{k:v for k,v in row.items() if k!='cancel'} for row in records.values()]
                self.reply(200,data);return
            files={'/':'index.html','/app.js':'app.js','/app.css':'app.css','/app.js.LEGAL.txt':'app.js.LEGAL.txt'}
            name=files.get(self.path)
            if name is None or not (ui/name).is_file():self.reply(404,dict(error='not_found'));return
            body=(ui/name).read_bytes();self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8' if name.endswith('.html') else 'text/css' if name.endswith('.css') else 'text/plain' if name.endswith('.txt') else 'application/javascript')
            self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
        def do_POST(self):
            origin=self.headers.get('Origin')
            if origin and origin!=f'http://127.0.0.1:{self.server.server_port}':self.reply(403,dict(error='origin'));return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096:raise ValueError()
                payload=json.loads(self.rfile.read(size));id=payload['id']
                if not isinstance(id,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',id):raise ValueError()
            except (ValueError,KeyError,TypeError):self.reply(400,dict(error='invalid_input'));return
            if self.path=='/lab/cancel':
                with lock:
                    row=records.get(id);ack=bool(row and row['status']=='running')
                    if ack:row['cancel'].set();row['cancel_requested']=True
                self.reply(200,dict(ack=ack));return
            if self.path!='/lab/stream':self.reply(404,dict(error='not_found'));return
            scenario=payload.get('scenario')
            if not isinstance(scenario,str) or scenario not in SCENARIOS:self.reply(400,dict(error='invalid_scenario'));return
            with lock:
                if id in records:self.reply(409,dict(error='duplicate_request'));return
                if sum(row['status']=='running' for row in records.values())>=8:self.reply(429,dict(error='busy'));return
                while len(records)>=64:
                    oldest=next((k for k,v in records.items() if v['status']!='running'),None)
                    if oldest is None:break
                    del records[oldest]
                row=dict(id=id,scenario=scenario,status='running',events=0,cancel_requested=False,cancel=threading.Event())
                records[id]=row
            self.send_response(200);self.send_header('Content-Type','text/event-stream; charset=utf-8');self.send_header('Cache-Control','no-cache');self.send_header('Connection','close');self.end_headers();self.close_connection=True
            seq=0;started=time.monotonic()
            def emit(kind,**fields):
                nonlocal seq
                data=dict(id=id,seq=seq,**fields);seq+=1
                frame=('event: '+kind+'\r\ndata: '+json.dumps(data,ensure_ascii=False)+'\r\n\r\n').encode()
                # Split inside the first non-ASCII codepoint where available.
                at=next((n+1 for n,b in enumerate(frame) if b>=128),len(frame)//2)
                self.wfile.write(frame[:at]);self.wfile.flush();self.wfile.write(frame[at:]);self.wfile.flush()
                with lock:row['events']+=1
            def finish(status,answer=None):
                with lock:row['status']=status
                emit('final',status=status,answer=answer)
            try:
                emit('start',fixture=True)
                endpoint=Endpoint('stream_fixture','local',frozenset({'text'}),512,128,'unicode-codepoint-fixture-NOT-model-tokenizer',lambda:Readiness('ready',time.monotonic()),len,lambda message,remaining:Generation(ANSWER,len(message),len(ANSWER)))
                route=Router([endpoint]).run('기한 확인',required=frozenset({'vision'}) if scenario=='refusal' else frozenset({'text'}),budget=Budget(calls=1,reserved_tokens=256,seconds=2))
                with lock:row['router_status']=route['status']
                if route['status']!='completed':finish(route['status']);return
                if scenario=='error':
                    emit('delta',text='처리 중');emit('error',code='fixture_error');finish('failed');return
                if scenario=='truncated':
                    emit('delta',text='부분 응답');self.wfile.write(b'event: final\ndata: {"id":');self.wfile.flush()
                    with lock:row['status']='truncated'
                    return
                width=1 if scenario in ('slow','deadline') else 5
                for offset in range(0,len(route['answer']),width):
                    if row['cancel'].wait(.08 if width==1 else .025):finish('cancelled');return
                    if time.monotonic()-started>1.0 and scenario=='deadline':finish('deadline_exceeded');return
                    emit('delta',text=route['answer'][offset:offset+width])
                finish('completed',route['answer'])
            except (BrokenPipeError,ConnectionResetError):
                with lock:
                    if row['status']=='running':row['status']='cancelled' if row['cancel'].is_set() else 'disconnected'
            finally:
                with lock:
                    if row['status']=='running':row['status']='failed'
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--ui',required=True);p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    server=make_server(a.ui,a.port);print(f'http://127.0.0.1:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
