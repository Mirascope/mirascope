import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream: llm.AsyncStream = await recommend_book.stream("fantasy")
    async for content in stream:
        print(content, end="", flush=True)


asyncio.run(main())
