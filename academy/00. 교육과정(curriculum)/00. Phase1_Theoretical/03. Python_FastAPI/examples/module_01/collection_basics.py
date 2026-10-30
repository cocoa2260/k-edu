values = ["chat", "ocr", "embedding"]
fixed_size = (1536, "float")
unique_models = {"gpt", "embedding"}
request = {"question": "Python이란?", "top_k": 3}

print(values)
print(fixed_size)
print(unique_models)
print(request)
