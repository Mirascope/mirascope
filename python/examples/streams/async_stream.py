import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream: llm.AsyncStream = recommend_book.stream_async("fantasy")
    async for chunk in stream:
        print(chunk, end="", flush=True)


asyncio.run(main())
