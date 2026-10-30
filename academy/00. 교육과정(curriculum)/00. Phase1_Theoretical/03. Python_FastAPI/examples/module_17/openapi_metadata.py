from fastapi import FastAPI

app = FastAPI(
    title="AI Backend API",
    description="Swagger 실습용 API",
    version="1.0.0",
)

@app.get("/models", tags=["models"], summary="모델 목록 조회")
def list_models() -> list[str]:
    return ["fake-model"]
