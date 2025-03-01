import asyncio

from mirascope import BaseMessageParam, llm


@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
async def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
