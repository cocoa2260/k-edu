import React, { useEffect, useRef, useState } from 'react';
import { askChat, getHealth } from './api.js';

const SAMPLE = '국내 당일 출장 식비 상한과 필요한 자료는?';

export default function App() {
  const [question, setQuestion] = useState(SAMPLE);
  const [busy, setBusy] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState('');
  const [server, setServer] = useState(null);
  const [healthError, setHealthError] = useState(false);
  const requestId = useRef(0);

  useEffect(() => {
    let live = true;
    getHealth().then(data => { if (live) setServer(data); })
      .catch(() => { if (live) setHealthError(true); });
    return () => { live = false; requestId.current += 1; };
  }, []);

  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setAnswer(null);
    setError('');
    const current = ++requestId.current;
    try {
      const result = await askChat(question);
      if (current === requestId.current) setAnswer(result);
    } catch (failure) {
      if (current === requestId.current) setError(failure.message ?? '알 수 없는 오류');
    } finally {
      if (current === requestId.current) setBusy(false);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <div className="eyebrow">K-EDU · AI 문서 도우미 실습</div>
        <h1>기본 AI 대화</h1>
        <p>오늘은 React에서 FastAPI를 거쳐 Qwen3 모델과 대화합니다. 문서 검색 기능은 다음 수업에서 직접 만듭니다.</p>
      </header>
      <div className="layout">
        <section className="panel" aria-labelledby="question-heading">
          <h2 id="question-heading">질문 보내기</h2>
          <form onSubmit={submit}>
            <label htmlFor="question">모델에게 질문을 입력하세요</label>
            <textarea id="question" rows="6" value={question} disabled={busy}
              onChange={event => setQuestion(event.target.value)} placeholder="질문 입력" />
            <div className="actions">
              <small className={question.length > 2000 ? 'count invalid' : 'count'}>{question.length} / 2000자</small>
              <button type="submit" disabled={busy || !question.trim() || question.length > 2000}>
                {busy ? '응답 기다리는 중…' : '질문 보내기'}
              </button>
            </div>
          </form>
          <button type="button" className="reset" disabled={busy} onClick={() => setQuestion(SAMPLE)}>예시 질문 다시 넣기</button>
        </section>
        <section className="panel" aria-labelledby="answer-heading" aria-busy={busy}>
          <h2 id="answer-heading">응답 결과</h2>
          <div className="answer" aria-live="polite">
            {busy && <p className="muted">모델 답변을 기다리고 있습니다.</p>}
            {!busy && error && <p className="alert" role="alert">{error}</p>}
            {!busy && answer && <p className="text-answer">{answer.answer}</p>}
            {!busy && !answer && !error && <p className="muted">질문을 보내면 여기에 응답이 표시됩니다.</p>}
          </div>
          <div className="info">
            <div><strong>Backend</strong><span>{server ? '설정 확인' : healthError ? '연결 실패' : '확인 중'}</span></div>
            <div><strong>Provider</strong><span>{answer?.provider ?? server?.provider ?? '—'}</span></div>
            <div><strong>Model</strong><span>{answer?.model ?? server?.model ?? '—'}</span></div>
          </div>
          <p className="caution">Backend 상태 확인은 실제 모델 응답 성공이 아닙니다. 이 단계의 답변은 가상 규정을 검색한 결과도 아닙니다.</p>
        </section>
      </div>
      <aside className="next">
        <h2>앞으로 추가할 기능</h2>
        <p>Prompt·Context → 실행 관리 → 문서 분할 → Embedding → 벡터 검색 → RAG → Tool Calling → Single-Agent → Multi-Agent</p>
        <p>이 기능들은 현재 비활성화된 메뉴가 아니라, 앞으로 학생이 직접 구현할 내용입니다.</p>
      </aside>
    </main>
  );
}
