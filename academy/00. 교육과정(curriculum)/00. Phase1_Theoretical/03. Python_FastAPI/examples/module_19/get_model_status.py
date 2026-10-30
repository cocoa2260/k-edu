from fastapi import FastAPI

app = FastAPI()

@app.get("/providers/{provider_name}/status")
def provider_status(provider_name: str) -> dict[str, object]:
    return {"provider": provider_name, "available": True}
