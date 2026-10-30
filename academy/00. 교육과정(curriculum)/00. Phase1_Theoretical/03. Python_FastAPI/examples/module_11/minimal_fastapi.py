from fastapi import FastAPI

app = FastAPI(title="Minimal API")

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastAPI is running"}

# 실행: uvicorn minimal_fastapi:app --reload
