from typing import Annotated, Literal
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/jobs")
def list_jobs(
    status: Literal["queued", "done"] | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, object]:
    return {"status": status, "limit": limit}
