import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream = await recommend_book.stream("fantasy")
    async for chunk in stream:
        print(chunk, end="", flush=True)


asyncio.run(main())
