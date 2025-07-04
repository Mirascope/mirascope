import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def recommend_book(genre: str) -> str:  # [!code highlight]
    return f"Recommend a {genre} book"


async def main():  # [!code highlight]
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())  # [!code highlight]
