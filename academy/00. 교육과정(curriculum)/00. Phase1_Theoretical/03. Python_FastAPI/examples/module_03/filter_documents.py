documents = [
    {"id": "a", "score": 0.93, "text": "FastAPI"},
    {"id": "b", "score": 0.61, "text": "Flask"},
    {"id": "c", "score": 0.88, "text": "Pydantic"},
]
response = [
    {"document_id": item["id"], "text": item["text"]}
    for item in documents
    if item["score"] >= 0.8
]
print(response)
