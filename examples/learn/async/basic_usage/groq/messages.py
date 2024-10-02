import asyncio

from mirascope.core import Messages, groq


@groq.call("llama-3.1-70b-versatile")
async def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
