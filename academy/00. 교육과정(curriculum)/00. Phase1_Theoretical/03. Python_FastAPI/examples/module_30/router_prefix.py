from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("")
def list_documents() -> list[str]:
    return ["doc-1"]

app = FastAPI()
app.include_router(router)
