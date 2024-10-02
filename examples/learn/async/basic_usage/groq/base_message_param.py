import asyncio

from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-70b-versatile")
async def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
