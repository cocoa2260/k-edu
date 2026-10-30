messages: list[dict[str, str]] = []
messages.append({"role": "user", "content": "안녕하세요"})
messages.append({"role": "assistant", "content": "무엇을 도와드릴까요?"})

print("count:", len(messages))
print("last:", messages[-1])
