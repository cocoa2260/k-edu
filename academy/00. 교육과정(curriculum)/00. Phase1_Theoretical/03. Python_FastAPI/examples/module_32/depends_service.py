from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello, {name}"

def get_service() -> GreetingService:
    return GreetingService()

@app.get("/greet/{name}")
def greet(name: str, service: Annotated[GreetingService, Depends(get_service)]) -> dict[str, str]:
    return {"message": service.greet(name)}
