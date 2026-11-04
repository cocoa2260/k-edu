// SSE framing subset: UTF-8, LF/CRLF/CR, comments, multiline data.
// No reconnect, Last-Event-ID replay, or automatic retries.
export class StreamProtocolError extends Error {}
export const terminal = s => ['completed','failed','cancelled'].includes(s.phase);
const statuses = new Set(['completed','failed','budget_exhausted','all_unavailable','deadline_exceeded','cancelled','output_limit']);

export class SSEDecoder {
  constructor(onEvent) {
    this.decoder=new TextDecoder('utf-8',{fatal:true});this.onEvent=onEvent;
    this.line='';this.data=[];this.event='';this.skipLF=false;this.bytes=0;this.size=0;this.closed=false;
  }
  text(text) {
    for(const c of text) {
      if(this.skipLF) {this.skipLF=false;if(c==='\n')continue;}
      if(c==='\r'||c==='\n') {this.endLine();this.skipLF=c==='\r';}
      else {this.line+=c;if(this.line.length>32768)throw new StreamProtocolError('line_limit');}
    }
  }
  endLine() {
    const line=this.line;this.line='';
    if(line==='') {
      if(this.data.length)this.onEvent({event:this.event||'message',data:this.data.join('\n')});
      this.data=[];this.event='';this.size=0;return;
    }
    if(line.startsWith(':'))return;
    const at=line.indexOf(':');const field=at<0?line:line.slice(0,at);
    let value=at<0?'':line.slice(at+1);if(value.startsWith(' '))value=value.slice(1);
    if(field==='data'){this.data.push(value);this.size+=value.length+1;if(this.size>131072)throw new StreamProtocolError('event_limit');}
    if(field==='event')this.event=value;
  }
  push(bytes) {
    if(this.closed)throw new StreamProtocolError('decoder_closed');
    this.bytes+=bytes.byteLength;if(this.bytes>1048576)throw new StreamProtocolError('stream_limit');
    this.text(this.decoder.decode(bytes,{stream:true}));
  }
  finish() {
    if(this.closed)return;this.text(this.decoder.decode());this.closed=true;
    // Application policy is stricter than generic SSE EOF discard semantics.
    if(this.line||this.data.length||this.event)throw new StreamProtocolError('truncated_frame');
  }
}

export function initialState(id) {
  return {id,phase:'waiting',draft:'',answer:null,lastSeq:-1,error:null,finalStatus:null,serverCancelAck:false};
}

export function applyEvent(state,event) {
  if(terminal(state))return state; // late data cannot overwrite a final/cancel state
  let value;try{value=JSON.parse(event.data);}catch{throw new StreamProtocolError('invalid_json');}
  if(!value||typeof value!=='object'||Array.isArray(value)||value.id!==state.id||!Number.isInteger(value.seq)||value.seq!==state.lastSeq+1)throw new StreamProtocolError('id_or_sequence');
  const next={...state,lastSeq:value.seq};
  if(event.event==='start') {
    if(state.lastSeq!==-1||value.fixture!==true)throw new StreamProtocolError('invalid_start');
    return {...next,phase:'streaming'};
  }
  if(state.lastSeq===-1)throw new StreamProtocolError('start_required');
  if(event.event==='delta') {
    if(state.error||typeof value.text!=='string'||!value.text||state.draft.length+value.text.length>16000)throw new StreamProtocolError('invalid_delta');
    return {...next,draft:state.draft+value.text};
  }
  if(event.event==='error') {
    if(value.code!=='fixture_error')throw new StreamProtocolError('invalid_error');
    return {...next,error:value.code};
  }
  if(event.event==='final') {
    if(!statuses.has(value.status))throw new StreamProtocolError('invalid_final');
    if(value.status==='completed'&&(state.error||!state.draft||value.answer!==state.draft))throw new StreamProtocolError('answer_mismatch');
    if(value.status!=='completed'&&value.answer!==null)throw new StreamProtocolError('unexpected_answer');
    return {...next,phase:value.status==='completed'?'completed':value.status==='cancelled'?'cancelled':'failed',finalStatus:value.status,answer:value.status==='completed'?state.draft:null};
  }
  throw new StreamProtocolError('unknown_event');
}

export async function consume(response,id,onState,signal) {
  if(!response.ok)throw new StreamProtocolError('http_status');
  if(response.headers.get('content-type')?.split(';')[0].trim()!=='text/event-stream'||!response.body)throw new StreamProtocolError('content_type');
  const reader=response.body.getReader();let state=initialState(id);
  const decoder=new SSEDecoder(event=>{if(signal?.aborted)throw new DOMException('Aborted','AbortError');state=applyEvent(state,event);onState(state);});
  try {
    while(true) {
      if(signal?.aborted)throw new DOMException('Aborted','AbortError');
      const {value,done}=await reader.read();if(done)break;
      decoder.push(value);
      if(terminal(state))return state; // first valid terminal ends this request
    }
    decoder.finish();if(!terminal(state))throw new StreamProtocolError('missing_final');
    return state;
  } finally {await reader.cancel().catch(()=>{});reader.releaseLock();}
}
