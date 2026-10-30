class DocumentService:
    def __init__(self):
        self._documents: list[str] = []

    def add(self, text: str) -> None:
        self._documents.append(text)

    def count(self) -> int:
        return len(self._documents)

service_a = DocumentService()
service_b = DocumentService()
service_a.add("A 문서")
print(service_a.count(), service_b.count())
