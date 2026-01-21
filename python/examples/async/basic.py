import asyncio

from mirascope import llm


@llm.call("openai/gpt-5-mini")
async def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    response = await recommend_book("fantasy")
    print(response.text())


asyncio.run(main())
