# Day 1 - 7교시. Cloud AI API와 OpenAI SDK 실습

> **수업 유형:** Python 실습  
> **선행 학습:** Day 1의 AI Model·Inference 및 Model/SDK/API 역할 구분  
> **이번 교시의 결과물:** API를 호출하는 Python 프로그램과 입력 검증·오류 처리를 갖춘 `ai_explainer.py`  
> **검증 주의:** 이 자료의 모델 ID·SDK 호출 형태는 원본 교육과정에 수록된 예제에 근거한다. 교육장 계정에서 실제 사용 가능한 모델, API 권한, 과금 조건, SDK 버전은 수업 전에 별도로 확인해야 한다. 이 강의자료의 작성만으로 실시간 API 호출이 검증된 것은 아니다.

## 개요 — 배운 모델을 Python에서 실제로 사용하기

앞선 교시에서 모델을 *만드는 데 쓰는 도구*와 이미 학습된 모델을 *실행하거나 호출하는 도구*를 구분했습니다. 이번 시간에는 전자의 설명을 반복하지 않고, Python 프로그램으로 **Cloud AI API에 요청을 보내고 응답을 처리하는 작업**을 직접 수행합니다.

```text
학생의 Python 프로그램
    ↓  OpenAI Python SDK
OpenAI API에 요청 전송
    ↓
Cloud 환경에서 모델 추론
    ↓
API 응답 수신
    ↓
우리 프로그램이 출력·검증·오류 처리
```

**이 수업에서 구현하는 것은 모델 학습(Training)이 아니라 이미 학습된 모델의 추론(Inference)을 API로 요청하는 프로그램입니다.** SDK의 메서드 이름을 외우는 것보다 요청 전·중·후에 Application이 무엇을 책임지는지 확인하는 것이 목표입니다.

---

# 1. 실습 목표와 완료 기준

이번 교시를 마치면 다음을 할 수 있어야 합니다.

1. API, SDK, AI Model의 역할을 실제 요청 흐름에서 구분한다.
2. Python 가상환경을 만들고 OpenAI Python SDK를 설치한다.
3. API Key를 소스 코드에 기록하지 않고 환경 변수로 제공한다.
4. `OpenAI()` Client와 `client.responses.create(...)`로 텍스트 생성 요청을 구성한다.
5. `response` 객체와 `response.output_text`를 구분하고 사용량 정보를 확인한다.
6. `instructions`와 `input`을 분리하여 같은 기능을 서로 다른 입력에 적용한다.
7. AI 호출을 재사용 가능한 함수로 분리하고 빈 입력을 API 요청 전에 검사한다.
8. 오류를 사용자 입력·인증·네트워크·모델/요청·Provider 문제로 구분한다.
9. 입력을 바꾸는 활동과 `ai_explainer.py` 응용 과제를 수행한다.

완료 기준은 단순히 화면에 문장이 출력되는 것이 아닙니다. **Key 비노출, 실제 요청·응답 구분, 입력 검증, 오류 처리, API 사용량 확인**까지 설명하고 시연할 수 있어야 합니다.

---

# 2. 준비 사항 — 실행 전 확인

## 2.1 교육장 환경

원본 교육과정의 권장 환경은 다음과 같습니다.

| 항목 | 준비 및 확인 사항 |
|---|---|
| Python | Python 3.11 이상을 권장하며, 실제 사용 버전을 확인 |
| 작업 환경 | 터미널, 코드 편집기, Python 가상환경 생성 권한 |
| 패키지 | `openai` Python SDK 설치 가능 |
| 네트워크 | OpenAI API에 접근 가능한 인터넷 환경 |
| 계정 | API 사용 권한과 과금·사용량 정책이 확인된 계정 또는 교육용 환경 |
| 인증 | 실제 API Key를 안전하게 전달·보관할 방법 |
| 모델 | 해당 계정에서 사용할 수 있는 모델 ID를 강사가 사전에 확인 |

**ChatGPT 웹사이트 이용 권한과 API 사용 권한은 동일하다고 가정하지 마세요.** 실습 계정이 준비되지 않았다면 라이브 호출을 완료했다고 표시하지 말고 코드 작성과 정적 검증만 진행합니다.

## 2.2 프로젝트 디렉터리

원본에 제시된 세 파일을 기본 실습으로 사용하고 마지막에 응용 과제 파일을 추가합니다.

```text
day1_cloud_ai/
├── .venv/                   # 가상환경: 버전 관리에 올리지 않음
├── app/
│   ├── basic_call.py        # 첫 호출·응답·Usage 확인
│   ├── instruction_call.py  # 입력과 지시 구분·함수 분리
│   ├── error_handling.py    # 입력 검증·예외 처리
│   └── ai_explainer.py      # 응용 과제
└── requirements.txt         # 검증한 SDK 버전 기록
```

