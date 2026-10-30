from fastapi import FastAPI

app = FastAPI()

@app.get("/documents")
def documents() -> list[dict[str, str]]:
    return [{"id": "doc-1"}]

@app.post("/chat")
def chat(question: str) -> dict[str, str]:
    return {"answer": question}
