import React,{useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {consume,initialState} from './stream.mjs';
import './style.css';

const labels={idle:'실행 대기',waiting:'서버 응답 대기',streaming:'수신 중',completed:'전송 완료',cancelled:'수신 취소',failed:'완료되지 않음'};
const scenarios=[['normal','정상 전송'],['error','오류 응답'],['truncated','중간 연결 종료'],['slow','느린 응답과 취소'],['refusal','기능 미지원'],['deadline','시간 한도']];
const messages={fixture_error:'실습 서버에서 오류가 발생했습니다.',truncated_frame:'최종 판정을 받기 전에 연결이 끝났습니다.',missing_final:'최종 판정을 받기 전에 연결이 끝났습니다.',all_unavailable:'요청한 기능을 지원하는 경로가 없습니다.',deadline_exceeded:'시간 한도를 초과해 부분 응답을 사용할 수 없습니다.',output_limit:'출력 길이 한도에 도달해 응답이 잘렸습니다.',budget_exhausted:'남은 호출 예산이 부족합니다.'};

function App() {
  const [scenario,setScenario]=useState('normal');const [state,setState]=useState({...initialState(''),phase:'idle'});
  const current=useRef(null);const generation=useRef(0);
  useEffect(()=>()=>{generation.current++;current.current?.controller.abort();},[]);
  const busy=['waiting','streaming'].includes(state.phase);
  async function start() {
    if(current.current&&!current.current.done)return;
    const token=++generation.current;const id=crypto.randomUUID();const controller=new AbortController();
    const run={token,id,controller,cancelled:false,done:false};current.current=run;setState(initialState(id));
    try {
      const response=await fetch('/lab/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,scenario}),signal:controller.signal});
      await consume(response,id,s=>{if(generation.current===token&&!run.cancelled)setState(s);},controller.signal);
    } catch(error) {
      if(generation.current===token&&!run.cancelled)setState(s=>({...s,phase:'failed',answer:null,finalStatus:'transport_error',error:error instanceof Error&&['missing_final','truncated_frame','answer_mismatch','content_type','http_status','id_or_sequence'].includes(error.message)?error.message:'stream_error'}));
    } finally {run.done=true;}
  }
  function cancel() {
    const run=current.current;if(!run||run.done)return;
    run.cancelled=true;run.controller.abort();run.done=true;
    setState(s=>({...s,phase:'cancelled',answer:null,finalStatus:'cancelled',serverCancelAck:false}));
    fetch('/lab/cancel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:run.id})})
      .then(r=>r.json()).then(r=>{if(generation.current===run.token)setState(s=>({...s,serverCancelAck:r.ack===true}));}).catch(()=>{});
  }
  return <main>
    <header><p className="eyebrow">K-EDU · L9 실습</p><h1>문서 답변의 전송 상태 확인</h1><p>내용이 조금 보인다고 완료된 답변은 아닙니다. 최종 판정까지 확인하세요.</p></header>
    <aside>교육용 고정 응답입니다. 실제 모델 생성이나 업무 승인 결과가 아닙니다.</aside>
    <section className="controls" aria-label="실행 조건">
      <label htmlFor="scenario">확인할 상황</label>
      <select id="scenario" value={scenario} disabled={busy} onChange={e=>setScenario(e.target.value)}>{scenarios.map(([v,l])=><option key={v} value={v}>{l}</option>)}</select>
      <div className="buttons"><button onClick={start} disabled={busy}>전송 시작</button><button className="secondary" onClick={cancel} disabled={!busy}>수신 취소</button></div>
    </section>
    <section className="result" aria-label="전송 결과" aria-busy={busy}>
      <div className="result-heading"><h2>답변</h2><span role="status" data-phase={state.phase}>{labels[state.phase]}</span></div>
      <div className="answer" data-testid="answer">{state.answer||state.draft||'아직 수신한 내용이 없습니다.'}</div>
      {state.draft&&state.phase!=='completed'&&<p className="notice">이 내용은 부분 응답이며 최종 답변으로 사용할 수 없습니다.</p>}
      {state.phase==='completed'&&<p className="notice">전송이 끝났습니다. 답변의 의미와 근거 검토는 별도입니다.</p>}
      {state.phase==='cancelled'&&<p className="notice">{state.serverCancelAck?'서버가 실습 전송의 취소 요청을 접수했습니다.':'서버의 취소 접수는 확인되지 않았습니다.'} 실제 모델 계산의 강제 중단을 뜻하지 않습니다.</p>}
      {state.phase==='failed'&&<p role="alert">{messages[state.error]||messages[state.finalStatus]||'전송 결과를 확인하지 못했습니다. 이 부분 응답은 사용할 수 없습니다.'}</p>}
    </section>
    <footer>한 번의 실행만 처리합니다. 연결이 끊겨도 자동 재호출하지 않습니다.</footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);
