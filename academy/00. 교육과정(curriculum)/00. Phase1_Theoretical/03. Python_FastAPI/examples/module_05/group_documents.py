documents = [
    {"id": 1, "status": "ready"},
    {"id": 2, "status": "processing"},
    {"id": 3, "status": "ready"},
]
grouped: dict[str, list[int]] = {}
for document in documents:
    grouped.setdefault(document["status"], []).append(document["id"])

print(grouped)
