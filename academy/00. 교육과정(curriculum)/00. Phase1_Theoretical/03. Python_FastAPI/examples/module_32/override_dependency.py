from fastapi import Depends, FastAPI

app = FastAPI()

def get_provider() -> str:
    return "real"

@app.get("/provider")
def provider(name: str = Depends(get_provider)) -> dict[str, str]:
    return {"provider": name}

def fake_provider() -> str:
    return "fake"

app.dependency_overrides[get_provider] = fake_provider
