from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    user_id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
def user(user_id: int) -> dict[str, object]:
    return {"user_id": user_id, "name": "Kim", "password_hash": "secret"}
