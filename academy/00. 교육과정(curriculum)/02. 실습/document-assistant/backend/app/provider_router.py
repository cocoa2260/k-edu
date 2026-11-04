"""U04 explicit capability/budget routing; not installed in the web factory.

Synchronous calls check a monotonic deadline before/after work, not hard cancel.
Every attempted generation reserves input + maximum output without refund.
Readiness/catalog/counts come from trusted adapters, never from document text.
"""
from dataclasses import dataclass
import hashlib
import math
import re
import time
from typing import Callable


class TemporaryFailure(Exception):
    """Only this normalized failure permits a different endpoint attempt."""


class TerminalFailure(Exception):
    pass


@dataclass(frozen=True)
class Readiness:
    status: str
    observed_at: float


@dataclass(frozen=True)
class Generation:
    text: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = 'stop'


@dataclass(frozen=True)
class Endpoint:
    alias: str
    scope: str
    features: frozenset
    context_limit: int
    max_output_tokens: int
    tokenizer_profile: str
    readiness: Callable[[], Readiness]
    count_input: Callable[[str], int]
    generate: Callable[[str, float], Generation]


@dataclass(frozen=True)
class Budget:
    calls: int = 2
    reserved_tokens: int = 4096
    seconds: float = 30.0
    readiness_ttl: float = 30.0

    def __post_init__(self):
        if type(self.calls) is not int or not 1<=self.calls<=8: raise ValueError('calls must be 1..8')
        if type(self.reserved_tokens) is not int or not 1<=self.reserved_tokens<=100000: raise ValueError('invalid reservation budget')
        for n in (self.seconds,self.readiness_ttl):
            if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or not 0<n<=300: raise ValueError('invalid time budget')


