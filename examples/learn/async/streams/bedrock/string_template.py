import asyncio

from mirascope.core import bedrock, prompt_template


@bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
