# AI 문서 도우미 — 기본 Chat 실습앱

수업에서는 `backend/`와 `frontend/`를 하나의 프로젝트로 계속 사용합니다. 처음에는 React 질문 → FastAPI → Ollama Qwen3 → React 답변까지 구현되어 있습니다. **문서 검색, Embedding, RAG, Agent는 아직 없습니다.**

## 준비

Python 3.11 이상(권장 3.11 또는 3.12), Node.js 20.19 이상(권장 22), npm, Ollama를 설치합니다. [자세한 순서](<../교안/부록. Python 가상환경 만들기.md>)는 `교안/` 폴더의 부록을 참고합니다. 단, 상대경로로 찾기 어려우면 VS Code에서 이 패키지의 `교안/부록. Python 가상환경 만들기.md`를 직접 여세요.

```bash
ollama pull qwen3:1.7b
ollama run qwen3:1.7b
```

Ollama 대화창에서 한국어로 한 번 질문하고 `/bye`로 빠져나옵니다.

## Backend — 첫 번째 터미널

**현재 터미널 위치: `실습앱/`**

**macOS/Linux**

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m pytest -q
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

**Windows PowerShell**

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

`.env.example`에는 `OLLAMA_MODEL=qwen3:1.7b`가 기본으로 설정되어 있습니다. Mac/Windows에서 Python 버전 경로가 다르면 부록의 해당 OS 절차를 따릅니다. `.env`에 키나 비밀번호를 기록한 후 공유하지 않습니다.

`http://127.0.0.1:8000/health`에서 모델명이 보여도 이것은 설정 확인일 뿐 실제 추론을 하지 않습니다.

## Frontend — 두 번째 터미널

**새 터미널을 `실습앱/`에서 열고 다음 명령을 실행**합니다.

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 **`http://127.0.0.1:5173`**를 열고 질문을 입력합니다. 최초 `npm install`은 인터넷에 연결되어 있어야 합니다. `npm run build`로 프런트엔드 빌드도 확인할 수 있습니다.

## 어떻게 확인하나요?

- Chat 질문의 응답이 나타나면 **실제 모델 연결을 확인**합니다. 단, Ollama 모델이 실행된 상태여야 합니다.
- 공백 입력·2000자 초과는 HTTP 422입니다.
- 모델 서비스 연결 실패는 503, 응답 이상은 502, 요청 시간 초과는 504입니다.
- `python -m pytest -q`와 `npm test`는 모델 없이도 실행하는 계약 테스트입니다. 둘 다 통과해도 실제 모델이 응답했다는 뜻은 아닙니다.

## 다음 수업에서는 무엇을 만들까요?

Prompt와 Context 입력 구성 → 실행 관리 → 문서 분할 → 실제 Embedding → 벡터 검색 → RAG → Tool Calling → Single-Agent → Multi-Agent. 지금은 각 기능의 **완성 코드를 포함하지 않습니다**.

## 문제 해결

| 증상 | 확인할 사항 |
|---|---|
| `ModuleNotFoundError` | `backend/` 폴더에서 해당 가상환경의 Python을 사용했는지 확인 |
| `OLLAMA_MODEL` 설정 오류 | `backend/.env` 파일과 `ollama list`에서 모델 이름 확인 |
| 503 | Ollama 실행 여부, `OLLAMA_BASE_URL` 확인 |
| 502 | Ollama 응답, 모델 이름, 서버 로그 확인 |
| 504 | 모델 추론 지연·메모리 부족 등 확인 |
| 브라우저 5173 접속 실패 | Node/npm 설치, `frontend/`에서 `npm run dev` 실행 여부 확인 |
| 모델 답변이 규정과 다름 | 아직 RAG가 없어 **문서 근거 검색을 하지 않는 단계**입니다 |

가상 규정의 `staff`·`restricted`는 교육용 표식이며 실제 사용자 인증을 구현한 것이 아닙니다.
