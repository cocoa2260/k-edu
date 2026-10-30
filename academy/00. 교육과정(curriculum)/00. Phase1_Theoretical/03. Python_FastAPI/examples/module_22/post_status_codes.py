from fastapi import FastAPI, status

app = FastAPI()

@app.post("/prompts", status_code=status.HTTP_201_CREATED)
def create_prompt(name: str) -> dict[str, str]:
    return {"name": name, "status": "created"}

@app.post("/summaries", status_code=status.HTTP_202_ACCEPTED)
def request_summary() -> dict[str, str]:
    return {"status": "processing"}
