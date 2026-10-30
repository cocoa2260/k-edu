from dataclasses import dataclass

@dataclass
class ChatMessage:
    role: str
    content: str

first = ChatMessage("user", "hello")
second = ChatMessage("user", "hello")
print(first)
print("equal:", first == second)
