from pydantic import BaseModel

class Document(BaseModel):
    document_id: int
    title: str

payload = {"document_id": "10", "title": "FastAPI"}
document = Document.model_validate(payload)
print(document)
print(type(document.document_id))
