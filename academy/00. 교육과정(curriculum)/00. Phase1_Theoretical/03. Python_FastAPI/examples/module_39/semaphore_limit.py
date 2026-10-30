import asyncio

async def generate(index: int, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        print("start", index)
        await asyncio.sleep(0.1)
        print("end", index)
        return f"result-{index}"

async def main() -> None:
    semaphore = asyncio.Semaphore(2)
    print(await asyncio.gather(*(generate(i, semaphore) for i in range(5))))

asyncio.run(main())
