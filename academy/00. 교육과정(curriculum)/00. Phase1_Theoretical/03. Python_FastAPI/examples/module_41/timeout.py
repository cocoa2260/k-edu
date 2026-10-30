import asyncio

async def slow_provider() -> str:
    await asyncio.sleep(1)
    return "done"

async def main() -> None:
    try:
        async with asyncio.timeout(0.1):
            print(await slow_provider())
    except TimeoutError:
        print("provider timeout")

asyncio.run(main())
