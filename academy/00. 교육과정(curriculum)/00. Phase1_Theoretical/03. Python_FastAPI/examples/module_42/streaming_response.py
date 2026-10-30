import asyncio
import json
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def events() -> AsyncIterator[str]:
    for token in ["Fast", "API", " stream"]:
        await asyncio.sleep(0.05)
        yield json.dumps({"type": "token", "data": token}) + "\n"
    yield json.dumps({"type": "done"}) + "\n"

@app.get("/stream")
def stream() -> StreamingResponse:
    return StreamingResponse(events(), media_type="application/x-ndjson")
