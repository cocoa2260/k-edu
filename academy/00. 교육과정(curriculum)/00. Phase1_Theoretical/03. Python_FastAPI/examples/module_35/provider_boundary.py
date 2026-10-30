from dataclasses import dataclass

@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str

class FakeProviderSDK:
    def create(self, prompt: str) -> dict[str, str]:
        return {"output_text": prompt.upper(), "model_id": "fake-v1"}

def generate(prompt: str) -> GenerationResult:
    raw = FakeProviderSDK().create(prompt)
    return GenerationResult(text=raw["output_text"], model=raw["model_id"])

print(generate("hello"))
