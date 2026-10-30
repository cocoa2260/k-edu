from fastapi import FastAPI

app = FastAPI()

@app.get("/documents/latest")
def latest() -> dict[str, str]:
    return {"id": "latest"}

@app.get("/documents/{document_id}")
def by_id(document_id: str) -> dict[str, str]:
    return {"id": document_id}
