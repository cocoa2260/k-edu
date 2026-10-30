import asyncio
from collections.abc import AsyncIterator

async def stream_tokens() -> AsyncIterator[str]:
    for token in ["Fast", "API", " streaming"]:
        await asyncio.sleep(0.05)
        yield token

async def main() -> None:
    async for token in stream_tokens():
        print(token, end="", flush=True)
    print()

asyncio.run(main())
