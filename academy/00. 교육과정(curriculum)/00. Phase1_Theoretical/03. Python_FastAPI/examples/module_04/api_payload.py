question = "Decorator란?"
payload = {
    "question": question.strip(),
    "options": {"temperature": 0.2, "stream": False},
    "metadata": {"source": "practice"},
}

required = {"question", "options"}
print("valid:", required.issubset(payload))
print(payload)
