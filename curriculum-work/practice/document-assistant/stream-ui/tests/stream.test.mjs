import test from 'node:test';
import assert from 'node:assert/strict';
import {SSEDecoder,initialState,applyEvent,consume} from '../src/stream.mjs';
const enc=new TextEncoder();
const event=(kind,seq,extra={})=>({event:kind,data:JSON.stringify({id:'run',seq,...extra})});
const wire=e=>`event: ${e.event}\ndata: ${e.data}\n\n`;
const start=event('start',0,{fixture:true}),delta=event('delta',1,{text:'한글🙂'}),final=event('final',2,{status:'completed',answer:'한글🙂'});
test('UTF8 and every byte boundary including emoji',()=>{
 const bytes=enc.encode(wire(start)+wire(delta)+wire(final));
 for(let split=0;split<=bytes.length;split++) {const events=[];const p=new SSEDecoder(e=>events.push(e));p.push(bytes.slice(0,split));p.push(bytes.slice(split));p.finish();assert.equal(events.length,3);assert.deepEqual(events[1],delta);}
});
test('one byte chunks',()=>{const events=[];const p=new SSEDecoder(e=>events.push(e));for(const byte of enc.encode(wire(delta)))p.push(Uint8Array.of(byte));p.finish();assert.deepEqual(events,[delta]);});
for(const ending of ['\n','\r\n','\r'])test('line endings '+JSON.stringify(ending),()=>{const events=[];const p=new SSEDecoder(e=>events.push(e));p.push(enc.encode(`: ping${ending}event: demo${ending}id: ignored${ending}data: one${ending}data: two${ending}${ending}`));p.finish();assert.deepEqual(events,[{event:'demo',data:'one\ntwo'}]);});
test('default message and empty data',()=>{const out=[];const p=new SSEDecoder(e=>out.push(e));p.push(enc.encode('data:\n\n'));p.finish();assert.deepEqual(out,[{event:'message',data:''}]);});
test('truncated frame rejected',()=>{const p=new SSEDecoder(()=>{});p.push(enc.encode('data: partial'));assert.throws(()=>p.finish(),/truncated_frame/);});
test('incomplete UTF8 rejected',()=>{const p=new SSEDecoder(()=>{});p.push(Uint8Array.of(0xe3));assert.throws(()=>p.finish());});
test('invalid UTF8 rejected',()=>assert.throws(()=>new SSEDecoder(()=>{}).push(Uint8Array.of(0xff))));
test('line cap',()=>assert.throws(()=>new SSEDecoder(()=>{}).push(enc.encode('x'.repeat(32769))),/line_limit/));
test('event cap',()=>{const p=new SSEDecoder(()=>{});assert.throws(()=>p.push(enc.encode(('data: '+'x'.repeat(32000)+'\n').repeat(5))),/event_limit/);});
test('stream cap',()=>{const p=new SSEDecoder(()=>{});assert.throws(()=>p.push(new Uint8Array(1048577)),/stream_limit/);});
test('complete state requires terminal event',()=>{let s=applyEvent(initialState('run'),start);s=applyEvent(s,delta);assert.equal(s.phase,'streaming');assert.equal(s.answer,null);s=applyEvent(s,final);assert.equal(s.phase,'completed');assert.equal(s.answer,'한글🙂');});
test('late event cannot overwrite terminal state',()=>{const s=[start,delta,final].reduce(applyEvent,initialState('run'));assert.equal(applyEvent(s,event('delta',3,{text:'late'})),s);});
test('local cancelled state cannot become success',()=>{const s={...initialState('run'),phase:'cancelled'};assert.equal(applyEvent(s,final),s);});
test('wrong request ID',()=>assert.throws(()=>applyEvent(initialState('other'),start),/id_or_sequence/));
test('sequence gap and duplicate rejected',()=>{const s=applyEvent(initialState('run'),start);assert.throws(()=>applyEvent(s,event('delta',2,{text:'x'})));assert.throws(()=>applyEvent(s,start));});
test('invalid JSON',()=>assert.throws(()=>applyEvent(initialState('run'),{event:'start',data:'{'}),/invalid_json/));
test('must start with fixture metadata',()=>{assert.throws(()=>applyEvent(initialState('run'),event('delta',0,{text:'x'})),/start_required/);assert.throws(()=>applyEvent(initialState('run'),event('start',0,{fixture:false})),/invalid_start/);});
test('final answer mismatch',()=>{const s=[start,delta].reduce(applyEvent,initialState('run'));assert.throws(()=>applyEvent(s,event('final',2,{status:'completed',answer:'wrong'})),/answer_mismatch/);});
test('unknown event and final status',()=>{const s=applyEvent(initialState('run'),start);assert.throws(()=>applyEvent(s,event('tool',1)));assert.throws(()=>applyEvent(s,event('final',1,{status:'unknown',answer:null})));});
for(const status of ['failed','budget_exhausted','all_unavailable','deadline_exceeded','output_limit','cancelled'])test('non-success '+status,()=>{const s=[start,delta,event('final',2,{status,answer:null})].reduce(applyEvent,initialState('run'));assert.equal(s.answer,null);assert.notEqual(s.phase,'completed');});
test('error event followed by final failed',()=>{const s=[start,event('error',1,{code:'fixture_error'}),event('final',2,{status:'failed',answer:null})].reduce(applyEvent,initialState('run'));assert.equal(s.error,'fixture_error');assert.equal(s.phase,'failed');});
test('data after error rejected',()=>{const s=[start,event('error',1,{code:'fixture_error'})].reduce(applyEvent,initialState('run'));assert.throws(()=>applyEvent(s,event('delta',2,{text:'x'})),/invalid_delta/);});
function response(text,type='text/event-stream',status=200){return new Response(enc.encode(text),{status,headers:{'Content-Type':type}});}
test('consumer HTTP status',async()=>assert.rejects(consume(response('',undefined,503),'run',()=>{}),/http_status/));
test('consumer MIME',async()=>assert.rejects(consume(response('','application/json'),'run',()=>{}),/content_type/));
test('consumer EOF without final',async()=>assert.rejects(consume(response(wire(start)+wire(delta)),'run',()=>{}),/missing_final/));
test('consumer complete',async()=>assert.equal((await consume(response(wire(start)+wire(delta)+wire(final)),'run',()=>{})).phase,'completed'));
test('consumer abort before read',async()=>{const c=new AbortController();c.abort();await assert.rejects(consume(response(wire(start)),'run',()=>{},c.signal),{name:'AbortError'});});
