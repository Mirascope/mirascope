import asyncio

from mirascope.core import gemini


@gemini.call("gemini-1.5-flash")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
