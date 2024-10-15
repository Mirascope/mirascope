import asyncio

from mirascope.core import Messages, bedrock


@bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
async def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
