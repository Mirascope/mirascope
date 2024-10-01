import asyncio

from mirascope.core import Messages, gemini


@gemini.call("gemini-1.5-flash", stream=True)
async def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
