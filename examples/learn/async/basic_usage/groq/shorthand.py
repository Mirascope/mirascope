import asyncio

from mirascope.core import groq


@groq.call("llama-3.1-70b-versatile")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
