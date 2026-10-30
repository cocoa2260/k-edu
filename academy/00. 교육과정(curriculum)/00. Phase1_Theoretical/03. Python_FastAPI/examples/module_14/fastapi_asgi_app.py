from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

# uvicorn fastapi_asgi_app:app --reload
#         module name -------^  ^--- application object