`requirements.txt`에 사용할 버전을 미리 임의로 확정하지 않습니다. 교육장에서 설치·실행한 버전을 기록해 다른 학생의 실행 결과와 비교할 수 있도록 합니다.

---

# 3. 가상환경 만들고 SDK 설치하기

가상환경(Virtual Environment)은 실습 프로젝트에서 사용할 Python 패키지를 다른 프로젝트와 분리하는 공간입니다. **설치하는 패키지는 SDK이고, GPT 모델을 학생 PC에 설치하는 것이 아닙니다.**

## 3.1 Windows PowerShell

프로젝트 폴더 `day1_cloud_ai`에서 실행합니다.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install openai
python -m pip show openai
```

PowerShell의 실행 정책 때문에 활성화가 거부되면 무작정 보안 설정을 영구적으로 낮추지 말고 교육장 환경 정책을 확인합니다. 가상환경 활성화 대신 `.venv\Scripts\python.exe`를 직접 사용하는 방법도 있습니다.

## 3.2 macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install openai
python -m pip show openai
```

활성화되면 터미널 프롬프트에 `(.venv)`가 표시될 수 있습니다. 반드시 표시 문구만으로 판단하지 말고 다음처럼 Python 실행 위치와 SDK 설치 여부를 확인합니다.

```bash
python --version
python -m pip show openai
```

설치 완료 후 **실제 설치된 SDK 버전**을 `requirements.txt`에 기록합니다.

```text
openai==<교육장에서 설치·검증한 버전>
```

이 줄의 `<...>`는 그대로 설치 명령에 쓰는 값이 아니라 강사가 실제 버전 번호로 바꿀 자리표시자입니다. 인터넷/패키지 설치가 실패하면 이를 **환경 문제**로 기록하고, API 인증 문제와 구분합니다.

---

# 4. API Key를 안전하게 설정하기

Cloud API 사용을 위해서는 인증 정보가 필요합니다. `OPENAI_API_KEY`는 SDK가 사용할 수 있는 환경 변수 이름입니다.

## 4.1 잘못된 방식

```python
# 실제 수업에서 이렇게 작성하지 않습니다.
api_key = "sk-xxxxxxxxxxxxxxxx"
```

실제 Key를 소스 파일에 쓰고 Git 저장소에 올리거나, 과제를 제출하면서 함께 공유하면 다른 사람이 그 Key로 API를 사용할 위험이 있습니다. 위 문자열은 설명을 위한 가짜 값입니다.

## 4.2 현재 터미널 세션에 설정하기

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="<본인의 실제 API Key>"
```

macOS / Linux:

```bash
export OPENAI_API_KEY="<본인의 실제 API Key>"
```

위 명령의 자리표시자는 실제 값을 뜻하지만, **실제 Key를 강사에게 채팅이나 스크린샷으로 전송하지 않습니다.** 화면 공유 중이라면 명령 입력과 터미널 이력 노출에도 주의합니다. 환경 변수 설정은 현재 터미널 세션에 적용되므로, 다른 터미널을 열면 다시 설정해야 할 수 있습니다.

실제 Key 값을 출력하지 않고 설정 여부만 확인하려면 다음 Python 명령을 실행합니다.

```bash
python -c "import os; print('API Key 설정됨' if os.getenv('OPENAI_API_KEY') else 'API Key 없음')"
```

`API Key 설정됨`은 단지 환경 변수에 값이 있다는 뜻입니다. **Key가 유효하거나 API 호출이 성공한다는 증거는 아닙니다.**

## 4.3 모델 선택도 실행 환경에 맞추기

원본 예제에서 사용한 모델 ID는 `gpt-5`입니다. 다만 모델 ID와 사용 가능 여부는 시점·계정·프로젝트에 따라 달라질 수 있습니다. 이번 수정본은 모델을 바꾸어 적는 대신 **원본 모델을 기본 예시로 남기고 교육장에서 지정한 모델로 교체할 수 있게** 구성합니다.

선택 사항 — 환경 변수로 모델 ID 지정:

```powershell
# Windows PowerShell 예시
$env:OPENAI_MODEL="<교육장에서 사용 가능하다고 확인한 모델 ID>"
```

```bash
# macOS / Linux 예시
export OPENAI_MODEL="<교육장에서 사용 가능하다고 확인한 모델 ID>"
```

환경 변수를 설정하지 않으면 뒤의 코드는 원본 예시인 `gpt-5`를 사용합니다. 해당 모델에 접근 권한이 없다면 다른 사용 가능한 모델 ID를 **확인한 후** 지정해야 합니다. 모델 문자열을 임의로 추측하여 성공을 기대하지 않습니다.

---

# 5. 첫 API 호출 — `basic_call.py`

파일 `app/basic_call.py`를 만들고 다음 코드를 작성합니다.

```python
import os
from openai import OpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5")


