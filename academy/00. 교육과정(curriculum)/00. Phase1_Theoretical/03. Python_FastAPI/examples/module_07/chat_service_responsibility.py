class ChatService:
    def answer(self, question: str) -> dict[str, str]:
        normalized = question.strip()
        if not normalized:
            raise ValueError("질문을 입력하세요.")
        return {"question": normalized, "answer": f"echo: {normalized}"}

service = ChatService()
print(service.answer("  FastAPI란?  "))
