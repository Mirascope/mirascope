import asyncio

from mirascope.core import mistral


@mistral.call("mistral-large-latest")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
