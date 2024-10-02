import asyncio

from mirascope.core import prompt_template, vertex


@vertex.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
