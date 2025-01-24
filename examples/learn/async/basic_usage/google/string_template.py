import asyncio

from mirascope.core import google, prompt_template


@google.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
