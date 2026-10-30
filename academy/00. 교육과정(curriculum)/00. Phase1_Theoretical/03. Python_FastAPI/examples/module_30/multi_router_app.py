from fastapi import APIRouter, FastAPI

chat_router = APIRouter(prefix="/chat")
health_router = APIRouter(prefix="/health")

@chat_router.get("")
def chat_status() -> dict[str, str]:
    return {"status": "ready"}

@health_router.get("")
def health() -> dict[str, str]:
    return {"status": "ok"}

app = FastAPI()
app.include_router(chat_router)
app.include_router(health_router)
