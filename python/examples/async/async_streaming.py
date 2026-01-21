import asyncio

from mirascope import llm


@llm.call("openai/gpt-5-mini")
async def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    response = await recommend_book.stream("fantasy")
    async for chunk in response.text_stream():
        print(chunk, end="", flush=True)


asyncio.run(main())
