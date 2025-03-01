import asyncio

from mirascope import llm


@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
