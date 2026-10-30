from typing import Annotated
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/jobs/{job_id}")
def get_job(job_id: Annotated[int, Path(ge=1)]) -> dict[str, int]:
    return {"job_id": job_id}
