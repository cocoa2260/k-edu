import asyncio
from time import perf_counter

async def fetch(name: str) -> str:
    await asyncio.sleep(0.1)
    return name

async def main() -> None:
    started = perf_counter()
    first = await fetch("answer")
    second = await fetch("documents")
    print(first, second, f"{perf_counter() - started:.3f}s")

asyncio.run(main())
