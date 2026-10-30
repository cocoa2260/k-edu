def normalize_questions(questions: list[str]) -> list[str]:
    return [question.strip() for question in questions if question.strip()]

raw: list[str] = ["  FastAPI? ", "", " Pydantic? "]
normalized = normalize_questions(raw)
print(normalized)
