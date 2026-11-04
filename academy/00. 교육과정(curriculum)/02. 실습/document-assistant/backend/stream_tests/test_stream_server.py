import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from tools.stream_lab import make_server


class StreamServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.ui=Path(cls.tmp.name);(cls.ui/'index.html').write_text('fixture')
        cls.server=make_server(cls.ui);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    def request(self,path,payload=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        try:
            c.request('GET' if payload is None else 'POST',path,body=None if payload is None else json.dumps(payload),headers=headers or {})
            r=c.getresponse();return r.status,dict(r.getheaders()),r.read()
        finally:c.close()
    def stream(self,id,scenario):return self.request('/lab/stream',dict(id=id,scenario=scenario))
    def test_normal_has_final_completed(self):
        status,headers,body=self.stream('normal-test','normal');self.assertEqual(status,200);self.assertTrue(headers['Content-Type'].startswith('text/event-stream'));self.assertIn('"status": "completed"',body.decode());self.assertIn('7일',body.decode())
    def test_router_refusal_no_delta(self):
        _,_,body=self.stream('refusal-test','refusal');self.assertIn(b'all_unavailable',body);self.assertNotIn(b'event: delta',body)
    def test_error_is_final_failed(self):
        _,_,body=self.stream('error-test','error');self.assertIn(b'event: error',body);self.assertIn(b'"status": "failed"',body)
    def test_truncation_is_not_final(self):
        _,_,body=self.stream('truncated-test','truncated');self.assertFalse(body.endswith(b'\r\n\r\n'));self.assertNotIn(b'"status": "completed"',body)
    def test_deadline_final(self):
        _,_,body=self.stream('deadline-test','deadline');self.assertIn(b'deadline_exceeded',body)
    def test_unknown_scenarios(self):
        for scenario in ('unknown',{},None):
            with self.subTest(scenario=scenario):self.assertEqual(self.stream('bad',scenario)[0],400)
    def test_unknown_id_cancel(self):self.assertEqual(json.loads(self.request('/lab/cancel',dict(id='unknown'))[2]),{'ack':False})
    def test_cross_origin_refused(self):self.assertEqual(self.request('/lab/stream',dict(id='cross',scenario='normal'),{'Origin':'https://example.com'})[0],403)
    def test_path_cannot_read_source_files(self):self.assertEqual(self.request('/../app/provider_router.py')[0],404)
    def test_duplicate_request_not_restarted(self):
        self.stream('duplicate-test','normal');self.assertEqual(self.stream('duplicate-test','normal')[0],409)
    def test_cancel_stops_fixture_generator(self):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        try:
            c.request('POST','/lab/stream',json.dumps(dict(id='cancel-test',scenario='slow')));response=c.getresponse()
            self.assertIn(b'event: start',response.readline());ack=json.loads(self.request('/lab/cancel',dict(id='cancel-test'))[2]);self.assertTrue(ack['ack'])
            body=response.read();self.assertIn(b'"status": "cancelled"',body)
        finally:c.close()


if __name__=='__main__':unittest.main()
