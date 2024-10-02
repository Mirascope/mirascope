import asyncio

from mirascope.core import mistral, prompt_template


@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
