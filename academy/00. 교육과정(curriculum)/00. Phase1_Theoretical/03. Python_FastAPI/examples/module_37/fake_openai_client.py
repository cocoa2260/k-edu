import asyncio

class FakeOpenAIClient:
    async def generate(self, instructions: str, input_text: str) -> str:
        await asyncio.sleep(0.05)
        return f"[{instructions}] {input_text.upper()}"

async def main() -> None:
    client = FakeOpenAIClient()
    print(await client.generate("짧게 답하세요", "FastAPI란?"))

asyncio.run(main())
