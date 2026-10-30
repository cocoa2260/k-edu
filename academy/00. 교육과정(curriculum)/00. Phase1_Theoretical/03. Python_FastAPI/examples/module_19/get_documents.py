from fastapi import FastAPI

app = FastAPI()

@app.get("/documents")
def list_documents() -> list[dict[str, object]]:
    return [
        {"id": 1, "title": "FastAPI"},
        {"id": 2, "title": "Pydantic"},
    ]
