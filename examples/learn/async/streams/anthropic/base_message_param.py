import asyncio

from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-20240620", stream=True)
async def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())