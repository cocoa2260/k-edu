import asyncio

async def generate(question: str) -> str:
    await asyncio.sleep(0.1)
    return f"answer:{question}"

async def main() -> None:
    results = await asyncio.gather(
        generate("Q1"),
        generate("Q2"),
        generate("Q3"),
    )
    print(results)

asyncio.run(main())
