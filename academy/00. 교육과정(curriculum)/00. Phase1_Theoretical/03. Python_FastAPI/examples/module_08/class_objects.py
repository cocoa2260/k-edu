class Document:
    def __init__(self, document_id: str, text: str):
        self.document_id = document_id
        self.text = text

    def word_count(self) -> int:
        return len(self.text.split())

first = Document("doc-1", "FastAPI uses type hints")
second = Document("doc-2", "Pydantic validates data")
print(first.document_id, first.word_count())
print(second.document_id, second.word_count())
