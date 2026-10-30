request = {
    "question": "FastAPI의 장점은?",
    "options": {"top_k": 2, "language": "ko"},
}
search_results = [
    {"document_id": "doc-1", "score": 0.92},
    {"document_id": "doc-2", "score": 0.85},
]

print(request["question"])
print(search_results[0]["document_id"])
