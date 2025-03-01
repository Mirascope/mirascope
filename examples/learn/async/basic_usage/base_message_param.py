import asyncio

from mirascope import BaseMessageParam, llm


@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
