from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class JobCreate(BaseModel):
    question: str

@app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
def create_job(request: JobCreate) -> dict[str, str]:
    return {"job_id": "job-1", "status": "queued", "question": request.question}
