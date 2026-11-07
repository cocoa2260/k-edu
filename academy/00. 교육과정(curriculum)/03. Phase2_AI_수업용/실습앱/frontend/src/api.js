// 모든 API 요청을 이 파일에서 관리합니다. 이후 단원도 같은 파일을 확장합니다.
export class ApiError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const messages = {
  422: '질문을 확인해 주세요. 빈 질문이거나 2000자를 넘는 입력입니다.',
  502: '모델 서비스의 응답이 올바르지 않습니다. 모델 및 서버 로그를 확인하세요.',
  503: 'Ollama 모델 서버에 연결할 수 없습니다. 실행 상태를 확인하세요.',
  504: '모델 응답 시간이 초과되었습니다.',
};

async function send(path, options = {}) {
  let response;
  try { response = await fetch(path, options); }
  catch { throw new ApiError('FastAPI에 연결하지 못했습니다. Backend와 React 개발 서버를 확인하세요.'); }
  let body;
  try { body = await response.json(); }
  catch { throw new ApiError('서버가 유효한 JSON을 반환하지 않았습니다.', response.status); }
  if (!response.ok) {
    throw new ApiError(messages[response.status] ?? `요청을 처리할 수 없습니다 (HTTP ${response.status}).`, response.status);
  }
  return body;
}

export function getHealth() { return send('/health'); }

export function askChat(message) {
  return send('/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
}
