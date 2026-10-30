import asyncio

attempts = 0

async def unstable_provider() -> str:
    global attempts
    attempts += 1
    if attempts < 3:
        raise ConnectionError("temporary failure")
    return "success"

async def call_with_retry(max_attempts: int = 3) -> str:
    for attempt in range(1, max_attempts + 1):
        try:
            return await unstable_provider()
        except ConnectionError:
            if attempt == max_attempts:
                raise
            await asyncio.sleep(0.05 * attempt)
    raise RuntimeError("unreachable")

print(asyncio.run(call_with_retry()))
