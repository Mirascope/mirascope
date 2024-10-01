import asyncio

from mirascope.core import groq


@groq.call("llama-3.1-8b-instant", stream=True)
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
