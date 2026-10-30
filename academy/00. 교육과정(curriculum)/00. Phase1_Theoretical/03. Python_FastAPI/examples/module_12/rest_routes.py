from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class DocumentCreate(BaseModel):
    title: str

@app.post("/documents", status_code=status.HTTP_201_CREATED)
def create_document(request: DocumentCreate) -> dict[str, object]:
    return {"id": 1, "title": request.title}

@app.get("/documents/{document_id}")
def get_document(document_id: int) -> dict[str, object]:
    return {"id": document_id, "title": "sample"}
