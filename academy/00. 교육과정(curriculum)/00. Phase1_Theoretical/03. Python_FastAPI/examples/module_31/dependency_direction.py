from typing import Protocol

class Translator(Protocol):
    def translate(self, text: str) -> str: ...

class FakeTranslator:
    def translate(self, text: str) -> str:
        return f"translated:{text}"

def translate_use_case(text: str, translator: Translator) -> str:
    return translator.translate(text)

print(translate_use_case("hello", FakeTranslator()))
