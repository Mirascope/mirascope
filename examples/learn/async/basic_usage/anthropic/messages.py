import asyncio

from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
async def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
