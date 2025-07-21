import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response: llm.Response = await recommend_book.call("fantasy")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
