from fastapi import FastAPI

app = FastAPI()

@app.get("/documents/{document_id}")
def get_document(document_id: int) -> dict[str, int]:
    return {"document_id": document_id}
