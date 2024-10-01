import asyncio

from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
