import asyncio

from mirascope.core import bedrock


@bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
