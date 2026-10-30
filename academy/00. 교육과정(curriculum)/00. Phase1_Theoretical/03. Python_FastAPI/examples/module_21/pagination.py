from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI()
ITEMS = [f"doc-{number}" for number in range(1, 21)]

@app.get("/documents")
def documents(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
) -> list[str]:
    return ITEMS[offset:offset + limit]
