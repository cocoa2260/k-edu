class RecordingClient:
    def __init__(self):
        self.last_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "fixed answer"

class ChatService:
    def __init__(self, client: RecordingClient):
        self.client = client

    def chat(self, question: str) -> str:
        return self.client.generate(f"질문: {question}")

client = RecordingClient()
assert ChatService(client).chat("test") == "fixed answer"
assert client.last_prompt == "질문: test"
print("service test passed")
