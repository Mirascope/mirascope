import asyncio

from mirascope import llm


@llm.prompt
async def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    response: llm.AsyncResponse = await recommend_book("openai/gpt-5-mini", "fantasy")
    print(response.text())


asyncio.run(main())
