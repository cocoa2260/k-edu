class AIClient:
    def provider_name(self) -> str:
        return "unknown"

class FakeAIClient(AIClient):
    def generate(self, prompt: str) -> str:
        return f"fake: {prompt}"

client = FakeAIClient()
print(client.provider_name())
print(client.generate("hello"))