class Router:
    def __init__(self,endpoints,*,allowed_scopes=frozenset({'local'}),clock=time.monotonic):
        if not endpoints or len({e.alias for e in endpoints})!=len(endpoints): raise ValueError('Distinct endpoints required')
        for e in endpoints:
            if not re.fullmatch(r'[a-z0-9_-]{1,40}',e.alias): raise ValueError('Invalid alias')
            if type(e.context_limit) is not int or type(e.max_output_tokens) is not int or not 0<e.max_output_tokens<e.context_limit: raise ValueError('Invalid context/output limit')
            if not isinstance(e.features,frozenset) or not e.features or not e.tokenizer_profile: raise ValueError('Explicit capabilities/tokenizer required')
        self.endpoints=tuple(endpoints);self.allowed_scopes=frozenset(allowed_scopes);self.clock=clock

    def run(self,message,*,required=frozenset({'text'}),budget=Budget(),cancelled=lambda:False):
        if not isinstance(message,str) or not message.strip() or len(message)>8000: raise ValueError('message must be 1..8000 characters')
        if not isinstance(required,frozenset) or not required: raise ValueError('Required capability set missing')
        start=self.clock();calls=reserved=0;trace=[]
        def result(status,text=None,endpoint=None):
            return dict(status=status,answer=text,endpoint=endpoint,calls=calls,reserved_tokens=reserved,
                elapsed_seconds=round(self.clock()-start,6),request_sha256=hashlib.sha256(message.encode()).hexdigest(),
                trace=trace,deadline_enforcement='synchronous pre/post checks; no forced cancellation',
                reservation_policy='sum(input + max_output) for every attempted generation, no refund')
        def stopped():
            if cancelled(): return 'cancelled'
            if self.clock()-start>=budget.seconds:return 'deadline_exceeded'
            return None
        for endpoint in self.endpoints:
            stop=stopped()
            if stop:return result(stop)
            item=dict(endpoint=endpoint.alias,scope=endpoint.scope,tokenizer_profile=endpoint.tokenizer_profile)
            trace.append(item)
            if endpoint.scope not in self.allowed_scopes:
                item['decision']='scope_denied';continue
            if not required.issubset(endpoint.features):
                item['decision']='capability_mismatch';continue
            try:
                ready=endpoint.readiness()
                if not isinstance(ready,Readiness) or not isinstance(ready.observed_at,(int,float)) or not math.isfinite(ready.observed_at): raise TerminalFailure()
                age=self.clock()-ready.observed_at
                if ready.status!='ready' or not 0<=age<=budget.readiness_ttl:
                    item['decision']='not_ready_or_stale';continue
                count=endpoint.count_input(message)
                if type(count) is not int or count<=0:raise TerminalFailure()
            except Exception:
                item['decision']='preflight_failed';return result('failed')
            stop=stopped()
            if stop:item['decision']=stop;return result(stop)
            need=count+endpoint.max_output_tokens
            item.update(input_tokens=count,max_output_tokens=endpoint.max_output_tokens,reservation=need)
            if need>endpoint.context_limit:
                item['decision']='context_overflow';continue
            if calls>=budget.calls or reserved+need>budget.reserved_tokens:
                item['decision']='budget_exhausted';return result('budget_exhausted')
            remaining=budget.seconds-(self.clock()-start)
            if remaining<=0:
                item['decision']='deadline_exceeded';return result('deadline_exceeded')
            calls+=1;reserved+=need
            item.update(attempt=calls,remaining_seconds=round(remaining,6))
            try:
                output=endpoint.generate(message,remaining)
            except TemporaryFailure:
                item['decision']='temporary_failure'
                stop=stopped()
                if stop:return result(stop)
                continue
            except Exception:
                item['decision']='terminal_failure';return result('failed')
            stop=stopped()
            if stop:item['decision']=stop;return result(stop)
            if (not isinstance(output,Generation) or not isinstance(output.text,str) or not output.text.strip()
                or len(output.text)>100000 or type(output.input_tokens) is not int or output.input_tokens!=count
                or type(output.output_tokens) is not int or not 0<output.output_tokens<=endpoint.max_output_tokens
                or output.finish_reason not in ('stop','length')):
                item['decision']='invalid_generation';return result('failed')
            if output.finish_reason=='length':
                item.update(decision='output_limit',reported_input_tokens=output.input_tokens,reported_output_tokens=output.output_tokens)
                return result('output_limit')
            item.update(decision='completed',reported_input_tokens=output.input_tokens,reported_output_tokens=output.output_tokens)
            return result('completed',output.text,endpoint.alias)
        return result('all_unavailable' if calls==0 else 'failed')


def hf_cpu_endpoint(provider,*,clock=time.monotonic):
    """Opt-in adapter for existing configured HFCpuProvider. No model loading here.

    Actual HF generation is not claimed by the fixture lab. Readiness is a local
    profile check, not a model health generation. Cancellation remains pre/post.
    """
    import json
    snapshot=json.dumps(provider.profile,sort_keys=True)
    profile=provider.profile
    def guard():
        if json.dumps(provider.profile,sort_keys=True)!=snapshot:raise TerminalFailure('Profile changed')
    def count(message):
        guard()
        prompt=provider.tokenizer.apply_chat_template([dict(role='user',content=message)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        tokens=len(provider.tokenizer(prompt,add_special_tokens=False)['input_ids'])
        if tokens>profile['input_token_limit']:raise TerminalFailure('Input limit')
        return tokens
    def generate(message,remaining):
        guard();before=len(provider.observations);text=provider.generate(message);guard()
        if len(provider.observations)!=before+1:raise TerminalFailure('Missing usage')
        usage=provider.observations[-1]
        if type(usage.get('hit_output_limit')) is not bool:raise TerminalFailure('Missing finish status')
        return Generation(text,usage['input_tokens'],usage['output_tokens'],'length' if usage['hit_output_limit'] else 'stop')
    return Endpoint(alias='hf_cpu',scope='local',features=frozenset({'text'}),
        context_limit=profile['teaching_total_token_limit'],max_output_tokens=profile['max_new_tokens'],
        tokenizer_profile=profile['model_id']+'@'+profile['revision']+' chat-template',
        readiness=lambda:(guard() or Readiness('ready',clock())),count_input=count,generate=generate)
