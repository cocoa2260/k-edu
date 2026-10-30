from dataclasses import dataclass, field

@dataclass(frozen=True)
class GenerationResult:
    answer: str
    model: str
    sources: tuple[str, ...] = field(default_factory=tuple)

result = GenerationResult("완료", "fake-model", ("doc-1",))
print(result)