def main() -> None:
    client = OpenAI()  # OPENAI_API_KEY 환경 변수 사용
    response = client.responses.create(
        model=MODEL_NAME,
        input="생성형 AI를 입문 개발자에게 두 문장으로 설명해줘.",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
```

실행:

```bash
python app/basic_call.py
```

## 5.1 요청이 처리되는 위치

| 코드 | 이 코드가 맡는 일 |
|---|---|
| `from openai import OpenAI` | Python SDK의 Client를 사용할 준비 |
| `OpenAI()` | 요청을 보낼 Client 객체 생성, 환경 변수의 Key 활용 |
| `model=MODEL_NAME` | 사용할 모델 ID 지정 |
| `input="..."` | 모델에 전달할 텍스트 입력 지정 |
| `client.responses.create(...)` | Responses API를 이용한 응답 생성 요청 |
| `response.output_text` | 응답에서 생성 텍스트를 편리하게 읽어 출력 |

`OpenAI()`를 호출했다고 곧바로 모델 추론이 발생하는 것은 아닙니다. **`client.responses.create(...)`에서 Cloud API에 요청을 보내고**, 서비스가 처리한 결과를 `response`로 받습니다. 학생 PC에는 SDK와 실행 코드가 있지만, 이 예제의 GPT 모델은 학생 PC에서 구동되지 않습니다.

## 5.2 실행 결과는 어떻게 판단할까?

실제 생성 문장은 모델과 실행 조건에 따라 달라지므로 답변 전문을 모범 출력으로 고정하지 않습니다. 성공했다면 다음을 확인합니다.

1. Python 프로세스가 오류 없이 종료되었습니다.
2. AI에 관한 한국어 응답이 출력되었습니다.
3. 대체로 ‘입문 개발자’와 ‘두 문장’이라는 지시가 반영되었습니다. 모델이 지시를 항상 완벽히 지킨다는 뜻은 아닙니다.

실행 전에 네트워크와 인증 정보가 준비되지 않았다면 여기까지의 결과는 **코드 작성 완료**이지 **API 호출 성공**이 아닙니다.

---

# 6. `Response` 객체와 생성된 문장 구분하기

첫 호출에서 `response`는 문자열 하나가 아니라 API 요청의 처리 결과를 표현하는 객체입니다. 응답에는 생성된 내용 외에도 요청 ID, 상태, 모델, 사용량 등 여러 정보가 포함될 수 있습니다.

`basic_call.py`의 마지막 출력 부분을 다음처럼 바꾸어 실행해봅니다.

```python
print("=== 생성된 텍스트 ===")
print(response.output_text)

print("=== 응답 식별자 ===")
print(response.id)

print("=== 상태 ===")
print(response.status)

print("=== 사용량 ===")
print(response.usage)
```

### 학생이 확인할 것

- `response.output_text`는 사용자에게 보여줄 **텍스트 내용**입니다.
- `response.id`와 `response.status`는 요청 결과를 확인하거나 문제를 추적할 때 도움이 됩니다.
- `response.usage`는 입력·출력 등의 Token 사용량을 확인할 때 참고합니다.
- 전체 `response` 객체를 `print(response)`로 확인할 수도 있지만 수업에서는 출력이 길 수 있으므로 필요한 필드를 먼저 읽습니다.

**응답 메타데이터와 입력·출력 내용에는 민감한 정보가 포함될 수 있습니다.** 실서비스 로그에 무조건 전체 객체를 남기지 말아야 하는 이유를 함께 설명합니다.

### 사용량의 의미

Token은 문자 수와 항상 일치하지 않습니다. 이번 시간에는 Token 분할 원리를 다시 강의하지 않고, **실제 API 응답에서 사용량이라는 측정값을 읽는 것**에 집중합니다. 사용량은 API 비용과 이용 제한을 이해하는 단서이지만, `usage` 값만으로 정확한 청구 금액을 임의 계산하지 않습니다. 요금 및 과금 정책은 별도 확인이 필요합니다.

---

# 7. 입력을 바꾸어 결과 비교하기

이제 `basic_call.py`의 `input` 문자열만 변경하며 실행합니다. 아래 세 입력은 원본 실습에 있던 예제입니다.

```text
① 생성형 AI를 설명해줘.

② 생성형 AI를 Python을 처음 배우는 학생에게
   두 문장으로 쉽게 설명해줘.

③ 생성형 AI와 일반적인 분류 모델의 차이를
   표가 아니라 세 개의 짧은 문장으로 설명해줘.
```

| 비교 요소 | 학생이 관찰할 내용 |
|---|---|
| 대상 | ‘처음 배우는 학생’이라는 조건이 설명 난이도에 어떤 영향을 주었는가? |
| 길이 | 두 문장·세 문장 조건을 지켰는가? |
| 형식 | 표를 사용하지 말라는 제약을 지켰는가? |
| 내용 | 사실관계에 문제가 있거나 앞선 강의와 어긋나는 내용은 없는가? |

**주의:** 단어 몇 개만 다른 응답을 얻었다고 좋은 프롬프트라고 판단하지 않습니다. 실제로 요청한 조건을 만족했는지가 관찰 기준입니다. Prompt Engineering 기법의 체계적인 비교는 Phase 2의 별도 학습에서 다룹니다.

---

# 8. `instructions`와 `input` 분리하기

원본에 소개된 Responses API의 두 입력 필드를 사용합니다.

- `instructions`: 응답 전반에 적용하고자 하는 지시입니다.
- `input`: 이번 요청에서 처리할 내용입니다.

`app/instruction_call.py`:

```python
import os
from openai import OpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5")
client = OpenAI()


def ask_ai(user_input: str) -> str:
    response = client.responses.create(
        model=MODEL_NAME,
        instructions=(
            "당신은 AI 입문자를 돕는 교육 조교입니다. "
            "전문 용어를 사용하면 바로 뒤에 쉬운 설명을 덧붙이세요. "
            "답변은 한국어로 간결하게 작성하세요."
        ),
        input=user_input,
    )
    return response.output_text


def main() -> None:
    print(ask_ai("Inference가 무엇인지 설명해줘."))


if __name__ == "__main__":
    main()
```

실행:

```bash
python app/instruction_call.py
```

## 8.1 왜 함수로 분리할까?

`main()`은 사용자 입력과 결과 출력에 집중하고, `ask_ai()`는 AI 요청을 만드는 코드를 담당합니다.

```text
main() — 입력과 출력
   ↓
ask_ai() — 모델·지시·SDK 호출
   ↓
Cloud API — 모델 추론
```

이렇게 나누면 `ask_ai("Feature가 무엇인가?")`, `ask_ai("Inference가 무엇인가?")`처럼 다른 입력에 같은 호출 구조를 재사용할 수 있습니다. 다음 교시에서는 이 함수를 FastAPI와 연결할 수 있는 Service의 출발점으로 삼습니다.

## 8.2 실습 질문

1. `input`을 바꾸었을 때 어떤 부분이 변하는가?
2. `instructions`의 ‘쉬운 설명’ 조건을 삭제하면 응답은 어떻게 달라질 수 있는가?
3. `ask_ai()`를 함수로 분리하지 않고 여러 파일에 같은 API 호출을 복사하면 어떤 유지보수 문제가 생기는가?

`instructions`에 무엇을 작성하면 반드시 지켜진다는 뜻은 아닙니다. 입력 구조와 응답 품질을 구분하여 관찰합니다.

---

# 9. API 호출 전에 사용자 입력 검증하기

모델에 물어보기 전에 **명확한 규칙으로 검사할 수 있는 것**은 우리 프로그램에서 검사합니다. 원본의 ‘공백 입력 금지’ 실습을 여기에서 구현합니다.

```python
def validate_input(user_input: str) -> str:
    cleaned = user_input.strip()
    if not cleaned:
        raise ValueError("입력 내용이 비어 있습니다.")
    return cleaned
```

동작 예:

```python
validate_input("  Inference란?  ")  # "Inference란?"
validate_input("   ")              # ValueError
```

이 검사는 **API를 호출하지 않아도** 시험할 수 있습니다. 유효하지 않은 입력에 비용을 들여 API 요청을 보내지 않는 것도 Application 설계의 중요한 책임입니다.

실무에서는 서비스 요구사항에 따라 입력 길이, 사용 권한, 허용된 데이터 종류 등도 확인할 수 있습니다. 다만 이번 교시에는 입력 검증의 첫 번째 기준인 **공백 여부**에 집중하고, 복잡한 Schema 검증은 8교시에서 구현합니다.

---

# 10. 오류를 구분해서 처리하기 — `error_handling.py`

## 10.1 실패는 한 가지 이유로 발생하지 않는다

다음 오류는 전부 ‘AI가 고장 났다’로 묶으면 안 됩니다.

| 실패 사례 | 문제가 발생한 위치 | 학생의 첫 확인 행동 |
|---|---|---|
| 공백 입력 | Application 입력 검증 | `strip()` 검사와 오류 메시지 확인 |
| Key 미설정·유효하지 않은 Key | 인증 설정 또는 Provider 인증 | 환경 변수 존재 여부·인증 상태 확인, Key 자체는 출력하지 않음 |
| 네트워크 끊김 | 네트워크 통신 | 인터넷 연결·접근 가능 여부 확인 |
| 허용되지 않는 모델 ID | 요청 또는 계정의 모델 권한 | 교육장에서 검증한 ID·계정 권한 확인 |
| 호출 제한 | Provider 이용 제한 | 정책·요청 빈도 확인; 무제한 재시도 금지 |
| 서버 오류·응답 지연 | Provider·네트워크·시간 초과 | 요청 상태를 기록하고 적절한 재시도/사용자 안내 판단 |

## 10.2 원본 예제의 기본 오류 처리 패턴

이번 수업에서는 먼저 Python의 `try`/`except`로 오류를 사용자에게 전달하는 경계를 학습합니다. 다음 코드는 교육용 단순화 예제입니다.

`app/error_handling.py`:

```python
import os
from openai import OpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5")


def validate_input(user_input: str) -> str:
    cleaned = user_input.strip()
    if not cleaned:
        raise ValueError("입력 내용이 비어 있습니다.")
    return cleaned


def ask_ai(user_input: str) -> str:
    cleaned = validate_input(user_input)

    try:
        client = OpenAI()  # Client 초기화 실패도 같은 경계에서 처리
        response = client.responses.create(
            model=MODEL_NAME,
            input=cleaned,
        )
    except Exception as error:
        # 교육용 기본 패턴: 실제 서비스에서는 SDK 오류 유형별로 분기합니다.
        raise RuntimeError("AI API 호출에 실패했습니다.") from error

    return response.output_text


def main() -> None:
    try:
        result = ask_ai("Cloud AI와 Local AI의 차이를 설명해줘.")
        print(result)
    except (ValueError, RuntimeError) as error:
        print(f"오류: {error}")


if __name__ == "__main__":
    main()
```

실행:

```bash
python app/error_handling.py
```

이 코드는 **빈 입력을 API 호출 이전에 거절**하고, SDK 호출에서 예외가 발생하면 호출 경계에서 `RuntimeError`로 바꾸어 전달합니다.

### 코드 해설

- `validate_input()`에서 실패하면 `ValueError`를 발생시킵니다. 이 경우에는 원격 요청을 만들지 않습니다.
- API 호출 중 오류가 나면 `except Exception`에서 잡습니다.
- `raise RuntimeError(...) from error`는 원래 예외와의 연결을 유지합니다. 학습 중 원인을 추적할 수 있지만, 사용자 화면에 내부 오류나 인증 정보를 그대로 노출해서는 안 됩니다.
- `main()`의 `except`는 사용자에게 간단한 오류 메시지를 출력합니다.

`OpenAI()` Client를 `try` 안에서 만들었기 때문에 Key 미설정 등 **Client 초기화 과정의 예외도 이 함수에서 처리**할 수 있습니다. 다만 패키지 설치 문제, SDK 가져오기(`import`) 오류, 모든 종류의 서비스 예외를 개별적으로 구분하는 완성된 코드는 아닙니다. 실제 서비스에서는 SDK가 제공하는 오류 유형, HTTP 상태, 시간 초과, Retry 가능 여부를 확인해 분리해야 합니다. 이 예제만으로 실서비스 오류 처리 검증 완료라고 판단하지 않습니다.

---

# 11. 일부러 실패시켜 보기 — 문제 위치 찾기

실습에서는 **먼저 안전하고 재현 가능한 실패**부터 확인합니다.

## 실습 A. 빈 입력

`main()` 안의 `ask_ai(...)` 입력을 공백으로 바꿉니다.

```python
result = ask_ai("   ")
```

예상 결과:

```text
오류: 입력 내용이 비어 있습니다.
```

이 실패는 **Application의 입력 검증 단계**에서 발생하며 실제 Key가 없어도 검증할 수 있는 동작입니다. API 요청이나 Token 사용량은 발생하지 않아야 합니다.

## 실습 B. 모델 ID 오류

강사가 허용한 환경에서만 `OPENAI_MODEL`을 **실제로 존재하지 않는 모델 이름**으로 바꾸어 호출합니다. 어떤 오류가 나오는지 계정·SDK에 따라 다를 수 있으므로 정확한 오류 문자열을 미리 단정하지 않습니다.

## 실습 C. Key 또는 네트워크 오류

강사가 통제할 수 있는 환경에서만 안전하게 시연합니다. 실습 중 실제 Key를 공개·복사·제출하거나 학생 전체의 네트워크를 중단시키지 않습니다.

| 활동 | 예상되는 분류 | 주의 |
|---|---|---|
| 공백 입력 | 입력 검증 | 로컬에서 확실히 재현 가능 |
| 잘못된 모델 이름 | 모델 선택·API 요청 | Provider 호출이 필요하고 오류 메시지는 환경 의존적 |
| Key 미설정 | 인증 환경 | Client 생성 단계에서 실패할 수 있음 |
| 인터넷 연결 불가 | 네트워크 | 실제 호출을 수행하는 환경에서만 관찰 가능 |

학생은 오류 메시지를 **그대로 암기하지 말고 어느 계층에서 실패했는지** 설명합니다.

---

# 12. Usage와 출력 변화를 관찰하기

`basic_call.py` 또는 `instruction_call.py`의 응답 처리 부분에서 다음을 출력해봅니다.

```python
print(response.output_text)
print(response.usage)
```

학생이 관찰할 항목:

- 입력을 더 자세히 작성하면 사용량이 어떻게 달라졌는가?
- 응답을 짧게 해 달라고 지시했을 때 실제 결과와 사용량이 어떻게 달라졌는가?
- 같은 입력을 여러 번 실행했을 때 출력 문장이 매번 완전히 같은가?

생성형 모델은 설정과 실행 조건에 따라 서로 다른 표현을 만들 수 있습니다. 여기에서는 5교시의 확률적 생성 원리를 다시 강의하기보다, **API 실습에서 관찰한 결과를 기록하는 방법**에 집중합니다.

| 실행 | 입력 변경 내용 | 요구한 형식 충족? | 출력에서 확인한 차이 | Usage 확인 여부 |
|---|---|---|---|---|
| 1 | 기본 입력 | 학생 기록 | 학생 기록 | 학생 기록 |
| 2 | 대상 독자 지정 | 학생 기록 | 학생 기록 | 학생 기록 |
| 3 | 문장 수 지정 | 학생 기록 | 학생 기록 | 학생 기록 |

**수업 운영 주의:** 반복 호출은 실제 API 사용량을 늘릴 수 있습니다. 호출 횟수와 비용 한도는 강사가 교육장 환경에 맞게 정합니다. 실패한 요청이라도 요청 종류 및 정책에 따라 사용량·요금 처리 방식이 달라질 수 있으므로 일률적으로 단정하지 않습니다.

---

# 13. 단계별 학생 실습

## 활동 1. 같은 개념을 서로 다른 독자에게 설명하기

원본 과제의 주제는 `Machine Learning`입니다. 같은 `ask_ai()` 함수를 사용하고 사용자 입력만 바꿉니다.

```python
print(ask_ai("Machine Learning을 초등학생에게 설명해줘."))
print(ask_ai("Machine Learning을 고등학생에게 설명해줘."))
print(ask_ai("Machine Learning을 Python 개발자에게 설명해줘."))
print(ask_ai("Machine Learning을 기업 관리자에게 설명해줘."))
```

**실습 결과에 적을 것:** 네 응답의 문장 길이만 비교하는 것이 아니라, 사용한 용어·설명 수준·독자에게 필요한 정보를 비교합니다. 각 호출은 실제 API 사용량을 발생시킬 수 있으므로 강사가 지정한 횟수만큼 실행합니다.

## 활동 2. 출력 제약을 바꾸어보기

처음 입력:

```text
AI와 Machine Learning의 차이를 설명해줘.
```

수정 입력:

```text
AI와 Machine Learning의 차이를 각각 한 문장으로 설명하고,
마지막에 둘의 관계를 한 문장으로 정리해줘.
```

**완료 기준:** 응답이 ‘각각 한 문장 + 관계 한 문장’이라는 조건을 얼마나 충족했는지 설명합니다. 단순히 답변이 다르게 나왔는지는 합격 기준이 아닙니다.

## 활동 3. 입력 검증 완성하기

원본 과제의 미완성 함수를 다음 요건에 맞게 작성합니다.

```python
def validate_input(user_input: str) -> str:
    cleaned = user_input.strip()
    if not cleaned:
        raise ValueError("입력 내용이 비어 있습니다.")
    if len(cleaned) < 2:
        raise ValueError("입력은 최소 두 글자 이상이어야 합니다.")
    return cleaned
```

이 코드를 앞의 `error_handling.py`에 적용하면 `ask_ai()`는 **검증된 문자열만** API로 보낼 수 있습니다.

직접 확인할 입력:

| 입력 | 기대 결과 | API 호출 여부 |
|---|---|---|
| `""` | 오류 | 없음 |
| `"   "` | 오류 | 없음 |
| `"A"` | 오류 | 없음 |
| `"AI"` | 통과 | 이후 API 호출 가능 |
| `"  Embedding  "` | 앞뒤 공백 제거 후 통과 | 이후 API 호출 가능 |

**설명:** 최소 두 글자 규칙은 모든 AI 서비스의 보편 규칙이 아니라 **이 과제를 위해 정한 예시 정책**입니다. 실제 요구사항에 따라 달라질 수 있습니다.

---

# 14. 응용 과제 — `ai_explainer.py` 만들기

이번 교시의 작은 완성 프로그램입니다. 사용자가 `Embedding` 같은 AI 용어를 입력하면 Cloud API에 설명을 요청하고 **자연어 형식**으로 결과를 출력합니다. JSON Schema와 FastAPI는 아직 사용하지 않습니다. 그것이 8교시의 학습 목표이기 때문입니다.

## 14.1 요구사항

1. 사용자에게 AI 용어를 입력받습니다.
2. 빈 입력과 공백뿐인 입력은 거부합니다.
3. 모델 호출 코드를 함수로 분리합니다.
4. 설명에 `용어`, `한 줄 정의`, `쉬운 설명`, `실무에서 만나는 위치`가 들어가도록 요청합니다.
5. AI 호출 오류가 발생했을 때 프로그램이 오류를 안내하도록 합니다.
6. API Key는 코드에 직접 기록하지 않습니다.

### 예시 입력

```text
Embedding
```

### 기대하는 출력의 구성

```text
용어: Embedding
한 줄 정의: (모델이 생성한 설명)
쉬운 설명: (모델이 생성한 설명)
실무에서 만나는 위치: (모델이 생성한 설명)
```

표현과 실제 문장은 호출마다 달라질 수 있습니다. 이 교시는 **요청한 네 항목이 생성되는지 관찰**하는 단계입니다. JSON으로 강제하고 구조를 기계적으로 검증하는 일은 8교시에서 수행합니다.

## 14.2 참고 구현

`app/ai_explainer.py`:

```python
import os
from openai import OpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5")


def explain_term(term: str) -> str:
    cleaned = term.strip()
    if not cleaned:
        raise ValueError("AI 용어를 입력해 주세요.")

    try:
        client = OpenAI()
        response = client.responses.create(
            model=MODEL_NAME,
            instructions=(
                "당신은 AI 입문 교육을 돕는 조교입니다. "
                "한국어로 설명하되 다음 항목을 포함하세요: "
                "용어, 한 줄 정의, 쉬운 설명, 실무에서 만나는 위치."
            ),
            input=cleaned,
        )
    except Exception as error:
        raise RuntimeError("AI 설명 생성 요청에 실패했습니다.") from error

    return response.output_text


def main() -> None:
    term = input("설명할 AI 용어를 입력하세요: ")
    try:
        result = explain_term(term)
        print(result)
    except (ValueError, RuntimeError) as error:
        print(f"오류: {error}")


if __name__ == "__main__":
    main()
```

실행:

```bash
python app/ai_explainer.py
```

이 코드는 **원본 응용 과제의 요구사항을 한 파일로 실습 가능하게 정리한 참고 구현**입니다. 입력 검증이 Client 생성보다 앞에 있고, SDK Client 생성 및 원격 호출 실패는 하나의 교육용 오류 메시지로 바꾸어 전달합니다. 다만 API 오류 유형을 세분화하거나, AI 응답에 네 항목이 반드시 있는지 자동 검증하는 완성된 코드는 아닙니다. 구조화 출력과 Schema 검증은 다음 교시로 이어집니다.

### 강사용 확인 질문

- `term.strip()`이 없다면 공백 입력은 어디까지 전달될까요?
- `explain_term()`의 책임은 무엇이고 `main()`의 책임은 무엇인가요?
- 네 항목이 빠진 응답이 돌아온다면 현재 코드는 이를 자동으로 탐지할 수 있나요?
- 왜 다음 교시에서 Pydantic 같은 검증 도구가 필요할까요?

---

# 15. 코드 없이도 판단해야 하는 보안·운영 기준

AI API 실습이 성공했다고 곧바로 운영 가능한 서비스가 된 것은 아닙니다. 이 교시에서는 최소한 다음 항목의 **이유와 책임 위치**를 이해합니다.

| 항목 | 왜 필요한가? | 이번 교시에서 다루는 수준 |
|---|---|---|
| Secret Management | Key 유출 방지 | 환경 변수 사용과 Source Code 비노출 |
| Input Validation | 잘못된 입력의 불필요한 호출 방지 | 공백·최소 길이 검사 |
| Error Handling | 실패를 사용자에게 구분해 전달 | 입력 오류와 원격 호출 오류 구분 |
| Timeout / Retry | 응답 지연과 일시적 실패에 대응 | 필요성 설명만 수행; 자동 재시도 구현하지 않음 |
| Rate Limit / Cost | 무제한 호출에 따른 차단·비용 위험 방지 | Usage 읽기 및 반복 호출 횟수 관리 |
| Logging | 문제 원인 추적 | 요청 상태 관찰; Key·민감정보는 기록 금지 |
| Model Configuration | 모델 교체·환경 차이 대응 | `OPENAI_MODEL` 또는 상수로 관리 |
| Fallback | Provider 장애 시 대체 처리 | 개념 소개만 수행 |
| Output Validation | 예상하지 못한 출력 차단 | 필요성 관찰; 구조화 검증은 8교시 |

웹 브라우저의 클라이언트 코드에 Provider API Key를 넣지 않습니다. 다음 교시에는 FastAPI가 인증 정보를 관리하며 AI Provider API와 통신하는 Backend의 역할을 맡습니다.

---

# 16. 실습 확인표 — 학생 제출 기준

실습이 끝나면 단순히 코드가 있는지만 확인하지 않습니다.

- [ ] 가상환경을 만들고 SDK 설치 상태를 확인했다.
- [ ] API Key를 Source Code에 작성하지 않았고, 환경 변수 설정 여부를 확인했다.
- [ ] 교육장에서 확인된 모델 ID를 사용했다.
- [ ] `basic_call.py`로 API 요청을 보냈고 결과 또는 실패 원인을 기록했다.
- [ ] `response.output_text`와 `response`의 메타데이터를 구분했다.
- [ ] `response.usage`를 확인했거나, 확인하지 못한 이유를 기록했다.
- [ ] `instructions`와 `input`의 역할을 코드에서 구분했다.
- [ ] `ask_ai()`로 호출을 함수화했다.
- [ ] 공백 입력이 원격 호출 이전에 거절되는 것을 확인했다.
- [ ] 오류를 하나 이상 재현하고 발생 위치를 설명했다.
- [ ] 입력 변경 활동에서 독자·길이·형식 요구사항의 준수 여부를 비교했다.
- [ ] `ai_explainer.py`를 작성하고 네 개의 출력 항목을 검토했다.

**실행 환경이 없는 학생:** 코드 작성 및 로컬 입력 검증을 완료할 수 있지만, 실제 API 응답·Usage·원격 오류 실습은 **미실행**으로 명확하게 기록합니다. 실습 목적을 이해한 것과 라이브 API 호출을 성공한 것은 서로 다른 성취입니다.

---

# 17. 이번 교시 핵심 정리

```text
Python Application
  ├── 사용자 입력 검증
  ├── 모델 이름과 요청 내용 구성
  ├── OpenAI SDK를 통한 요청
  │     ↓
  │   Cloud API → 모델 Inference
  │     ↓
  ├── Response 수신
  ├── output_text / usage 확인
  ├── 오류 처리
  └── 사용자에게 결과 제공
```

반드시 기억해야 할 내용은 네 가지입니다.

1. **SDK는 Cloud API와 통신하는 도구이며 모델 자체가 아닙니다.**
2. **API Key는 소스에 넣지 않고 안전하게 관리합니다.**
3. **AI 호출 전에 검증할 수 있는 입력은 Application에서 먼저 처리합니다.**
4. **응답은 그대로 맹신하지 않고 내용·형식·실패 가능성을 확인합니다.**

모델 학습이나 API 내부 동작 원리를 다시 설명하는 시간이 아니라, **Cloud 모델을 호출하는 프로그램의 최소 책임을 직접 구현한 시간**입니다.

---

# 18. 다음 교시 연결 — FastAPI와 Structured Output

이번 교시에는 터미널에서 실행하는 Python 프로그램을 만들었습니다.

```text
현재: Python CLI → OpenAI SDK → Cloud API → Text 출력

다음: Client → FastAPI → AI Service → Cloud API
                                   ↓
                           Structured Output
                                   ↓
                           Pydantic Validation
                                   ↓
                              JSON Response
```

8교시에서는 `ask_ai()`처럼 분리한 호출 코드를 **Web API의 Service 계층**으로 옮기고, 지금은 사람이 읽으며 확인한 응답 항목을 **프로그램이 검증할 수 있는 데이터**로 다룹니다.

---

# 참고자료 및 확인 필요 사항

원본 교육과정에 명시된 참고 대상으로만 기록합니다. 이 수정본에서 외부 사이트를 열어 현재 API 사양을 검증하지는 않았습니다.

- OpenAI API 공식 문서 — Responses API
- OpenAI API 공식 문서 — Model Guide
- OpenAI Python SDK 공식 자료
- Python 공식 문서 — Virtual Environments
- 같은 교육과정의 8교시: FastAPI와 AI 통합·Structured Output 실습

> **수업 전 추가 검증 필요:** 실제 사용 가능한 모델 ID, OpenAI Python SDK 버전, API Key 권한, 계정 과금·사용량 정책, 네트워크, 실제 Responses API 호출·응답, 학습자 운영체제별 실행. 확인하지 않은 항목을 ‘실행 검증 완료’로 표시하지 않습니다.
