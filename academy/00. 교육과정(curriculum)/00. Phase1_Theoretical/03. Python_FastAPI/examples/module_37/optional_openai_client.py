import asyncio
import os

async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY가 없어 실제 호출을 건너뜁니다.")
        return

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key)
    response = await client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        input="FastAPI를 한 문장으로 설명하세요.",
    )
    print(response.output_text)

asyncio.run(main())
