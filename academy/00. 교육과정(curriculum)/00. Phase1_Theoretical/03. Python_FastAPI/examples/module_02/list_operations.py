models = ["model-a", "model-b"]
models.append("model-c")
models[0] = "model-a-v2"
removed = models.pop(1)

for index, model in enumerate(models, start=1):
    print(index, model)
print("removed:", removed)
