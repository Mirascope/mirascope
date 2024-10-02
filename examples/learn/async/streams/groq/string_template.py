import asyncio

from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile", stream=True)
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
