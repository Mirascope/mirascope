import asyncio

from mirascope.core import azure, prompt_template


@azure.call(model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
