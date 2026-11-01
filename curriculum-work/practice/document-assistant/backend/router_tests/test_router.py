from dataclasses import replace
import json
import unittest
from types import SimpleNamespace

from app.provider_router import Budget,Endpoint,Generation,Readiness,Router,TemporaryFailure,TerminalFailure,hf_cpu_endpoint


class Clock:
    now=100.
    def __call__(self):return self.now


class RouterTests(unittest.TestCase):
    def setUp(self):self.clock=Clock();self.invoked=[]
    def endpoint(self,alias='a',**changes):
        def generate(message,remaining):
            self.invoked.append((alias,remaining));return Generation('고정 응답',len(message),5)
        return replace(Endpoint(alias,'local',frozenset({'text'}),100,10,'unicode-codepoint-fixture',lambda:Readiness('ready',self.clock()),len,generate),**changes)
    def run_route(self,endpoints=None,**kwargs):return Router(endpoints or [self.endpoint()],clock=self.clock).run('질문',**kwargs)
    def temporary(self,*args):raise TemporaryFailure('secret must not appear')
    def test_success(self):
        r=self.run_route();self.assertEqual(r['status'],'completed');self.assertEqual(r['reserved_tokens'],12)
    def test_capability_mismatch_zero_calls(self):
        r=self.run_route(required=frozenset({'vision'}));self.assertEqual(r['calls'],0);self.assertFalse(self.invoked)
    def test_scope_denied_before_probe(self):
        e=self.endpoint(scope='external',readiness=lambda:1/0)
        r=self.run_route([e]);self.assertEqual(r['trace'][0]['decision'],'scope_denied');self.assertEqual(r['calls'],0)
    def test_readiness_not_a_configuration_flag(self):
        for state in ('configured','unknown','loading','failed'):
            with self.subTest(state=state):self.assertEqual(self.run_route([self.endpoint(readiness=lambda:Readiness(state,self.clock()))])['calls'],0)
    def test_stale_and_future_readiness(self):
        for when in (0.,101.):
            with self.subTest(time=when):self.assertEqual(self.run_route([self.endpoint(readiness=lambda:Readiness('ready',when))])['calls'],0)
    def test_invalid_readiness_terminal(self):
        r=self.run_route([self.endpoint(readiness=lambda:None)]);self.assertEqual(r['status'],'failed');self.assertEqual(r['calls'],0)
    def test_context_overflow_before_generation(self):
        r=self.run_route([self.endpoint(context_limit=11)]);self.assertEqual(r['calls'],0);self.assertEqual(r['trace'][0]['decision'],'context_overflow')
    def test_context_exact_boundary(self):self.assertEqual(self.run_route([self.endpoint(context_limit=12)])['status'],'completed')
    def test_prompt_not_silently_truncated(self):
        captured=[];e=self.endpoint(count_input=lambda p:captured.append(p) or len(p),context_limit=11)
        self.run_route([e]);self.assertEqual(captured,['질문']);self.assertFalse(self.invoked)
    def test_bad_input_count(self):
        for value in (0,-1,True,1.5):
            with self.subTest(count=value):self.assertEqual(self.run_route([self.endpoint(count_input=lambda _:value)])['calls'],0)
    def test_token_budget_denies_first_call(self):self.assertEqual(self.run_route(budget=Budget(reserved_tokens=11))['calls'],0)
    def test_token_budget_exact_boundary(self):self.assertEqual(self.run_route(budget=Budget(reserved_tokens=12))['status'],'completed')
    def test_failure_reservation_not_refunded(self):
        r=self.run_route([self.endpoint(generate=self.temporary),self.endpoint('b')],budget=Budget(reserved_tokens=23));self.assertEqual(r['status'],'budget_exhausted');self.assertEqual(r['reserved_tokens'],12);self.assertEqual(r['calls'],1)
    def test_temporary_failure_fallback(self):
        r=self.run_route([self.endpoint(generate=self.temporary),self.endpoint('b')]);self.assertEqual(r['endpoint'],'b');self.assertEqual(r['calls'],2);self.assertEqual(r['reserved_tokens'],24)
    def test_call_budget_shared_across_endpoints(self):
        r=self.run_route([self.endpoint(generate=self.temporary),self.endpoint('b')],budget=Budget(calls=1));self.assertEqual(r['status'],'budget_exhausted');self.assertEqual(r['calls'],1)
    def test_terminal_failure_no_fallback(self):
        def broken(*args):raise TerminalFailure('secret')
        r=self.run_route([self.endpoint(generate=broken),self.endpoint('b')]);self.assertEqual(r['status'],'failed');self.assertEqual(r['calls'],1);self.assertFalse(self.invoked)
    def test_unknown_exception_no_fallback(self):
        r=self.run_route([self.endpoint(generate=lambda *a:1/0),self.endpoint('b')]);self.assertEqual(r['calls'],1);self.assertEqual(r['status'],'failed')
    def test_output_limit_is_not_completed_or_fallback(self):
        r=self.run_route([self.endpoint(generate=lambda *a:Generation('partial',2,10,'length')),self.endpoint('b')]);self.assertEqual(r['status'],'output_limit');self.assertIsNone(r['answer']);self.assertEqual(r['calls'],1)
    def test_invalid_output_no_repair_or_fallback(self):
        for output in (None,Generation('',2,1),Generation('x',3,1),Generation('x',2,11),Generation('x',True,1),Generation('x',2,0)):
            with self.subTest(output=output):
                r=self.run_route([self.endpoint(generate=lambda *a:output),self.endpoint('b')]);self.assertEqual(r['status'],'failed');self.assertEqual(r['calls'],1)
    def test_deadline_during_preflight_no_generation(self):
        def count(p):self.clock.now+=5;return len(p)
        r=self.run_route([self.endpoint(count_input=count)],budget=Budget(seconds=1));self.assertEqual(r['status'],'deadline_exceeded');self.assertEqual(r['calls'],0)
    def test_late_success_discarded_no_fallback(self):
        def slow(*a):self.clock.now+=2;return Generation('late',2,1)
        r=self.run_route([self.endpoint(generate=slow),self.endpoint('b')],budget=Budget(seconds=1));self.assertEqual(r['status'],'deadline_exceeded');self.assertIsNone(r['answer']);self.assertEqual(r['calls'],1)
    def test_deadline_after_temporary_failure(self):
        def slow(*a):self.clock.now+=2;raise TemporaryFailure()
        r=self.run_route([self.endpoint(generate=slow),self.endpoint('b')],budget=Budget(seconds=1));self.assertEqual(r['status'],'deadline_exceeded');self.assertEqual(r['calls'],1)
    def test_cancel_before_request(self):self.assertEqual(self.run_route(cancelled=lambda:True)['calls'],0)
    def test_cancel_after_call(self):
        flag=[]
        def generation(*a):flag.append(True);return Generation('ignored',2,1)
        r=self.run_route([self.endpoint(generate=generation)],cancelled=lambda:bool(flag));self.assertEqual(r['status'],'cancelled');self.assertIsNone(r['answer'])
    def test_remaining_time_forwarded(self):self.run_route(budget=Budget(seconds=7));self.assertEqual(self.invoked[0][1],7)
    def test_trace_does_not_include_raw_prompt_or_exception(self):
        r=self.run_route([self.endpoint(generate=self.temporary)]);encoded=json.dumps(r['trace'],ensure_ascii=False);self.assertNotIn('질문',encoded);self.assertNotIn('secret',encoded)
    def test_all_unavailable(self):self.assertEqual(self.run_route(required=frozenset({'stream'}))['status'],'all_unavailable')
    def test_duplicate_endpoints_refused(self):
        with self.assertRaises(ValueError):Router([self.endpoint(),self.endpoint()])
    def test_invalid_budget(self):
        for args in (dict(calls=0),dict(calls=True),dict(seconds=float('nan')),dict(seconds=-1),dict(reserved_tokens=0)):
            with self.subTest(args=args),self.assertRaises(ValueError):Budget(**args)
    def test_empty_request_rejected(self):
        with self.assertRaises(ValueError):Router([self.endpoint()]).run(' ')
    def test_hf_adapter_profile_and_usage(self):
        class Tokenizer:
            def apply_chat_template(self,*a,**k):return '123'
            def __call__(self,*a,**k):return {'input_ids':[1,2,3]}
        provider=SimpleNamespace(profile=dict(teaching_total_token_limit=100,max_new_tokens=10,input_token_limit=90,model_id='fixture',revision='fixed'),tokenizer=Tokenizer(),observations=[])
        def generate(p):provider.observations.append(dict(input_tokens=3,output_tokens=2,hit_output_limit=False));return 'fixed'
        provider.generate=generate;e=hf_cpu_endpoint(provider,clock=self.clock)
        r=self.run_route([e]);self.assertEqual(r['status'],'completed');self.assertEqual(r['reserved_tokens'],13)
        provider.profile['max_new_tokens']=99
        r=self.run_route([e]);self.assertEqual(r['calls'],0);self.assertEqual(r['status'],'failed')
    def test_hf_missing_usage_refused(self):
        from types import SimpleNamespace
        p=SimpleNamespace(profile=dict(teaching_total_token_limit=100,max_new_tokens=10,input_token_limit=90,model_id='fixture',revision='fixed'),tokenizer=SimpleNamespace(apply_chat_template=lambda *a,**k:'x',__call__=lambda *a,**k:{'input_ids':[1]}),observations=[])
        # Direct endpoint invocation isolates the existing-provider usage contract.
        p.generate=lambda message:'x';e=hf_cpu_endpoint(p,clock=self.clock)
        with self.assertRaises(TerminalFailure):e.generate('x',1)


if __name__=='__main__':unittest.main()
