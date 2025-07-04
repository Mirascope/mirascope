import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book.call_async("fantasy")  # [!code highlight]
    print(response.content)


asyncio.run(main())  # [!code highlight]
