from dataclasses import dataclass

@dataclass(frozen=True)
class Prompt:
    instructions: str
    input_text: str

def build_summary_prompt(text: str, language: str) -> Prompt:
    return Prompt(
        instructions=f"{language}로 세 문장 이내로 요약하세요.",
        input_text=text.strip(),
    )

print(build_summary_prompt("FastAPI 문서", "한국어"))
